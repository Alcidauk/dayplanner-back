from fastapi import FastAPI
from app.database.database import engine, Base
from app.routers import user, auth, activity, google_calendar, user_info
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from config import SECRET_KEY, CORS_ORIGINS

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # pour tests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine, checkfirst=True)

app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(user_info.router, prefix="/user_info", tags=["User_Info"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(activity.router, prefix="/activity", tags=["Activity"])
app.include_router(google_calendar.router, prefix="/google_calendar", tags=["Google-Calendar"])

