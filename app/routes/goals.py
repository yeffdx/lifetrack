from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import select

from app.csrf import require_csrf
from app.extensions import db
from app.models import Goal
from app.services import GoalService
from .helpers import handle_validation

goals_bp = Blueprint("goals", __name__)


def _goal_or_404(goal_id: int) -> Goal:
    goal = db.session.get(Goal, goal_id)
    if goal is None:
        abort(404)
    return goal


@goals_bp.get("/")
def index():
    return render_template("goals.html", goals=list(db.session.scalars(select(Goal).order_by(Goal.status, Goal.target_date))))


@goals_bp.post("/")
@require_csrf
@handle_validation("goals.index")
def create():
    GoalService.create(request.form)
    flash("Objetivo creado.", "success")
    return redirect(url_for("goals.index"))


@goals_bp.post("/<int:goal_id>/progress")
@require_csrf
@handle_validation("goals.index")
def progress(goal_id: int):
    GoalService.update_progress(_goal_or_404(goal_id), request.form.get("value"), request.form.get("recorded_at"))
    flash("Progreso registrado.", "success")
    return redirect(url_for("goals.index"))


@goals_bp.post("/<int:goal_id>/delete")
@require_csrf
def delete(goal_id: int):
    GoalService.delete(_goal_or_404(goal_id))
    flash("Objetivo eliminado.", "success")
    return redirect(url_for("goals.index"))
