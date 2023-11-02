import asyncio

from core.utils import logger


def retry_for_success(max_attempts=12, delay=0):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for _ in range(max_attempts):
                try:
                    result = await func(*args, **kwargs)
                    if result:
                        return result
                except Exception as e:
                    logger.debug(f"Retry Error: {e}")
                await asyncio.sleep(delay)  # Adjust the sleep duration as needed
            raise Exception(f"Unvalid response")
            # return None  # Or raise an exception if needed
        return wrapper
    return decorator
