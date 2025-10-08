"""
Authentication and Authorization Module.
Handles API security, rate limiting, and access control.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.core.config import get_settings
import time

settings = get_settings()

# Security schemas
api_key_header = APIKeyHeader(name="x-api-key", auto_error=True)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    """JWT token model."""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """JWT token data."""
    sub: str
    scopes: List[str]
    exp: int


class RateLimiter:
    """Rate limiter using Redis."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.window_size = 60  # 1 minute
        self.max_requests = settings.rate_limit_per_minute
        self._cache = {}  # In-memory cache for development
        
    async def is_rate_limited(self, key: str) -> bool:
        """Check if request should be rate limited."""
        current_time = time.time()
        window_start = current_time - self.window_size
        
        # Clean old entries
        self._cache = {
            k: v for k, v in self._cache.items() 
            if v > window_start
        }
        
        # Get requests in current window
        requests = len([t for t in self._cache.values() if t > window_start])
        
        if requests >= self.max_requests:
            return True
            
        self._cache[f"{key}:{current_time}"] = current_time
        return False


class SecurityManager:
    """Handles authentication, authorization and rate limiting."""
    
    def __init__(self):
        """Initialize security manager."""
        self.rate_limiter = RateLimiter()
        
    async def authenticate_api_key(
        self, 
        api_key: str = Security(api_key_header)
    ) -> bool:
        """Validate API key."""
        if api_key != settings.api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        return True
        
    def create_access_token(
        self,
        data: Dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({
            "exp": expire.timestamp(),
            "iat": datetime.utcnow().timestamp()
        })
        
        return jwt.encode(
            to_encode,
            settings.jwt_secret,
            algorithm="HS256"
        )
        
    async def verify_token(
        self,
        token: str = Depends(oauth2_scheme)
    ) -> TokenData:
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=["HS256"]
            )
            
            if payload.get("exp", 0) < time.time():
                raise HTTPException(
                    status_code=401,
                    detail="Token has expired"
                )
                
            return TokenData(
                sub=payload.get("sub"),
                scopes=payload.get("scopes", []),
                exp=payload.get("exp")
            )
            
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )
            
    async def check_rate_limit(self, key: str) -> None:
        """Check rate limit for API key."""
        if await self.rate_limiter.is_rate_limited(key):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
            
    def verify_scope(
        self,
        required_scope: str,
        token_data: TokenData = Depends(verify_token)
    ) -> bool:
        """Verify token has required scope."""
        if required_scope not in token_data.scopes:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        return True