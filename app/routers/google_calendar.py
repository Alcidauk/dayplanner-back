from fastapi import APIRouter, Depends, HTTPException
from googleapiclient.discovery import build
from app.authentication.security import get_current_user
from app.calendar_events import get_google_credentials
from app.models.user import User
from datetime import datetime

router = APIRouter()


@router.get("/events")
def get_calendar_events(user: User = Depends(get_current_user)):
    if not user.google_account_id:
        raise HTTPException(status_code=400, detail="Google account not linked")

    creds = get_google_credentials(user)
    service = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow().isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])

    formatted_events = [
        {
            "id": event.get("id"),
            "title": event.get("summary"),
            "start": event["start"].get("dateTime", event["start"].get("date")),
            "end": event["end"].get("dateTime", event["end"].get("date")),
            "location": event.get("location"),
        }
        for event in events
    ]

    return {"events": formatted_events}
