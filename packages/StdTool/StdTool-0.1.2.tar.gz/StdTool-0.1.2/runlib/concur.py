import contextlib
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Iterable, Callable
from ..syslib.console import tqdm


@contextlib.contextmanager
def thread_as_complete(func: Callable, arg_iter: Iterable, process=4):
    with ThreadPoolExecutor(max_workers=process) as pool:
        with tqdm(as_completed([pool.submit(func, i) for i in arg_iter]), total=len(list(arg_iter))) as iter_:
            yield iter_


@contextlib.contextmanager
def process_as_complete(func: Callable, arg_iter: Iterable, process=4):
    with ProcessPoolExecutor(max_workers=process) as pool:
        with tqdm(as_completed([pool.submit(func, i) for i in arg_iter]), total=len(list(arg_iter))) as iter_:
            yield iter_


def test(ts):
    time.sleep(ts)
    return ts


if __name__ == '__main__':

    print(time.ctime())
    with process_as_complete(_test, range(10)) as c:
        for i in c:
            print(time.ctime(), i.result(), 'xx')
