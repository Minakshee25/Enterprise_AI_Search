import jwt

from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.config import settings


security = HTTPBearer()


TENANT_ID = settings.entra_tenant_id

ISSUER = (
    f"https://login.microsoftonline.com/"
    f"{TENANT_ID}/v2.0"
)

JWKS_URL = (
    f"https://login.microsoftonline.com/"
    f"{TENANT_ID}/discovery/v2.0/keys"
)


jwks_client = jwt.PyJWKClient(
    JWKS_URL
)

async def validate_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
):
    token = credentials.credentials

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(
            token
        )

        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.entra_api_client_id,
            issuer=ISSUER,
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token",
        )

    scopes = claims.get(
        "scp",
        "",
    ).split()

    if "access_as_user" not in scopes:
        raise HTTPException(
            status_code=403,
            detail="Missing required scope",
        )

    return claims