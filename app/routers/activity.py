import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import requests
from app.lib.rag import build_rag_prompt, call_llm
from app.models.activity import Activity
from app.schemas.activity import ActivityResponse

from app.models.user import User
from app.models.user_info import UserInfo
from app.authentication.security import get_current_user, get_db
from sqlalchemy import desc
from app.lib.retriever import fetch_real_places

router = APIRouter()


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


@router.delete("/delete_activity/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    activity = db.query(Activity).filter_by(id=activity_id, user_id=user.id, source="user").first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activité non trouvée"
        )
    db.delete(activity)
    db.commit()
    return


@router.get("/activities_manual")
def get_activities_from_db(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    activities = db.query(Activity).filter_by(user_id=user.id, source='user').order_by(desc(Activity.id)).all()
    return {"activities": activities}


@router.get("/activities/{source}")
def get_activities_from_ai(
    source: str = "openai",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_info = db.query(UserInfo).filter_by(user_id=user.id).first()
    if not user_info:
        raise HTTPException(status_code=404, detail="Infos utilisateur non trouvées")

    place = user_info.place
    interests = user_info.interests if isinstance(user_info.interests, list) else [user_info.interests]
    already_suggested = [a.title for a in db.query(Activity).filter_by(user_id=user.id).all()]

    real_places = fetch_real_places(place, interests, source=source)
    prompt = build_rag_prompt(place, interests, real_places, already_suggested)
    try:
        result_text = call_llm(source, prompt)
        result_json = json.loads(result_text)
        for activity in result_json["activities"]:
            db.add(Activity(
                title=activity["title"],
                description=activity["description"],
                location=activity["location"],
                duration=activity["duration"],
                user_id=user.id,
                source=source
            ))
        db.commit()
        return result_json
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail=f"{source} n'est pas en cours d'execution. Verifiez que {source}"
                                                    f"est démarré.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Réponse JSON invalide de {source}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur {source}: {str(e)}")
