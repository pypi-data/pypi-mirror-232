# fzf.py
from __future__ import annotations

import logging
import shlex
from typing import TYPE_CHECKING
from typing import Any

from pyselector import constants
from pyselector import helpers
from pyselector.key_manager import KeyManager

if TYPE_CHECKING:
    from pyselector.interfaces import PromptReturn

log = logging.getLogger(__name__)


class Fzf:
    def __init__(self) -> None:
        self.name = "fzf"
        self.url = constants.HOMEPAGE_FZF
        self.keybind = KeyManager()

    @property
    def command(self) -> str:
        return helpers.check_command(self.name, self.url)

    def _build_command(  # noqa: C901
        self,
        case_sensitive,
        multi_select,
        prompt,
        **kwargs,
    ) -> list[str]:
        header: list[str] = []
        args = shlex.split(self.command)

        if case_sensitive is not None:
            args.append("+i" if case_sensitive else "-i")

        if kwargs.get("mesg"):
            header.extend(shlex.split(f"'{kwargs.pop('mesg')}'"))

        if kwargs.get("cycle"):
            kwargs.pop("cycle")
            args.append("--cycle")

        if not kwargs.pop("preview", None):
            args.append("--no-preview")

        if kwargs.get("height"):
            args.extend(shlex.split(f"--height {kwargs.pop('height')}"))

        if prompt:
            args.extend(["--prompt", prompt])

        if multi_select:
            args.append("--multi")

        # FIX: rethink keybinds for FZF
        # log.warning("keybinds are disabled")
        for key in self.keybind.registered_keys:
            log.debug("key=%s not supported in fzf", key)
            # args.extend(shlex.split(f"--bind='{key.bind}:{key.action}'"))
            # if not key.hidden:
            #     header.append(f"Use {key.bind} {key.description}")

        if kwargs:
            for arg, value in kwargs.items():
                log.debug("'%s=%s' not supported", arg, value)

        if header:
            mesg = "\n".join(msg.replace("\n", " ") for msg in header)
            args.extend(shlex.split(f"--header '{mesg}'"))

        return args

    def prompt(
        self,
        items: list[Any] | tuple[Any] | None = None,
        case_sensitive: bool | None = None,
        multi_select: bool = False,
        prompt: str = "PySelector> ",
        **kwargs,
    ) -> PromptReturn:
        if not items:
            items = []

        args = self._build_command(case_sensitive, multi_select, prompt, **kwargs)
        selection, code = helpers._execute(args, items)
        log.debug("selection=%s", selection)
        log.debug("code=%s", code)
        return selection, code
