from sqlalchemy import Column, Integer, String, JSON

from app.database.database import Base


class UserInfo(Base):
    __tablename__ = "userinfo"
    id = Column(Integer, primary_key=True, index=True)
    place = Column(String, index=True)
    interests = Column(JSON, index=True)


