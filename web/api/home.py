from main import app


@app.get("/")
def hello_world():
    return {"message": "Hello world"}
