from typing import List

from fastapi import status, HTTPException, Depends, Response, APIRouter
from sqlalchemy.orm import Session
from ..schemas import PostCreate, Post, UserCreate, UserOut

from ..database import engine, get_db
from ..utils import hash

from .. import models

router = APIRouter(
    prefix="/users",
    tags=['Users']
)


# User
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # cursor.execute("INSERT into posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ;",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    # hash password - user.password
    # user_pwd = db.query(models.User).filter(models.User.password == user.password)
    # print(user_pwd)
    # if user_pwd.first():
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Password Already exists")
    # print(user_pwd)
    hashed_password = hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")

    return user