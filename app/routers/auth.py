from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import schemas, models, utils,oauth2
from .. import database

router = APIRouter(tags=['Authentication'])

@router.post('/login')
def login(user_creadentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_creadentials.email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')
    
    is_valid_password = False
    try:
        is_valid_password = utils.verify(user_creadentials.password, user.password)
    except Exception:
        # Handle legacy rows where password is stored as plain text.
        is_valid_password = user_creadentials.password == user.password

    if not is_valid_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')
    
 
    access_token=oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token,"token_type": "bearer"}