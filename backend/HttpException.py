from fastapi import HTTPException

def raise_for_error(out: dict) -> None:
    error = out.get("error")
    if not error:
        return
    if error in (
        "Wrong username or password",
        "Login failed",
        "Invalid username or password",
    ):
        raise HTTPException(status_code=401, detail=error)
    if error in (
        "Admin required",
        "Admin rights required",
    ):
        raise HTTPException(status_code=403, detail=error)
    if error in (
        "User not found",
        "Not found",
        "Collection not found",
    ):
        raise HTTPException(status_code=404, detail=error)
    if error in (
        "Internal server error",
        "Database connection failed",
        "SQL execution failed",
        "Prompt file missing",
        "MongoDB connection failed"
    ):
        raise HTTPException(status_code=500, detail=error)
    raise HTTPException(status_code=400, detail=error)