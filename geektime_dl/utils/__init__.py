# coding=utf8
from functools import wraps
from ._logging import logger


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def synchronized(lock_attr='_lock'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            lock = getattr(self, lock_attr)
            try:
                lock.acquire()
                return func(self, *args, **kwargs)
            finally:
                lock.release()
        return wrapper
    return decorator


def format_path(path):
    return path.replace(' ', '').replace('/', '').replace('\\', '').replace(':', '')


def debug_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug("function={}\targs={}\tkwargs={}".format(func.__name__, args, kwargs))
        return result

    return wrapper


