from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.activity import Activity
from app.models.block import Block
from app.models.user import User
from jose import jwt, JWTError
import os
from typing import Optional

router = APIRouter(prefix="/activities/filters", tags=["activities"])
JWT_SECRET = os.getenv("JWT_SECRET", "changeme")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    from fastapi.security import OAuth2PasswordBearer
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
    token = oauth2_scheme()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("")
def get_filtered_activities(type: Optional[str] = None, actor_id: Optional[str] = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        blocked_by = db.query(Block.blocker_id).filter(Block.blocked_id == user.id).all()
        blocked_by_ids = [b[0] for b in blocked_by]
        query = db.query(Activity).filter(~Activity.actor_id.in_(blocked_by_ids))
        if type:
            query = query.filter(Activity.type == type)
        if actor_id:
            query = query.filter(Activity.actor_id == actor_id)
        activities = query.order_by(Activity.created_at.desc()).all()
        return [{"id": str(a.id), "type": a.type.value, "actor_id": str(a.actor_id), "target_id": str(a.target_id), "description": a.description, "created_at": a.created_at.isoformat()} for a in activities]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch filtered activities: {str(e)}")
