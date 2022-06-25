from typing import Optional

from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel

import psycopg2
from psycopg2.extras import RealDictCursor
import time

from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None


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


my_posts = [
    {"title": "Post 1", "content": "Content Post 1", "id": 1},
    {"title": "Post 2", "content": "Content Post 2", "id": 2},
]


def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
async def root():
    return {"message": "Welcome to myAPIs"}


@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * from posts")
    posts = cursor.fetchall()
    # print(posts)
    return {"data": posts}


# title str, content str
@app.post("/post", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("INSERT into posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ;",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id:int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", str(id))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with {id} was not found')
    return {"post_detail": post}


@app.delete("/posts/{id}")
def delete_post(id:int, status_code=status.HTTP_204_NO_CONTENT):
    # deleting post
    # find the index of the post o be deleted
    # delete post with pop() method
    cursor.execute("DELETE FROM posts WHERE id = %s returning *", str(id))
    delete_post = cursor.fetchone()
    conn.commit()
    if delete_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id:int, post: Post):
    cursor.execute("UPDATE posts SET title=%s, content = %s, published =%s WHERE id =%s returning *",
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with {id} does not exist")
    return {"data": updated_post}
