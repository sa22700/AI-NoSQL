import flet as ft
from core.ErrorLog import log_error

def show_login(page: ft.Page, state, api, go) -> None:
    page.clean()
    databases_txt = ft.Text("Databases: -")
    database_tf = ft.TextField(label="Database name", width=400)
    username_tf = ft.TextField(label="Username", width=400)
    password_tf = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=400,
    )
    status_txt = ft.Text("")

    async def load_databases_click(e) -> None:
        try:
            response = await api.list_databases()

            if response.status_code != 200:
                databases_txt.value = f"Databases load failed: {response.text}"
                page.update()
                return

            data = response.json()
            databases = data.get("databases", [])

            if databases:
                databases_txt.value = "Databases: " + ", ".join(databases)
            else:
                databases_txt.value = "Databases: none"

            page.update()

        except Exception as ex:
            log_error(f"Databases load failed: {ex}")
            databases_txt.value = f"Databases load failed: {ex}"
            page.update()

    async def login_click(e) -> None:
        database_name = (database_tf.value or "").strip()
        username = (username_tf.value or "").strip()
        password = password_tf.value or ""
        if not database_name:
            status_txt.value = "Database name is missing"
            page.update()
            return
        if not username or not password:
            status_txt.value = "Username or password is missing"
            page.update()
            return
        payload = {
            "database_name": database_name,
            "username": username,
            "password": password,
        }
        try:
            loader = await api.login(payload)
            if loader.status_code != 200:
                try:
                    status_txt.value = f"Login failed: {loader.json().get('detail')}"

                except Exception:
                    log_error(f"Login failed: {loader.text}")
                    status_txt.value = f"Login failed: {loader.text}"

                page.update()
                return
            state.database_name = database_name
            state.username = username
            state.password = password
            go("main menu")

        except Exception as ex:
            log_error(f"Request failed: {ex}")
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def exit_click(e) -> None:
        await page.window.destroy()

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        databases_txt,
                        ft.Button("Refresh databases", on_click=load_databases_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                database_tf,
                username_tf,
                password_tf,
                ft.Row(
                    [
                        ft.Button("Login", on_click=login_click),
                        ft.Button("Exit", on_click=exit_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                status_txt,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    page.update()