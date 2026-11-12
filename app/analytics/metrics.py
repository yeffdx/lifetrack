"""Data transformations used by the dashboard and analysis screen."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from app.models import Goal, Habit, Task
from app.services.habits import HabitService


def _task_frame(tasks: list[Task]) -> pd.DataFrame:
    rows = [{"id": task.id, "status": task.status, "created_at": task.created_at, "completed_at": task.completed_at, "due_date": task.due_date} for task in tasks]
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=["id", "status", "created_at", "completed_at", "due_date"])
    for column in ("created_at", "completed_at", "due_date"):
        frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return frame


def dashboard_metrics(tasks: list[Task], habits: list[Habit], goals: list[Goal]) -> dict:
    frame = _task_frame(tasks)
    total = len(frame)
    completed = int((frame["status"] == "completed").sum()) if total else 0
    habit_stats = [HabitService.stats(habit) for habit in habits if habit.active]
    return {
        "pending_tasks": total - completed,
        "completed_tasks": completed,
        "task_completion": round((completed / total) * 100, 1) if total else None,
        "active_habits": len(habit_stats),
        "habit_completion": round(float(np.mean([stat["percent"] for stat in habit_stats])), 1) if habit_stats else None,
        "active_goals": sum(goal.status == "active" for goal in goals),
    }


def _recommendations(task_frame: pd.DataFrame, habit_stats: list[dict]) -> list[str]:
    recommendations = []
    if not task_frame.empty:
        completed = task_frame.dropna(subset=["completed_at"]).copy()
        if not completed.empty:
            completed["week"] = completed["completed_at"].dt.to_period("W")
            weekly = completed.groupby("week").size()
            if len(weekly) >= 2 and weekly.iloc[-1] < weekly.iloc[-2]:
                recommendations.append("La última semana registrada tiene menos tareas finalizadas que la anterior; revisa la planificación próxima.")
    if habit_stats and np.mean([stat["percent"] for stat in habit_stats]) < 50:
        recommendations.append("El cumplimiento promedio de hábitos está por debajo de 50 % en sus días programados; considera reducir temporalmente la carga o ajustar la frecuencia.")
    return recommendations


def build_analysis(tasks: list[Task], habits: list[Habit], goals: list[Goal]) -> dict:
    """Produces trace-ready data strictly from persisted records, never synthetic rows."""
    frame = _task_frame(tasks)
    completion_series: list[dict] = []
    activity_series: list[dict] = []
    weekly_series: list[dict] = []
    monthly_series: list[dict] = []
    period_comparison = None
    if not frame.empty:
        completed = frame.dropna(subset=["completed_at"]).copy()
        if not completed.empty:
            completed["day"] = completed["completed_at"].dt.date.astype(str)
            completion_series = [{"date": str(key), "count": int(value)} for key, value in completed.groupby("day").size().items()]
            completed["week"] = completed["completed_at"].dt.to_period("W")
            weekly = completed.groupby("week").size()
            weekly_series = [{"period": str(key), "count": int(value)} for key, value in weekly.items()]
            completed["month"] = completed["completed_at"].dt.to_period("M")
            monthly_series = [{"period": str(key), "count": int(value)} for key, value in completed.groupby("month").size().items()]
            if len(weekly) >= 2:
                previous, latest = int(weekly.iloc[-2]), int(weekly.iloc[-1])
                period_comparison = {"previous": previous, "latest": latest, "difference": latest - previous}
            completed["weekday"] = completed["completed_at"].dt.day_name()
            activity_series = [{"day": str(key), "count": int(value)} for key, value in completed.groupby("weekday", sort=False).size().items()]
    habit_stats = [{"name": habit.name, **HabitService.stats(habit)} for habit in habits if habit.active]
    goal_series = []
    for goal in goals:
        goal_series.append({"name": goal.title, "dates": [update.recorded_at.isoformat() for update in goal.updates], "values": [update.value for update in goal.updates], "unit": goal.unit})
    return {
        "task_completion": completion_series,
        "weekly_completion": weekly_series,
        "monthly_completion": monthly_series,
        "period_comparison": period_comparison,
        "activity": activity_series,
        "habits": habit_stats,
        "goals": goal_series,
        "recommendations": _recommendations(frame, habit_stats),
    }
