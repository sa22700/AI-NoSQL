# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import json
from core.Model import create_mongo_query
from core.Documents import get_known_fields, execute_query

def ask_database(llm, collection, collection_name: str) -> None:
    known_fields = get_known_fields(collection)
    if not known_fields:
        print("Collection has no known fields yet. Add at least one document first.")
        return
    question = input("Question: ").strip()
    try:
        query = create_mongo_query(
            llm=llm,
            question=question,
            collection_name=collection_name,
            known_fields=known_fields
        )
        print("Generated query:")
        print(json.dumps(query, indent=2, ensure_ascii=False))
        if query is None:
            print("Query was not executed because model output was invalid")
            return
        print("Result:")
        execute_query(collection, query)

    except json.JSONDecodeError:
        print("Model did not return valid JSON")

    except ValueError as error:
        print(f"Rejected query: {error}")