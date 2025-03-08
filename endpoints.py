from fastapi import FastAPI, Request
from models import RecurringTask

app = FastAPI()

@app.post("/recurring-task")
async def test(task: RecurringTask):
    print(task.data.properties)
    return { "success": True }