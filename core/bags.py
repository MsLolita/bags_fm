from fake_useragent import UserAgent

from core.utils import (
    InitSession,
    Twitter,
    logger, str_to_file
)
from core.utils.handlers import retry_for_success


class Bags(InitSession):
    referral = None

    def __init__(self, cookies: dict, proxy: str | None) -> None:
        super().__init__(proxy=proxy)
        self.twitter = Twitter(cookies, proxy)

        self.headers = {
            'authority': 'api.bags.fm',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'uk-UA,uk;q=0.9',
            'referer': 'https://bags.fm/',
            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random,
        }

        self.cookies = {'invited_by': Bags.referral}

        self.username = None

    async def register(self):
        await self.twitter.define_session()

        await self.twitter.set_up_cookies()

        self.username = await self.bind_twitter()
        if self.username is not None:
            return True

    async def bind_twitter(self):
        logger.debug(f"Starting to bind twitter")
        oauth_token = await self.get_oauth_token()
        oauth_verifier = await self.twitter.bind(oauth_token)

        return await self.approve_binding(oauth_token, oauth_verifier)

    @retry_for_success()
    async def get_oauth_token(self):
        url = 'https://api.bags.fm/api/v1/twitter/login'

        response = await self.session.get(url, allow_redirects=False)
        resp_text = await response.text()
        if "https://bags.fm" not in resp_text:
            oauth_token = Bags.parse_oauth_token(resp_text)
            logger.debug(f"Get oauth_token: {oauth_token}")
            return oauth_token

    @staticmethod
    def parse_oauth_token(resp_text: str):
        return resp_text.split('?oauth_token=')[1].split('">')[0]

    @retry_for_success()
    async def approve_binding(self, oauth_token: str, oauth_verifier: str):
        url = 'https://api.bags.fm/api/v1/twitter/callback'

        params = {
            'oauth_token': oauth_token,
            'oauth_verifier': oauth_verifier,
        }

        response = await self.session.get(url, params=params)
        resp_text = await response.text()

        logger.debug(f"approve_binding: {resp_text}")
        if "error" not in resp_text.lower():
            username = resp_text.split('"username":"')[1].split('","')[0]

            return username

    def logs(self, file_name: str, msg_result: str = "can't register"):
        file_msg = f"{self.twitter}|{self.proxy}"
        str_to_file(f"./logs/{file_name}.txt", file_msg)

        if msg_result:
            msg_result = f" | {msg_result}"
        if file_name == "success":
            logger.success(f"{self.username}{msg_result}")
        else:
            logger.error(f"{self.username}{msg_result}")

    async def close(self):
        await super().close()
        await self.twitter.close()
