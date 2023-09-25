import builtins
import collections
import functools
import inspect
import itertools
import operator
from numbers import Number
from typing import Callable, List, NoReturn, Optional, Dict, TypeVar, Iterable, Sequence, Tuple, Union, Set, Type, \
    Protocol

from forbiddenfruit import curse
from typing_extensions import Self, ParamSpec

_P = ParamSpec("_P")
_R = TypeVar("_R")
_F = Callable[[_P], _R]
_Pred = Callable[[_P], bool]
_P2 = ParamSpec("_P2")
_R2 = TypeVar("_R2")


# https://github.com/yx-z/daydream/edit/master/meta.py
class let:
    """
    x = 10
    let(x=1) >> x+2  # 3
    x == 10
    """

    def __init__(self: Self, /, **kwargs: _P.kwargs) -> None:
        glob = inspect.currentframe().f_back.f_globals
        self.existing_globals = {k: glob[k] for k in kwargs if k in glob}
        self.temp_globals = {k for k in kwargs if k not in glob}
        glob.update(kwargs)
        for k, v in builtins.filter(lambda t: isinstance(t[1], lazy), kwargs.items()):
            glob[k] = eval(v.expr, glob, inspect.currentframe().f_back.f_locals)

    def __rshift__(self: Self, val: _P, /) -> _P:
        glob = inspect.currentframe().f_back.f_globals
        glob.update(self.existing_globals)
        for k in self.temp_globals:
            del glob[k]
        return val


class lazy:
    """
    x = 10
    let(x=1, y=lazy("x+1")) >> x+y  # 3
    x == 10
    """

    def __init__(self: Self, expr: builtins.str, /) -> None:
        if not isinstance(expr, builtins.str):
            raise RuntimeError(f"<class lazy> expects expression str, got {expr}")
        self.expr = expr


def always(val: _P, /) -> Callable[..., _P]:
    return lambda *args, **kwargs: val


def identity(val: _P, /) -> _P:
    return val


def chain_only(func: _F, /) -> None:
    curse(object, func.__name__, func)


def chainable(func: _F, /) -> _F:
    chain_only(func)
    return func


@chain_only
def apply(self: _P, func: _F, /) -> _P:
    func(self)
    return self


@chain_only
def also(self: _P, val_unused: _R) -> _P:
    # side effect is evaluated (which resulted in `val_unused`) before passed in to this function
    return self


@chain_only
def then(self: _P, func: _F, /) -> _R:
    return func(self)


@chain_only
def setattr(self: _P, /, **kwargs: _P.kwargs) -> _P:
    for k, v in kwargs.items():
        builtins.setattr(self, k, v)
    return self


@chain_only
def setitem(self: _P, /, key: _P2, val: _R) -> _P:
    self[key] = val
    return self


@chain_only
def apply_unpack(self: _P, func: _F, /) -> _R:
    func(*self)
    return self


@chain_only
def then_unpack(self: _P, func: _F, /) -> _R:
    return func(*self)


@chain_only
def min(self: Iterable[_P], /, *, key: _F = identity) -> _P:
    return builtins.min(self, key=key)


@chain_only
def max(self: Iterable[_P], /, *, key: _F = identity) -> _P:
    return builtins.max(self, key=key)


@chain_only
def range(self: int, /, *, start: Optional[int] = None, step: Optional[int] = None) -> Iterable[int]:
    if start is None and step is None:
        return builtins.range(self)
    if step is None:
        return builtins.range(start, self)
    return builtins.range(start, self, step)


@chain_only
def all(self: Iterable[_P], predicate: _Pred = identity) -> bool:
    return builtins.all(predicate(i) for i in self)


@chain_only
def any(self: Iterable[_P], predicate: _Pred = identity) -> bool:
    return builtins.any(predicate(i) for i in self)


