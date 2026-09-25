from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_empty_solution_rejected():

    response = client.post(
        "/attempts/",
        json={
            "problem_id": 1,
            "solution": ""
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Solution cannot be empty"
    )

def test_invalid_problem_submission():
    response = client.post(
        "/attempts/",
        json={
            "problem_id": 9999,
            "solution": "class ParkingLot {}",
        },
    )

    assert response.status_code == 404