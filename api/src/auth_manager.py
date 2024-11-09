import os
from typing import Optional

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError

from api.src.types.user import UserRow

bearer_scheme = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret")


def decode_jwt(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token

    :param token: The JWT token
    :return: Decoded payload if valid, otherwise raises an HTTPException
    """
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> UserRow:
    """
    Dependency that validates the JWT token from the Authorization header

    :param credentials: Bearer token credentials
    :return: Decoded JWT payload containing user details
    """
    token = credentials.credentials
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return payload
