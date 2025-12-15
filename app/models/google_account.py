from sqlalchemy import Column, Integer, String, DateTime
from app.database.database import Base
from sqlalchemy.orm import relationship


class GoogleAccount(Base):
    __tablename__ = "google_accounts"
    id = Column(Integer, primary_key=True, index=True)
    google_sub = Column(String)
    email = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    token_expiry = Column(DateTime)
    user = relationship("User", back_populates="google_account", uselist=False)
