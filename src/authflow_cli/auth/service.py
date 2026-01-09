from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import json
import os
from ..core.config import settings
from ..core.security import PasswordHasher

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    disabled: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserInDB(User):
    hashed_password: str

class AuthService:
    def __init__(self):
        self.db = self._load_db()

    def _load_db(self):
        """Loads the user database from a persistent JSON file."""
        if not os.path.exists(settings.CREDENTIALS_PATH):
            return {}
        with open(settings.CREDENTIALS_PATH, "r") as f:
            return json.load(f).get("users", {})

    def get_user(self, username: str) -> Optional[UserInDB]:
        """Looks up a user by their username."""
        user_data = self.db.get(username)
        return UserInDB(**user_data) if user_data else None

    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """Verifies username and password, returning user if valid."""
        user = self.get_user(username)
        if not user or not PasswordHasher.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Generates a signed JWT access token with optional expiration."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

auth_service = AuthService()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """FastAPI dependency to extract the user from a Bearer token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = auth_service.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure the user is active (not disabled)."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
