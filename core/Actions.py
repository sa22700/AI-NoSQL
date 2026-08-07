# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

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
            "error": (
                "Collection has no known fields yet. "
                "Add at least one document first."
            )
        }
        if print_output:
            print(f"Error: {result['error']}")
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
        if query is None:
            result = {
                "ok": False,
                "result": [],
                "error": "Model output was invalid"
            }
            if print_output:
                print(f"Error: {result['error']}")
            return result
        result = execute_query(
            collection=collection,
            query=query
        )
        if print_output:
            print("\nQuery:")
            print(query)
            if result["error"]:
                print(f"\nError: {result['error']}")
            else:
                print("\nAnswer:")
                if not result["result"]:
                    print("No results.")
                else:
                    for document in result["result"]:
                        for key, value in document.items():
                            print(f"{key}: {value}")
        return result

    except ValueError as error:
        result = {
            "ok": False,
            "result": [],
            "error": f"Rejected query: {error}"
        }

        if print_output:
            print(f"Error: {result['error']}")
        return result

    except EOFError as error:
        result = {
            "ok": False,
            "result": [],
            "error": str(error)
        }

        if print_output:
            print(f"Error: {result['error']}")
        return result

    except KeyboardInterrupt:
        result = {
            "ok": False,
            "result": [],
            "error": "Query cancelled"
        }

        if print_output:
            print(f"Error: {result['error']}")
        return result