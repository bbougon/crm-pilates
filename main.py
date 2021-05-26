from fastapi import FastAPI


app = FastAPI(
    title="CRM Pilates"
)

@app.get("/")
def hello_world():
    return {"message": "Hello world"}