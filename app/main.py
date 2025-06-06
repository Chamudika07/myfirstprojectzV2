from fastapi import FastAPI
from .database import engine
from . import models 
from .routers import post , user , auth , vote
from .config import setting



models.Base.metadata.create_all(bind=engine)
app = FastAPI()
 
#def find_post_id(id):  
#    for p in my_post:
#        if p['id'] == id:
#            return p 

#def find_index_for_post(id):
#    for i , p in enumerate (my_post):
#        if p['id'] == id:
#            return i 

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

