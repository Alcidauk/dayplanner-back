from sqlalchemy import Column, Integer, String, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.database.database import Base
from sqlalchemy.orm import relationship


class UserInfo(Base):
    __tablename__ = "user_info"
    id = Column(Integer, primary_key=True, index=True)
    place = Column(String, index=True)
    interests = Column(JSONB, index=True)
    user = relationship("User", back_populates="user_info", uselist=False)
    user_id = Column(Integer, ForeignKey("users.id"))


Index('ix_user_interests_category', UserInfo.interests['category'].astext, postgresql_using='btree')


