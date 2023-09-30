"""
Utility to create a `tensordict`-like tensorclass using a superclass instead of
the provided decorator `@tensorclass`.

This is useful when you want typing to work properly, and is more explicit.
"""

from __future__ import annotations

import types
import typing as T

from tensordict import TensorDict, TensorDictBase, tensorclass
from typing_extensions import override

__all__ = ["Tensorclass", "TypedTensorDict", "TensorDict", "TensorDictBase"]
__dir__ = ["Tensorclass", "TypedTensorDict", "TensorDict", "TensorDictBase"]


@T.dataclass_transform()
class TensorclassMeta(type):
    """
    TensorclassMeta is a metaclass that wraps the `@tensorclass` decorator around the child.
    """

    def __new__(cls, name: str, bases: tuple[type, ...], ns: dict[str, T.Any], **kwds):
        # if len(bases) == 0:
        #     return super().__new__(cls, name, tuple(bases), ns, **kwds)

        bases = types.resolve_bases(bases)
        tc = super().__new__(cls, name, tuple(bases), ns, **kwds)
        tc = tensorclass(tc)  # type: ignore

        return tc

    @override
    def __instancecheck__(cls, ins: T.Any) -> bool:
        return isinstance(ins, TensorDictBase) or super().__instancecheck__(ins)

    @override
    def __subclasscheck__(cls, sub: T.Any) -> bool:
        return issubclass(sub, TensorDictBase) or super().__subclasscheck__(sub)


class Tensorclass(metaclass=TensorclassMeta):
    """
    Tensorclass is a class that allows you to create a `tensordict`-like
    tensorclass using a superclass instead of the provided decorator `@tensorclass`.
    """

    def __post_init__(self):
        pass


# def _tensorclass_flatten(obj: Tensorclass) -> T.Tuple[T.List[T.Any], pytree.Context]:


# def _tensorclass_unflatten(values: T.List[T.Any], context: pytree.Context) -> Tensorclass:
#     ...

# def _tensorclass_serialize(context: pytree.Context) -> T.Any:
#     ...

# def _tensorclass_deserialize(dumpable_context: pytree.DumpableContext) -> Tensorclass:
#     ...


class TypedTensorDict(TensorDict):
    __slots__ = ()

    def __new__(cls, *args, **kwargs) -> TensorDict:
        return TensorDict(*args, **kwargs)

    def __class_getitem__(cls, item):
        return item
