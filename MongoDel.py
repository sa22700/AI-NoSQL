import json
from pymongo.errors import PyMongoError
from core.mongodb import get_collection

def delete_document(
    client,
    database_name: str,
    collection_name: str,
    filter_query: dict
) -> None:
    if not filter_query:
        print("Empty filter is not allowed for delete")
        return
    collection = get_collection(client, database_name, collection_name)
    try:
        result = collection.delete_one(filter_query)
        print("Document delete result:")
        print(json.dumps({
            "filter": filter_query,
            "deleted_count": result.deleted_count
        }, indent=2, ensure_ascii=False, default=str))

    except PyMongoError as error:
        print(f"MongoDB error: {error}")