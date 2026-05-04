import json
from pymongo.errors import PyMongoError
from core.MongoDB import get_collection

def update_document(
    client,
    database_name: str,
    collection_name: str,
    filter_query: dict,
    update_fields: dict
) -> None:
    if not filter_query:
        print("Empty filter is not allowed for update")
        return
    if not update_fields:
        print("Empty update was not applied")
        return
    collection = get_collection(client, database_name, collection_name)
    try:
        result = collection.update_one(
            filter_query,
            {"$set": update_fields}
        )
        print("Document update result:")
        print(json.dumps({
            "filter": filter_query,
            "update": update_fields,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }, indent=2, ensure_ascii=False, default=str))

    except PyMongoError as error:
        print(f"MongoDB error: {error}")