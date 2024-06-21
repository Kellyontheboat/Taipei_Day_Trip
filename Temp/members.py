from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
import time
from database import execute_query

SECRET_KEY = "your_secret_key"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Member(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    token: str

# Verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Authenticate member
def authenticate_member(email: str, password: str):
    query = "SELECT id, email, password FROM members WHERE email = %s"
    result = execute_query(query, (email,))
    if result and verify_password(password, result[0]['password']):
        return result[0]
    return None

# Create JWT token
def create_access_token(data: dict, expires_delta: int = 3600):
    to_encode = data.copy()
    expire = time.time() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# Decode JWT token
def decode_access_token(token: str):
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_jwt
    except jwt.PyJWTError:
        return None

# Get current member from the token
def get_current_member(token: str):
    decoded_token = decode_access_token(token)
    if not decoded_token:
        return None
    query = "SELECT id, email FROM members WHERE email = %s"
    member = execute_query(query, (decoded_token["email"],))
    return member[0] if member else None

