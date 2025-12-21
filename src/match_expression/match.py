from __future__ import annotations

import inspect
from enum import Enum
from typing import Any, Callable, Literal, TypeGuard, overload

PRIMITIVE_TYPES = (int, float, str, bool, bytes, type(None))
COLLECTION_TYPES = (list, tuple, dict, set, frozenset)
BUILTIN_TYPES = PRIMITIVE_TYPES + COLLECTION_TYPES


class Match[V]:
    def __init__(self, value: V) -> None:
        self.value = value

    @overload
    def case[P, R](
        self,
        pattern: type[P],
        then: Callable[[P], R],
    ) -> Case[V, P, R]: ...

    @overload
    def case[P, R](
        self,
        pattern: type[P],
        then: Callable[[], R],
    ) -> Case[V, P, R]: ...

    @overload
    def case[P, R](
        self,
        pattern: type[P],
        then: R,
    ) -> Case[V, P, R]: ...

    @overload
    def case[P, R](
        self,
        pattern: P,
        then: Callable[[P], R],
    ) -> Case[V, P, R]: ...

    @overload
    def case[P, R](
        self,
        pattern: P,
        then: Callable[[], R],
    ) -> Case[V, P, R]: ...

    @overload
    def case[P, R](
        self,
        pattern: P,
        then: R,
    ) -> Case[V, P, R]: ...

    def case[P, R](
        self,
        pattern: P | type[P],
        then: R | Callable[[P], R] | Callable[[], R],
    ) -> Case[V, P, R]:
        if isinstance(pattern, type):
            matched = isinstance(self.value, pattern)
        else:
            if type(pattern) in PRIMITIVE_TYPES or isinstance(pattern, Enum):
                # Primitive type matching
                matched = self.value == pattern
            elif type(pattern) in COLLECTION_TYPES:
                # Collection type matching
                matched = False  # TODO: implement collection matching
            else:
                # Custom type matching
                matched = type(pattern) is type(self.value)

        return Case(self.value, then, matched) 


class Case[V, P, R]:
    def __init__(
        self, value: V, then: R | Callable[[P], R] | Callable[[], R], matched: bool
    ) -> None:
        self.value = value
        self.then = then
        self.matched = matched

    @overload
    def case[UP, UR](
        self,
        pattern: type[UP],
        then: Callable[[UP], UR],
    ) -> Case[V, P | UP, R | UR]: ...

    @overload
    def case[UP, UR](
        self,
        pattern: type[UP],
        then: Callable[[], UR],
    ) -> Case[V, P | UP, R | UR]: ...

    @overload
    def case[UP, UR](
        self,
        pattern: type[UP],
        then: UR,
    ) -> Case[V, P | UP, R | UR]: ...

    @overload
    def case[UP, UR](
        self,
        pattern: UP,
        then: Callable[[UP], UR],
    ) -> Case[V, P | UP, R | UR]: ...

    @overload
    def case[UP, UR](
        self,
        pattern: UP,
        then: Callable[[], UR],
    ) -> Case[V, P | UP, R | UR]: ...

    @overload
    def case[UP, UR](
        self,
        pattern: UP,
        then: UR,
    ) -> Case[V, P | UP, R | UR]: ...

    def case[UP, UR](
        self,
        pattern: UP | type[UP],
        then: UR | Callable[[UP], UR] | Callable[[], UR],
    ) -> Case[V, P | UP, R | UR]:
        if self.matched:
            return self

        if isinstance(pattern, type):
            matched = isinstance(self.value, pattern)
        else:
            if type(pattern) in PRIMITIVE_TYPES or isinstance(pattern, Enum):
                # Primitive type matching
                matched = self.value == pattern
            elif type(pattern) in COLLECTION_TYPES:
                # Collection type matching
                matched = False  # TODO: implement collection matching
            else:
                # Custom type matching
                matched = type(pattern) is type(self.value)

        return Case(self.value, then, matched) 

    @overload
    def exhaustive(self) -> R: ...

    @overload
    def exhaustive(self, eval: Literal[True]) -> R: ...

    @overload
    def exhaustive(
        self, eval: Literal[False]
    ) -> Callable[[P], R] | Callable[[], R]: ...

    def exhaustive(self, eval: bool = True) -> R | Callable[[P], R] | Callable[[], R]:
        if not self.matched:
            raise ExhaustiveError(self.value)
        if eval:
            return _unwrap(self.value, self.then)
        else:
            return self.then

    @overload
    def otherwise[UR](
        self,
        default: UR | Callable[[], UR],
    ) -> R | UR: ...

    @overload
    def otherwise[UR](
        self,
        default: UR | Callable[[], UR],
        eval: Literal[True],
    ) -> R | UR: ...

    @overload
    def otherwise[UR](
        self,
        default: UR | Callable[[], UR],
        eval: Literal[False],
    ) -> Callable[[P], R] | Callable[[], R | UR]: ...

    def otherwise[UR](
        self,
        default: UR | Callable[[], UR],
        eval: bool = True,
    ) -> R | UR | Callable[[P], R] | Callable[[], R | UR]:
        if self.matched:
            if eval:
                return _unwrap(self.value, self.then)
            else:
                return self.then
        if eval and callable(default):
            return default()
        return default


def match[V](value: V) -> Match[V]:
    return Match[V](value)


def _is_not_callable[V, R](
    value: R | Callable[[V], R] | Callable[[], R],
) -> TypeGuard[R]:
    return not callable(value)


def _is_class[R](value: Callable[..., R]) -> TypeGuard[type[R]]:
    return inspect.isclass(value)


def _is_no_arg_callable[V, R](
    func: Callable[[], R] | Callable[[V], R],
) -> TypeGuard[Callable[[], R]]:
    sig = inspect.signature(func)
    return len(sig.parameters) == 0


def _unwrap[V, R](
    value: V,
    then: R | Callable[[V], R] | Callable[[], R],
) -> R:
    if _is_not_callable(then):
        return then

    if _is_class(then):
        return then 

    if _is_no_arg_callable(then):
        return then()
    else:
        return then(value)


class ExhaustiveError(Exception):
    def __init__(self, value: Any) -> None:
        super().__init__(f"Non-exhaustive match. Unhandled value: {value}")
        self.value = value
