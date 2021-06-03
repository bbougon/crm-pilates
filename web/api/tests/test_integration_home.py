from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_post_classroom():
    response = client.post("/classroom", json={"name":"advanced classroom", "schedule":"10:00", "start_date": "2019-07-07"})

    assert response.status_code == 201