from fastapi import FastAPI
from models import RecurringEvent
from notion import NotionClientWrapper

app = FastAPI()
client = NotionClientWrapper()


@app.post("/recurring-event")
async def recurring_event(task: RecurringEvent):
    properties = task.data.properties
    has_end_on = properties.end_on.date is not None

    await client.generate_recurring_event(
        recurring_event_id=task.data.id,
        title=properties.title.title[0].plain_text,
        type=properties.type.multi_select[0].name,
        tag=properties.tag.multi_select[0].name,
        start_on=properties.start_on.date.start,
        end_on=properties.end_on.date.start if has_end_on else None,
        frequency=properties.frequency.number,
        unit=properties.unit.multi_select[0].name
    )

    return {"success": True}


@app.get("/my-day-notification")
async def my_day_notification():
    await client.notify_of_my_day()
    return {"success": True}


@app.get("/test")
async def test():
    return {"success": True}
