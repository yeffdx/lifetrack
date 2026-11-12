import calendar
from datetime import date

from flask import Blueprint, render_template, request
from sqlalchemy import select

from app.analytics import dashboard_metrics
from app.extensions import db
from app.models import Goal, Habit, Task

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def dashboard():
    tasks = list(db.session.scalars(select(Task)))
    habits = list(db.session.scalars(select(Habit)))
    goals = list(db.session.scalars(select(Goal)))
    recent_tasks = sorted(tasks, key=lambda task: task.created_at, reverse=True)[:6]
    return render_template("dashboard.html", metrics=dashboard_metrics(tasks, habits, goals), recent_tasks=recent_tasks, habits=habits)


@main_bp.get("/calendar")
def calendar_view():
    today = date.today()
    try:
        year = int(request.args.get("year", today.year))
        month = int(request.args.get("month", today.month))
        if not 1 <= month <= 12:
            raise ValueError
        current = date(year, month, 1)
    except ValueError:
        current = today.replace(day=1)
    tasks = list(db.session.scalars(select(Task).where(Task.due_date.is_not(None))))
    habits = list(db.session.scalars(select(Habit).where(Habit.active.is_(True))))
    goals = list(db.session.scalars(select(Goal).where(Goal.target_date.is_not(None))))
    events: dict[date, list[dict]] = {}
    for task in tasks:
        events.setdefault(task.due_date, []).append({"kind": "task", "label": task.title, "done": task.status == "completed"})
    for habit in habits:
        for week in calendar.monthcalendar(year, month):
            for day_number in week:
                if day_number:
                    day = date(year, month, day_number)
                    if habit.scheduled_on(day):
                        events.setdefault(day, []).append({"kind": "habit", "label": habit.name, "done": any(item.checkin_date == day and item.completed for item in habit.checkins)})
    for goal in goals:
        events.setdefault(goal.target_date, []).append({"kind": "goal", "label": goal.title, "done": goal.status == "completed"})
    previous = (current.replace(day=1) - date.resolution).replace(day=1)
    next_month = (current.replace(day=28) + date.resolution * 4).replace(day=1)
    return render_template("calendar.html", current=current, weeks=calendar.monthcalendar(year, month), events=events, previous=previous, next_month=next_month, today=today)
