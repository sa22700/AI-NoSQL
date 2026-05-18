from fastapi import FastAPI, HTTPException
from argon2 import PasswordHasher
from ModelBase import (
    LoginRequest, LoginResponse,
    QueryRequest, QueryResponse,
    AddUserRequest, AddUserResponse,
    DeleteUserRequest, DeleteUserResponse,
    DropCollectionRequest, DropCollectionResponse,
    AddDocumentRequest, AddDocumentResponse,
    UpdateDocumentRequest, UpdateDocumentResponse,
    UpdateUserRequest, UpdateUserResponse
)
from backend.ModelBase import UpdateUserRequest
from core.Users import add_user, delete_user, update_user
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
from HttpException import raise_for_error

app = FastAPI()
client = create_client()
llm = load_model()
ph = PasswordHasher()

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> dict:
    try:
        user = login_user(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if user is None:
            out = {
                "ok": False,
                "username": None,
                "error": "Invalid username or password",
            }
            raise_for_error(out)
            return out
        return {
            "ok": True,
            "username": user.get("username"),
            "error": None,
        }

    except HTTPException:
        raise

    except Exception as error:
        out = {
            "ok": False,
            "username": None,
            "error": str(error)
        }
        raise_for_error(out)
        return out

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> dict:
    try:
        user = login_user(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if user is None:
            out = {
                "ok": False,
                "result": [],
                "error": "Invalid username or password",
            }
            raise_for_error(out)
            return out
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
            out = {
                "ok": False,
                "result": [],
                "error": "Model did not return valid query",
            }
            raise_for_error(out)
            return out
        out = execute_query(collection, mongo_query)
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as error:
        out = {
            "ok": False,
            "result": [],
            "error": str(error)
        }
        raise_for_error(out)
        return out

@app.post("/add_users", response_model=AddUserResponse)
def add_users(request: AddUserRequest) -> dict:
    try:
        admin = require_admin(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if admin is None:
            out = {
                "ok": False,
                "username": None,
                "error": "Admin rights required",
            }
            raise_for_error(out)
            return out
        if request.new_password != request.confirm_password:
            out = {
                "ok": False,
                "username": None,
                "error": "Passwords do not match",
            }
            raise_for_error(out)
            return out
        user = {
            "username": request.new_username,
            "password": ph.hash(request.new_password),
            "is_admin": request.is_admin,
        }
        out = add_user(
            client=client,
            database_name=request.database_name,
            user=user,
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as error:
        out = {
            "ok": False,
            "username": None,
            "error": str(error)
        }
        raise_for_error(out)
        return out

@app.post("/delete_users", response_model=DeleteUserResponse)
def delete_users(request: DeleteUserRequest) -> dict:
    try:
        admin = require_admin(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if admin is None:
            out = {
                "ok": False,
                "deleted": None,
                "error": "Admin rights required",
            }
            raise_for_error(out)
            return out
        if not request.confirm:
            out = {
                "ok": False,
                "deleted": None,
                "error": "Confirmation required",
            }
            raise_for_error(out)
            return out
        result = delete_user(
            client=client,
            database_name=request.database_name,
            filter_query={"username": request.username_to_delete},
        )
        if not result.get("ok"):
            out = {
                "ok": False,
                "deleted": None,
                "error": result.get("error"),
            }
            raise_for_error(out)
            return out
        return {
            "ok": True,
            "deleted": request.username_to_delete,
            "error": None,
        }

    except HTTPException:
        raise

    except Exception as error:
        out = {
            "ok": False,
            "deleted": None,
            "error": str(error)
        }
        raise_for_error(out)
        return out

@app.post("/drop_collections", response_model=DropCollectionResponse)
def drop_collections(request: DropCollectionRequest) -> dict:
    try:
        admin = require_admin(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if admin is None:
            out = {
                "ok": False,
                "dropped": None,
                "error": "Admin rights required",
            }
            raise_for_error(out)
            return out
        out = drop_collection(
            client=client,
            database_name=request.database_name,
            collection_name=request.collection_name,
            confirm=request.confirm,
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as error:
        out = {
            "ok": False,
            "dropped": None,
            "error": str(error)
        }
        raise_for_error(out)
        return out

@app.post("/add_documents", response_model=AddDocumentResponse)
def add_documents(request: AddDocumentRequest) -> dict:
    try:
        user = login_user(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if user is None:
            out = {
                "ok": False,
                "inserted_id": None,
                "document": None,
                "error": "Invalid username or password",
            }
            raise_for_error(out)
            return out
        collection = get_collection(
            client=client,
            database_name=request.database_name,
            collection_name=request.collection_name,
        )
        out = add_document(
            collection=collection,
            document=request.document,
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as error:
        out = {
            "ok": False,
            "inserted_id": None,
            "document": None,
            "error": str(error)
        }
        raise_for_error(out)
        return out

@app.put("/update_documents", response_model=UpdateDocumentResponse)
def update_documents(request: UpdateDocumentRequest) -> dict:
    try:
        user = login_user(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if user is None:
            out = {
                "ok": False,
                "filter": None,
                "updated": None,
                "matched_count": 0,
                "modified_count": 0,
                "error": "Invalid username or password",
            }
            raise_for_error(out)
            return out
        out = update_document(
            client=client,
            database_name=request.database_name,
            collection_name=request.collection_name,
            filter_query=request.filter_query,
            update_fields=request.update_fields,
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as error:
        out = {
            "ok": False,
            "filter": None,
            "updated": None,
            "matched_count": 0,
            "modified_count": 0,
            "error": str(error)
        }
        raise_for_error(out)
        return out

@app.put("/update_users", response_model=UpdateUserResponse)
def update_users(request: UpdateUserRequest) -> dict:
    try:
        admin = require_admin(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if admin is None:
            out = {
                "ok": False,
                "filter": None,
                "updated": None,
                "matched_count": 0,
                "modified_count": 0,
                "error": "Admin rights required",
            }
            raise_for_error(out)
            return out
        filter_query = {
            "username": request.username_to_update,
        }
        update_fields = {}
        if request.new_username is not None:
            new_username = request.new_username.strip()
            if not new_username:
                out = {
                    "ok": False,
                    "filter": filter_query,
                    "updated": None,
                    "matched_count": 0,
                    "modified_count": 0,
                    "error": "Username cannot be empty",
                }
                raise_for_error(out)
                return out
            if new_username.startswith("$"):
                out = {
                    "ok": False,
                    "filter": filter_query,
                    "updated": None,
                    "matched_count": 0,
                    "modified_count": 0,
                    "error": "Username cannot start with $",
                }
                raise_for_error(out)
                return out
            update_fields["username"] = new_username
        if request.new_password is not None or request.confirm_password is not None:
            if not request.new_password or not request.confirm_password:
                out = {
                    "ok": False,
                    "filter": filter_query,
                    "updated": None,
                    "matched_count": 0,
                    "modified_count": 0,
                    "error": "Password and confirmation are required",
                }
                raise_for_error(out)
                return out
            if request.new_password != request.confirm_password:
                out = {
                    "ok": False,
                    "filter": filter_query,
                    "updated": None,
                    "matched_count": 0,
                    "modified_count": 0,
                    "error": "Passwords do not match",
                }
                raise_for_error(out)
                return out
            update_fields["password"] = ph.hash(request.new_password)
        if request.is_admin is not None:
            update_fields["is_admin"] = request.is_admin
        if not update_fields:
            out = {
                "ok": False,
                "filter": filter_query,
                "updated": None,
                "matched_count": 0,
                "modified_count": 0,
                "error": "Empty update was not applied",
            }
            raise_for_error(out)
            return out
        out = update_user(
            client=client,
            database_name=request.database_name,
            filter_query=filter_query,
            update_fields=update_fields,
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as error:
        out = {
            "ok": False,
            "filter": None,
            "updated": None,
            "matched_count": 0,
            "modified_count": 0,
            "error": str(error),
        }
        raise_for_error(out)
        return out

@app.get("/health")
def health() -> dict:
    return {"ok": True}