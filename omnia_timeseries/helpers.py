from functools import wraps
import time

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
                except Exception as e:
                    _tries -= 1
                    if _tries == 0:
                        msg = str(f'Function: {f.__name__} Failed despite best efforts after {total_tries} tries.')
                        logger.warning(msg)
                    else:
                        msg = str(f'Function: {f.__name__} failed with {e}. Retrying in {_delay} seconds, with {_tries} retries remaining!\n')
                        logger.warning(msg)
                    time.sleep(_delay)
                    _delay *= backoff_factor
                    exception = e
            if exception is not None:
                raise exception

        return func_with_retries
    return retry_decorator