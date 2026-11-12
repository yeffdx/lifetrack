from datetime import date

from app.extensions import db
from app.models import Goal, GoalUpdate
from .validation import ValidationError, optional_date, required_text


class GoalService:
    @staticmethod
    def _number(value: str | float | None, field: str) -> float:
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"{field} debe ser numérico.") from exc

    @staticmethod
    def create(data: dict) -> Goal:
        initial = GoalService._number(data.get("initial_value"), "El valor inicial")
        target = GoalService._number(data.get("target_value"), "El valor objetivo")
        if initial == target:
            raise ValidationError("El valor objetivo debe ser distinto del inicial.")
        goal = Goal(
            title=required_text(data.get("title"), "El título", 160),
            unit=required_text(data.get("unit"), "La unidad", 40),
            initial_value=initial, current_value=initial, target_value=target,
            start_date=optional_date(data.get("start_date"), "La fecha inicial") or date.today(),
            target_date=optional_date(data.get("target_date"), "La fecha objetivo"),
        )
        db.session.add(goal)
        db.session.flush()
        db.session.add(GoalUpdate(goal=goal, value=initial, recorded_at=goal.start_date))
        db.session.commit()
        return goal

    @staticmethod
    def update_progress(goal: Goal, value: str | float, recorded_at: str | None = None) -> Goal:
        number = GoalService._number(value, "El progreso")
        recorded = optional_date(recorded_at, "La fecha de actualización") or date.today()
        if recorded < goal.start_date:
            raise ValidationError("La actualización no puede ser anterior al inicio del objetivo.")
        goal.current_value = number
        if goal.reached_target:
            goal.status = "completed"
        db.session.add(GoalUpdate(goal=goal, value=number, recorded_at=recorded))
        db.session.commit()
        return goal

    @staticmethod
    def delete(goal: Goal) -> None:
        db.session.delete(goal)
        db.session.commit()
