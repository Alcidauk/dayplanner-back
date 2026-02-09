from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    location = Column(String, index=True)
    duration = Column(String, index=True)
    user = relationship("User", back_populates="activities", uselist=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    source = Column(String, index=True)
