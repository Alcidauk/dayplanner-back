from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

# Crée le moteur de base de données
engine = create_engine(DATABASE_URL)

# Crée une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base de déclaration des modèles SQLAlchemy
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
