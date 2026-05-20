from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import schemas, models, utils, oauth2
from .. import database

router = APIRouter(
    tags=["Authentication"]
)

@router.post('/login')
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')
    
    is_valid_password = False
    try:
        is_valid_password = utils.verify(user_credentials.password, user.password)
    except Exception:
        # Handle legacy rows where password is stored as plain text.
        is_valid_password = user_credentials.password == user.password

    if not is_valid_password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')
    
 
    access_token=oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token,"token_type": "bearer"}