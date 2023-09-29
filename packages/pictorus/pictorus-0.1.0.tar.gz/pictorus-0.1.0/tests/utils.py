import time
from typing import Callable


def wait_for_condition(condition: Callable[[], bool], timeout=1):
    start = time.time()
    while not condition():
        if time.time() - start > timeout:
            raise TimeoutError()

        time.sleep(0.1)
