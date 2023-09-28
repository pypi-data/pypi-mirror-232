from __future__ import annotations

import logging
import shlex
import sys
from typing import TYPE_CHECKING
from typing import Iterable

from pyselector import constants
from pyselector import helpers
from pyselector.key_manager import KeyManager

if TYPE_CHECKING:
    from pyselector.interfaces import PromptReturn


log = logging.getLogger(__name__)

ROFI_RETURN_CODE_START = 10


class RofiBeta:
    """
    A Python wrapper for the rofi application, which provides a simple and
    efficient way to display a list of items for user selection.

    This class provides a convenient interface for building and executing rofi commands,
    allowing customization of various settings such as case sensitivity, multi-select,
    prompt message, and more

    Methods:
        prompt(items=None, case_sensitive=False, multi_select=False, prompt="PySelector> ", **kwargs):
        Displays a rofi selection window with the specified items and settings,
        returns the selected item(s) and return code.
    """

    def __init__(self) -> None:
        self.name = "rofi"
        self.url = constants.HOMEPAGE_ROFI
        self.keybind = KeyManager()

        self.keybind.code_count = ROFI_RETURN_CODE_START

    @property
    def command(self) -> str:
        return helpers.check_command(self.name, self.url)

    def _build_command(
        self, case_sensitive, multi_select, prompt, **kwargs
    ) -> list[str]:
        args = _build_base_args(
            self.command, case_sensitive, multi_select, prompt, **kwargs
        )
        args = _add_theme_args(args, kwargs.pop("theme", None))
        args = _add_lines_arg(args, kwargs.pop("lines", None))
        args = _add_prompt_arg(args, prompt)
        args = _add_markup_arg(args, kwargs.pop("markup", False))
        messages = _process_messages(kwargs.pop("mesg", None))
        args = _add_filter_arg(args, kwargs.pop("filter", None))
        args = _add_location_arg(args, kwargs.pop("location", None))
        dimensions_args = _process_dimensions(
            kwargs.pop("width", None), kwargs.pop("height", None)
        )
        args = _add_case_and_multi_args(args, case_sensitive, multi_select)
        args = _add_dimensions_theme_arg(args, dimensions_args)
        args = _add_keybinds(args, self.keybind)
        args = _add_messages_arg(args, messages)
        args = _add_remaining_kwargs(args, kwargs)
        args = _add_title_markup_arg(args, kwargs.pop("title_markup", False))
        return args

    def prompt(
        self,
        items: Iterable[str | int] | None = None,
        case_sensitive: bool = False,
        multi_select: bool = False,
        prompt: str = "PySelector> ",
        **kwargs,
    ) -> PromptReturn:
        """Prompts the user with a rofi window containing the given items
           and returns the selected item and code.

        Args:
            items (Iterable[str, int], optional):  The items to display in the rofi window
            case_sensitive (bool, optional):       Whether or not to perform a case-sensitive search
            multi_select (bool, optional):         Whether or not to allow the user to select multiple items
            prompt (str, optional):                The prompt to display in the rofi window
            **kwargs:                              Additional keyword arguments.

        Keyword Args:
            lines    (int): The number of lines to display in the selection window.
            mesg     (str): A message to display at the top of the selection window.
            filter   (str): Filter the list by setting text in input bar to filter.
            location (str): The location of the selection window (e.g. "upper-left", "center" or "bottom-right").
            width    (str): The width of the selection window (e.g. 60%).
            height   (str): The height of the selection window (e.g. 50%).
            theme    (str): The path of the rofi theme to use.

        Returns:
            A tuple containing the selected item (str or list of str if `multi_select` enabled) and the return code (int).

        Return Code Value
            0: Row has been selected accepted by user.
            1: User cancelled the selection.
            10-28: Row accepted by custom keybinding.
        """
        if items is None:
            items = []

        args = self._build_command(case_sensitive, multi_select, prompt, **kwargs)
        selection, code = helpers._execute(args, items)

        print('returncode:', code)
        print('selection:', selection)

        if multi_select:
            return helpers.parse_multiple_bytes_lines(selection), code
        return helpers.parse_bytes_line(selection), code

    @staticmethod
    def location(direction: str = "center") -> str:
        """
        Specify where the window should be located. The numbers map to the
        following locations on screen:

            1 2 3
            8 0 4
            7 6 5

        Default: 0
        """
        location = {
            "upper-left": 1,
            "left": 8,
            "bottom-left": 7,
            "upper-center": 2,
            "center": 0,
            "bottom-center": 6,
            "upper-right": 3,
            "right": 4,
            "bottom-right": 5,
        }
        try:
            position = str(location[direction])
        except KeyError as e:
            err_msg = f"location {direction!r} not found.\nchoose from {list(location)}"
            log.error(err_msg)
            raise ValueError(err_msg) from e
            sys.exit(1)
        return position


