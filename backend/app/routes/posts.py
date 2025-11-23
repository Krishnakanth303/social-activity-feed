
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.post import Post
from app.models.user import User
from jose import jwt, JWTError
from pydantic import BaseModel
import os

router = APIRouter(prefix="/posts", tags=["posts"])
JWT_SECRET = os.getenv("JWT_SECRET", "changeme")

from pydantic import Field

class PostRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

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

@router.post("")
def create_post(data: PostRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not data.content or len(data.content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Post content cannot be empty")
    try:
        post = Post(user_id=user.id, content=data.content.strip())
        db.add(post)
        db.commit()
        db.refresh(post)
        return {"id": str(post.id), "content": post.content, "user_id": str(post.user_id)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")

@router.get("")
def list_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.is_deleted == False).all()
    return [{"id": str(p.id), "content": p.content, "user_id": str(p.user_id)} for p in posts]

@router.delete("/{id}")
def delete_post(id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != user.id and user.role.value not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    post.is_deleted = True
    db.commit()
    return {"detail": "Post deleted"}
