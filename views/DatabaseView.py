# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import flet as ft
import json
from core.ErrorLog import log_error
from ui.Parser import parse_simple_document

def show_database(page: ft.Page, state, api, go) -> None:
    page.clean()
    collection_tf = ft.TextField(
        label="Collection name",
        width=400,
    )
    document_tf = ft.TextField(
        label='Document JSON, for example {"name": "test", "value": 123}',
        multiline=True,
        width=700,
        min_lines=8,
    )
    status_txt = ft.Text("")
    result_tf = ft.TextField(
        label="Result",
        multiline=True,
        read_only=True,
        width=700,
        min_lines=10,
    )

    async def add_document_click(e) -> None:
        collection_name = (collection_tf.value or "").strip()
        document_text = (document_tf.value or "").strip()
        if not collection_name:
            status_txt.value = "Collection name missing"
            page.update()
            return
        if not document_text:
            status_txt.value = "Document JSON missing"
            page.update()
            return
        try:
            document = parse_simple_document(document_text)

        except ValueError as error:
            status_txt.value = f"Invalid document: {error}"
            page.update()
            return
        payload = {
            "database_name": state.database_name,
            "collection_name": collection_name,
            "username": state.username,
            "password": state.password,
            "document": document,
        }
        status_txt.value = "Running..."
        page.update()
        try:
            response = await api.add_document(payload)
            if response.status_code != 200:
                try:
                    status_txt.value = f"Add document failed: {response.json().get('detail')}"

                except Exception:
                    log_error(f"Add document failed: {response.text}")
                    status_txt.value = f"Add document failed: {response.text}"

                page.update()
                return
            data = response.json()
            status_txt.value = "OK"
            result_tf.value = json.dumps(data, indent=2, ensure_ascii=False)
            page.update()

        except Exception as ex:
            log_error(f"Request failed: {ex}")
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def back_click(e) -> None:
        go("main menu")
    page.add(
        ft.Column(
            [
                ft.Text(f"User: {state.username}"),
                ft.Text(f"Database: {state.database_name}"),
                collection_tf,
                document_tf,
                ft.Row(
                    [
                        ft.Button("Add document", on_click=add_document_click),
                        ft.Button("Back", on_click=back_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                status_txt,
                result_tf,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    page.update()