from typing import Optional


import aiohttp
from aiohttp import ClientSession
from aiohttp_proxy import ProxyConnector

from data.config import MOBILE_PROXY, MOBILE_PROXY_CHANGE_IP_LINK


class InitSession:
    def __init__(self, proxy: Optional[str] = None) -> None:
        self.proxy = proxy

        self.session = ClientSession(
            connector=ProxyConnector.from_url(self.proxy) if self.proxy else None
        )

    async def define_proxy(self, proxy: str):
        if MOBILE_PROXY:
            await InitSession.change_ip()
            self.proxy = MOBILE_PROXY

        if proxy is not None:
            self.proxy = f"http://{proxy}"

    @staticmethod
    async def change_ip():
        async with ClientSession() as session:
            await session.get(MOBILE_PROXY_CHANGE_IP_LINK)

    async def close(self):
        await self.session.close()
