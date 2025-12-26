from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config import OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

from app.models.user import User
from app.models.user_info import UserInfo
from app.authentication.security import get_current_user, get_db

router = APIRouter()


@router.get("/activities")
def get_activities(user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    user_info = db.query(UserInfo).filter_by(user_id=user.id).first()
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User info not found")

    place = user_info.place
    interests = user_info.interests

    prompt = f"""
    Je suis un assistant qui recommande des activités. 
    L'utilisateur se trouve à {place} et ses centres d'intérêt sont : 
{', '.join(interests) if isinstance(interests, list) else interests}.
    Peux-tu me proposer une liste de 5 activités adaptées à ce lieu et à ses intérêts ?
    Merci de répondre sous forme de json exploitable directement par une application front
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
                                                  max_tokens=300)
        result_json = response.choices[0].message.content
        return {"activities": result_json}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")
