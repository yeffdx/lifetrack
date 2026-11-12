from flask import Blueprint, render_template
from sqlalchemy import select
import plotly.graph_objects as go

from app.analytics import build_analysis
from app.extensions import db
from app.models import Goal, Habit, Task

analysis_bp = Blueprint("analysis", __name__)


def _chart(figure: go.Figure) -> str:
    figure.update_layout(template="plotly_white", margin=dict(l=35, r=20, t=40, b=35), height=290)
    return figure.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False})


@analysis_bp.get("/")
def index():
    analysis = build_analysis(list(db.session.scalars(select(Task))), list(db.session.scalars(select(Habit))), list(db.session.scalars(select(Goal))))
    task, activity, habit = analysis["task_completion"], analysis["activity"], analysis["habits"]
    charts = {
        "tasks": _chart(go.Figure(go.Scatter(x=[row["date"] for row in task], y=[row["count"] for row in task], mode="lines+markers", name="Tareas"))),
        "weekly": _chart(go.Figure(go.Bar(x=[row["period"] for row in analysis["weekly_completion"]], y=[row["count"] for row in analysis["weekly_completion"]], name="Semanal"))),
        "monthly": _chart(go.Figure(go.Bar(x=[row["period"] for row in analysis["monthly_completion"]], y=[row["count"] for row in analysis["monthly_completion"]], name="Mensual"))),
        "activity": _chart(go.Figure(go.Bar(x=[row["day"] for row in activity], y=[row["count"] for row in activity], name="Finalizadas"))),
        "habits": _chart(go.Figure(go.Bar(x=[row["name"] for row in habit], y=[row["percent"] for row in habit], name="Cumplimiento (%)"))),
    }
    goal_figure = go.Figure()
    for goal in analysis["goals"]:
        goal_figure.add_trace(go.Scatter(x=goal["dates"], y=goal["values"], mode="lines+markers", name=goal["name"]))
    charts["goals"] = _chart(goal_figure)
    return render_template("analysis.html", analysis=analysis, charts=charts)
