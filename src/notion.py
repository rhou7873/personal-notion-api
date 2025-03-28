import os
from datetime import date, datetime
from dateutils import relativedelta
from notion_client import AsyncClient
from typing import Dict, List
import logging
import requests


class NotionClientWrapper:

    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        self.__NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
        self.__CALENDAR_DB_ID = str(os.getenv("NOTION_CALENDAR_DB_ID"))
        self.__PUSH_API_URL = str(os.getenv("PUSH_API_URL"))
        self.__PUSH_API_USER_KEY = os.getenv("PUSH_API_USER_KEY")
        self.__PUSH_API_TOKEN = os.getenv("PUSH_API_TOKEN")

        self.__DATE_FORMAT = "%Y-%m-%d"
        self.__MY_DAY_URL = ("https://www.notion.so/1b1d368108968019a866d49dc1f784f5"
                             "?v=1b1d3681089680c6a94f000c5727cadb&pvs=4")
        self.__NOTION = AsyncClient(auth=self.__NOTION_API_TOKEN)

        if self.__class__ is None:
            raise Exception(
                "NOTION_CALENDAR_DB_ID environment variable isn't set")

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

        start_on_date = datetime.strptime(start_on, self.__DATE_FORMAT)
        end_on_date = datetime.strptime(
            end_on, self.__DATE_FORMAT) if end_on else None

        # add emoji to the recurring event page, just cuz
        await self.__NOTION.pages.update(recurring_event_id, icon={"emoji": "🔄"})

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
            page = await self.__NOTION.pages.retrieve(recurring_event_id)
            if page["in_trash"]:
                logging.info(
                    f"Recurring event (ID: {recurring_event_id}) was trashed")
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

    async def notify_of_my_day(self):
        # fetch today's tasks from Notion database
        params = {
            "database_id": self.__CALENDAR_DB_ID,
            "filter_properties": ["title"],
            "filter": {
                "and": [
                    {
                        "property": "Type",
                        "select": {
                            "equals": "Task"
                        }
                    },
                    {
                        "property": "Date",
                        "date": {
                            "on_or_before": datetime.now().strftime(self.__DATE_FORMAT)
                        }
                    },
                    {
                        "property": "Done",
                        "checkbox": {
                            "equals": False
                        }
                    }
                ]
            }
        }
        query_response = await self.__NOTION.databases.query(**params)
        todays_tasks = [task["properties"]["Name"]["title"][0]["plain_text"]
                        for task in query_response["results"]]

        # if there's no pending tasks today, don't send notification
        if len(todays_tasks) == 0:
            return

        # format tasks into bulleted list string
        todays_tasks_formatted = "\n"
        for task in todays_tasks:
            todays_tasks_formatted += f"\n\t- {task}"

        # send HTTP POST request to Pushover API to send mobile push notification
        params = {
            "token": self.__PUSH_API_TOKEN,
            "user": self.__PUSH_API_USER_KEY,
            "title": "My Day Reminder",
            "message": f"You have some pending tasks to complete today:{todays_tasks_formatted}",
            "url": self.__MY_DAY_URL,
            "url_title": "View My Day"
        }
        requests.post(url=self.__PUSH_API_URL, params=params)

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
                "database_id": self.__CALENDAR_DB_ID
            },
            "icon": {
                "emoji": "🔄",
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
                        "start": due_date.strftime(self.__DATE_FORMAT)
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

        return await self.__NOTION.pages.create(**payload)

    async def __delete_events(self, event_ids: List[str]):
        for id in event_ids:
            await self.__NOTION.pages.update(id, in_trash=True)
