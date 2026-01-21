import os

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from dotenv import load_dotenv
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from passlib.context import CryptContext
from sqlalchemy import delete
from sqlalchemy import select

from database import new_session
from models.auth import BlacklistedTokenOrm
from models.auth import UserOrm
from repositories.auth import UserRepository




load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




def create_access_token(data: dict) -> str:
    """Создает JWT access токен."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt




async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserOrm:
    """Получает текущего пользователя на основе JWT токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    async with new_session() as session:
        query = delete(BlacklistedTokenOrm).where(
            BlacklistedTokenOrm.expires_at < datetime.now(timezone.utc)
        )
        await session.execute(query)
        await session.commit()
    
    async with new_session() as session:
        query = select(BlacklistedTokenOrm).where(BlacklistedTokenOrm.token == token)
        result = await session.execute(query)
        
        if result.scalars().first():
            raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = await UserRepository.get_user_by_email(email)
    
    if user is None:
        raise credentials_exception
    
    return user




def get_password_hash(password: str) -> str:
    """Создает хэш пароля."""
    return pwd_context.hash(password)