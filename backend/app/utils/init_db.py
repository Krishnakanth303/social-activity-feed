from app.db import engine
from app.models.base import Base
from app.models.user import User
from app.models.post import Post
from app.models.like import Like
from app.models.follow import Follow
from app.models.block import Block
from app.models.activity import Activity

# Create all tables
Base.metadata.create_all(bind=engine)
