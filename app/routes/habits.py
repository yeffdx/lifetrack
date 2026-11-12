from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import select

from app.csrf import require_csrf
from app.extensions import db
from app.models import Habit
from app.services import HabitService
from app.services.validation import ValidationError
from .helpers import handle_validation

habits_bp = Blueprint("habits", __name__)


def _habit_or_404(habit_id: int) -> Habit:
    habit = db.session.get(Habit, habit_id)
    if habit is None:
        abort(404)
    return habit


@habits_bp.get("/")
def index():
    habits = list(db.session.scalars(select(Habit).order_by(Habit.active.desc(), Habit.name)))
    return render_template("habits.html", habits=habits, stats={habit.id: HabitService.stats(habit) for habit in habits}, today=date.today())


@habits_bp.post("/")
@require_csrf
@handle_validation("habits.index")
def create():
    HabitService.create(request.form)
    flash("Hábito creado.", "success")
    return redirect(url_for("habits.index"))


@habits_bp.get("/<int:habit_id>/edit")
def edit(habit_id: int):
    return render_template("habit_edit.html", habit=_habit_or_404(habit_id))


@habits_bp.post("/<int:habit_id>/edit")
@require_csrf
@handle_validation("habits.index")
def update(habit_id: int):
    HabitService.update(_habit_or_404(habit_id), request.form)
    flash("Configuración del hábito actualizada.", "success")
    return redirect(url_for("habits.index"))


@habits_bp.post("/<int:habit_id>/checkin")
@require_csrf
@handle_validation("habits.index")
def checkin(habit_id: int):
    day_text = request.form.get("date")
    try:
        selected = date.fromisoformat(day_text) if day_text else date.today()
    except ValueError as exc:
        raise ValidationError("La fecha de registro no es válida.") from exc
    HabitService.check_in(_habit_or_404(habit_id), selected)
    flash("Registro de hábito actualizado.", "success")
    return redirect(url_for("habits.index"))


@habits_bp.post("/<int:habit_id>/delete")
@require_csrf
def delete(habit_id: int):
    HabitService.delete(_habit_or_404(habit_id))
    flash("Hábito eliminado.", "success")
    return redirect(url_for("habits.index"))
