__all__ = (
    "Bump",
    "EnumLower",
    "GitSHA",
    "PathIs",
    "PathSuffix",
    "FileName",
    "ProjectRepos",
)

import enum
from pathlib import Path
from typing import Callable


class Bump(enum.Enum):
    MAJOR = enum.auto()
    MINOR = enum.auto()
    PATCH = enum.auto()


class EnumLower(enum.Enum):
    def _generate_next_value_(self: str, *args):
        return self.lower()


class GitSHA(EnumLower):
    BASE = enum.auto()
    LOCAL = enum.auto()
    REMOTE = enum.auto()


class PathIs(EnumLower):
    """
    Path Is Dir or File Enum Class.

    Examples:
        >>> from ppip.utils.enums import PathIs
        >>>
        >>> PathIs.EXISTS.value
        'exists'
    """
    EXISTS = enum.auto()
    IS_DIR = enum.auto()
    IS_FILE = enum.auto()


class _PathSuffix(enum.Enum):
    def _generate_next_value_(self: str, *args) -> Path | Callable[[str], Path]:
        return Path(
            (f'__{self.rstrip("_")}__' if self.endswith('_') else '' if self == 'NONE' else self).lower())


class PathSuffix(_PathSuffix):
    # noinspection PyCallingNonCallable
    """
        Path Suffix Enum Class

        Examples:
            >>> from ppip.utils.enums import PathSuffix
            >>>
            >>> PathSuffix.TOML("hola")
            PosixPath('hola.toml')
            >>> PathSuffix.TOML.dot
            PosixPath('.toml')

        """
    NONE = enum.auto()  # ''
    BASH = enum.auto()
    CFG = enum.auto()
    ENV = enum.auto()
    GIT = enum.auto()
    GITCONFIG = enum.auto()
    INI = enum.auto()
    J2 = enum.auto()
    JINJA2 = enum.auto()
    JSON = enum.auto()
    LOG = enum.auto()
    MD = enum.auto()
    MONGO = enum.auto()
    OUT = enum.auto()
    PTH = enum.auto()
    PY = enum.auto()
    PYI = enum.auto()
    RLOG = enum.auto()
    RST = enum.auto()
    SCRIPTS = enum.auto()
    SH = enum.auto()
    SHELVE = enum.auto()
    SSH = enum.auto()
    TOML = enum.auto()
    TXT = enum.auto()
    YAML = enum.auto()
    YML = enum.auto()

    def __call__(self, name=None):
        return Path((name if name else self.name) + self.dot.name)

    @property
    def dot(self): return Path('.' + str(self.value.name))

    @property
    def name(self): return self.value.name


# noinspection PyCallingNonCallable
class FileName(enum.Enum):
    """
    File Names

    >>> from ppip.utils.enums import FileName
    >>>
    >>> FileName.INIT()
    PosixPath('__init__.py')
    >>> FileName.PYPROJECT()
    PosixPath('pyproject.toml')
    """
    INIT = PathSuffix.PY("__init__")
    MAIN = PathSuffix.PY("__main__")
    PACKAGE = PathSuffix.JSON("package")
    PYPROJECT = PathSuffix.TOML("pyproject")
    REQUIREMENTS = PathSuffix.TXT("requirements")
    README = PathSuffix.MD("README")
    SETTINGS = PathSuffix.INI("setup")
    SETUP = PathSuffix.CFG("setup")

    def __call__(self) -> Path:
        return self.value


class ProjectRepos(enum.Enum):
    DICT = enum.auto()
    INSTANCES = enum.auto()
    NAMES = enum.auto()
    PATHS = enum.auto()
