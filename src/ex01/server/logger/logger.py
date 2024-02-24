from loguru import logger
from functools import wraps
from time import perf_counter

def Loger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        logger.info(f"function start: ({func.__name__}) with parameters:\n{args}:\n")
        start = perf_counter()
        try:
            result = func(*args, **kwargs)
            logger.info(f"The function ({func.__name__}) ended with the result:\n{result}")
            logger.info(f"The function ({func.__name__}) has been completed for {(perf_counter() - start):.4f}\n")
        except Exception as e:
                logger.exception(f"The function ({func.__name__}) ended with an error", e)
        return result
    return wrapper