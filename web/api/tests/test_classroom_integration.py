from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_post_classroom():
    response = client.post("/classroom", json={"name":"advanced classroom", "hour":"10:00", "day": "2019-08-05"})

    assert response.status_code == 201