from sqlalchemy import Integer, Column, DateTime, JSON

from app.database.database import Base


class UserAvailability(Base):
    __tablename__ = "useravailability"
    id = Column(Integer, primary_key=True, index=True)

    starting_hour = Column(DateTime, index=True)
    ending_hour = Column(DateTime, index=True)
    available_days = Column(JSON, index=True)