@chain_only
def map(self: Iterable[_P], func: _F, /, *other: Iterable[_P2]) -> Iterable[_R]:
    return builtins.map(func, self, *other)


@chain_only
def map_dict(self: Dict[_P, _P2], /, *, key_func: _F = identity,
             val_func: Callable[[_P2], _R2] = identity) -> Dict[_R, _R2]:
    return {key_func(k): val_func(v) for k, v in self.items()}


@chain_only
def filter(self: Iterable[_P], predicate: _Pred = identity, /) -> Iterable[_P]:
    return builtins.filter(predicate, self)


@chain_only
def filter_val(self: Dict[_P, _P2], predicate: Callable[[_P2], bool], /) -> Dict[_P, _P2]:
    return {k: v for k, v in self.items() if predicate(v)}


@chain_only
def last(self: Sequence[_P], predicate: _Pred = always(True), /) -> _P:
    return builtins.next(i for i in builtins.reversed(self) if predicate(i))


@chainable
def first(self: Iterable[_P], predicate: _Pred = always(True), /) -> _P:
    return builtins.next(i for i in self if predicate(i))


# alias
curse(object, "next", first)


@chain_only
def sum(self: Iterable[_P], /, *, of: Callable[[_P], Number] = identity,
        predicate: _Pred = always(True)) -> int:
    return builtins.sum(of(i) for i in self if predicate(i))


@chain_only
def count(self: Iterable[_P], predicate: _Pred = always(True), /) -> int:
    return builtins.sum(1 for i in self if predicate(i))


@chain_only
def len(self: Iterable[_P]) -> int:
    return builtins.len(self)


@chain_only
def reversed(self: Sequence[_P], /) -> Sequence[_P]:
    return builtins.reversed(self)


@chain_only
def sorted(self: Iterable[_P], /, *, key: _F = identity, reverse: bool = False) -> List[_P]:
    return builtins.sorted(self, key=key, reverse=reverse)


@chain_only
def reduce(self: Iterable[_P], func: Callable[[_P, _P], _R], /, *, initial: Optional[_R] = None) -> _R:
    return functools.reduce(func, self, initial) if initial is not None else functools.reduce(func, self)


@chain_only
def partition(self: Iterable[_P], predicate: _Pred = identity, /) -> Tuple[List[_P], List[_P]]:
    true = []
    false = []
    for i in self:
        (true if predicate(i) else false).append(i)
    return true, false


@chain_only
def counter(self: Iterable[_P]) -> Dict[_P, int]:
    return collections.Counter(self)


@chain_only
def groupby(self: Iterable[_P], key: _F, /) -> Dict[_R, List[_P]]:
    return itertools.groupby(self, key=key)


@chain_only
def chain(self: Iterable[Iterable[_P]], /) -> Iterable[_P]:
    return itertools.chain(self)


@chain_only
def zip(self: Iterable[_P], /, *other: Iterable[_P2]) -> Iterable[Tuple[_P, _P2]]:
    return builtins.zip(self, *other)


@chain_only
def enumerate(self: Iterable[_P]) -> Iterable[Tuple[int, _P]]:
    return builtins.enumerate(self)


@chain_only
def tuple(self: Iterable[_P], /) -> Tuple[_P, ...]:
    return builtins.tuple(self)


@chain_only
def list(self: Iterable[_P], /) -> List[_P]:
    return builtins.list(self)


@chain_only
def set(self: Iterable[_P], /) -> Set[_P]:
    return builtins.set(self)


@chain_only
def dict(self: Iterable[Tuple[_P, _P2]], /) -> Dict[_P, _P2]:
    return builtins.dict(self)


@chain_only
def join(self: Iterable[_P], sep: builtins.str = "", /, to_str: Callable[[_P], str] = builtins.str) -> builtins.str:
    return sep.join(builtins.map(to_str, self))


@chain_only
def starmap(self: Iterable[Iterable[_P]], func: Callable[[Iterable[_P]], _R], /) -> Iterable[_R]:
    return itertools.starmap(func, self)


