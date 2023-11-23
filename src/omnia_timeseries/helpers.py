from functools import wraps
from logging import debug
import time
from omnia_timeseries.models import TimeseriesRequestFailedException

# Reasonable status codes to retry, based on descriptions at https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
retry_status_codes = [408, 409, 425, 429, 502, 503, 504]


def retry(total_tries=3, initial_wait=0.5, backoff_factor=2, logger=None):
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = total_tries, initial_wait
            exception = None
            while _tries > 0:
                logger.debug(f'{total_tries + 1 - _tries}. try:')
                try:
                    return f(*args, **kwargs)
                except TimeseriesRequestFailedException as e:
                    _tries -= 1
                    if e.status_code in retry_status_codes:
                        if _tries == 0:
                            msg = str(
                                f'Function: {f.__name__} Failed despite best efforts after {total_tries} tries.')
                            logger.warning(msg)
                        else:
                            msg = str(
                                f'Function: {f.__name__} failed with {e}. Retrying in {_delay} seconds, with {_tries} retries remaining!\n')
                            logger.warning(msg)
                        time.sleep(_delay)
                        _delay *= backoff_factor
                        exception = e
                    else:
                        logger.debug(
                            f"Status code {e.status_code} not retryable")
                        exception = e
                        break
            if exception is not None:
                raise exception

        return func_with_retries
    return retry_decorator
