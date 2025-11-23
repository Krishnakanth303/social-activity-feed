import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.models.base import Base
import enum

class ActivityType(enum.Enum):
    post = "post"
    like = "like"
    follow = "follow"
    delete_user = "delete_user"
    delete_post = "delete_post"
    block = "block"

class Activity(Base):
    __tablename__ = "activities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(ActivityType), nullable=False)
    target_id = Column(UUID(as_uuid=True))  # Can be user or post
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
