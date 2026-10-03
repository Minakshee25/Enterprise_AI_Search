from uuid import UUID

from fastapi import Depends, HTTPException

from app.auth.entra import validate_access_token
from app.db.database import get_pool


async def get_current_user(
    claims: dict = Depends(validate_access_token),
) -> UUID:

    oid = claims.get("oid")
    tid = claims.get("tid")

    if not oid or not tid:
        raise HTTPException(
            status_code=401,
            detail="Token does not contain oid/tid",
        )

    email = claims.get("preferred_username")
    display_name = claims.get("name")

    db = get_pool()

    user_id = await db.fetchval(
        """
        INSERT INTO users (
            entra_object_id,
            tenant_id,
            email,
            display_name
        )
        VALUES ($1, $2, $3, $4)

        ON CONFLICT (
            tenant_id,
            entra_object_id
        )

        DO UPDATE SET
            email = EXCLUDED.email,
            display_name = EXCLUDED.display_name,
            updated_at = NOW()

        RETURNING id
        """,
        UUID(oid),
        UUID(tid),
        email,
        display_name,
    )

    return user_id