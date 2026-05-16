from fastapi import FastAPI
from argon2 import PasswordHasher
from ModelBase import (
    LoginRequest, LoginResponse,
    QueryRequest, QueryResponse,
    AddUserRequest, AddUserResponse,
    DeleteUserRequest, DeleteUserResponse,
    DropCollectionRequest, DropCollectionResponse,
    AddDocumentRequest, AddDocumentResponse,
    UpdateDocumentRequest, UpdateDocumentResponse,
)
from core.Users import add_user, delete_user
from core.Documents import (
    add_document,
    update_document,
    drop_collection,
    execute_query,
    get_known_fields,
)
from core.Model import create_mongo_query, load_model
from core.Login import login_user, require_admin
from core.Database import create_client, get_collection

app = FastAPI()
client = create_client()
llm = load_model()
ph = PasswordHasher()

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> dict:
    user = login_user(
        client=client,
        database_name=request.database_name,
        username=request.username,
        password=request.password,
    )
    if user is None:
        return {
            "ok": False,
            "username": None,
            "error": "Invalid username or password",
        }
    return {
        "ok": True,
        "username": user.get("username"),
        "error": None,
    }

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> dict:
    user = login_user(
        client=client,
        database_name=request.database_name,
        username=request.username,
        password=request.password,
    )
    if user is None:
        return {
            "ok": False,
            "result": [],
            "error": "Invalid username or password",
        }
    collection = get_collection(
        client=client,
        database_name=request.database_name,
        collection_name=request.collection_name,
    )
    known_fields = get_known_fields(collection)
    mongo_query = create_mongo_query(
        llm=llm,
        question=request.query,
        collection_name=request.collection_name,
        known_fields=known_fields,
    )
    if mongo_query is None:
        return {
            "ok": False,
            "result": [],
            "error": "Model did not return valid query",
        }
    return execute_query(collection, mongo_query)

@app.post("/add_users", response_model=AddUserResponse)
def add_users(request: AddUserRequest) -> dict:
    admin = require_admin(
        client=client,
        database_name=request.database_name,
        username=request.username,
        password=request.password,
    )
    if admin is None:
        return {
            "ok": False,
            "error": "Admin rights required",
        }
    if request.new_password != request.confirm_password:
        return {
            "ok": False,
            "username": None,
            "error": "Passwords do not match",
        }
    user = {
        "username": request.new_username,
        "password": ph.hash(request.new_password),
        "is_admin": False,
    }
    return add_user(
        client=client,
        database_name=request.database_name,
        user=user,
    )

@app.post("/delete_users", response_model=DeleteUserResponse)
def delete_users(request: DeleteUserRequest) -> dict:
    admin = require_admin(
        client=client,
        database_name=request.database_name,
        username=request.username,
        password=request.password,
    )
    if admin is None:
        return {
            "ok": False,
            "error": "Admin rights required",
        }
    if not request.confirm:
        return {
            "ok": False,
            "deleted": None,
            "error": "Confirmation required",
        }
    result = delete_user(
        client=client,
        database_name=request.database_name,
        filter_query={"username": request.username_to_delete},
    )
    if not result.get("ok"):
        return {
            "ok": False,
            "deleted": None,
            "error": result.get("error"),
        }
    return {
        "ok": True,
        "deleted": request.username_to_delete,
        "error": None,
    }

@app.post("/drop_collections", response_model=DropCollectionResponse)
def drop_collections(request: DropCollectionRequest) -> dict:
    admin = require_admin(
        client=client,
        database_name=request.database_name,
        username=request.username,
        password=request.password,
    )
    if admin is None:
        return {
            "ok": False,
            "error": "Admin rights required",
        }
    return drop_collection(
        client=client,
        database_name=request.database_name,
        collection_name=request.collection_name,
        confirm=request.confirm,
    )

@app.post("/add_documents", response_model=AddDocumentResponse)
def add_documents(request: AddDocumentRequest) -> dict:
    user = login_user(
        client=client,
        database_name=request.database_name,
        username=request.username,
        password=request.password,
    )
    if user is None:
        return {
            "ok": False,
            "inserted_id": None,
            "document": None,
            "error": "Invalid username or password",
        }
    collection = get_collection(
        client=client,
        database_name=request.database_name,
        collection_name=request.collection_name,
    )
    return add_document(
        collection=collection,
        document=request.document,
    )

@app.put("/update_documents", response_model=UpdateDocumentResponse)
def update_documents(request: UpdateDocumentRequest) -> dict:
    user = login_user(
        client=client,
        database_name=request.database_name,
        username=request.username,
        password=request.password,
    )
    if user is None:
        return {
            "ok": False,
            "filter": None,
            "updated": None,
            "matched_count": 0,
            "modified_count": 0,
            "error": "Invalid username or password",
        }
    return update_document(
        client=client,
        database_name=request.database_name,
        collection_name=request.collection_name,
        filter_query=request.filter_query,
        update_fields=request.update_fields,
    )

@app.get("/health")
def health() -> dict:
    return {"ok": True}