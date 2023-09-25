from __future__ import annotations

from typing_extensions import ParamSpec, TypeAlias
from typing import Any, Union, Generic, Literal, TypeVar, Callable, Awaitable

from tarina import lang
from nepattern import MatchMode, BasePattern, MatchFailed
from nonebot.internal.adapter.message import Message, MessageSegment

from .uniseg import Segment, UniMessage

T = TypeVar("T")
TMS = TypeVar("TMS", bound=MessageSegment)
TCallable = TypeVar("TCallable", bound=Callable[..., Any])
P = ParamSpec("P")


class SegmentPattern(BasePattern[TMS], Generic[TMS, P]):
    def __init__(
        self,
        name: str,
        origin: type[TMS],
        call: Callable[P, TMS],
        additional: Callable[..., bool] | None = None,
    ):
        super().__init__(
            model=MatchMode.TYPE_CONVERT,
            origin=origin,
            alias=name,
            accepts=[MessageSegment],
            validators=[additional] if additional else [],
        )
        self.pattern = name
        self.call = call

    def match(self, input_: Any) -> TMS:
        if not isinstance(input_, self.origin):
            raise MatchFailed(lang.require("nepattern", "type_error").format(target=type(input_)))
        if input_.type != self.pattern:
            raise MatchFailed(lang.require("nepattern", "content_error").format(target=input_))
        return input_

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> TMS:
        return self.call(*args, **kwargs)  # type: ignore


class TextSegmentPattern(BasePattern[TMS], Generic[TMS, P]):
    def __init__(
        self,
        name: str,
        origin: type[TMS],
        call: Callable[P, TMS],
        locator: Callable[[str, str], bool] | None = None,
    ):
        super().__init__(
            model=MatchMode.TYPE_CONVERT,
            origin=origin,
            alias=name,
            accepts=[MessageSegment, str],
        )
        self.pattern = name
        self.call = call
        self.locator = locator

    def match(self, input_: Any) -> TMS:
        if not isinstance(input_, (str, self.origin)):  # type: ignore
            raise MatchFailed(lang.require("nepattern", "type_error").format(target=type(input_)))
        if isinstance(input_, str):
            if self.locator and not self.locator(input_, self.pattern):
                raise MatchFailed(lang.require("nepattern", "content_error").format(target=input_))
            return self.call(input_)  # type: ignore
        if input_.type != self.pattern:
            raise MatchFailed(lang.require("nepattern", "content_error").format(target=input_))
        return input_

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> TMS:
        return self.call(*args, **kwargs)  # type: ignore


OutputType = Literal["help", "shortcut", "completion"]
TConvert: TypeAlias = Callable[
    [OutputType, str], Union[Message, UniMessage, Awaitable[Union[Message, UniMessage]]]
]
MReturn: TypeAlias = Union[
    Union[str, Segment, UniMessage, Message, MessageSegment],
    Awaitable[Union[str, Segment, UniMessage, Message, MessageSegment]],
]
