import json
from pymongo.errors import PyMongoError
from core.MongoDB import get_collection


def add_user(
    client,
    database_name: str,
    user: dict
) -> None:
    if not user:
        print("Empty user was not added")
        return
    collection = get_collection(client, database_name, "users")
    username = user.get("username")
    if not username:
        print("Username is missing")
        return
    try:
        existing_user = collection.find_one({"username": username})
        if existing_user is not None:
            print("User already exists")
            return
        result = collection.insert_one(user)
        print("User added:")
        print(json.dumps({
            "inserted_id": str(result.inserted_id),
            "username": username
        }, indent=2, ensure_ascii=False, default=str))

    except PyMongoError as error:
        print(f"MongoDB error: {error}")