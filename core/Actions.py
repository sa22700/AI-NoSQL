# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import json
from core.Documents import execute_query, get_known_fields
from core.Model import create_mongo_query

def ask_database(
    llm,
    collection,
    collection_name: str,
    question: str | None = None,
    print_output: bool = True
) -> dict:
    known_fields = get_known_fields(collection)
    if not known_fields:
        result = {
            "ok": False,
            "result": [],
            "error": "Collection has no known fields yet. Add at least one document first."
        }
        if print_output:
            print(result["error"])
        return result
    if question is None:
        question = input("Question: ").strip()
    try:
        query = create_mongo_query(
            llm=llm,
            question=question,
            collection_name=collection_name,
            known_fields=known_fields
        )
        if print_output:
            print("Generated query:")
            print(json.dumps(query, indent=2, ensure_ascii=False, default=str))
        if query is None:
            result = {
                "ok": False,
                "result": [],
                "error": "Query was not executed because model output was invalid"
            }
            if print_output:
                print(result["error"])
            return result
        result = execute_query(collection, query)
        if print_output:
            print("Result:")
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        return result

    except json.JSONDecodeError:
        result = {
            "ok": False,
            "result": [],
            "error": "Model did not return valid JSON"
        }
        if print_output:
            print(result["error"])
        return result

    except ValueError as error:
        result = {
            "ok": False,
            "result": [],
            "error": f"Rejected query: {error}"
        }
        if print_output:
            print(result["error"])
        return result