import flet as ft
import json
from core.ErrorLog import log_error

def show_update_document(page: ft.Page, state, api, go) -> None:
    page.clean()
    collection_tf = ft.TextField(
        label="Collection name",
        value=state.collection_name,
        width=400,
    )
    filter_tf = ft.TextField(
        label='Filter JSON, for example {"name": "test"}',
        multiline=True,
        width=700,
        min_lines=4,
    )
    update_tf = ft.TextField(
        label='Update fields JSON, for example {"price": 99}',
        multiline=True,
        width=700,
        min_lines=4,
    )
    confirm_cb = ft.Checkbox(label="I confirm update", value=False)
    status_txt = ft.Text("")

    async def do_update_click(e) -> None:
        collection_name = (collection_tf.value or "").strip()
        filter_text = (filter_tf.value or "").strip()
        update_text = (update_tf.value or "").strip()
        if not collection_name:
            status_txt.value = "Collection name missing"
            page.update()
            return
        if collection_name.lower() == "users":
            status_txt.value = "Use user update view for users collection"
            page.update()
            return
        if not filter_text:
            status_txt.value = "Filter JSON missing"
            page.update()
            return
        if not update_text:
            status_txt.value = "Update fields JSON missing"
            page.update()
            return
        if not confirm_cb.value:
            status_txt.value = "Confirm update first"
            page.update()
            return
        try:
            filter_query = json.loads(filter_text)
            update_fields = json.loads(update_text)

        except json.JSONDecodeError as error:
            status_txt.value = f"Invalid JSON: {error}"
            page.update()
            return

        if not isinstance(filter_query, dict):
            status_txt.value = "Filter must be a JSON object"
            page.update()
            return
        if not isinstance(update_fields, dict):
            status_txt.value = "Update fields must be a JSON object"
            page.update()
            return
        payload = {
            "database_name": state.database_name,
            "collection_name": collection_name,
            "username": state.username,
            "password": state.password,
            "filter_query": filter_query,
            "update_fields": update_fields,
        }
        status_txt.value = "Updating..."
        page.update()
        try:
            response = await api.update_document(payload)
            if response.status_code != 200:
                try:
                    status_txt.value = f"Update failed: {response.json().get('detail')}"

                except Exception:
                    log_error(f"Update failed: {response.text}")
                    status_txt.value = f"Update failed: {response.text}"

                page.update()
                return
            data = response.json()
            state.collection_name = collection_name
            status_txt.value = "OK: updated"
            confirm_cb.value = False
            page.snack_bar = ft.SnackBar(
                ft.Text(json.dumps(data, indent=2, ensure_ascii=False))
            )
            page.snack_bar.open = True
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
                filter_tf,
                update_tf,
                confirm_cb,
                ft.Row(
                    [
                        ft.Button("Update", on_click=do_update_click),
                        ft.Button("Back", on_click=back_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                status_txt,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    page.update()