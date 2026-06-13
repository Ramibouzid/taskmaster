import logging
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Project, Task
from app.forms import ProjectForm
from app.services import create_project

logger = logging.getLogger(__name__)
projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/")
@login_required
def list_projects():
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    return render_template("projects/list.html", projects=projects)


@projects_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = ProjectForm()
    if form.validate_on_submit():
        create_project(name=form.name.data, user_id=current_user.id,
                       description=form.description.data or "",
                       color=form.color.data or "#6366f1")
        flash("Project created!", "success")
        return redirect(url_for("projects.list_projects"))
    return render_template("projects/form.html", form=form, title="New Project")


@projects_bp.route("/<int:project_id>")
@login_required
def detail(project_id):
    project = db.session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        flash("Project not found.", "error")
        return redirect(url_for("projects.list_projects"))
    tasks = project.tasks.order_by(Task.position).all()
    return render_template("projects/detail.html", project=project, tasks=tasks)


@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit(project_id):
    project = db.session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        flash("Project not found.", "error")
        return redirect(url_for("projects.list_projects"))
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data or ""
        project.color = form.color.data or "#6366f1"
        db.session.commit()
        flash("Project updated!", "success")
        return redirect(url_for("projects.list_projects"))
    return render_template("projects/form.html", form=form, title="Edit Project", project=project)


@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
def delete(project_id):
    project = db.session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        flash("Project not found.", "error")
        return redirect(url_for("projects.list_projects"))
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted.", "info")
    return redirect(url_for("projects.list_projects"))
