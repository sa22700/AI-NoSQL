from core.MongoDB import (
    create_client,
    get_collection,
    add_document,
    get_known_fields,
    list_databases,
    list_collections
)
from core.SubProcess import (
    create_document_from_input,
    select_document_filter,
    ask_database
)
from core.MongoModel import load_model
from core.MongoUser import add_user
from core.MongoDel import delete_document
from core.MongoDrop import drop_collection
from core.MongoUpd import update_document

def main() -> None:
    client = create_client()
    print(list_databases(client))
    database_name = input("Create/select database: ")
    print(list_collections(client, database_name))
    collection_name = input("Create/select collection: ")
    collection = get_collection(
        client=client,
        database_name=database_name,
        collection_name=collection_name
    )
    print("Loading model...")
    llm = load_model()
    print("Model loaded.")
    while True:
        print("\n1: Add document")
        print("2: Ask database")
        print("3: Show known fields")
        print("4: Add user")
        print("5: Delete document")
        print("6: Drop collection")
        print("7: Update document")
        print("0: Exit")
        choice = input("Select: ")
        if choice == "1":
            document = create_document_from_input()
            add_document(collection, document)
        elif choice == "2":
            ask_database(llm, collection, collection_name)
        elif choice == "3":
            fields = get_known_fields(collection)
            print(fields)
        elif choice == "4":
            user = create_document_from_input()
            add_user(client, database_name, collection_name, user)
        elif choice == "5":
            print("Delete filter:")
            filtered = select_document_filter(collection)
            if filtered is not None:
                delete_document(client, database_name, collection_name, filtered)
        elif choice == "6":
            drop_collection(client, database_name, collection_name)
            collections = list_collections(client, database_name)
            print(collections)
            collection_name = input("Create/select collection: ").strip()
            if not collection_name:
                print("Collection name cannot be empty")
                continue
            collection = get_collection(
                client=client,
                database_name=database_name,
                collection_name=collection_name
            )
        elif choice == "7":
            filtered = select_document_filter(collection)
            if filtered is None:
                continue
            print("Update fields:")
            update = create_document_from_input()
            if update:
                update_document(client, database_name, collection_name, filtered, update)
            else:
                print("Empty update was not executed")
        elif choice == "0":
            break
        else:
            print("Unknown selection")
    client.close()

if __name__ == "__main__":
    main()