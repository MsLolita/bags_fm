import asyncio
import traceback

from core.utils import logger


def retry_for_success(max_attempts=3, delay=1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for _ in range(max_attempts):
                try:
                    result = await func(*args, **kwargs)
                    if result:
                        return result
                except Exception as e:
                    logger.debug(f"Retry Error: {e} | {traceback.format_exc()}")
                await asyncio.sleep(delay)  # Adjust the sleep duration as needed
            raise Exception(f"Unvalid response")
            # return None  # Or raise an exception if needed
        return wrapper
    return decorator
