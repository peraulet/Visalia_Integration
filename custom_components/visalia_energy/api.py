# -----------------------------
# custom_components/visalia_energy/api.py
# -----------------------------
import aiohttp

class VisaliaAPI:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None

    async def authenticate(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://siri.visalia.rocks/api/v1/users/token/",
                json={"username": self.username, "password": self.password},
            ) as resp:
                data = await resp.json()
                self.token = data.get("access")

    async def get_invoices(self):
        if not self.token:
            await self.authenticate()

        headers = {"Authorization": f"Bearer {self.token}"}

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get("https://siri.visalia.rocks/api/v1/invoices/?page=1") as resp:
                if resp.status == 401:
                    # Token expirado, reintenta autenticación
                    await self.authenticate()
                    headers["Authorization"] = f"Bearer {self.token}"
                    async with aiohttp.ClientSession(headers=headers) as retry_session:
                        retry_resp = await retry_session.get("https://siri.visalia.rocks/api/v1/invoices/?page=1")
                        return await retry_resp.json()
                return await resp.json()
