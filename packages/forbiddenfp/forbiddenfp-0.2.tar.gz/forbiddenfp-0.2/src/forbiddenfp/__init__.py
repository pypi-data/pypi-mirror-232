import collections
import functools
import inspect
from numbers import Number
from typing import Callable, List, NoReturn, Optional, Dict, TypeVar, Iterable, Sequence, Tuple

from forbiddenfruit import curse
from typing_extensions import Self, ParamSpec

P = ParamSpec("P")
R = TypeVar("R")
F = Callable[[P], R]


# https://github.com/yx-z/daydream/edit/master/meta.py
# A loose mockup of Haskell's `let ... in ...` notation
# to restrict variable scope in the expression only (in `__rshift__`)
class let:
    def __init__(self: Self, **kwargs: P.kwargs) -> None:
        self.existing_globals = {k: globals()[k] for k in kwargs if k in globals()}
        self.temp_globals = {k for k in kwargs if k not in globals()}
        inspect.currentframe().f_back.f_globals.update(kwargs)
        globals().update({k: v for k, v in kwargs.items() if not isinstance(v, lazy)})
        for k, v in filter(lambda t: isinstance(t[1], lazy), kwargs.items()):
            inspect.currentframe().f_back.f_globals[k] = v

    T = TypeVar("T")

    def __rshift__(self: Self, val: T) -> T:
        inspect.currentframe().f_back.f_globals.update(self.existing_globals)
        for k in self.temp_globals:
            del inspect.currentframe().f_back.f_globals[k]
        return val


# sentinel class to lazy eval `kwargs` in `let`
class lazy:
    def __init__(self: Self, expr: str) -> None:
        if not isinstance(expr, str):
            raise RuntimeError(f"<class lazy> expects expression str, got {expr}")
        self.expr = expr


def constantly(val: P) -> Callable[..., P]:
    return lambda *args, **kwargs: val


def identity(val: P) -> P:
    return val


def chainable(func: F, /) -> F:
    curse(object, func.__name__, func)
    return func


@chainable
def apply(self: P, func: F, /) -> P:
    func(self)
    return self


@chainable
def then(self: P, func: F, /) -> R:
    return func(self)


@chainable
def assign(self: P, **kwargs: P.kwargs) -> P:
    for k, v in kwargs.items():
        setattr(self, k, v)
    return self


@chainable
def apply_unpack(self: P, func: F, /) -> R:
    func(*self)
    return self


@chainable
def then_unpack(self: P, func: F, /) -> R:
    return func(*self)


@chainable
def transform(self: Iterable[P], func: Callable[[P], R], /) -> Iterable[R]:
    return (func(i) for i in self)


P2 = ParamSpec("P2")
R2 = TypeVar("R2")


@chainable
def transform_dict(self: Dict[P, P2], *, key_func: Callable[[P], R] = identity,
                   val_func: Callable[[P2], R2] = identity) -> Dict[R, R2]:
    return {key_func(k): val_func(v) for k, v in self.items()}


@chainable
def require(self: Iterable[P], func: Callable[[P], bool], /) -> Iterable[P]:
    return (i for i in self if func(i))


@chainable
def require_val(self: Dict[P, P2], func: Callable[[P2], bool], /) -> Dict[P, P2]:
    return {k: v for k, v in self.items() if func(v)}


@chainable
def last(self: Sequence[P], *, predicate: Callable[[P], bool] = constantly(True)) -> P:
    return next(i for i in reversed(self) if predicate(i))


@chainable
def first(self: Iterable[P], *, predicate: Callable[[P], bool] = constantly(True)) -> P:
    return next(i for i in self if predicate(i))


@chainable
def total(self: Iterable[P], *, by_func: Callable[[P], Number] = identity,
          predicate: Callable[[P], bool] = constantly(True)) -> int:
    return sum(by_func(i) for i in self if predicate(i))


@chainable
def count(self: Iterable[P], *, filter_func: Callable[[P], bool] = constantly(True)) -> int:
    return sum(1 for i in self if filter_func(i))


@chainable
def reverse(self: Sequence[P]) -> Sequence[P]:
    return reversed(self)


@chainable
def to_sorted(self: Iterable[P], by_func: Callable[[P], R] = identity, /) -> List[P]:
    return sorted(self, key=by_func)


@chainable
def fold(self: Iterable[P], func: Callable[[P, P], R], *, init: Optional[R] = None) -> R:
    return functools.reduce(func, self, init) if init is not None else functools.reduce(func, self)


@chainable
def partition(self: Iterable[P], func: Callable[[P], bool], /) -> Tuple[List[P], List[P]]:
    true = []
    false = []
    for i in self:
        if func(i):
            true.append(i)
        else:
            false.append(i)
    return true, false


@chainable
def frequency(self: Iterable[P]) -> Dict[P, int]:
    return collections.Counter(self)


@chainable
def group_by(self: Iterable[P], extract: Callable[[P], R]) -> Dict[R, List[P]]:
    res = collections.defaultdict(list)
    for i in self:
        res[extract(i)].append(i)
    return res


@chainable
def if_present(self: P, func: Callable[[P], R], /) -> Optional[R]:
    return func(self) if self else None


@chainable
def or_else(self: P, val: R, /) -> R:
    return self if self else val


@chainable
def or_eval(self: P, func: Callable[[P], R], /) -> R:
    return self if self else func(self)


@chainable
def or_raise(self: P, func: Callable[[P], Exception], /) -> P:
    if self:
        return self
    raise func(self)


@chainable
def raise_as(self: P, func: Callable[[P], Exception], /) -> NoReturn:
    raise func(self)
