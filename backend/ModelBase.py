from pydantic import BaseModel
from typing import Any

class LoginRequest(BaseModel):
    database_name: str
    username: str
    password: str

class LoginResponse(BaseModel):
    username: str | None = None
    ok: bool
    error: str | None = None
    is_admin: bool | None = None

class QueryRequest(LoginRequest):
    collection_name: str
    query: str

class QueryResponse(BaseModel):
    result: list[dict[str, Any]]
    ok: bool
    error: str | None = None

class AddUserRequest(LoginRequest):
    new_username: str
    new_password: str
    confirm_password: str
    is_admin: bool = False

class AddUserResponse(BaseModel):
    username: str | None = None
    ok: bool
    error: str | None = None

class DeleteUserRequest(LoginRequest):
    username_to_delete: str
    confirm: bool = False

class DeleteUserResponse(BaseModel):
    deleted: str | None = None
    ok: bool
    error: str | None = None

class DropCollectionRequest(LoginRequest):
    collection_name: str
    confirm: bool = False

class DropCollectionResponse(BaseModel):
    dropped: str | None = None
    ok: bool
    error: str | None = None

class AddDocumentRequest(LoginRequest):
    collection_name: str
    document: dict[str, Any]

class AddDocumentResponse(BaseModel):
    inserted_id: str | None = None
    document: dict[str, Any] | None = None
    ok: bool
    error: str | None = None

class UpdateDocumentRequest(LoginRequest):
    collection_name: str
    filter_query: dict[str, Any]
    update_fields: dict[str, Any]

class UpdateDocumentResponse(BaseModel):
    filter: dict[str, Any] | None = None
    updated: dict[str, Any] | None = None
    matched_count: int = 0
    modified_count: int = 0
    ok: bool
    error: str | None = None

class UpdateUserRequest(LoginRequest):
    username_to_update: str
    new_username: str | None = None
    new_password: str | None = None
    confirm_password: str | None = None
    is_admin: bool | None = None

class UpdateUserResponse(BaseModel):
    filter: dict[str, Any] | None = None
    updated: dict[str, Any] | None = None
    matched_count: int = 0
    modified_count: int = 0
    ok: bool
    error: str | None = None