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
