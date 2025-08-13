from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud, auth, dependencies
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI User & Content with JWT")

# Users

@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    updated_user = crud.update_user(db, user_id, user_update)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    crud.delete_user(db, user_id)
    return

# Authentication (token)

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Content

@app.get("/content/", response_model=List[schemas.ContentResponse])
def read_contents(db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    return crud.get_contents_by_owner(db, current_user.id)

@app.post("/content/", response_model=schemas.ContentResponse, status_code=status.HTTP_201_CREATED)
def create_content(content: schemas.ContentCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    return crud.create_content(db, content, current_user.id)

@app.get("/content/{content_id}", response_model=schemas.ContentResponse)
def read_content(content_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    content = crud.get_content(db, content_id)
    if content is None or content.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@app.put("/content/{content_id}", response_model=schemas.ContentResponse)
def update_content(content_id: int, content_update: schemas.ContentUpdate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    content = crud.get_content(db, content_id)
    if content is None or content.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Content not found or not authorized")
    return crud.update_content(db, content_id, content_update)

@app.delete("/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content(content_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    content = crud.get_content(db, content_id)
    if content is None or content.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Content not found or not authorized")
    crud.delete_content(db, content_id)
    return
