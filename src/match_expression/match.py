from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Literal, overload

from .error import ExhaustiveError
from .helper import unwrap

PRIMITIVE_TYPES = (int, float, str, bool, bytes, type(None))


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
        matched = _check_match(self.value, pattern)
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

        matched = _check_match(self.value, pattern)
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
            return unwrap(self.value, self.then)
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
                return unwrap(self.value, self.then)
            else:
                return self.then
        if eval and callable(default):
            return default()
        return default


def match[V](value: V) -> Match[V]:
    return Match[V](value)


def _check_match(value: Any, pattern: Any) -> bool:
    if isinstance(pattern, type):
        return isinstance(value, pattern)
    elif isinstance(pattern, tuple):
        return _match_tuple(value, pattern)
    else:
        return _match_element(value, pattern)


def _match_tuple(value: Any, pattern: tuple[Any, ...]) -> bool:
    if not isinstance(value, tuple):
        return False
    if len(value) != len(pattern):
        return False
    return all(_match_element(v, p) for v, p in zip(value, pattern))


def _match_element(value: Any, pattern: Any) -> bool:
    if isinstance(pattern, type):
        return isinstance(value, pattern)
    elif type(pattern) in PRIMITIVE_TYPES or isinstance(pattern, Enum):
        return value == pattern
    else:
        return type(value) is type(pattern)
