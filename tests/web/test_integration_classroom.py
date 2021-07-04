from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_post_classroom():
    response = client.post("/classrooms", json={"name":"advanced classroom", "start_date": "2019-08-05T10:00"})

    assert response.status_code == 201
    assert response.headers["Location"] == f"/classrooms/{response.json()['id']}"