import pytest

from app.extensions import db
from app.models import Task


@pytest.mark.parametrize("path", ["/", "/tasks/", "/habits/", "/goals/", "/calendar", "/analysis/"])
def test_pages_render_and_offer_all_appearances(client, path):
    response = client.get(path)
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert 'data-theme-select' in page
    for theme in ("light", "dark", "black"):
        assert f'value="{theme}"' in page


def test_task_creation_route_persists_task(client, app):
    response = client.post("/tasks/", data={"title": "Ruta probada", "priority": "low"})
    assert response.status_code == 302
    with app.app_context():
        assert db.session.query(Task).filter_by(title="Ruta probada").count() == 1


def test_post_without_csrf_is_rejected_when_enabled(client, app):
    app.config["CSRF_ENABLED"] = True
    response = client.post("/tasks/", data={"title": "No permitido", "priority": "low"})
    assert response.status_code == 400
