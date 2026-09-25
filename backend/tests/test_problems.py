from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_problems():

    response = client.get("/problems/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 3


def test_get_single_problem():

    response = client.get("/problems/1")

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Parking Lot"


def test_problem_not_found():

    response = client.get("/problems/99999")

    assert response.status_code == 404