from .. import models , schams , utils
from ..database import  SessionLocal , get_db
from sqlalchemy.orm import Session 
from fastapi import FastAPI , Response , status , HTTPException , Depends , APIRouter

router = APIRouter(
    prefix = "/user",
    tags = ['users']
)

#user API 
@router.post("/" , status_code = status.HTTP_201_CREATED , response_model = schams.User)
def create_user(user : schams.UserCreate , db : Session = Depends(get_db)):
    try:
       #cursor.execute(""" INSERT INTO users (name , email , password) VALUES(%s , %s , %s)RETURNING *; #""" , 
       #               (user.name , user.email , user.password))
       #new_user = cursor.fetchone()

       hash_pwd = utils.hash(user.password)
       user.password = hash_pwd

       new_user = models.User(**user.dict()) 
       db.add(new_user)
       db.commit()
       db.refresh(new_user)
       if not new_user:
           raise HTTPException(status_code=500 ,detail="Failed to create user")
       return new_user
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code = 500 , detail =f"Database Error: {str(e)}") 

@router.get("/" , response_model= list [schams.User])
def get_Users(db: Session = Depends(get_db)):
    user = db.query(models.User).all()

    return user

@router.get("/{id}" , response_model = schams.User)
def get_user (id : int , db : Session = Depends(get_db) ):

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = f"user with {id} was not found")
    return user

@router.delete("/{id}" , status_code = status.HTTP_204_NO_CONTENT)
def delete_user (id : int , db : Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id)

    if user.first() == None :
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = F"User with id : {id} not found") 
    user.delete(synchronize_session = False)
    db.commit()

    return Response(status_code = status.HTTP_204_NO_CONTENT)

@router.put("/{id}" , status_code=status.HTTP_200_OK , response_model = schams.User)
def update_user (id : int , updated_user : schams.UserCreate ,  db : Session = Depends(get_db)):

    user_query = db.query(models.User).filter(models.User.id == id)
 
    user = user_query.first()

    if user is None :
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = F"User with id : {id} not found")
    
    user_query.update(updated_user.dict() , synchronize_session=False)
    db.commit()
    updated = user_query.first()
    return updated