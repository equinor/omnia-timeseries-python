from functools import wraps
import random
import time
from typing import Optional
import requests
from omnia_timeseries.models import TimeseriesRequestFailedException

# Reasonable status codes to retry, based on descriptions at https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
retry_status_codes = [408, 409, 425, 429, 502, 503, 504]

# Bound server-provided delays so a malformed header cannot stall a caller.
max_retry_after_seconds = 30.0


def _wait_time(delay: float, retry_after: Optional[float] = None) -> float:
    """Jitter retries and honor Retry-After without waiting less than requested."""
    wait = random.uniform(delay / 2, delay)
    if retry_after is not None:
        wait = max(wait, min(retry_after, max_retry_after_seconds))
    return wait


def retry(total_tries=3, initial_wait=0.5, backoff_factor=2, logger=None):
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = total_tries, initial_wait
            exception = None
            while _tries > 0:
                if logger is not None:
                    logger.debug(f"{total_tries + 1 - _tries}. try:")
                try:
                    return f(*args, **kwargs)
                except (
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError,
                ) as e:
                    if not (
                        isinstance(e, requests.exceptions.ConnectTimeout)
                        or kwargs.get("request_type") == "get"
                    ):
                        raise
                    _tries -= 1
                    exception = e
                    wait = _wait_time(_delay)
                    _delay *= backoff_factor
                    if _tries > 0:
                        if logger is not None:
                            logger.warning(
                                f"Function: {f.__name__} failed with {type(e).__name__}. Retrying in {wait:.2f} seconds, with {_tries} retries remaining!"
                            )
                        time.sleep(wait)
                    elif logger is not None:
                        logger.warning(
                            f"Function: {f.__name__} Failed despite best efforts after {total_tries} tries."
                        )
                except TimeseriesRequestFailedException as e:
                    _tries -= 1
                    if e.status_code in retry_status_codes:
                        wait = _wait_time(_delay, e.retry_after)
                        if _tries == 0:
                            msg = str(
                                f"Function: {f.__name__} Failed despite best efforts after {total_tries} tries."
                            )
                            if logger is not None:
                                logger.warning(msg)
                        else:
                            msg = str(
                                f"Function: {f.__name__} failed with {e}. Retrying in {wait:.2f} seconds, with {_tries} retries remaining!\n"
                            )
                            if logger is not None:
                                logger.warning(msg)
                        if _tries > 0:
                            time.sleep(wait)
                        _delay *= backoff_factor
                        exception = e
                    else:
                        if logger is not None:
                            logger.debug(f"Status code {e.status_code} not retryable")
                        exception = e
                        break
            if exception is not None:
                raise exception

        return func_with_retries

    return retry_decorator
