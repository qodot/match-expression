from __future__ import annotations

import inspect
from typing import Any, Callable, TypeGuard


def unwrap[V, R](
    value: V,
    then: R | Callable[..., R],
) -> R:
    if _is_not_callable(then):
        return then

    if _is_class(then):
        return then

    param_count = _get_callable_param_count(then)

    if param_count == 0:
        return then()
    elif param_count == 1:
        return then(value)
    else:
        if isinstance(value, tuple):
            return then(*value)
        return then(value)


def _is_not_callable[V, R](
    value: R | Callable[[V], R] | Callable[[], R],
) -> TypeGuard[R]:
    return not callable(value)


def _is_class[R](value: Callable[..., R]) -> TypeGuard[type[R]]:
    return inspect.isclass(value)


def _get_callable_param_count(func: Callable[..., Any]) -> int:
    sig = inspect.signature(func)
    return len(sig.parameters)
