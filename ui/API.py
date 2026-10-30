# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import httpx

class ApiClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _get(
            self,
            path: str,
            timeout: float | None = None,
    ) -> httpx.Response:
        t = self.timeout if timeout is None else timeout

        async with httpx.AsyncClient(timeout=t) as client:
            return await client.get(
                f"{self.base_url}{path}",
            )

    async def _post(
        self,
        path: str,
        payload: dict,
        timeout: float | None = None,
    ) -> httpx.Response:
        t = self.timeout if timeout is None else timeout

        async with httpx.AsyncClient(timeout=t) as client:
            return await client.post(
                f"{self.base_url}{path}",
                json=payload,
            )

    async def _put(
        self,
        path: str,
        payload: dict,
        timeout: float | None = None,
    ) -> httpx.Response:
        t = self.timeout if timeout is None else timeout

        async with httpx.AsyncClient(timeout=t) as client:
            return await client.put(
                f"{self.base_url}{path}",
                json=payload,
            )

    async def login(self, payload: dict) -> httpx.Response:
        return await self._post("/login", payload)

    async def ai_nosql(self, payload: dict) -> httpx.Response:
        return await self._post("/query", payload, timeout=120.0)

    async def add_user(self, payload: dict) -> httpx.Response:
        return await self._post("/add_users", payload)

    async def delete_user(self, payload: dict) -> httpx.Response:
        return await self._post("/delete_users", payload)

    async def add_document(self, payload: dict) -> httpx.Response:
        return await self._post("/add_documents", payload)

    async def update_document(self, payload: dict) -> httpx.Response:
        return await self._put("/update_documents", payload)

    async def drop_collection(self, payload: dict) -> httpx.Response:
        return await self._post("/drop_collections", payload)

    async def update_user(self, payload: dict) -> httpx.Response:
        return await self._put("/update_users", payload)

    async def list_databases(self) -> httpx.Response:
        return await self._get("/databases")

    async def list_collections(self, payload: dict) -> httpx.Response:
        return await self._post("/collections", payload)