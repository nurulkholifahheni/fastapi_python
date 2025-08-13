from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash, verify_password

# User CRUD

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    user_db = get_user(db, user_id)
    if not user_db:
        return None
    if user_update.username:
        user_db.username = user_update.username
    if user_update.email:
        user_db.email = user_update.email
    if user_update.password:
        user_db.hashed_password = get_password_hash(user_update.password)
    db.commit()
    db.refresh(user_db)
    return user_db

def delete_user(db: Session, user_id: int):
    user_db = get_user(db, user_id)
    if user_db:
        db.delete(user_db)
        db.commit()
    return user_db

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Content CRUD

def get_contents_by_owner(db: Session, owner_id: int):
    return db.query(models.Content).filter(models.Content.owner_id == owner_id).all()

def get_content(db: Session, content_id: int):
    return db.query(models.Content).filter(models.Content.id == content_id).first()

def create_content(db: Session, content: schemas.ContentCreate, owner_id: int):
    db_content = models.Content(**content.dict(), owner_id=owner_id)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def update_content(db: Session, content_id: int, content_update: schemas.ContentUpdate):
    content_db = get_content(db, content_id)
    if not content_db:
        return None
    if content_update.title is not None:
        content_db.title = content_update.title
    if content_update.body is not None:
        content_db.body = content_update.body
    db.commit()
    db.refresh(content_db)
    return content_db

def delete_content(db: Session, content_id: int):
    content_db = get_content(db, content_id)
    if content_db:
        db.delete(content_db)
        db.commit()
    return content_db
