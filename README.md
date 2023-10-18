# otto
A minimalistic framework for adding skills to LLMs, taking into account agent multi-tenancy.



```python

import ottoai

import requests
from ics import Calendar

class ICalendar:
    def __init__(self, ical_link: str):
        self.ical_link = ical_link
        self.calendar = self._load_calendar()
    
    def _load_calendar(self) -> Calendar:
        # Fetch the ical content from the link
        response = requests.get(self.ical_link)
        response.raise_for_status()
        return Calendar(response.text)

    def search_events(self, start_time, end_time):
        # Filter events within the given time range
        return [event for event in self.calendar.events if start_time <= event.begin <= end_time]

    def get_calendar_details(self, start_time, end_time):
        events = self.search_events(start_time, end_time)
        details = []
        
        for event in events:
            detail = {
                'summary': event.name,
                'description': event.description,
                'begin': event.begin,
                'end': event.end,
                'attendees': [attendee for attendee in event.attendees],
            }
            
            if "zoom.us" in event.description or "zoom.us" in event.location:
                detail['location'] = 'Zoom Call'
            else:
                detail['location'] = event.location

            details.append(detail)
        
        return details



calendar_skill = ottoai.Skill(ICalendar)

calendar_skill.chat()

```

This will launch the skill and you can have around that skill.

```bash

Otto: "Hi! my name is Otto (you can change my name), and right now we are on the calendar skill, to get started, what is your calendar ilink"
You: "https://..."
Otto: "Perfect, what do you want to know from your calendar."
You: "Do I have in person meetings tomorrow?"
Otto: "What date is it tomorrow?"
You: "Tomorrow is October 18 2023"
Otto: "You have one event tomorrow at 213 vallejo st, san francisco california"

```



