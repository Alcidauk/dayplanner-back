from fastapi import APIRouter, Depends, HTTPException
from googleapiclient.discovery import build
from app.authentication.security import get_current_user
from app.lib.calendar_events import get_google_credentials, add_event_to_calendar
from app.models.user import User
from datetime import datetime
import traceback

router = APIRouter()


@router.get("/events")
def get_calendar_events(user: User = Depends(get_current_user), date=""):
    if not user.google_account_id:
        raise HTTPException(status_code=400, detail="Google account not linked")
    try:
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
                "summary": event.get("summary"),
                "start": event["start"].get("dateTime", event["start"].get("date")),
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "location": event.get("location"),
            }
            for event in events
        ]
        if date:
            date_events = []
            for event in formatted_events:
                event_start_date = event['start'].split('T')[0]
                target_date = date.split('T')[0]
                if event_start_date == target_date:
                    date_events.append(event)
            return {"events": date_events}
        return {"events": formatted_events}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add_google_event")
def add_google_event(event_body: dict, user: User = Depends(get_current_user)):
    if not user.google_account:
        raise HTTPException(status_code=403, detail="User not connected to Google")
    try:
        add_event_to_calendar(user, event_body)
        print(f'evenement ajouté: {event_body}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"success": True, "message": "Événement ajouté à Google Calendar"}
