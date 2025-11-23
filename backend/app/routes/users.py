
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.user import User
from app.models.follow import Follow
from app.models.block import Block
from jose import jwt, JWTError
from pydantic import BaseModel
import os

router = APIRouter(prefix="/users", tags=["users"])
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

@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {"id": str(user.id), "username": user.username, "email": user.email, "role": user.role.value}

@router.put("/me")
def update_me(username: str = None, email: str = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if username:
        user.username = username
    if email:
        user.email = email
    db.commit()
    db.refresh(user)
    return {"id": str(user.id), "username": user.username, "email": user.email}

@router.post("/{id}/follow")
def follow_user(id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not id or len(id) < 1:
        raise HTTPException(status_code=400, detail="User ID required")
    if id == str(user.id):
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    target = db.query(User).filter(User.id == id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if db.query(Follow).filter(Follow.follower_id == user.id, Follow.followed_id == id).first():
        raise HTTPException(status_code=400, detail="Already following")
    try:
        follow = Follow(follower_id=user.id, followed_id=id)
        db.add(follow)
        db.commit()
        return {"detail": f"Now following {target.username}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to follow user: {str(e)}")

@router.post("/{id}/block")
def block_user(id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not id or len(id) < 1:
        raise HTTPException(status_code=400, detail="User ID required")
    if id == str(user.id):
        raise HTTPException(status_code=400, detail="Cannot block yourself")
    target = db.query(User).filter(User.id == id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if db.query(Block).filter(Block.blocker_id == user.id, Block.blocked_id == id).first():
        raise HTTPException(status_code=400, detail="Already blocked")
    try:
        block = Block(blocker_id=user.id, blocked_id=id)
        db.add(block)
        db.commit()
        return {"detail": f"Blocked {target.username}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to block user: {str(e)}")

@router.delete("/{id}")

def delete_user(id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    target = db.query(User).filter(User.id == id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role.value not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(target)
    db.commit()
    return {"detail": "User deleted by {}".format(user.role.value)}

@router.post("/admins")
def create_admin(username: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role.value != "owner":
        raise HTTPException(status_code=403, detail="Only owner can create admins")
    target = db.query(User).filter(User.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.role = "admin"
    db.commit()
    return {"detail": f"{username} promoted to admin"}

@router.delete("/admins/{id}")
def delete_admin(id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role.value != "owner":
        raise HTTPException(status_code=403, detail="Only owner can delete admins")
    target = db.query(User).filter(User.id == id, User.role == "admin").first()
    if not target:
        raise HTTPException(status_code=404, detail="Admin not found")
    target.role = "user"
    db.commit()
    return {"detail": "Admin demoted to user"}
