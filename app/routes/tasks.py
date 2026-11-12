from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.csrf import require_csrf
from app.extensions import db
from app.models import Task
from app.services import TaskService
from .helpers import handle_validation

tasks_bp = Blueprint("tasks", __name__)


def _task_or_404(task_id: int) -> Task:
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)
    return task


@tasks_bp.get("/")
def index():
    search, status = request.args.get("q", ""), request.args.get("status", "")
    return render_template("tasks.html", tasks=TaskService.list_tasks(search, status), search=search, status=status)


@tasks_bp.post("/")
@require_csrf
@handle_validation("tasks.index")
def create():
    TaskService.create(request.form)
    flash("Tarea creada.", "success")
    return redirect(url_for("tasks.index"))


@tasks_bp.get("/<int:task_id>/edit")
def edit(task_id: int):
    return render_template("task_edit.html", task=_task_or_404(task_id))


@tasks_bp.post("/<int:task_id>/edit")
@require_csrf
@handle_validation("tasks.index")
def update(task_id: int):
    TaskService.update(_task_or_404(task_id), request.form)
    flash("Tarea actualizada.", "success")
    return redirect(url_for("tasks.index"))


@tasks_bp.post("/<int:task_id>/toggle")
@require_csrf
def toggle(task_id: int):
    task = TaskService.toggle_completion(_task_or_404(task_id))
    flash("Tarea reabierta." if task.status == "pending" else "Tarea completada.", "success")
    return redirect(request.referrer or url_for("tasks.index"))


@tasks_bp.post("/<int:task_id>/delete")
@require_csrf
def delete(task_id: int):
    TaskService.delete(_task_or_404(task_id))
    flash("Tarea eliminada.", "success")
    return redirect(url_for("tasks.index"))