@chain_only
def accumulate(self: Iterable[Iterable[_P]], /, *, func: Callable[[_R, _P], _R] = operator.add,
               initial: Optional[_R] = None) -> Iterable[_R]:
    return itertools.accumulate(self, func, initial=initial) if initial is not None else itertools.accumulate(self,
                                                                                                              func)


@chain_only
def pairwise(self: Iterable[_P], /) -> Iterable[Tuple[_P, _P]]:
    return itertools.pairwise(self)


@chain_only
def product(self: Iterable[_P], /, *other: Iterable[_P2], repeat: int = 1) -> Iterable[Tuple[_P, _P2]]:
    return itertools.product(self, *other, repeat=repeat)


@chain_only
def repeat(self: _P, /, times: Optional[int] = None) -> Iterable[_P]:
    return itertools.repeat(self, times)


@chain_only
def takewhile(self: Iterable[_P], /, predicate: _Pred = identity) -> Iterable[_P]:
    return itertools.takewhile(predicate, self)


@chain_only
def dropwhile(self: Iterable[_P], /, predicate: _Pred = identity) -> Iterable[_P]:
    return itertools.dropwhile(predicate, self)


@chain_only
def str(self: _P, /) -> builtins.str:
    return builtins.str(self)


@chain_only
def repr(self: _P, /) -> builtins.str:
    return builtins.repr(self)


@chain_only
def format(self: _P, format_str: builtins.str, /) -> builtins.str:
    return builtins.format(self, format_str)


@chain_only
def if_true(self: _P, func: _F, /, *, predicate: _Pred = identity) -> Optional[_R]:
    return func(self) if predicate(self) else None


@chain_only
def or_else(self: _P, val: _R, /, *, predicate: _Pred = identity) -> _R:
    return self if predicate(self) else val


@chain_only
def or_eval(self: _P, func: _F, /, *, predicate: _Pred = identity) -> _R:
    return self if predicate(self) else func(self)


ExceptionFuncOrException = Union[Callable[[_P], Exception], Exception]


@chain_only
def or_raise(self: _P, func_or_val: ExceptionFuncOrException, /, *, predicate: _Pred = identity) -> _P:
    if predicate(self):
        return self
    if callable(func_or_val):
        raise func_or_val(self)
    raise func_or_val


@chain_only
def raise_as(self: _P, func_or_val: ExceptionFuncOrException, /) -> NoReturn:
    if callable(func_or_val):
        raise func_or_val(self)
    raise func_or_val


ExceptionType = Type[Exception]


@chain_only
def then_catch(self: _P, exception_type: ExceptionType, func: _F, /, *,
               exception_handler: Callable[[_P, ExceptionType], _R2]) -> Union[_R, _R2]:
    try:
        return func(self)
    except exception_type as e:
        return exception_handler(self, e)


@chain_only
def apply_while(self: _P, func: Callable[[_P], _P], /, *, predicate: _Pred = identity) -> _P:
    while predicate(self):
        self = func(self)
    return self


class _Context(Protocol):
    def __enter__(self: Self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        ...

    def __exit__(self: Self, *args: _P.args, **kwargs: _P.kwargs) -> _R2:
        ...


@chain_only
def with_context(self: _P, context_func: Callable[[_P], _Context], /, *,
                 then: Union[Callable[[_P, _R], _R2], Callable[[_P], _R2]]) -> _R2:
    with context_func(self) as r:
        if r is None:
            return then(self)
        return then(self, r)


@chainable
def compose(*funcs: Iterable[Callable[[_P], _R]]) -> Callable[[_P2], _R2]:
    def _compose2(f: Callable[[_R], _R2], g: _F, /) -> Callable[[_P], _R2]:
        return lambda *args, **kwargs: f(g(*args, **kwargs))

    return functools.reduce(_compose2, funcs)
