import time as _time
import datetime as _datetime
from .console import Fore

now = _datetime.datetime.now
time_ = _time.time
wait = _time.sleep
f_now = lambda: now().strftime('%Y-%m-%d %H:%M:%S')
c_now = lambda: now().ctime()
week = lambda: now().weekday()


def time_counter(func):
    from functools import wraps

    @wraps(func)
    def inner(*args, **kwargs):
        t = _time.perf_counter()
        ret = func(*args, **kwargs)
        print(
            f'{Fore.RESET}函数{Fore.LIGHTYELLOW_EX}{func.__name__}{Fore.RESET}运行耗时:{Fore.RED}{_time.perf_counter() - t:.12f} s{Fore.RESET}')
        return ret

    return inner
