from datetime import datetime

from sqlalchemy import select

from app.extensions import db
from app.models import Task, TaskEvent
from .validation import ValidationError, optional_date, required_text


class TaskService:
    priorities = {"low", "medium", "high"}

    @staticmethod
    def list_tasks(search: str = "", status: str = "") -> list[Task]:
        statement = select(Task).order_by(Task.status, Task.due_date.is_(None), Task.due_date, Task.created_at.desc())
        if search.strip():
            statement = statement.where(Task.title.ilike(f"%{search.strip()}%"))
        if status in {"pending", "completed"}:
            statement = statement.where(Task.status == status)
        return list(db.session.scalars(statement))

    @staticmethod
    def create(data: dict) -> Task:
        priority = data.get("priority", "medium")
        if priority not in TaskService.priorities:
            raise ValidationError("La prioridad no es válida.")
        task = Task(
            title=required_text(data.get("title"), "El título", 160),
            description=(data.get("description") or "").strip() or None,
            priority=priority,
            due_date=optional_date(data.get("due_date"), "La fecha de vencimiento"),
        )
        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def update(task: Task, data: dict) -> Task:
        priority = data.get("priority", "medium")
        if priority not in TaskService.priorities:
            raise ValidationError("La prioridad no es válida.")
        task.title = required_text(data.get("title"), "El título", 160)
        task.description = (data.get("description") or "").strip() or None
        task.priority = priority
        task.due_date = optional_date(data.get("due_date"), "La fecha de vencimiento")
        db.session.commit()
        return task

    @staticmethod
    def toggle_completion(task: Task) -> Task:
        if task.status == "completed":
            task.status, task.completed_at, event = "pending", None, "reopened"
        else:
            task.status, task.completed_at, event = "completed", datetime.utcnow(), "completed"
        db.session.add(TaskEvent(task=task, event_type=event))
        db.session.commit()
        return task

    @staticmethod
    def delete(task: Task) -> None:
        db.session.delete(task)
        db.session.commit()
