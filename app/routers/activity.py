import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.schemas.activity import ActivityResponse, ActivityCreate
from config import OPENAI_API_KEY
from openai import OpenAI

from app.models.user import User
from app.models.user_info import UserInfo
from app.authentication.security import get_current_user, get_db

router = APIRouter()

client = OpenAI(api_key=OPENAI_API_KEY)


@router.post("/add_activity", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def add_activity(activity: dict,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):

    activity_obj = Activity(title=activity['title'],
                            description=activity['description'],
                            location=activity['location'],
                            duration=activity['duration'],
                            user_id=user.id,
                            source='user'
                            )
    db.add(activity_obj)
    db.commit()
    return activity_obj


@router.get("/activities")
def get_activities(user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    user_info = db.query(UserInfo).filter_by(user_id=user.id).first()
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User info not found")

    place = user_info.place
    interests = user_info.interests
    already_suggested_activities = db.query(Activity).filter_by(user_id=user.id).all()
    prompt = f"""
    Tu es une API.

    Réponds UNIQUEMENT par un JSON valide.
    Aucun texte.
    Aucune explication.
    Aucun markdown.
    Pas de ```.

    Format EXACT attendu :
    {{
      "activities": [
        {{
          "title": "string",
          "description": "string",
          "location": "string",
          "duration": "string"
        }}
      ]
    }}

    Lieu : {place}
    Centres d'intérêt : {', '.join(interests) if isinstance(interests, list) else interests}
    Les activités proposées ne doivent pas figurer 
    dans la liste des activités déjà proposées : {[asa.title for asa in already_suggested_activities]} 
    et doivent être des activités réelles
    """

    try:
        response = client.chat.completions.create(model="gpt-4o-mini",
                                                  messages=[
                                                      {"role": "system",
                                                       "content":
                                                           "Tu es un assistant expert en suggestions d'activités."},
                                                      {"role": "user", "content": prompt}
                                                  ],
                                                  temperature=0.7,
                                                  max_tokens=800)
        result_text = response.choices[0].message.content
        result_json = json.loads(result_text)
        for activity in result_json['activities']:
            activity_obj = Activity(title=activity['title'],
                                    description=activity['description'],
                                    location=activity['location'],
                                    duration=activity['duration'],
                                    user_id=user.id,
                                    source='openai')
            db.add(activity_obj)
        db.commit()
        return result_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")