def _build_base_args(
    command,
    case_sensitive,
    multi_select,
    prompt,
    **kwargs,
) -> list[str]:
    args = shlex.split(command)
    args.extend(["-dmenu", "-sync", "-no-custom"])
    if not case_sensitive:
        args.append("-i")
    if multi_select:
        args.append("-multi-select")
    if prompt:
        args.extend(["-p", prompt])
    return args


def _add_theme_args(args: list[str], theme) -> list[str]:
    if theme:
        args.extend(["-theme", theme])
    return args


def _add_lines_arg(args: list[str], lines: int) -> list[str]:
    if lines is not None:
        args.extend(["-l", str(lines)])
    return args


def _add_prompt_arg(args: list[str], prompt: str) -> list[str]:
    if prompt:
        args.extend(["-p", prompt])
    return args


def _add_markup_arg(args: list[str], markup: bool) -> list[str]:
    if markup:
        args.append("-markup-rows")
    return args


def _process_messages(mesg: str) -> list[str]:
    messages = []
    if mesg:
        messages.extend(shlex.split(f"'{mesg}'"))
    return messages


def _add_filter_arg(args: list[str], filter_arg: str) -> list[str]:
    if filter_arg:
        args.extend(["-filter", filter_arg])
    return args


def _add_location_arg(args: list[str], location: str) -> list[str]:
    if location:
        args.extend(["-location", RofiBeta.location(location)])
    return args


def _process_dimensions(width: str, height: str) -> list[str]:
    dimensions_args = []
    if width:
        dimensions_args.append(f"width: {width};")
    if height:
        dimensions_args.append(f"height: {height};")
    return dimensions_args


def _add_case_and_multi_args(
    args: list[str], case_sensitive: bool, multi_select: bool
) -> list[str]:
    if case_sensitive:
        args.append("-case-sensitive")
    else:
        args.append("-i")
    if multi_select:
        args.append("-multi-select")
    return args


def _add_dimensions_theme_arg(args: list[str], dimensions_args: list[str]) -> list[str]:
    if dimensions_args:
        formated_string = " ".join(dimensions_args)
        args.extend(shlex.split("-theme-str 'window {" + formated_string + "}'"))
    return args


def _add_keybinds(args: list[str], keybinds: KeyManager) -> list[str]:
    messages = []
    for key in keybinds.registered_keys:
        args.extend(shlex.split(f"-kb-custom-{key.id} {key.bind}"))
        if not key.hidden:
            messages.append(f"{constants.BULLET} Use <{key.bind}> {key.description}")
    args.extend(_add_messages_arg([], messages))
    return args


def _add_messages_arg(args, messages) -> list[str]:
    if messages:
        mesg = "\n".join(messages)
        args.extend(shlex.split(f"-mesg '{mesg}'"))
    return args


def _add_remaining_kwargs(args, kwargs) -> list[str]:
    for arg, value in kwargs.items():
        log.debug("'%s=%s' not supported", arg, value)
    return args


def _add_title_markup_arg(args, title_markup) -> list[str]:
    markup_value = "true" if title_markup else "false"
    args.extend(shlex.split(f"-theme-str 'textbox {{ markup: {markup_value};}}'"))
    return args
