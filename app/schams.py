from pydantic import BaseModel , EmailStr 
from typing import Optional
from pydantic.types import conint

class PostBase(BaseModel):
    title : str
    content : str
    published : bool = True

class PostCreate(PostBase):
    pass

class User (BaseModel):
    id : int
    name : str
    email : EmailStr

    model_config = {
        "from_attributes" : True
    }

class Post(PostBase):
    id : int
    woner_id : int
    owner : User
    
    model_config = {
        "from_attributes": True
}

class PostWithVote(BaseModel):
    post : Post
    vote : int
    
    model_config = {
        "from_attributes": True
} 

class UserBase (BaseModel):
    name : str
    email : EmailStr
    password : str

class UserCreate(UserBase):
    pass 


class UserLogin (BaseModel):
    email : EmailStr
    password : str


class Token (BaseModel):
    access_token : str
    token_type : str

class TokenData ( BaseModel):
    id : Optional[str] = None
    
class Vote(BaseModel):
    post_id : int
    dir : conint(le=1)    
    
