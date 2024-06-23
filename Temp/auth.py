from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import jwt
import time
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED

# Secret key for JWT encoding/decoding
SECRET_KEY = "secret_key_for_JWT"

# Define password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create FastAPI instance
app = FastAPI()

# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/user/auth")
