import flet as ft
from core.ErrorLog import log_error

def show_delete_collection(page: ft.Page, state, api, go) -> None:
    page.clean()
    collect_del_tf = ft.TextField(
        label="Collection to delete",
        value=state.collection_name,
        width=400,
    )
    confirm_cb = ft.Checkbox(label="I confirm delete", value=False)
    status_txt = ft.Text("")

    async def do_delete_click(e) -> None:
        collection_name = (collect_del_tf.value or "").strip()
        if not collection_name:
            status_txt.value = "Collection missing"
            page.update()
            return
        if collection_name.lower() == "users":
            status_txt.value = "Users collection cannot be deleted from this view"
            page.update()
            return
        if not confirm_cb.value:
            status_txt.value = "Confirm delete first"
            page.update()
            return
        payload = {
            "database_name": state.database_name,
            "username": state.username,
            "password": state.password,
            "collection_name": collection_name,
            "confirm": bool(confirm_cb.value),
        }
        status_txt.value = "Deleting..."
        page.update()
        try:
            response = await api.drop_collection(payload)
            data = response.json() if response is not None else {}
            if not (200 <= response.status_code < 300) or data.get("error"):
                detail = data.get("detail") or data.get("error") or getattr(response, "text", "Unknown error")
                status_txt.value = f"Delete failed: {detail}"
                page.update()
                return
            status_txt.value = f"OK: dropped {data.get('dropped')}"
            confirm_cb.value = False
            if state.collection_name == collection_name:
                state.collection_name = ""
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
                ft.Text(f"Admin: {state.username}"),
                ft.Text(f"Database: {state.database_name}"),
                collect_del_tf,
                confirm_cb,
                ft.Row(
                    [
                        ft.Button("Delete", on_click=do_delete_click),
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