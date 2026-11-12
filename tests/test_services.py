from datetime import date, timedelta

import pytest
from sqlalchemy import select

from app.analytics import build_analysis, dashboard_metrics
from app.extensions import db
from app.models import Goal, Habit, Task
from app.services import GoalService, HabitService, TaskService
from app.services.validation import ValidationError


def test_task_lifecycle_preserves_completion_history(app):
    with app.app_context():
        task = TaskService.create({"title": "Entregar informe", "priority": "high", "due_date": "2026-12-01"})
        TaskService.toggle_completion(task)
        TaskService.toggle_completion(task)
        stored = db.session.get(Task, task.id)
        assert stored.status == "pending"
        assert [event.event_type for event in stored.events] == ["completed", "reopened"]


def test_task_rejects_missing_title(app):
    with app.app_context(), pytest.raises(ValidationError):
        TaskService.create({"title": "   ", "priority": "medium"})


def test_habit_uses_only_scheduled_past_days_for_streak(app):
    today = date.today()
    with app.app_context():
        habit = HabitService.create({"name": "Leer", "frequency": "daily", "start_date": (today - timedelta(days=2)).isoformat()})
        HabitService.check_in(habit, today - timedelta(days=2))
        HabitService.check_in(habit, today)
        stats = HabitService.stats(habit)
        assert stats["scheduled"] == 3
        assert stats["completed"] == 2
        assert stats["max_streak"] == 1
        assert stats["current_streak"] == 1


def test_goal_progress_supports_decreasing_target(app):
    with app.app_context():
        goal = GoalService.create({"title": "Reducir tiempo", "unit": "minutos", "initial_value": "60", "target_value": "30"})
        GoalService.update_progress(goal, "30")
        assert goal.status == "completed"
        assert goal.progress_percent == 100.0


def test_dashboard_and_analysis_are_based_on_persisted_entities(app):
    with app.app_context():
        task = TaskService.create({"title": "Tarea real", "priority": "medium"})
        TaskService.toggle_completion(task)
        habit = HabitService.create({"name": "Caminar", "frequency": "daily"})
        HabitService.check_in(habit)
        goal = GoalService.create({"title": "Escribir", "unit": "páginas", "initial_value": "0", "target_value": "10"})
        metrics = dashboard_metrics([task], [habit], [goal])
        analysis = build_analysis([task], [habit], [goal])
        assert metrics["completed_tasks"] == 1
        assert metrics["active_habits"] == 1
        assert analysis["task_completion"]
        assert analysis["habits"][0]["name"] == "Caminar"
