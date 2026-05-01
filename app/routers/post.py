from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from .. import models
from .. import schemas
from .. import oauth2
from ..database import get_db


router = APIRouter()


def _serialize_post(post: models.Post, votes: int):
    owner = post.owner
    return {
        "post": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "published": post.published,
            "created_at": post.created_at,
            "owner_id": post.owner_id,
            "owner": None if owner is None else {
                "id": owner.id,
                "email": owner.email,
                "created_at": owner.created_at,
            },
        },
        "votes": votes,
    }

# Root
@router.get("/")
def root():
    return {"message": "Hello World"}


# Get all posts
@router.get("/posts", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str]=""):
    
    
    posts=db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return [_serialize_post(post, votes) for post, votes in posts]


# Create post
@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostOut)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    
    new_post = models.Post(owner_id=current_user.id, **post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post



# Get single post
@router.get("/posts/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    post=db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )

    return _serialize_post(post[0], post[1])


# Delete post
@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )
     

    if post.owner_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Not authorized to perform  requested action")
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Update post
@router.put("/posts/{id}")
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )

    if post.owner_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Not authorized to perform  requested action")
    
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()