import os
from datetime import date, datetime
from dateutils import relativedelta
from notion_client import AsyncClient
from typing import Dict, List
import logging

class NotionClientWrapper:

    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        self.DATE_FORMAT = "%Y-%m-%d"
        self.__notion = AsyncClient(auth=os.getenv("NOTION_API_TOKEN"))
        self.__calendar_db_id = str(os.getenv("NOTION_CALENDAR_DB_ID"))

        if self.__class__ is None:
            raise Exception("NOTION_CALENDAR_DB_ID environment variable isn't set")

    async def generate_recurring_event(self,
                                      recurring_event_id: str,
                                      title: str,
                                      type: str,
                                      tag: str,
                                      start_on: str,
                                      frequency: int,
                                      unit: str,
                                      end_on: str | None = None):
        """
        Generates the multiple instances of tasks for a given recurring task into
        my Calendar Database.
        """
        STANDARD_UNITS = {
            "Day(s)": "days",
            "Week(s)": "weeks",
            "Month(s)": "months",
            "Year(s)": "years"
        }
        unit = STANDARD_UNITS[unit]

        start_on_date = datetime.strptime(start_on, self.DATE_FORMAT)
        end_on_date = datetime.strptime(
            end_on, self.DATE_FORMAT) if end_on else None

        MAX_TASKS = {
            "days": 365,
            "weeks": 52,
            "months": 24,
            "years": 5
        }

        timedelta_params: Dict = {unit: frequency}
        current_date: date = start_on_date
        event_buffer: List[str] = []
        for _ in range(MAX_TASKS[unit]):
            if end_on_date and current_date > end_on_date:
                break
            
            # if recurring event is trashed during generation, stop future
            # generation and trash events that have already been generated
            page = await self.__notion.pages.retrieve(recurring_event_id)
            if page["in_trash"]:
                logging.info(f"Recurring event (ID: {recurring_event_id}) was trashed")
                await self.__delete_events(event_ids=event_buffer)
                break

            recurring_event_instance = await self.__create_event(
                title=title,
                due_date=current_date,
                type=type,
                tag=tag,
                recurring_event_id=recurring_event_id,
            )
            event_buffer.append(recurring_event_instance["id"])

            current_date += relativedelta(**timedelta_params)

    async def __create_event(self,
                            title: str,
                            due_date: date,
                            type: str,
                            tag: str,
                            recurring_event_id: str | None = None):
        """
        Creates a single Task in my Calendar Database.
        """

        # Structure of "New Page" for Calendar Database
        payload = {
            "parent": {
                "database_id": self.__calendar_db_id
            },
            "properties": {
                "Name": {
                    "id": "title",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": title,
                                "link": None
                            }
                        }
                    ]
                },
                "Done": {
                    "checkbox": False
                },
                "Type": {
                    "select": {
                        "name": type 
                    }
                },
                "Date": {
                    "date": {
                        "start": due_date.strftime(self.DATE_FORMAT)
                    }
                },
                "Tag": {
                    "select": {
                        "name": tag
                    }
                },
                "Recurring Event": {
                    "relation": [
                        {
                            "id": recurring_event_id
                        }
                    ]
                }
            }
        }

        return await self.__notion.pages.create(**payload)

    async def __delete_events(self, event_ids: List[str]):
        for id in event_ids:
            await self.__notion.pages.update(id, in_trash=True)