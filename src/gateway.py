from fastapi import FastAPI
from models import RecurringEvent
from notion import NotionClientWrapper
from datetime import datetime

app = FastAPI()
client = NotionClientWrapper()

@app.post("/recurring-task")
async def test(task: RecurringEvent):
    properties = task.data.properties
    has_end_on = properties.end_on.date is not None

    await client.generate_recurring_event(
        recurring_event_id=task.data.id,
        title=properties.title.title[0].plain_text,
        type=properties.type.select.name,
        tag=properties.tag.multi_select[0].name,
        start_on=properties.start_on.date.start,
        end_on=properties.end_on.date.start if has_end_on else None,
        frequency=properties.frequency.number,
        unit=properties.unit.multi_select[0].name
    )

    return { "success": True }