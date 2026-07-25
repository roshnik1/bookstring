from functools import cached_property
from subprocess import run, CompletedProcess
from pydantic import BaseModel

from typing import Tuple, Optional


class LSOFInfo(BaseModel):
    port: int

    @property
    def _process(self) -> CompletedProcess:
        return run(
            ["lsof", "-Fcpn", "-i", f"tcp:{self.port}"],
            capture_output=True,
        )

    @cached_property
    def raw(self) -> Optional[Tuple[str, str, str, str]]:
        if self._process.stdout:
            return tuple(self._process.stdout.decode().split("\n")[:4])
        return None

    @property
    def running(self) -> bool:
        try:
            del self.raw
        except AttributeError:
            pass
        return bool(self.raw)

    @property
    def pid(self) -> int:
        assert self.raw
        return int(self.raw[0][1:])

    @property
    def program(self) -> str:
        assert self.raw
        return self.raw[1]

    @property
    def mapping(self) -> str:
        assert self.raw
        return self.raw[3]