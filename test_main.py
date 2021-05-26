from fastapi.testclient import TestClient

from classroom_creation import ClassroomCreation
from main import app, create_classroom

client = TestClient(app)


def test_hello_world():
    response = client.get("")

    assert response.status_code == 200
    assert response.json()["message"] == "Hello world"
 

def test_post_classroom():
    response = client.post("/classroom", json={"name":"advanced classroom", "hour":"10:00"})
    
    assert response.status_code == 201


def test_create_classroom():
    classroom_json = {"name":"advanced classroom", "hour":"10:00"}

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json))

    assert response["name"] == "advanced classroom"
    assert response["hour"] == "10:00"
    assert response["id"]