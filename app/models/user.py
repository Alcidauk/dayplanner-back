from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    google_account_id = Column(Integer, ForeignKey("google_accounts.id"), unique=True, nullable=True)
    email = Column(String, index=True)
    google_account = relationship("GoogleAccount", back_populates="user")
    user_info = relationship("UserInfo", back_populates="user", uselist=False)
    activities = relationship("Activity", back_populates="user", uselist=False)

