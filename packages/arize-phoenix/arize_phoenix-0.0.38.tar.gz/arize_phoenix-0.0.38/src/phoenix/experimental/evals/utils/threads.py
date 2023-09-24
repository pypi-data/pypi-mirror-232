"""High-level support for working with threads in asyncio
Directly copied from: https://github.com/python/cpython/blob/main/Lib/asyncio/threads.py#L12
since this helper function 'to_thread' is not available in python<3.9
"""

import contextvars
import functools
from asyncio import events
from typing import Any

__all__ = ("to_thread",)


async def to_thread(func, /, *args, **kwargs) -> Any:  # type:ignore
    """Asynchronously run function *func* in a separate thread.

    Any *args and **kwargs supplied for this function are directly passed
    to *func*. Also, the current :class:`contextvars.Context` is propagated,
    allowing context variables from the main thread to be accessed in the
    separate thread.

    Return a coroutine that can be awaited to get the eventual result of *func*.
    """
    loop = events.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)
