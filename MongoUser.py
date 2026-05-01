import json
from pymongo.errors import PyMongoError

from core.mongodb import get_collection


def add_user(
    client,
    database_name: str,
    collection_name: str,
    user: dict
) -> None:
    if not user:
        print("Empty user was not added")
        return

    collection = get_collection(client, database_name, collection_name)

    try:
        result = collection.insert_one(user)

        print("User added:")
        print(json.dumps({
            "inserted_id": str(result.inserted_id),
            "user": user
        }, indent=2, ensure_ascii=False, default=str))

    except PyMongoError as error:
        print(f"MongoDB error: {error}")