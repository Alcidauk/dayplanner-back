from sqlalchemy import Integer, Column, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.database import Base


class UserAvailability(Base):
    __tablename__ = "user_availability"
    id = Column(Integer, primary_key=True, index=True)

    starting_hour = Column(DateTime, index=True)
    ending_hour = Column(DateTime, index=True)
    available_days = Column(JSONB, index=True)
    user = relationship("User", back_populates="user_availability", uselist=False)


Index("ix_user_availability_available_days_category", UserAvailability.available_days['category'].astext,
      postgresql_using="btree"
      )
