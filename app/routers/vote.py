from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import schemas, database, models, oauth2
from ..websocket_manager import manager   # ✅ import the manager
from sqlalchemy.orm import Session

router = APIRouter(prefix="/vote", tags=['Vote'])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote(
    vote: schemas.Vote,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Check if post exists
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {vote.post_id} does not exist"
        )
    
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} has already voted on post {vote.post_id}"
            )

        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()

        # ✅ Find who owns this post
        post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

        # ✅ Don't notify if you voted on your own post
        if post and post.owner_id != current_user.id:
            await manager.send_notification(
                user_id=post.owner_id,
                message={
                    "type": "new_vote",
                    "message": f"{current_user.email} liked your post!",
                    "post_id": vote.post_id,
                }
            )

        return {"message": "Successfully added vote"}

    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote does not exist"
            )

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully deleted vote"}