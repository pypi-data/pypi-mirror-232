import inspect
from typing import Callable, List, NoReturn, Optional, Dict, TypeVar, Any, Iterable

from typing_extensions import Self, ParamSpec

from forbiddenfruit import curse

__all__ = ["let", "lazy", "apply", "then", "assign", "unpack_self", "unpack_then", "transform", "transform_dict",
           "require", "require_val", "if_present", "or_else", "or_eval", "or_raise", "raising"]

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
def unpack_self(self: P, func: F, /) -> R:
    func(*self)
    return self


@chainable
def unpack_then(self: P, func: F, /) -> R:
    return func(*self)


@chainable
def transform(self: Iterable[P], func: Callable[[P], R], /) -> List[R]:
    return [func(i) for i in self]


P2 = ParamSpec("P2")
R2 = TypeVar("R2")


@chainable
def transform_dict(self: Dict[P, P2], *, key_func: Callable[[P], R] = lambda k: k,
                   val_func: Callable[[P2], R2] = lambda v: v) -> Dict[R, R2]:
    return {key_func(k): val_func(v) for k, v in self.items()}


@chainable
def require(self: Iterable[P], func: Callable[[P], bool], /) -> List[P]:
    return [i for i in self if func(i)]


@chainable
def require_val(self: Dict[P, P2], func: Callable[[P2], bool], /) -> Dict[P, P2]:
    return {k: v for k, v in self.items() if func(v)}


@chainable
def first_if(self: Iterable[P], func: Callable[[P], bool], /) -> P:
    return next(i for i in self if func(i))


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
def raising(self: P, func: Callable[[P], Exception], /) -> NoReturn:
    raise func(self)
