from typing import List, Optional
from fastapi import Depends

from fastapi import status, HTTPException, Depends, Response, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..schemas import PostCreate, Post, PostOut

from ..database import engine, get_db

from .. import models, oauth2

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# @router.get("/", response_model=List[Post])
@router.get("/", response_model=List[PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ''):
    # cursor.execute("SELECT * from posts")
    # posts = cursor.fetchall()
    # print(limit)
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes"))\
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)\
        .filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # print(results)
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    # print(current_user.id)
    # print(posts)
    # print(posts)
    return posts


# title str, content str
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("INSERT into posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ;",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    # print(user_id)
    # print(current_user.id)
    # print(current_user.email)
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=PostOut)
def get_post(id:int, db: Session = Depends(get_db), response_model=Post, current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("SELECT * FROM posts WHERE id = %s", str(id))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes"))\
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)\
        .filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with {id} was not found')
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail=f"Not Authorized to perform request")
    return post


@router.delete("/{id}")
def delete_post(id:int, status_code=status.HTTP_204_NO_CONTENT, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # deleting post
    # find the index of the post o be deleted
    # delete post with pop() method

    # cursor.execute("DELETE FROM posts WHERE id = %s returning *", str(id))
    # delete_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not Authorized to perform request")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}")
def update_post(id:int, updated_post: PostCreate, db: Session = Depends(get_db), response_model=Post, current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("UPDATE posts SET title=%s, content = %s, published =%s WHERE id =%s returning *",
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not Authorized to perform request")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
