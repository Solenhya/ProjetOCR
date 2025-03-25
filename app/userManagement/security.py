from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashing and password verification functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT token creation function
def create_access_token(data: dict, expires_delta: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")):
    to_encode = data.copy()
    expires_delta=int(expires_delta)
    expire = datetime.now() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt