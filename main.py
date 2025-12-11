from fastapi import FastAPI
from app.database.database import engine, Base
from app.routers import user

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(user.router, prefix="/user", tags=["User"])

