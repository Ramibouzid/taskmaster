import logging
import traceback
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Task, Project
from app.forms import TaskForm
from app.services import create_task, update_task, delete_task, move_task

logger = logging.getLogger(__name__)
tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/")
@login_required
def board():
    try:
        projects = Project.query.filter_by(user_id=current_user.id).all()
        statuses = Task.STATUSES
        tasks_by_status = {}
        for s in statuses:
            tasks_by_status[s] = Task.query.filter_by(
                status=s
            ).filter(
                (Task.assignee_id == current_user.id) | (Task.created_by == current_user.id)
            ).order_by(Task.position).all()
        return render_template("tasks/board.html", tasks_by_status=tasks_by_status,
                               statuses=statuses, projects=projects)
    except Exception as e:
        logger.error("Board error: %s\n%s", str(e), traceback.format_exc())
        return render_template("errors/500.html"), 500


@tasks_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = TaskForm()
    form.project_id.choices = [(0, "No Project")] + [
        (p.id, p.name) for p in Project.query.filter_by(user_id=current_user.id).all()
    ]
    if form.validate_on_submit():
        pid = form.project_id.data if form.project_id.data and form.project_id.data != 0 else None
        max_pos = Task.query.filter_by(status=form.status.data).count()
        task = create_task(
            title=form.title.data,
            description=form.description.data or "",
            status=form.status.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            estimated_hours=form.estimated_hours.data,
            project_id=pid,
            created_by=current_user.id,
            assignee_id=current_user.id,
            position=max_pos,
        )
        flash("Task created!", "success")
        return redirect(url_for("tasks.board"))
    return render_template("tasks/form.html", form=form, title="New Task")


@tasks_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.board"))
    form = TaskForm(obj=task)
    form.project_id.choices = [(0, "No Project")] + [
        (p.id, p.name) for p in Project.query.filter_by(user_id=current_user.id).all()
    ]
    if form.validate_on_submit():
        pid = form.project_id.data if form.project_id.data and form.project_id.data != 0 else None
        update_task(task.id, title=form.title.data, description=form.description.data,
                    status=form.status.data, priority=form.priority.data,
                    due_date=form.due_date.data, estimated_hours=form.estimated_hours.data,
                    project_id=pid)
        flash("Task updated!", "success")
        return redirect(url_for("tasks.board"))
    if form.project_id.data is None and task.project_id:
        form.project_id.data = task.project_id
    return render_template("tasks/form.html", form=form, title="Edit Task", task=task)


@tasks_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete(task_id):
    if delete_task(task_id):
        flash("Task deleted.", "info")
    else:
        flash("Task not found.", "error")
    return redirect(url_for("tasks.board"))


@tasks_bp.route("/move", methods=["POST"])
@login_required
def move():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400
    task = move_task(data["task_id"], data["status"], data.get("position", 0))
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"ok": True})


@tasks_bp.route("/export-pdf")
@login_required
def export_pdf():
    from flask import send_file
    from app.services import generate_tasks_pdf
    tasks = Task.query.filter(
        (Task.assignee_id == current_user.id) | (Task.created_by == current_user.id)
    ).order_by(Task.position).all()
    buf = generate_tasks_pdf(tasks, current_user)
    return send_file(buf, mimetype="application/pdf", as_attachment=True,
                     download_name="task_report.pdf")


@tasks_bp.route("/<int:task_id>")
@login_required
def detail(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.board"))
    return render_template("tasks/detail.html", task=task)
