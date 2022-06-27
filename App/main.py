from typing import List

from fastapi import FastAPI, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .schemas import PostCreate, Post, UserCreate, UserOut

import psycopg2
from psycopg2.extras import RealDictCursor
import time

from . import models
from .database import engine, get_db
from .utils import hash

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(host='127.0.0.1', database='fastapi', user='allgift', password='Matt6:33',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Database connection was successful')
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error was", error)
        time.sleep(2)


# my_posts = [
#     {"title": "Post 1", "content": "Content Post 1", "id": 1},
#     {"title": "Post 2", "content": "Content Post 2", "id": 2},
# ]
#
#
# def find_post(id):
#     for p in my_posts:
#         if p['id'] == id:
#             return p
#
#
# def find_index_post(id):
#     for i, p in enumerate(my_posts):
#         if p['id'] == id:
#             return i


@app.get("/")
async def root():
    return {"message": "Welcome to myAPIs"}


@app.get("/posts", response_model=List[Post])
def get_posts(db: Session = Depends(get_db), response_model=Post):
    # cursor.execute("SELECT * from posts")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    # print(posts)
    return posts


# title str, content str
@app.post("/post", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("INSERT into posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ;",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{id}")
def get_post(id:int, db: Session = Depends(get_db), response_model=Post):
    # cursor.execute("SELECT * FROM posts WHERE id = %s", str(id))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with {id} was not found')
    return post


@app.delete("/posts/{id}")
def delete_post(id:int, status_code=status.HTTP_204_NO_CONTENT, db: Session = Depends(get_db)):
    # deleting post
    # find the index of the post o be deleted
    # delete post with pop() method

    # cursor.execute("DELETE FROM posts WHERE id = %s returning *", str(id))
    # delete_post = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with {id} does not exist")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id:int, updated_post: PostCreate, db: Session = Depends(get_db), response_model=Post):
    # cursor.execute("UPDATE posts SET title=%s, content = %s, published =%s WHERE id =%s returning *",
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with {id} does not exist")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


# User
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # cursor.execute("INSERT into posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ;",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    # hash password - user.password
    hashed_password = hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users/{id}", response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")

    return user