from fastapi import FastAPI, HTTPException
from argon2 import PasswordHasher
from backend.ModelBase import (
    LoginRequest, LoginResponse,
    QueryRequest, QueryResponse,
    AddUserRequest, AddUserResponse,
    DeleteUserRequest, DeleteUserResponse,
    DropCollectionRequest, DropCollectionResponse,
    AddDocumentRequest, AddDocumentResponse,
    UpdateDocumentRequest, UpdateDocumentResponse,
    UpdateUserRequest, UpdateUserResponse
)
from core.Users import add_user, delete_user, update_user
from core.Documents import (
    add_document,
    update_document,
    drop_collection,
    execute_query,
    get_known_fields,
)
from core.Model import create_mongo_query, load_model
from core.Database import (
    create_client,
    get_collection,
    list_databases,
    list_collections
)
from backend.HttpException import raise_for_error
from backend.Verify import verify_user, verify_admin
from core.ErrorLog import log_error

app = FastAPI()
client = create_client()
llm = load_model()
ph = PasswordHasher()

@app.post("/login", response_model=LoginResponse)
def login_endpoint(request: LoginRequest) -> dict:
    try:
        user = verify_user(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        return {
            "ok": True,
            "username": user.get("username"),
            "is_admin": bool(user.get("is_admin", False)),
            "error": None
        }

    except HTTPException:
        raise

    except Exception as error:
        log_error(f"login_endpoint failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest) -> dict:
    try:
        verify_user(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
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
        out = execute_query(collection, mongo_query)
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as error:
        log_error(f"query_endpoint failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/add_users", response_model=AddUserResponse)
def add_users_endpoint(request: AddUserRequest) -> dict:
    try:
        verify_admin(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if request.new_password != request.confirm_password:
            out = {
                "ok": False,
                "username": None,
                "error": "Passwords do not match",
            }
            raise_for_error(out)
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
        log_error(f"add_users_endpoint failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/delete_users", response_model=DeleteUserResponse)
def delete_users_endpoint(request: DeleteUserRequest) -> dict:
    try:
        verify_admin(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if not request.confirm:
            out = {
                "ok": False,
                "deleted": None,
                "error": "Confirmation required",
            }
            raise_for_error(out)
        result = delete_user(
            client=client,
            database_name=request.database_name,
            filter_query={"username": request.username_to_delete},
        )
        raise_for_error(result)
        if result.get("deleted_count", 0) == 0:
            out = {
                "ok": False,
                "deleted": None,
                "error": "User not found",
            }
            raise_for_error(out)
        return {
            "ok": True,
            "deleted": request.username_to_delete,
            "error": None,
        }

    except HTTPException:
        raise

    except Exception as error:
        log_error(f"delete_users_endpoint failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/drop_collections", response_model=DropCollectionResponse)
def drop_collections_endpoint(request: DropCollectionRequest) -> dict:
    try:
        verify_admin(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if request.collection_name.strip().lower() == "users":
            out = {
                "ok": False,
                "dropped": None,
                "error": "Users collection cannot be dropped",
            }
            raise_for_error(out)
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
        log_error(f"drop_collections_endpoint failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/add_documents", response_model=AddDocumentResponse)
def add_documents_endpoint(request: AddDocumentRequest) -> dict:
    try:
        verify_user(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        if request.collection_name.strip().lower() == "users":
            out = {
                "ok": False,
                "inserted_id": None,
                "document": None,
                "error": "Adding documents to users collection is not allowed",
            }
            raise_for_error(out)
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
        log_error(f"add_documents_endpoint failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/update_documents", response_model=UpdateDocumentResponse)
def update_documents_endpoint(request: UpdateDocumentRequest) -> dict:
    try:
        verify_user(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        out = update_document(
            client=client,
            database_name=request.database_name,
            collection_name=request.collection_name,
            filter_query=request.filter_query,
            update_fields=request.update_fields,
        )
        raise_for_error(out)
        if out.get("matched_count", 0) == 0:
            out = {
                "ok": False,
                "filter": request.filter_query,
                "updated": None,
                "matched_count": 0,
                "modified_count": 0,
                "error": "Document not found",
            }
            raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as error:
        log_error(f"update_documents_endpoint failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/update_users", response_model=UpdateUserResponse)
def update_users_endpoint(request: UpdateUserRequest) -> dict:
    try:
        verify_admin(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
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
        out = update_user(
            client=client,
            database_name=request.database_name,
            filter_query=filter_query,
            update_fields=update_fields,
        )
        raise_for_error(out)
        if out.get("matched_count", 0) == 0:
            out = {
                "ok": False,
                "filter": filter_query,
                "updated": None,
                "matched_count": 0,
                "modified_count": 0,
                "error": "User not found",
            }
            raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as error:
        log_error(f"update_users_endpoint failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/databases")
def databases_endpoint() -> dict:
    try:
        return {
            "ok": True,
            "databases": list_databases(client),
            "error": None,
        }

    except Exception as error:
        log_error(f"databases_endpoint failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/collections")
def collections_endpoint(request: LoginRequest) -> dict:
    try:
        verify_user(
            client=client,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
        )
        return {
            "ok": True,
            "collections": list_collections(client, request.database_name),
            "error": None,
        }

    except HTTPException:
        raise

    except Exception as error:
        log_error(f"collections_endpoint failed: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
def health() -> dict:
    return {"ok": True}