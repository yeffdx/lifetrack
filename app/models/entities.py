from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("priority IN ('low', 'medium', 'high')", name="valid_task_priority"),
        CheckConstraint("status IN ('pending', 'completed')", name="valid_task_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="pending")
    due_date: Mapped[date | None] = mapped_column(Date)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    events: Mapped[list[TaskEvent]] = relationship(back_populates="task", cascade="all, delete-orphan", order_by="TaskEvent.occurred_at")

    @property
    def is_overdue(self) -> bool:
        return self.status == "pending" and self.due_date is not None and self.due_date < date.today()


class TaskEvent(Base):
    __tablename__ = "task_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    task: Mapped[Task] = relationship(back_populates="events")


class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = (CheckConstraint("frequency IN ('daily', 'weekdays')", name="valid_habit_frequency"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    frequency: Mapped[str] = mapped_column(String(10), nullable=False, default="daily")
    # Monday=0 through Sunday=6. Empty means every day for daily habits.
    weekdays: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    start_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    checkins: Mapped[list[HabitCheckin]] = relationship(back_populates="habit", cascade="all, delete-orphan", order_by="HabitCheckin.checkin_date")

    def scheduled_on(self, day: date) -> bool:
        if day < self.start_date:
            return False
        if self.frequency == "daily":
            return True
        return str(day.weekday()) in self.weekdays.split(",")


class HabitCheckin(Base):
    __tablename__ = "habit_checkins"
    __table_args__ = (UniqueConstraint("habit_id", "checkin_date", name="one_checkin_per_habit_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True)
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    habit: Mapped[Habit] = relationship(back_populates="checkins")


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (CheckConstraint("status IN ('active', 'completed', 'paused')", name="valid_goal_status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    initial_value: Mapped[float] = mapped_column(Float, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    target_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(12), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updates: Mapped[list[GoalUpdate]] = relationship(back_populates="goal", cascade="all, delete-orphan", order_by="GoalUpdate.recorded_at")

    @property
    def progress_percent(self) -> float:
        denominator = self.target_value - self.initial_value
        if denominator == 0:
            return 0.0
        return ((self.current_value - self.initial_value) / denominator) * 100

    @property
    def reached_target(self) -> bool:
        return (self.target_value >= self.initial_value and self.current_value >= self.target_value) or (
            self.target_value < self.initial_value and self.current_value <= self.target_value
        )


class GoalUpdate(Base):
    __tablename__ = "goal_updates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today, index=True)
    goal: Mapped[Goal] = relationship(back_populates="updates")
