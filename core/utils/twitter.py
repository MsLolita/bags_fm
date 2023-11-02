from typing import Optional

from core.utils import InitSession, logger


class Twitter(InitSession):
    def __init__(self, cookies: Optional[dict] = None, proxy: Optional[str] = None) -> None:
        super().__init__(proxy=proxy)

        self.cookies = cookies

        self.headers = {
            'authority': 'api.twitter.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://api.twitter.com',
            'referer': 'https://api.twitter.com/oauth/authenticate',
            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        }

    async def set_up_cookies(self):
        self.session.cookie_jar.update_cookies(self.cookies)
        if len(self.cookies.keys()) == 1:
            await self.set_up_cookies_by_ct0()

    async def set_up_cookies_by_ct0(self):
        url = 'https://api.twitter.com/1.1/account/settings.json'

        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'uk',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'content-type': 'application/json',
            'origin': 'https://twitter.com',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en',
        }

        params = {'include_mention_filter': 'true', 'include_nsfw_user_flag': 'true', 'include_nsfw_admin_flag': 'true', 'include_ranked_timeline': 'true', 'include_alt_text_compose': 'true', 'ext': 'ssoConnections', 'include_country_code': 'true', 'include_ext_dm_nsfw_media_filter': 'true', 'include_ext_sharing_audiospaces_listening_data_with_followers': 'true'}

        res = await self.session.get(url, headers=headers, params=params)

        self.session.headers['x-csrf-token'] = res.cookies["ct0"].value

    async def bind(self, oauth_token: str):
        authenticity_token = await self.authentication(oauth_token)
        logger.debug(f"Get authenticity_token: {authenticity_token}")
        return await self.authorize(authenticity_token, oauth_token)

    async def authentication(self, oauth_token: str):
        url = "https://api.twitter.com/oauth/authenticate"

        params = {
            "oauth_token": oauth_token
        }

        response = await self.session.get(url, params=params)
        resp_text = await response.text()

        # self.username = resp_text.split('<span class="name">')[1].split('</')[0]

        return resp_text.split('authenticity_token" value="')[1].split('"')[0]

    async def authorize(self, authenticity_token: str, auth_token: str):
        url = 'https://api.twitter.com/oauth/authorize'

        data = {
            'authenticity_token': authenticity_token,
            'redirect_after_login': f'https://api.twitter.com/oauth/authorize?oauth_token={auth_token}',
            'oauth_token': auth_token,
        }

        response = await self.session.post(url, data=data)
        resp_text = await response.text()

        oauth_verifier = resp_text.split("oauth_verifier=")[1].split('">')[0]
        logger.debug(f"Get oauth_verifier: {oauth_verifier}")

        return oauth_verifier
