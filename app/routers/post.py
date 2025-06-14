from sqlalchemy import func
from .. import models , schams , oauth2
from ..database import SessionLocal , get_db 
from sqlalchemy.orm import Session 
from fastapi import FastAPI , Response , status , HTTPException , Depends , APIRouter
from typing import List , Optional

router = APIRouter(
    prefix = "/post",
    tags = ['posts']
)
# post API 
@router.get("/" , response_model = List[schams.PostWithVote])
def get_posts(db: Session = Depends(get_db) , current_user : int = Depends(oauth2.get_current_user) , 
              limit : int = 100 , skip : int = 0 , search : Optional[str] = ""):

    #cursor.execute(""" SELECT * FROM posts """)
    #posts = cursor.fetchall()
    
    #posts = db.query(models.Post).filter(models.Post.woner_id == 
                                         #current_user.id).limit(limit).offset(skip).all()
                                         
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    posts = db.query(models.Post , func.count(models.Vote.post_id).label("vots")).join(models.Vote , models.Vote.post_id == models.Post.id , isouter = True
                                    ).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    #result = db.query(models.Post, func.count(models.Vote.post_id).label("vots"))\
    #    .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)\
    #    .filter(models.Post.title.contains(search))\
    #    .group_by(models.Post.id)\
    #    .limit(limit).offset(skip).all()   
    

    return [{"post": post, "vote": vote} for post, vote in posts]

@router.post("/",  status_code=status.HTTP_201_CREATED , response_model = schams.Post)
def create_post(post: schams.PostCreate , db : Session = Depends(get_db) , 
                current_user : int = Depends(oauth2.get_current_user)):
    try:
        #cursor.execute("""
        #    INSERT INTO posts (title, content, published)
        #    VALUES (%s, %s, %s)
        #    RETURNING *;
        #""", (post.title, post.content, post.published))
        new_post = models.Post(
            #title = post.title ,
            #content = post.content ,
            #published = post.published
            woner_id = current_user.id , **post.dict( )
        )
        

        #new_post = cursor.fetchone()  # Fetch the inserted row
        db.add(new_post)
        db.commit()  # Commit the transaction
        db.refresh(new_post)

        if not new_post:
            raise HTTPException(status_code=500, detail="Failed to create post")

        return new_post

    except Exception as e:
        db.rollback()  # Rollback the transaction to avoid an aborted state
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")


@router.get("/{id}" , response_model = schams.PostWithVote)
def get_post(id : int , db : Session = Depends(get_db) , current_user : int = 
             Depends(oauth2.get_current_user)):
    
    #cursor.execute(""" SELECT * FROM posts WHERE id = %s """ ,(str(id),))
    #post = cursor.fetchone()

    #post = find_post (id)

    #post = db.query(models.Post).filter(models.Post.id == id).first()
    
    post = db.query(models.Post , func.count(models.Vote.post_id).label("vots")).join(models.Vote , models.Vote.post_id == models.Post.id , isouter = True
                                    ).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , 
                            detail = f"post with {id} was not found")
        
    post_obj, vote = post
    return {"post": post_obj, "vote": vote}   
    
    
@router.delete("/{id}" , status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id : int , db : Session = Depends(get_db) , current_user : int = 
                Depends(oauth2.get_current_user)):
    
    #index = find_index_post(id)
    #cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", str((id),))
    #delete_post = cursor.fetchone()
    #conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()
    if post == None :
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , 
                            detail = f"Post with id : {id} not found")
    #my_post.pop(index)
    
    if post.woner_id != current_user.id :
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN , 
                            detail = "Not authorized to perform requested action")   

    post_query.delete(synchronize_session = False)
    db.commit()
    
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@router.put("/{id}" , status_code = status.HTTP_200_OK , response_model = schams.Post)
def update_post (id : int , updated_post : schams.PostCreate ,  db : Session = Depends(get_db) , 
                 current_user : int = Depends(oauth2.get_current_user)):

    #index = find_index_post(id)
    #cursor.execute("""UPDATE  posts SET title = %s, content = %s, published = %s  WHERE id = %s  returning *""", 
    #             (post.title , post.content , post.published , str((id),)))
    #update_post = cursor.fetchone()
    #conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None :
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , 
                            detail = F"Post with id : {id} not found")

    if post.woner_id != current_user.id :
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN , 
                            detail = "Not authorized to perform requested action")
    
    #post_dict = post.dict()
    #post_dict['id'] = id
    #my_post[index] = post_dict

    post_query.update(updated_post.dict() , synchronize_session=False)
    db.commit()
    updated = post_query.first()
    return updated