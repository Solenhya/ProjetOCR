from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.userManagement.security import verify_password, create_access_token
from app.userManagement.userAccess import get_user
from jose import JWTError,jwt
from typing import Optional
import os

class Token(BaseModel):
    access_token: str
    token_type: str

async def login_for_access_token(form_data: OAuth2PasswordRequestForm):
    # Use your user verification logic here
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.userPassword):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Create and return token
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Exception for authentication errors
credentials_exception = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str):
    # Use JWT decoding and validation logic here
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception