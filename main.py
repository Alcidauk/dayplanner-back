from fastapi import FastAPI
from app.database.database import engine, Base
from app.routers import user, auth

app = FastAPI()
Base.metadata.create_all(bind=engine, checkfirst=True)

app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

