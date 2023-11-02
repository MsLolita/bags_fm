from typing import Optional

from aiohttp import ClientSession
from aiohttp_proxy import ProxyConnector

from data.config import MOBILE_PROXY, MOBILE_PROXY_CHANGE_IP_LINK


class InitSession:
    def __init__(self, proxy: Optional[str] = None) -> None:
        self.proxy = proxy

        self.cookies = None
        self.headers = None
        self.session = None

    async def define_session(self):
        if MOBILE_PROXY:
            await InitSession.change_ip()
            self.proxy = MOBILE_PROXY

        self.session = ClientSession(
            headers=self.headers,
            connector=ProxyConnector.from_url(f"http://{self.proxy}") if self.proxy else None,
            cookies=self.cookies
        )

    @staticmethod
    async def change_ip():
        async with ClientSession() as session:
            await session.get(MOBILE_PROXY_CHANGE_IP_LINK)

    async def close(self):
        await self.session.close()
