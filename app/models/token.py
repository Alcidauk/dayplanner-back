from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship


class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    token_expiry = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    google_account_id = Column(Integer, ForeignKey("google_accounts.id"), nullable=True)
    user = relationship(
        "User",
        back_populates="token",
        uselist=False
    )
    google_account = relationship(
        "GoogleAccount",
        back_populates="token",
        uselist=False,
        foreign_keys="[GoogleAccount.token_id]"
    )

