import time
from openai import (
    APIConnectionError, APITimeoutError, RateLimitError, InternalServerError
)

from utils.logger import logger


def is_retryable_error(error):
    return isinstance( error,
                      (APIConnectionError, APITimeoutError, RateLimitError,
                       InternalServerError,))


def wait_before_retry(attempt):
    wait_time = 2** attempt

    logger.warning(
        "Temporary API error, Retrying in %s seconds.",
        wait_time,
    )

    time.sleep(wait_time)