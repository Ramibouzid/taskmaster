import io
import logging
from datetime import datetime, timezone

from app.extensions import db
from app.models import Task, Project, User

logger = logging.getLogger(__name__)


def create_task(title, created_by, **kwargs):
    task = Task(title=title, created_by=created_by, **kwargs)
    db.session.add(task)
    db.session.commit()
    logger.info("Task created: id=%s title=%s", task.id, task.title)
    return task


def update_task(task_id, **kwargs):
    task = db.session.get(Task, task_id)
    if not task:
        logger.warning("Task not found for update: id=%s", task_id)
        return None
    for key, value in kwargs.items():
        if value is not None and hasattr(task, key):
            setattr(task, key, value)
    task.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    logger.info("Task updated: id=%s", task_id)
    return task


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return False
    db.session.delete(task)
    db.session.commit()
    logger.info("Task deleted: id=%s", task_id)
    return True


def move_task(task_id, status, position):
    task = db.session.get(Task, task_id)
    if not task:
        return None
    task.status = status
    task.position = position
    task.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    logger.info("Task moved: id=%s -> %s", task_id, status)
    return task


def create_project(name, user_id, **kwargs):
    project = Project(name=name, user_id=user_id, **kwargs)
    db.session.add(project)
    db.session.commit()
    logger.info("Project created: id=%s name=%s", project.id, project.name)
    return project


def get_dashboard_stats(user_id):
    tasks = Task.query.filter(
        (Task.assignee_id == user_id) | (Task.created_by == user_id)
    )
    now = datetime.now(timezone.utc)
    return {
        "total": tasks.count(),
        "todo": tasks.filter(Task.status == "todo").count(),
        "in_progress": tasks.filter(Task.status == "in_progress").count(),
        "done": tasks.filter(Task.status == "done").count(),
        "overdue": tasks.filter(
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status != "done"
        ).count(),
        "projects": Project.query.filter(Project.user_id == user_id).count(),
    }


def generate_tasks_pdf(tasks, user):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Task Report - {user.name}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 7, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    statuses = ["backlog", "todo", "in_progress", "done"]
    labels = {"backlog": "Backlog", "todo": "To Do", "in_progress": "In Progress", "done": "Done"}
    for status in statuses:
        status_tasks = [t for t in tasks if t.status == status]
        if not status_tasks:
            continue
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(243, 244, 246)
        pdf.cell(0, 8, f" {labels[status]} ({len(status_tasks)})", new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.set_font("Helvetica", "", 10)
        for task in status_tasks:
            pdf.cell(0, 6, f"  {task.title}", new_x="LMARGIN", new_y="NEXT")
            detail = f"  Priority: {task.priority}"
            if task.due_date:
                detail += f" | Due: {task.due_date.strftime('%Y-%m-%d')}"
            if task.estimated_hours:
                detail += f" | Est: {task.estimated_hours}h"
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(0, 5, detail, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
        pdf.ln(3)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf
