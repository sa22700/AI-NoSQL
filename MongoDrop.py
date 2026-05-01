import json
from pymongo.errors import PyMongoError

from core.mongodb import get_collection


def drop_collection(
    client,
    database_name: str,
    collection_name: str
) -> None:
    confirm = input(f"Type DROP to delete collection '{collection_name}': ")

    if confirm != "DROP":
        print("Drop cancelled")
        return

    collection = get_collection(client, database_name, collection_name)

    try:
        collection.drop()

        print("Collection dropped:")
        print(json.dumps({
            "database": database_name,
            "collection": collection_name
        }, indent=2, ensure_ascii=False, default=str))

    except PyMongoError as error:
        print(f"MongoDB error: {error}")