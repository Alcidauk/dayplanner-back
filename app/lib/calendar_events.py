"""
# TODO je l'ai mis la pour le moment ce sera utilisable plus tard
"""
from fastapi import HTTPException
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from app.models.user import User
from app.authentication.security import decrypt_token

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


def get_google_credentials(user: User):
    credentials = Credentials(
        token=decrypt_token(user.google_account.token[0].google_access_token),
        refresh_token=decrypt_token(user.google_account.token[0].google_refresh_token),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(GoogleRequest())
    return credentials


def add_event_to_calendar(user: User, event_body: dict):
    try:
        creds = get_google_credentials(user)
        service = build("calendar", "v3", credentials=creds)

        event_dict = {
            "summary": event_body.get("summary", "Nouvel événement"),
            "description": event_body.get("description", ""),
            "location": event_body.get("location", ""),
            "start": {
                "dateTime": event_body["start"],
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": event_body["end"],
                "timeZone": "UTC"
            }
        }
        created_event = service.events().insert(calendarId="primary", body=event_dict).execute()
        return {"success": True, "event": created_event}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Calendar error: {str(e)}")