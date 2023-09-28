__all__ = (
    "CalledProcessError",
    "CmdError",
    "FileConfig",
    "GroupUser",
    "TempDir",
    "Top",
)

import dataclasses
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import AnyStr
from typing import Sequence

from .typings import StrOrBytesPath


class CalledProcessError(subprocess.SubprocessError):
    """
    Patched :class:`subprocess.CalledProcessError`.

    Raised when run() and the process returns a non-zero exit status.

    Attributes:
        cmd: The command that was run.
        returncode: The exit code of the process.
        output: The output of the process.
        stderr: The error output of the process.
        completed: :class:`subprocess.CompletedProcess` object.
    """
    returncode: int
    cmd: StrOrBytesPath | Sequence[StrOrBytesPath]
    output: AnyStr | None
    stderr: AnyStr | None
    completed: subprocess.CompletedProcess | None

    def __init__(self, returncode: int | None = None,
                 cmd: StrOrBytesPath | Sequence[StrOrBytesPath] | None = None,
                 output: AnyStr | None = None, stderr: AnyStr | None = None,
                 completed: subprocess.CompletedProcess | None = None) -> None:
        """
        Patched :class:`subprocess.CalledProcessError`.

        Args:
            cmd: The command that was run.
            returncode: The exit code of the process.
            output: The output of the process.
            stderr: The error output of the process.
            completed: :class:`subprocess.CompletedProcess` object.

        Examples:
            >>> import subprocess
            >>> 3/0  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            ZeroDivisionError: division by zero
            >>> subprocess.run(["ls", "foo"], capture_output=True, check=True)  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            classes.CalledProcessError:
              Return Code:
                1
            <BLANKLINE>
              Command:
                ['ls', 'foo']
            <BLANKLINE>
              Stderr:
                b'ls: foo: No such file or directory\\n'
            <BLANKLINE>
              Stdout:
                b''
            <BLANKLINE>
        """
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.stderr = stderr
        self.completed = completed
        if self.returncode is None:
            self.returncode = self.completed.returncode
            self.cmd = self.completed.args
            self.output = self.completed.stdout
            self.stderr = self.completed.stderr

    def _message(self):
        if self.returncode and self.returncode < 0:
            try:
                return f"Died with {signal.Signals(-self.returncode)!r}."
            except ValueError:
                return f"Died with with unknown signal {-self.returncode}."
        else:
            return f"{self.returncode:d}"

    def __str__(self):
        return f"""
  Return Code:
    {self._message()}

  Command:
    {self.cmd}

  Stderr:
    {self.stderr}

  Stdout:
    {self.output}
"""

    @property
    def stdout(self) -> str:
        """Alias for output attribute, to match stderr"""
        return self.output

    @stdout.setter
    def stdout(self, value):
        # There's no obvious reason to set this, but allow it anyway so
        # .stdout is a transparent alias for .output
        self.output = value


class CmdError(subprocess.CalledProcessError):
    """
    Raised when run() and the process returns a non-zero exit status.

    Attribute:
      process: The CompletedProcess object returned by run().
    """

    def __init__(self, process=None):
        super().__init__(process.returncode, process.args, output=process.stdout, stderr=process.stderr)

    def __str__(self):
        value = super().__str__()
        if self.stderr is not None:
            value += "\n" + self.stderr
        if self.stdout is not None:
            value += "\n" + self.stdout
        return value


@dataclasses.dataclass
class GroupUser:
    group: int | str
    user: int | str


@dataclasses.dataclass
class FileConfig:
    file: Path | None = None
    config: dict = dataclasses.field(default_factory=dict)


class TempDir(tempfile.TemporaryDirectory):
    """
    Wrapper for :class:`tempfile.TemporaryDirectory` that provides Path-like

    Examples:
        >>> from ppip.utils.classes import TempDir
        >>> from ppip.utils.variables import MACOS
        >>> with TempDir() as tmp:
        ...     if MACOS:
        ...         assert tmp.parts[1] == "var"
        ...         assert tmp.resolve().parts[1] == "private"
    """

    def __enter__(self) -> Path:
        """
        Return the path of the temporary directory

        Returns:
            Path of the temporary directory
        """
        return Path(self.name)


@dataclasses.dataclass
class Top:
    init_py: Path | None
    installed: bool | None
    name: str
    path: Path | None
    prefix: str
    pth: Path | None
    pth_source: Path | None
    pyproject_toml: Path | None
    root: Path | None
    top: Path | None
    """Superproject top"""
    venv: Path | None


subprocess.CalledProcessError = CalledProcessError
