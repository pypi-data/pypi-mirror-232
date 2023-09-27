"""
forbiddenfp - Some builtin/itertools functions that can be chained after objects, in favor of more functional programming.

https://github.com/yx-z/forbiddenfp
"""
import builtins
import collections
import functools
import inspect
import itertools
import operator
from numbers import Number
from typing import Callable, List, NoReturn, Optional, Dict, TypeVar, Iterable, Sequence, Tuple, Union, Set, Type, \
    ContextManager

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
    # x is still 10
    """

    def __init__(self: Self, **kwargs: _P.kwargs) -> None:
        glob = inspect.currentframe().f_back.f_globals
        self.existing_globals = {k: glob[k] for k in kwargs if k in glob}
        self.temp_globals = {k for k in kwargs if k not in glob}
        glob.update(kwargs)
        for k, v in builtins.filter(lambda t: isinstance(t[1], lazy), kwargs.items()):
            glob[k] = eval(v.expr, glob, inspect.currentframe().f_back.f_locals)

    def __rshift__(self: Self, val: _P) -> _P:
        glob = inspect.currentframe().f_back.f_globals
        glob.update(self.existing_globals)
        for k in self.temp_globals:
            del glob[k]
        return val


class lazy:
    """
    x = 10
    let(x=1, y=lazy("x+1")) >> x+y  # 3
    # x is still 10
    """

    def __init__(self: Self, expr: builtins.str) -> None:
        if not isinstance(expr, builtins.str):
            raise RuntimeError(f"<class lazy> expects expression str, got {expr}")
        self.expr = expr


def always(val: _P) -> Callable[..., _P]:
    return lambda *args, **kwargs: val


def identity(val: _P) -> _P:
    return val


def truthful(val: _P) -> bool:
    return bool(val)


def is_none(val: _P) -> bool:
    return val is None


def negate(func: _Pred) -> _Pred:
    return lambda *args, **kwargs: not func(*args, **kwargs)


falseful = negate(truthful)
not_none = negate(is_none)


def compose(*funcs: Iterable[Callable[[_P], _R]]) -> Callable[[_P2], _R2]:
    def _compose2(f: Callable[[_R], _R2], g: _F) -> Callable[[_P], _R2]:
        return lambda *args, **kwargs: f(g(*args, **kwargs))

    return functools.reduce(_compose2, funcs)


def chain_as(name: str, cls: Type = object) -> Callable[[_F], _F]:
    def decorator(func: _F) -> _F:
        curse(cls, name, func)
        return func

    return decorator


def chain_for(cls: Type) -> Callable[[_F], _F]:
    def decorator(func: _F) -> _F:
        return chain_as(func.__name__, cls)(func)

    return decorator


def chainable(func: _F) -> _F:
    return chain_as(func.__name__)(func)


@chainable
def apply(self: _P, func: _F) -> _P:
    func(self)
    return self


# don't clash function name with builtin print. But we can still chain as `object().print()`.
@chain_as("print")
def apply_print(self: _P, print_func: _F = builtins.print) -> _P:
    print_func(self)
    return self


@chainable
def pair(self: _P, func: _F) -> Tuple[_P, _R]:
    return self, func(self)


@chainable
def pairwise(self: Iterable[_P]) -> Iterable[Tuple[_P, _R]]:
    return itertools.pairwise(self)


@chainable
def also(self: _P, _: _R) -> _P:
    # side effect is evaluated before passing in to this function
    return self


@chainable
def then(self: _P, func: _F) -> _R:
    return func(self)


@chainable
def then_use(self: _P, val: _R) -> _R:
    return val


@chain_as("setattr")
def set_attr(self: _P, **kwargs: _P.kwargs) -> _P:
    for k, v in kwargs.items():
        builtins.setattr(self, k, v)
    return self


@chainable
def setitem(self: _P, key: _P2, val: _R) -> _P:
    self[key] = val
    return self


@chainable
def apply_unpack(self: _P, func: _F) -> _R:
    func(*self)
    return self


@chainable
def then_unpack(self: _P, func: _F) -> _R:
    return func(*self)


@chainable
def empty(self: Iterable[_P]) -> bool:
    return all(False for _ in self)


def tee(self: Iterable[_P], n: int = 2) -> Tuple[_P, ...]:
    return itertools.tee(self, n)


@chain_as("min")
def min_iter(self: Iterable[_P], key: _F = identity) -> _P:
    return builtins.min(self, key=key)


@chain_as("max")
def max_iter(self: Iterable[_P], key: _F = identity) -> _P:
    return builtins.max(self, key=key)


@chain_as("range")
def range_up_to(self: int, start: Optional[int] = None, step: Optional[int] = None) -> Iterable[int]:
    if start is None and step is None:
        return builtins.range(self)
    if step is None:
        return builtins.range(start, self)
    return builtins.range(start, self, step)


@chain_as("all")
def all_iter(self: Iterable[_P], predicate: _Pred = truthful) -> bool:
    return builtins.all(predicate(i) for i in self)


@chain_as("any")
def any_iter(self: Iterable[_P], predicate: _Pred = truthful) -> bool:
    return builtins.any(predicate(i) for i in self)


@chain_as("map")
def map_iter(self: Iterable[_P], func: _F, *other: Iterable[_P2]) -> Iterable[_R]:
    return builtins.map(func, self, *other)


@chainable
def map_dict(self: Dict[_P, _P2], key_func: _F = identity, val_func: Callable[[_P2], _R2] = identity) -> Dict[
    _R, _R2]:
    return {key_func(k): val_func(v) for k, v in self.items()}


@chain_as("filter")
def filter_iter(self: Iterable[_P], predicate: _Pred = truthful) -> Iterable[_P]:
    return builtins.filter(predicate, self)


@chainable
def filter_val(self: Dict[_P, _P2], predicate: Callable[[_P2], bool]) -> Dict[_P, _P2]:
    return {k: v for k, v in self.items() if predicate(v)}


@chainable
def last(self: Sequence[_P], predicate: _Pred = always(True)) -> Optional[_P]:
    return builtins.next((i for i in builtins.reversed(self) if predicate(i)), None)


@chain_as("next")
@chainable
def first(self: Iterable[_P], predicate: _Pred = always(True)) -> Optional[_P]:
    return builtins.next((i for i in self if predicate(i)), None)


@chain_as("sum")
def sum_iter(self: Iterable[_P], of: Callable[[_P], Number] = identity, predicate: _Pred = truthful) -> int:
    return builtins.sum(of(i) for i in self if predicate(i))


@chain_as("len")
def len_iter(self: Iterable[_P], predicate: _Pred = truthful) -> int:
    return builtins.sum(1 for i in self if predicate(i))


@chain_as("reversed")
def reversed_iter(self: Sequence[_P]) -> Sequence[_P]:
    return builtins.reversed(self)


@chain_as("sorted")
def sorted_iter(self: Iterable[_P], key: _F = identity, reverse: bool = False) -> List[_P]:
    return builtins.sorted(self, key=key, reverse=reverse)


@chainable
def reduce(self: Iterable[_P], func: Callable[[_P, _P], _R], initial: Optional[_R] = None) -> _R:
    return functools.reduce(func, self, initial) if initial is not None else functools.reduce(func, self)


@chainable
def separate(self: Iterable[_P], predicate: _Pred = truthful) -> Tuple[List[_P], List[_P]]:
    true_part = []
    false_part = []
    for i in self:
        (true_part if predicate(i) else false_part).append(i)
    return true_part, false_part


@chainable
def counter(self: Iterable[_P]) -> Dict[_P, int]:
    return collections.Counter(self)


@chainable
def groupby(self: Iterable[_P], key: _F) -> Dict[_R, List[_P]]:
    return itertools.groupby(self, key=key)


@chainable
def chain(self: Iterable[Iterable[_P]]) -> Iterable[_P]:
    return itertools.chain(self)


@chain_as("zip")
def zip_iter(self: Iterable[_P], *other: Iterable[_P2]) -> Iterable[Tuple[_P, _P2]]:
    return builtins.zip(self, *other)


@chain_as("enumerate")
def enumerate_iter(self: Iterable[_P]) -> Iterable[Tuple[int, _P]]:
    return builtins.enumerate(self)


@chain_as("tuple")
def tuple_iter(self: Iterable[_P]) -> Tuple[_P, ...]:
    return builtins.tuple(self)


@chain_as("list")
def list_iter(self: Iterable[_P]) -> List[_P]:
    return builtins.list(self)


@chain_as("set")
def set_iter(self: Iterable[_P]) -> Set[_P]:
    return builtins.set(self)


@chain_as("dict")
def dict_iter(self: Iterable[Tuple[_P, _P2]]) -> Dict[_P, _P2]:
    return builtins.dict(self)


@chainable
def join(self: Iterable[_P], sep: builtins.str = "", to_str: Callable[[_P], str] = builtins.str) -> builtins.str:
    return sep.join(builtins.map(to_str, self))


@chainable
def starmap(self: Iterable[Iterable[_P]], func: Callable[[Iterable[_P]], _R]) -> Iterable[_R]:
    return itertools.starmap(func, self)


@chainable
def accumulate(self: Iterable[Iterable[_P]], func: Callable[[_R, _P], _R] = operator.add,
               initial: Optional[_R] = None) -> Iterable[_R]:
    return (itertools.accumulate(self, func, initial=initial) if initial is not None
            else itertools.accumulate(self, func))


@chainable
def pairwise(self: Iterable[_P]) -> Iterable[Tuple[_P, _P]]:
    return itertools.pairwise(self)


@chainable
def product(self: Iterable[_P], *other: Iterable[_P2], repeat: int = 1) -> Iterable[Tuple[_P, _P2]]:
    return itertools.product(self, *other, repeat=repeat)


@chainable
def repeat(self: _P, times: Optional[int] = None) -> Iterable[_P]:
    return itertools.repeat(self, times)


@chainable
def inifinite(self: _P) -> Iterable[_P]:
    return itertools.repeat(self, None)


@chainable
def cycle(self: _P) -> Iterable[_P]:
    return itertools.cycle(self)


@chainable
def takewhile(self: Iterable[_P], predicate: _Pred = truthful) -> Iterable[_P]:
    return itertools.takewhile(predicate, self)


@chain_as("next_n")
@chain_as("first_n")
@chainable
def islice_up_to(self: Iterable[_P], stop: int, predicate: _Pred = always(True)) -> Iterable[_P]:
    return itertools.islice(builtins.filter(predicate, self), stop)


@chainable
def islice(
        self: Iterable[_P], start: int, stop: Optional[int], step: int = 1, predicate: _Pred = always(True)
) -> Iterable[_P]:
    return itertools.islice(builtins.filter(predicate, self), start, stop, step)


@chainable
def dropwhile(self: Iterable[_P], predicate: _Pred = truthful) -> Iterable[_P]:
    return itertools.dropwhile(predicate, self)


@chain_as("str")
def str_obj(self: _P) -> builtins.str:
    return builtins.str(self)


@chain_as("repr")
def repr_obj(self: _P) -> builtins.str:
    return builtins.repr(self)


@chain_as("format")
def format_obj(self: _P, format_str: builtins.str) -> builtins.str:
    return builtins.format(self, format_str)


@chainable
def if_true(self: _P, func: _F, predicate: _Pred = truthful) -> Optional[_R]:
    return func(self) if predicate(self) else None


@chainable
def or_else(self: _P, val: _R, predicate: _Pred = truthful) -> _R:
    return self if predicate(self) else val


@chainable
def or_eval(self: _P, func: _F, predicate: _Pred = truthful) -> _R:
    return self if predicate(self) else func(self)


ExceptionFuncOrException = Union[Callable[[_P], Exception], Exception]


@chainable
def or_raise(self: _P, func_or_val: ExceptionFuncOrException, predicate: _Pred = truthful) -> _P:
    if predicate(self):
        return self
    if callable(func_or_val):
        raise func_or_val(self)
    raise func_or_val


@chainable
def raise_as(self: _P, func_or_val: ExceptionFuncOrException) -> NoReturn:
    if callable(func_or_val):
        raise func_or_val(self)
    raise func_or_val


ExceptionType = Type[Exception]


@chainable
def then_catch(self: _P, exception_type: ExceptionType, func: _F,
               exception_handler: Callable[[_P, ExceptionType], _R2]) -> Union[_R, _R2]:
    try:
        return func(self)
    except exception_type as e:
        return exception_handler(self, e)


@chainable
def apply_while(self: _P, func: Callable[[_P], _P], predicate: _Pred = truthful) -> _P:
    while predicate(self):
        self = func(self)
    return self


@chainable
def generate_while(self: _P, func: Callable[[_P], _P], predicate: _Pred = truthful) -> Iterable[_P]:
    while predicate(self):
        yield self
        self = func(self)


@chainable
def with_context(self: _P, context_func: Callable[[_P], ContextManager],
                 then: Union[Callable[[_P, _R], _R2], Callable[[_P], _R2]]) -> _R2:
    with context_func(self) as r:
        if r is None:
            return then(self)
        return then(self, r)


@chainable
def take_unpacked(self: Iterable[_P],
                  func_iterable: Callable[[Iterable[_P], Callable[[Iterable[_P]], _R], _P.kwargs], _R2],
                  func_vararg: Callable[[_P.args], _R]) -> _R2:
    """
    Given an iterable `self`, a `func_iterable` that takes a (function that acts on the single parameter iterable),
    and a `func_vararg` that takes a (function that acts on variable length args, as opposed to the single parameter),
    Call `func_iterable on the iterable but with `func_vararg`.

    E.g. Given `filter = lambda iterable, predicate: [i for i in iterable if predicate(i)]`,
    `[(1,2), (3,4)].filter(lambda tup: tup[1] == 2)  # [(1,2)]`, where `tup` is an iterable.
    It can be rewritten as `[(1,2), (3,4)].take_unpacked(filter, lambda _, snd: snd == 2)`
    """
    return func_iterable(self, lambda iterable: func_vararg(*iterable))
