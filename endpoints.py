from fastapi import FastAPI

app = FastAPI()

@app.post("/recurring-task")
async def test():
    print("hit the test endpoint")
    return {"message": "Hello World"}