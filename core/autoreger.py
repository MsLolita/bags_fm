import random
import traceback
from asyncio import Semaphore, create_task, gather, sleep

from core.utils import file_to_list, shift_file, logger, CookiesManager
from core.bags import Bags

from data.config import (
    REFERRAL, THREADS, CUSTOM_DELAY, TWITTERS_FILE_PATH, PROXIES_FILE_PATH
)


class AutoReger:
    def __init__(self):
        self.success = 0

    @staticmethod
    def get_accounts():
        twitters = CookiesManager(TWITTERS_FILE_PATH).get_cookies()
        proxies = file_to_list(PROXIES_FILE_PATH)

        min_accounts_len = len(twitters)

        if not twitters:
            logger.info(f"No twitters!")
            return

        accounts = []

        for i in range(min_accounts_len):
            accounts.append((
                twitters[i],
                proxies[i] if len(proxies) > i else None
            ))

        return accounts

    @staticmethod
    def remove_account():
        return shift_file(TWITTERS_FILE_PATH), shift_file(PROXIES_FILE_PATH)

    async def start(self):
        Bags.referral = REFERRAL.split('/$')[-1]

        accounts = AutoReger.get_accounts()

        if not accounts:
            return

        logger.info(f"Successfully grab {len(accounts)} accounts")

        semaphore = Semaphore(THREADS)

        tasks = []
        for account in accounts:
            task = create_task(self.register(account, semaphore))
            tasks.append(task)

        await gather(* tasks, return_exceptions=True)

        if self.success:
            logger.success(f"Successfully registered {self.success} accounts :)")
        else:
            logger.warning(f"No accounts registered :(")

    async def register(self, account: tuple, semaphore: Semaphore):
        cookies, proxy = account
        logs = {"ok": False, "msg": ""}

        try:
            async with semaphore:
                bags = Bags(cookies, proxy)
                await AutoReger.custom_delay()

                await bags.define_session()

                logs["ok"] = await bags.register()
        except Exception as e:
            logs["msg"] = e
            logger.debug(f"Error: {e} | {traceback.format_exc()}")
            logger.error(f"Error {e}")

        await bags.close()

        AutoReger.remove_account()

        if logs["ok"]:
            bags.logs("success", logs["msg"])
            self.success += 1
        else:
            bags.logs("fail", logs["msg"])

    @staticmethod
    async def custom_delay():
        if CUSTOM_DELAY[1] > 0:
            sleep_time = random.uniform(CUSTOM_DELAY[0], CUSTOM_DELAY[1])
            logger.info(f"Sleep for {int(sleep_time)} seconds")
            await sleep(sleep_time)

    @staticmethod
    def is_file_empty(path: str):
        return not open(path).read().strip()
