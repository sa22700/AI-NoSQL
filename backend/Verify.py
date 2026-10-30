# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from fastapi import HTTPException
from backend.HttpException import raise_for_error
from core.ErrorLog import log_error
from core.Login import login_user

def verify_user(client, database_name: str, username: str, password: str) -> dict:
    try:
        user = login_user(
            client=client,
            database_name=database_name,
            username=username,
            password=password,
        )
        if user is None:
            out = {
                "ok": False,
                "error": "Invalid username or password",
            }
            raise_for_error(out)
        return user

    except HTTPException:
        raise

    except Exception as error:
        log_error(f"verify_user failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

def verify_admin(client, database_name: str, username: str, password: str) -> dict:
    user = verify_user(
        client=client,
        database_name=database_name,
        username=username,
        password=password,
    )
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    return user