import asyncio
import traceback
from typing_extensions import TypeAlias
from typing import Dict, Union, Literal, Callable, ClassVar, Optional, Awaitable

from nonebot import get_driver
from nonebot.typing import T_State
from nonebot.params import EventMessage
from nonebot.plugin.on import on_message
from nonebot.internal.matcher import matchers
from nonebot.internal.rule import Rule as Rule
from nonebot.adapters import Bot, Event, Message
from tarina import lang, init_spec, is_awaitable
from nonebot.utils import run_sync, is_coroutine_callable
from arclet.alconna.exceptions import SpecialOptionTriggered
from arclet.alconna import (
    Args,
    Alconna,
    Arparma,
    AllParam,
    CommandMeta,
    CompSession,
    output_manager,
    command_manager,
)

from .config import Config
from .typings import TConvert
from .uniseg import UniMessage
from .argv import FallbackMessage
from .model import CompConfig, CommandResult
from .consts import ALCONNA_RESULT, ALCONNA_EXEC_RESULT

TProvider: TypeAlias = Callable[
    ["AlconnaRule", Event, T_State, Bot],
    Union[Message, UniMessage, None, Awaitable[Union[Message, UniMessage, None]]],
]


class AlconnaRule:
    """检查消息字符串是否能够通过此 Alconna 命令。

    参数:
        command: Alconna 命令
        skip_for_unmatch: 是否在命令不匹配时跳过该响应
        auto_send_output: 是否自动发送输出信息并跳过响应
        output_converter: 输出信息字符串转换为 Message 方法
        message_provider: 自定义消息提供器
        comp_config: 自动补全配置
        use_origin: 是否使用未经 to_me 等处理过的消息
        use_cmd_start: 是否使用 nb 全局配置里的命令前缀
    """

    default_converter: ClassVar[TConvert]
    default_provider: ClassVar[TProvider]

    __slots__ = (
        "command",
        "skip",
        "auto_send",
        "output_converter",
        "message_provider",
        "comp_config",
        "use_origin",
    )

    def __init__(
        self,
        command: Alconna,
        skip_for_unmatch: bool = True,
        auto_send_output: bool = False,
        output_converter: Optional[TConvert] = None,
        message_provider: Optional[TProvider] = None,
        comp_config: Optional[CompConfig] = None,
        use_origin: bool = False,
        use_cmd_start: bool = False,
        use_cmd_sep: bool = False,
    ):
        self.comp_config = comp_config
        self.use_origin = use_origin
        try:
            global_config = get_driver().config
            config = Config.parse_obj(global_config)
            self.auto_send = auto_send_output or config.alconna_auto_send_output
            if (
                not command.prefixes
                and (use_cmd_start or config.alconna_use_command_start)
                and global_config.command_start
            ):
                command_manager.delete(command)
                command.prefixes = list(global_config.command_start)
                command._hash = command._calc_hash()
                command_manager.register(command)
            if (use_cmd_sep or config.alconna_use_command_sep) and global_config.command_sep:
                command.separators = tuple(global_config.command_sep)
                command_manager.resolve(command).separators = tuple(global_config.command_sep)
            if config.alconna_auto_completion and not self.comp_config:
                self.comp_config = {}
            self.use_origin = use_origin or config.alconna_use_origin
        except ValueError:
            self.auto_send = auto_send_output
        self.command = command
        self.skip = skip_for_unmatch
        self.output_converter = output_converter or self.__class__.default_converter
        self.message_provider = message_provider or self.__class__.default_provider
        if not is_coroutine_callable(self.output_converter):
            self.output_converter = run_sync(self.output_converter)
        if not is_coroutine_callable(self.message_provider):
            self.message_provider = run_sync(self.message_provider)

    def __repr__(self) -> str:
        return f"Alconna(command={self.command!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AlconnaRule) and self.command.path == other.command.path

    def __hash__(self) -> int:
        return hash(self.command.__hash__())

    async def handle(self, bot: Bot, event: Event, msg: Message):
        interface = CompSession(self.command)
        if self.comp_config is None:
            return self.command.parse(msg)
        res = None
        with interface:
            res = self.command.parse(msg)
        if res:
            return res
        meta = CommandMeta(compact=True, hide=True)
        _tab = Alconna(self.comp_config.get("tab", ".tab"), Args["offset", int, 1], [], meta=meta)
        _enter = Alconna(
            self.comp_config.get("enter", ".enter"),
            Args["content", AllParam, []],
            [],
            meta=meta,
        )
        _exit = Alconna(self.comp_config.get("exit", ".exit"), [], meta=meta)

        _waiter = on_message(priority=self.comp_config.get("priority", -1), block=True)
        _futures: Dict[str, asyncio.Future] = {}
        res = Arparma(
            self.command.path,
            msg,
            False,
            error_info=SpecialOptionTriggered("completion"),
        )

        @_waiter.handle()
        async def _waiter_handle(_bot: Bot, _event: Event, content: Message = EventMessage()):
            if _exit.parse(content).matched:
                _futures["_"].set_result(False)
                await _waiter.finish()
            if (mat := _tab.parse(content)).matched:
                interface.tab(mat.query[int]("offset", 1))
                if self.comp_config.get("lite", False):  # type: ignore
                    out = interface.current()
                else:
                    out = "\n".join(interface.lines())
                await self._send(out, _bot, _event, res)  # type: ignore
                _waiter.skip()
            if (mat := _enter.parse(content)).matched:
                _futures["_"].set_result(mat.content)
                await _waiter.finish()
            await self._send(interface.current(), _bot, _event, res)  # type: ignore
            _waiter.skip()

        def clear():
            interface.clear()
            _waiter.destroy()
            _waiter.handlers.clear()
            matchers.pop(-1)
            command_manager.delete(_tab)
            command_manager.delete(_enter)
            command_manager.delete(_exit)

        help_text = (
            f"{lang.require('comp/nonebot', 'tab').format(cmd=_tab.command)}\n"
            f"{lang.require('comp/nonebot', 'enter').format(cmd=_enter.command)}\n"
            f"{lang.require('comp/nonebot', 'exit').format(cmd=_exit.command)}"
        )

        while interface.available:
            await self._send(str(interface), bot, event, res)
            await self._send(help_text, bot, event, res)
            _future = _futures.setdefault("_", asyncio.get_running_loop().create_future())
            _future.add_done_callback(lambda x: _futures.pop("_"))
            try:
                await asyncio.wait_for(_future, timeout=self.comp_config.get("timeout", 60))
            except asyncio.TimeoutError:
                await self._send(lang.require("comp/nonebot", "timeout"), bot, event, res)
                clear()
                return res
            ans: Union[Message, Literal[False]] = _future.result()
            if ans is False:
                await self._send(lang.require("comp/nonebot", "exited"), bot, event, res)
                clear()
                return res
            param = list(ans)
            if not param or not param[0]:
                param = None
            try:
                with interface:
                    res = interface.enter(param)
            except Exception as e:
                traceback.print_exc()
                await self._send(str(e), bot, event, res)
        clear()
        return res

    async def __call__(self, event: Event, state: T_State, bot: Bot) -> bool:
        if not (msg := await self.message_provider(self, event, state, bot)):
            return False
        elif isinstance(msg, UniMessage):
            msg = await msg.export(bot, fallback=True)
        Arparma._additional.update(bot=lambda: bot, event=lambda: event, state=lambda: state)
        with output_manager.capture(self.command.name) as cap:
            output_manager.set_action(lambda x: x, self.command.name)
            try:
                arp = await self.handle(bot, event, msg)
            except Exception as e:
                arp = Arparma(self.command.path, msg, False, error_info=e)
            may_help_text: Optional[str] = cap.get("output", None)
        if not arp.matched and not may_help_text and self.skip:
            return False
        if not may_help_text and arp.error_info:
            may_help_text = repr(arp.error_info)
        if self.auto_send and may_help_text:
            await self._send(may_help_text, bot, event, arp)
            return False
        state[ALCONNA_RESULT] = CommandResult(self.command, arp, may_help_text)
        exec_result = self.command.exec_result
        for key, value in exec_result.items():
            if is_awaitable(value):
                exec_result[key] = await value
            elif isinstance(value, (str, Message)):
                exec_result[key] = await bot.send(event, value)
        state[ALCONNA_EXEC_RESULT] = exec_result
        return True

    async def _send(self, text: str, bot: Bot, event: Event, arp: Arparma) -> Message:
        _t = str(arp.error_info) if isinstance(arp.error_info, SpecialOptionTriggered) else "help"
        try:
            msg = await self.output_converter(_t, text)  # type: ignore
            if isinstance(msg, UniMessage):
                msg = await msg.export(bot, fallback=True)
            return await bot.send(event, msg)  # type: ignore
        except NotImplementedError:
            return await bot.send(event, event.get_message().__class__(text))


@init_spec(AlconnaRule)
def alconna(rule: AlconnaRule) -> Rule:
    return Rule(rule)


AlconnaRule.default_converter = lambda _, x: FallbackMessage(x)


def _default_provider(rule: AlconnaRule, event: Event, state: T_State, bot: Bot):
    if event.get_type() != "message":
        return None
    msg: Message = event.get_message()
    if rule.use_origin:
        try:
            msg: Message = getattr(event, "original_message", msg)  # type: ignore
        except (NotImplementedError, ValueError):
            return None
    return msg


AlconnaRule.default_provider = _default_provider


def set_message_provider(fn: TProvider):
    AlconnaRule.default_provider = fn


def set_output_converter(fn: TConvert):
    AlconnaRule.default_converter = fn
