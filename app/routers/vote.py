from fastapi import FastAPI , Response , status , HTTPException , Depends , APIRouter
from sqlalchemy.orm import Session 
from .. import models , schams , oauth2 , database
from ..database import SessionLocal , get_db 

router = APIRouter(
    prefix = "/vote",
    tags = ['Vote']
)

@router.post("/" , status_code = status.HTTP_201_CREATED)
def vote( vote : schams.Vote , db : Session = Depends(get_db) , current_user : int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    
    if not post :
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = f"post with id {vote.post_id} does not exits")
    
    
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id , models.Vote.user_id == current_user.id)
    
    found_vote = vote_query.first()
    
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT , detail = f"User {current_user.id} has alrady voted on post {vote.post_id}")
        
        new_vote = models.Vote(user_id = current_user.id , post_id = vote.post_id)  
        db.add(new_vote)  
        db.commit()
        db.refresh(new_vote)
        return {"massege" : "Successfully added vote"}
    
    else:
        if not found_vote :
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "Vote does not exist")
        
        vote_query.delete(synchronize_session = False)
        db.commit()
        
        return {"massege" : "succesfully deleted vote"}
        
        
    
    
    