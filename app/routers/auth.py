from fastapi import FastAPI , Response , status , HTTPException , Depends , APIRouter
from .. import utils , schams , models , oauth2
from sqlalchemy.orm import Session 
from ..database import  SessionLocal , get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags = ['Authentication']
)

@router.post("/login" , response_model = schams.Token)
#def login(user_credentials : schams.UserLogin , db : Session = Depends(get_db) ):
def login(user_credentials : OAuth2PasswordRequestForm = Depends() , db : Session = Depends(get_db) ):

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = f"invalide Email Credentials")
    
    if not utils.verify(user_credentials.password , user.password):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = f"invalide password Credentials")
    

    access_token = oauth2.create_access_token(data = {"user_id" : user.id })

    return {"access_token" : access_token , "token_type" : "bearer"}
