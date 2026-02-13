import json
import requests

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.schemas.activity import ActivityResponse
from config import OPENAI_API_KEY, OLLAMA_MODEL, OLLAMA_BASE_URL
from openai import OpenAI

from app.models.user import User
from app.models.user_info import UserInfo
from app.authentication.security import get_current_user, get_db
from sqlalchemy import desc

router = APIRouter()

openai_client = OpenAI(api_key=OPENAI_API_KEY)


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


@router.get("/activities_manual")
def get_activities_from_db(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    activities = db.query(Activity).filter_by(user_id=user.id, source='user').order_by(desc(Activity.id)).all()
    return {"activities": activities}


@router.get("/activities/{source}")
def get_activities_from_ai(source: str = "openai", user: User = Depends(get_current_user),
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

    Réponds UNIQUEMENT par un JSON valide. Aucun texte. Aucune explication. Aucun markdown. Pas de ```.
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
    if source == "openai":
        try:
            response = openai_client.chat.completions.create(model="gpt-4o-mini",
                                                             messages=[
                                                                 {"role": "system",
                                                                  "content":
                                                                      "Tu es un assistant expert"
                                                                      "en suggestions d'activités."},
                                                                 {"role": "user", "content": prompt}
                                                             ],
                                                             temperature=0.7,
                                                             max_tokens=800)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"{source} error: {response.text}")
            result_text = response.choices[0].message.content
        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=503, detail=f"Ollama is not running.Make sure {source} is started.")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"Invalid JSON response from {source}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{source} error: {str(e)}")

    elif source == "ollama":
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "temperature": 0.7,
                    "stream": False,
                    "format": "json"
                },
                timeout=120
            )
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"{source} error: {response.text}")
            result_text = response.json()["response"]
        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=503, detail=f"Ollama is not running.Make sure {source} is started.")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"Invalid JSON response from {source}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{source} error: {str(e)}")
    else:
        raise HTTPException(status_code=500, detail=f"source must be openai or ollama")

    result_json = json.loads(result_text)
    for activity in result_json['activities']:
        activity_obj = Activity(title=activity['title'],
                                description=activity['description'],
                                location=activity['location'],
                                duration=activity['duration'],
                                user_id=user.id,
                                source=source)
        db.add(activity_obj)
    db.commit()
    return result_json
