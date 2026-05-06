# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import pymongo
from core.Config import MONGO_URI

def create_client() -> pymongo.MongoClient:
    return pymongo.MongoClient(MONGO_URI)

def get_collection(
    client,
    database_name: str,
    collection_name: str
) -> pymongo.collection.Collection:
    db = client[database_name]
    return db[collection_name]

def list_databases(client) -> list[str]:
    system_databases = {"admin", "config", "local"}
    return [
        database_name
        for database_name in client.list_database_names()
        if database_name not in system_databases
    ]

def list_collections(client, database_name: str) -> list[str]:
    db = client[database_name]
    return db.list_collection_names()