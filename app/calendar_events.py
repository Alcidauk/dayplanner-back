"""
# TODO je l'ai mis la pour le moment ce sera utilisable plus tard
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from app.models.user import User
from app.authentication.security import decrypt_token

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


def get_google_credentials(user: User):
    return Credentials(
        token=decrypt_token(user.google_account.access_token),
        refresh_token=decrypt_token(user.google_account.refresh_token),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )


def add_event_to_calendar(user: User, event_body: dict):
    creds = get_google_credentials(user)
    service = build("calendar", "v3", credentials=creds)
    service.events().insert(calendarId="primary", body=event_body).execute()
