from core.MongoDB import (
    create_client,
    get_collection,
    add_document,
    get_known_fields,
    list_databases,
    list_collections,
    get_users,
    check_user
)
from core.SubProcess import (
    create_document_from_input,
    select_document_filter,
    ask_database,
    create_user_from_input
)
from core.MongoModel import load_model
from core.MongoUser import add_user
from core.MongoDel import delete_document
from core.MongoDrop import drop_collection
from core.MongoUpd import update_document
from getpass import getpass

def main() -> None:
    client = create_client()
    print(list_databases(client))
    database_name = input("Create/select database: ").strip()
    print(list_collections(client, database_name))
    while True:
        username = input("Enter username: ").strip()
        password = getpass("Enter password: ").strip()
        if check_user(client, database_name, username, password):
            print("Login successful")
            break
        else:
            print("Invalid username or password")
    collection_name = input("Create/select collection: ").strip()
    if collection_name == "users":
        print("The users collection is reserved for authentication")
        client.close()
        return
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
        print("8: Get users list")
        print("0: Exit")
        choice = input("Select: ").strip()
        if choice == "1":
            document = create_document_from_input()
            add_document(collection, document)
        elif choice == "2":
            ask_database(llm, collection, collection_name)
        elif choice == "3":
            fields = get_known_fields(collection)
            print(fields)
        elif choice == "4":
            user = create_user_from_input()
            if user is not None:
                add_user(client, database_name, user)
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
        elif choice == "8":
            users = get_users(client, database_name)
            for user in users:
                print(json.dumps(user, indent=2, ensure_ascii=False, default=str))
        elif choice == "0":
            break
        else:
            print("Unknown selection")
    client.close()

if __name__ == "__main__":
    main()