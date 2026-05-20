import flet as ft
from core.ErrorLog import log_error


def show_register(page: ft.Page, state, api, go) -> None:
    page.clean()
    new_user_tf = ft.TextField(label="New username", width=400)
    new_pass_tf = ft.TextField(
        label="New password",
        password=True,
        can_reveal_password=True,
        width=400,
    )
    confirm_tf = ft.TextField(
        label="Confirm password",
        password=True,
        can_reveal_password=True,
        width=400,
    )
    is_admin_tf = ft.Checkbox(label="Is admin", value=False)
    status_txt = ft.Text("")

    async def create_user_click(e) -> None:
        new_username = (new_user_tf.value or "").strip()
        new_password = new_pass_tf.value or ""
        confirm_password = confirm_tf.value or ""
        if not state.database_name:
            status_txt.value = "Database name is missing"
            page.update()
            return
        if not state.username or not state.password:
            status_txt.value = "You are not logged in"
            page.update()
            return
        if not new_username or not new_password or not confirm_password:
            status_txt.value = "Missing fields"
            page.update()
            return
        payload = {
            "database_name": state.database_name,
            "username": state.username,
            "password": state.password,
            "new_username": new_username,
            "new_password": new_password,
            "confirm_password": confirm_password,
            "is_admin": bool(is_admin_tf.value),
        }
        status_txt.value = "Creating user..."
        page.update()
        try:
            response = await api.add_user(payload)
            if response.status_code != 200:
                try:
                    status_txt.value = f"Create failed: {response.json().get('detail')}"

                except Exception:
                    log_error(f"Create failed: {response.text}")
                    status_txt.value = f"Create failed: {response.text}"

                page.update()
                return
            data = response.json()
            status_txt.value = f"OK: created user {data.get('username')}"
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
                new_user_tf,
                new_pass_tf,
                confirm_tf,
                is_admin_tf,
                ft.Row(
                    [
                        ft.Button("Create", on_click=create_user_click),
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