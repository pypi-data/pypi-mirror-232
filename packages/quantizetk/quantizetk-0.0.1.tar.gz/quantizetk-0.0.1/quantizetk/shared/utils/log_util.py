import time
from typing import Callable, TypeVar

T = TypeVar("T")


def log(
    func: Callable[..., T],
    msg: str,
    log_result: bool = False,
    format_result: Callable[..., str] = str,
):
    message = f"start: [ {msg} ]"

    print(message)

    start = time.time()
    value = func()
    end = time.time()

    message = f"end: [ {msg} ] : [ {str(end-start)}s ]"
    if log_result:
        message += f" : [{format_result(value)}]"
    print(message)

    return value
