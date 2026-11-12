from datetime import date, timedelta

from sqlalchemy import select

from app.extensions import db
from app.models import Habit, HabitCheckin
from .validation import ValidationError, optional_date, required_text


class HabitService:
    @staticmethod
    def _weekdays(data: dict) -> str:
        frequency = data.get("frequency", "daily")
        if frequency not in {"daily", "weekdays"}:
            raise ValidationError("La frecuencia no es válida.")
        values = sorted({str(value) for value in data.getlist("weekdays")}) if hasattr(data, "getlist") else sorted(set(data.get("weekdays", [])))
        if frequency == "weekdays" and (not values or any(value not in {str(i) for i in range(7)} for value in values)):
            raise ValidationError("Selecciona al menos un día de la semana.")
        return ",".join(values) if frequency == "weekdays" else ""

    @staticmethod
    def create(data: dict) -> Habit:
        start_date = optional_date(data.get("start_date"), "La fecha inicial") or date.today()
        habit = Habit(
            name=required_text(data.get("name"), "El nombre", 120),
            frequency=data.get("frequency", "daily"),
            weekdays=HabitService._weekdays(data),
            start_date=start_date,
        )
        db.session.add(habit)
        db.session.commit()
        return habit

    @staticmethod
    def update(habit: Habit, data: dict) -> Habit:
        habit.name = required_text(data.get("name"), "El nombre", 120)
        habit.frequency = data.get("frequency", "daily")
        habit.weekdays = HabitService._weekdays(data)
        habit.start_date = optional_date(data.get("start_date"), "La fecha inicial") or habit.start_date
        habit.active = data.get("active") == "on"
        db.session.commit()
        return habit

    @staticmethod
    def check_in(habit: Habit, checkin_day: date | None = None) -> HabitCheckin:
        checkin_day = checkin_day or date.today()
        if checkin_day > date.today() or not habit.scheduled_on(checkin_day):
            raise ValidationError("Solo puedes registrar días programados que ya ocurrieron.")
        checkin = db.session.scalar(select(HabitCheckin).where(HabitCheckin.habit_id == habit.id, HabitCheckin.checkin_date == checkin_day))
        if checkin:
            checkin.completed = not checkin.completed
        else:
            checkin = HabitCheckin(habit=habit, checkin_date=checkin_day, completed=True)
            db.session.add(checkin)
        db.session.commit()
        return checkin

    @staticmethod
    def stats(habit: Habit, end: date | None = None) -> dict:
        """Pure date iteration: absent past check-ins count as missed scheduled days."""
        end = min(end or date.today(), date.today())
        if habit.start_date > end:
            return {"scheduled": 0, "completed": 0, "percent": 0.0, "current_streak": 0, "max_streak": 0}
        completed = {item.checkin_date for item in habit.checkins if item.completed}
        days = []
        cursor = habit.start_date
        while cursor <= end:
            if habit.scheduled_on(cursor):
                days.append(cursor)
            cursor += timedelta(days=1)
        flags = [day in completed for day in days]
        maximum = current = 0
        for flag in flags:
            current = current + 1 if flag else 0
            maximum = max(maximum, current)
        trailing = 0
        for flag in reversed(flags):
            if not flag:
                break
            trailing += 1
        return {
            "scheduled": len(days), "completed": sum(flags),
            "percent": round((sum(flags) / len(days)) * 100, 1) if days else 0.0,
            "current_streak": trailing, "max_streak": maximum,
        }

    @staticmethod
    def delete(habit: Habit) -> None:
        db.session.delete(habit)
        db.session.commit()
