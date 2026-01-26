from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship


class GoogleAccount(Base):
    __tablename__ = "google_accounts"
    id = Column(Integer, primary_key=True, index=True)
    google_sub = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"), unique=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    token = relationship("Token",
                         back_populates="google_account",
                         uselist=True,
                         foreign_keys=[token_id]
                         )
    user = relationship("User",
                        back_populates="google_account",
                        uselist=False
                        )
