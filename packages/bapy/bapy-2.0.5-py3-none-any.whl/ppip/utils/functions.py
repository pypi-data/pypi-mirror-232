"""Ppip functions module"""
__all__ = (
    "aiocmd",
    "aiocommand",
    "ami",
    "brew_bundle",
    "chdir",
    "cmd",
    "cmdrun",
    "cmdsudo",
    "command",
    "dependencies",
    "requirements",
    "distribution",
    "exec_module_from_file",
    "findfile",
    "findup",
    "flatten",
    "getpths",
    "getsitedir",
    "group_user",
    "logger",
    "parent",
    "returncode",
    "stdout",
    "superproject",
    "supertop",
    "suppress",
    "syssudo",
    "toiter",
    "top",
    "tox",
    "version",
    "which",
)

import asyncio
import contextlib
import copy
import fnmatch
import getpass
import grp
import importlib.metadata
import importlib.util
import os
import pwd
import re
import shutil
import subprocess
import sys
import sysconfig
import types
import venv
from pathlib import Path
from pathlib import PurePath
from typing import Any
from typing import AnyStr
from typing import Callable
from typing import cast
from typing import Iterable
from typing import Optional, Union
from typing import ParamSpec
from typing import TypeVar

import loguru
import packaging.requirements
import toml

from ..env import USER
from .classes import CalledProcessError
from .classes import CmdError
from .classes import GroupUser
from .classes import TempDir
from .classes import Top
from .constants import LOGGER_DEFAULT_FMT
from .enums import FileName
from .enums import PathIs
from .enums import PathSuffix
from .errors import CommandNotFound
from .errors import InvalidArgument
from .typings import AnyPath
from .typings import ExcType
from .typings import StrOrBytesPath
from .variables import EXECUTABLE
from .variables import EXECUTABLE_SITE
from .variables import PPIP_DATA
from .variables import PW_ROOT
from .variables import PW_USER

P = ParamSpec("P")
T = TypeVar("T")


async def aiocmd(*args, **kwargs) -> subprocess.CompletedProcess:
    """
    Async Exec Command

    Examples:
        >>> import asyncio
        >>> from ppip.utils.classes import TempDir
        >>> with TempDir() as tmp:
        ...     rv = asyncio.run(aiocmd("git", "clone", "https://github.com/octocat/Hello-World.git", cwd=tmp))
        ...     assert rv.returncode == 0
        ...     assert (tmp / "Hello-World" / "README").exists()

    Args:
        *args: command and args
        **kwargs: subprocess.run kwargs

    Raises:
        JetBrainsError

    Returns:
        None
    """
    proc = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, **kwargs
    )

    out, err = await proc.communicate()
    completed = subprocess.CompletedProcess(
        args, returncode=proc.returncode, stdout=out.decode() if out else None, stderr=err.decode() if err else None
    )
    if completed.returncode != 0:
        raise CmdError(completed)
    return completed


async def aiocommand(
        data: str | list, decode: bool = True, utf8: bool = False, lines: bool = False
) -> subprocess.CompletedProcess:
    """
    Asyncio run cmd.

    Args:
        data: command.
        decode: decode and strip output.
        utf8: utf8 decode.
        lines: split lines.

    Returns:
        CompletedProcess.
    """
    proc = await asyncio.create_subprocess_shell(
        data, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, loop=asyncio.get_running_loop()
    )
    out, err = await proc.communicate()
    if decode:
        out = out.decode().rstrip(".\n")
        err = err.decode().rstrip(".\n")
    elif utf8:
        out = out.decode("utf8").strip()
        err = err.decode("utf8").strip()

    out = out.splitlines() if lines else out

    return subprocess.CompletedProcess(data, proc.returncode, out, cast(Any, err))


def ami(user: str = "root") -> bool:
    """
    Check if Current User is User in Argument (default: root)

    Examples:
        >>> from ppip.utils.functions import ami
        >>>
        >>> ami(os.getenv("USER"))
        True
        >>> ami()
        False

    Arguments:
        user: to check against current user (Default: False)

    Returns:
        CompletedProcess if the current user is not the same as user, None otherwise
    """
    return os.getuid() == pwd.getpwnam(user or getpass.getuser()).pw_uid


def brew_bundle(brewfile: Path | str = PPIP_DATA / "Brewfile", c: Optional[str] = None) -> int:
    """
    Installs brewfile under data directory

    Examples:
        >>> from ppip.utils.functions import brew_bundle
        >>> assert brew_bundle() == 0
        >>> assert brew_bundle(c="convert") is None

    Args:
        brewfile: brewfile to install
        c: command that needs to be absent to run brew bundle
    """

    if which("brew") and brewfile.exists() and (c is None or not which(c)):
        return returncode(
            [
                "brew",
                "bundle",
                "--no-lock",
                "--quiet",
                f"--file={brewfile}",
            ],
            shell=False
        )


@contextlib.contextmanager
def chdir(data: StrOrBytesPath | bool = True) -> Iterable[tuple[Path, Path]]:
    """
    Change directory and come back to previous directory.

    Examples:
        # FIXME: Ubuntu
        >>> from pathlib import Path
        >>> from ppip.utils.functions import chdir
        >>> from ppip.utils.variables import MACOS
        >>>
        >>> previous = Path.cwd()
        >>> new = Path('/usr/local')
        >>> with chdir(new) as (p, n):
        ...     assert previous == p
        ...     assert new == n
        ...     assert n == Path.cwd()
        >>>
        >>> new = Path('/bin/ls')
        >>> with chdir(new) as (p, n):
        ...     assert previous == p
        ...     assert new.parent == n
        ...     assert n == Path.cwd()
        >>>
        >>> new = Path('/bin/foo')
        >>> with chdir(new) as (p, n):
        ...     assert previous == p
        ...     assert new.parent == n
        ...     assert n == Path.cwd()
        >>>
        >>> with chdir() as (p, n):
        ...     assert previous == p
        ...     if MACOS
        ...         assert "var" in str(n)
        ...     assert n == Path.cwd() # doctest: +SKIP

    Args:
        data: directory or parent if file or True for temp directory

    Returns:
        Old directory and new directory
    """

    def y(new):
        os.chdir(new)
        return oldpwd, new

    oldpwd = Path.cwd()
    try:
        if data is True:
            with TempDir() as tmp:
                yield y(tmp)
        else:
            yield y(parent(data, none=False))
    finally:
        os.chdir(oldpwd)


def cmd(*args, **kwargs) -> subprocess.CompletedProcess:
    """
    Exec Command

    Examples:
        >>> from ppip.utils.classes import TempDir
        >>> with TempDir() as tmp:
        ...     rv = cmd("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert (tmp / "README").exists()

    Args:
        *args: command and args
        **kwargs: subprocess.run kwargs

    Raises:
        CmdError

    Returns:
        None
    """

    completed = subprocess.run(args, **kwargs, capture_output=True, text=True)

    if completed.returncode != 0:
        raise CmdError(completed)
    return completed


def cmdrun(
        data: Iterable, exc: bool = False, lines: bool = True, shell: bool = True, py: bool = False, pysite: bool = True
) -> subprocess.CompletedProcess | int | list | str:
    """
    Runs a cmd.

    Examples:
        >>> import ppip
        >>> from ppip.utils.functions import cmdrun
        >>> from ppip.utils.functions import tox
        >>>
        >>> cmdrun('ls a')  # doctest: +ELLIPSIS
        CompletedProcess(args='ls a', returncode=..., stdout=[], stderr=[...])
        >>> assert 'Requirement already satisfied' in cmdrun('pip install pip', py=True).stdout[0]
        >>> cmdrun('ls a', shell=False, lines=False)  # doctest: +ELLIPSIS
        CompletedProcess(args=['ls', 'a'], returncode=..., stdout='', stderr=...)
        >>> cmdrun('echo a', lines=False)  # Extra '\' added to avoid docstring error.
        CompletedProcess(args='echo a', returncode=0, stdout='a\\n', stderr='')
        >>> assert "venv" not in cmdrun("sysconfig", py=True, lines=False).stdout
        >>> if not tox:
        ...     import sysconfig; print(sysconfig.get_paths())
        ...     print("No tox")
        ...     print(__file__)
        ...     assert "venv" in cmdrun("sysconfig", py=True, pysite=False, lines=False).stdout

    Args:
        data: command.
        exc: raise exception.
        lines: split lines so ``\\n`` is removed from all lines (extra '\' added to avoid docstring error).
        py: runs with python executable.
        shell: expands shell variables and one line (shell True expands variables in shell).
        pysite: run on site python if running on a VENV.

    Returns:
        Union[CompletedProcess, int, list, str]: Completed process output.

    Raises:
        CmdError:
    """
    if py:
        m = "-m"
        if isinstance(data, str) and data.startswith("/"):
            m = ""
        data = f"{EXECUTABLE_SITE if pysite else EXECUTABLE} {m} {data}"
    elif not shell:
        data = toiter(data)

    text = not lines

    proc = subprocess.run(data, shell=shell, capture_output=True, text=text)

    def std(out=True):
        if out:
            if lines:
                return proc.stdout.decode("utf-8").splitlines()
            else:
                # return proc.stdout.rstrip('.\n')
                return proc.stdout
        else:
            if lines:
                return proc.stderr.decode("utf-8").splitlines()
            else:
                # return proc.stderr.decode("utf-8").rstrip('.\n')
                return proc.stderr

    rv = subprocess.CompletedProcess(proc.args, proc.returncode, std(), std(False))
    if rv.returncode != 0 and exc:
        raise CmdError(rv)
    return rv


def cmdsudo(*args, user: str = "root", **kwargs) -> subprocess.CompletedProcess | None:
    """
    Run Program with sudo if user is different that the current user

    Arguments:
        *args: command and args to run
        user: run as user (Default: False)
        **kwargs: subprocess.run kwargs

    Returns:
        CompletedProcess if the current user is not the same as user, None otherwise
    """
    if not ami(user):
        return cmd(["sudo", "-u", user, *args], **kwargs)
    return None


def command(*args, **kwargs) -> subprocess.CompletedProcess:
    """
    Exec Command with the following defaults compared to :func:`subprocess.run`:

        - capture_output=True
        - text=True
        - check=True

    Examples:
        >>> from ppip.utils.classes import TempDir
        >>> with TempDir() as tmp:
        ...     rv = command("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert (tmp / ".git").exists()

    Args:
        *args: command and args
        **kwargs: `subprocess.run` kwargs

    Raises:
        CmdError

    Returns:
        None
    """

    completed = subprocess.run(args, **kwargs, capture_output=True, text=True)

    if completed.returncode != 0:
        raise CalledProcessError(completed=completed)
    return completed


def dependencies(
        data: Path | str | None = None, install: bool = False, upgrade: bool = False, extras: bool = True
) -> dict[str, list[packaging.requirements.Requirement]] | str | None:
    # noinspection PyUnresolvedReferences
    """
    List or install dependencies for a package from pyproject.toml, project directory (using pytproject.toml)
        or package name. If package name will search on Distribution

    Examples:
        >>> from pathlib import Path
        >>> import typer
        >>> import ppip
        >>> from ppip.utils.functions import dependencies
        >>> from ppip.utils.functions import requirements
        >>> from ppip.utils.functions import superproject
        >>>
        >>> def names(req, k):
        ...     return [i.name for i in req[k]]
        >>>
        >>> def check(req, k, name):
        ...     assert name in names(req, k)
        >>>
        >>> def check_toml(req):
        ...     check(req, "dependencies", "build")
        ...     check(req, "dev", "ipython")
        ...     check(req, "docs", "sphinx")
        ...     check(req, "tests", "pytest")
        >>>
        >>> def check_typer(req):
        ...     check(req, "dependencies", "click")
        ...     check(req, "all", "colorama")
        ...     check(req, "dev", "flake8")
        ...     check(req, "doc", "mkdocs")
        ...     check(req, "test", "pytest")

        >>> ppip_root = supertop(ppip.__file__)
        >>> check_toml(dependencies(ppip_root))  # doctest: +SKIP
        >>>
        >>> with chdir(ppip_root):
        ...     check_toml(dependencies("pyproject.toml"))  # doctest: +SKIP
        >>>
        >>> check_toml(dependencies())  # doctest: +SKIP
        >>>
        >>> check_typer(dependencies("typer"))
        >>>
        >>> with chdir(parent(typer.__file__)):
        ...     check_typer(dependencies())

    Args:
        data: pyproject.toml path, package name to search in Distribution or project directory
            to find pyproject.toml.  If None, the default, will search up for the top
            of the project pyproject.toml or project name if installed in cwd.
        install: install requirements, False to list (default: True)
        upgrade: upgrade requirements (default: False)
        extras: extras (default: True)

    Returns:
        Requirements or None if install

    Raises:
        CalledProcessError: if pip install command fails.
        InvalidArgument: could not find pyproject.toml or should be: pyproject.toml path,
            package name to search in Distribution or project; directory to add pyproject.toml
    """

    # noinspection PyUnusedLocal
    def quote(d):
        return [f'"{i}"' if {">", "<"} & set(i) else i for i in d]

    deps, ex, error, read, up = [], {}, None, True, []

    if data is None:
        t = top()
        data = top().pyproject_toml
        if data is None and t.installed:
            data = t.name
        elif data is None:
            raise InvalidArgument(f"{t=}; could not find pyproject.toml or package name")

    if (pyproject := Path(data)).is_file() is False and len(pyproject.parts) == 1:
        requires = importlib.metadata.Distribution.from_name(data).requires
        for item in requires:
            if "; extra" in item:
                values = item.split(" ; extra == ")
                key = values[1].replace('"', "")
                if key not in ex:
                    ex[key] = []
                ex[key].append(values[0])
            else:
                deps.append(item)
        read = False
    elif pyproject.is_file():
        pass
    elif pyproject.is_dir():
        pyproject /= "pyproject.toml"
        if not pyproject.is_file:
            error = True
    else:
        error = True

    if error:
        raise InvalidArgument(
            f"{data=}; should be: pyproject.toml path, "
            f"package name to search in Distribution or project; directory to add pyproject.toml"
        )

    if read:
        conf = toml.load(pyproject)
        deps = conf["project"].get("dependencies", [])
        if extras:
            ex = conf["project"].get("optional-dependencies", {})
    if install and (deps or ex):
        if upgrade:
            up = [
                "--upgrade",
            ]
        if extras:
            ex = list(ex.values())
        executable = v / "bin/python" if (v := pyproject.parent / "venv").is_dir() else sys.executable
        return subprocess.check_output(
            [executable, "-m", "pip", "install", *up, "-q", *(deps + flatten(ex, recurse=True))]
        ).decode()

    rv = {"dependencies": deps} | ex
    return {key: [packaging.requirements.Requirement(req) for req in value] for key, value in rv.items()}


requirements = dependencies


def distribution(data: Optional[Path | str] = None) -> importlib.metadata.Distribution:
    """
    Package installed version

    Examples:
        >>> import rich
        >>> from importlib.metadata import Distribution
        >>> from ppip.utils.functions import distribution
        >>>
        >>> # FIXME: instance false
        >>> assert isinstance(distribution("rich"), Distribution)  # doctest: +SKIP

    Args:
        data: package name or path to use basename (Default: `ROOT`)

    Returns
        Installed version
    """
    return suppress(
        importlib.metadata.Distribution.from_name,
        data if len(toiter(data, split="/")) == 1 else data.name,
        exception=importlib.metadata.PackageNotFoundError,
    )


def exec_module_from_file(file: Union[Path, str], name: Optional[str] = None) -> types.ModuleType:
    """
    executes module from file location

    Examples:
        >>> import ppip
        >>> from ppip.utils.functions import exec_module_from_file
        >>> m = exec_module_from_file(ppip.__file__)
        >>> assert m.__name__ == ppip.__name__

    Args:
        file: file location
        name: module name (default from file)

    Returns:
        Module instance
    """
    file = Path(file)
    spec = importlib.util.spec_from_file_location(name or file.parent.name
                                                  if file.name == "__init__.py" else file.stem, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def findfile(pattern, path: Optional[Union[Path, str]] = None) -> list[Path]:
    """
    Find file with pattern

    Examples:
        >>> from pathlib import Path
        >>> import ppip
        >>> from ppip.utils.functions import findfile
        >>>
        >>> assert Path(ppip.__file__) in findfile("*.py")

    Args:
        pattern:
        path: default cwd

    Returns:
        list of files found
    """
    result = []
    for root, _, files in os.walk(path or Path.cwd()):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(Path(root, name))
    return result


def findup(
        path: StrOrBytesPath = None,
        kind: PathIs = PathIs.IS_FILE,
        name: str | PathSuffix | Path | Callable[..., Path] = PathSuffix.ENV.dot,
        uppermost: bool = False,
) -> Path | None:
    """
    Find up if name exists or is file or directory.

    Examples:
        >>> import email.mime.application
        >>> from pathlib import Path
        >>> import ppip
        >>> import ppip.utils
        >>> from ppip.utils.enums import PathSuffix, FileName
        >>> from ppip.utils.functions import chdir, findup, parent
        >>>
        >>>
        >>> file = Path(email.mime.application.__file__)
        >>>
        >>> with chdir(parent(ppip.__file__)):
        ...     pyproject_toml = findup(ppip.__file__, name=FileName.PYPROJECT())
        ...     assert pyproject_toml.is_file()
        >>>
        >>> with chdir(parent(ppip.utils.__file__)):
        ...     utils_init_py = findup(name=FileName.INIT())
        ...     assert utils_init_py.is_file()
        ...     assert utils_init_py == Path(ppip.utils.__file__)
        ...     ppip_init_py = findup(name=FileName.INIT(), uppermost=True)
        ...     assert ppip_init_py.is_file()
        ...     assert ppip_init_py == Path(ppip.__file__)
        >>>
        >>> assert findup(kind=PathIs.IS_DIR, name=ppip.__name__) == Path(ppip.__name__).parent.resolve()
        >>>
        >>> assert findup(file, kind=PathIs.EXISTS, name=FileName.INIT()) == file.parent / FileName.INIT()
        >>> assert findup(file, name=FileName.INIT()) == file.parent / FileName.INIT()
        >>> assert findup(file, name=FileName.INIT(), uppermost=True) == file.parent.parent / FileName.INIT()

    Args:
        path: CWD if None or Path.
        kind: Exists, file or directory.
        name: File or directory name.
        uppermost: Find uppermost found if True (return the latest found if more than one) or first if False.

    Returns:
        Path if found.
    """
    name = (
        name
        if isinstance(name, str)
        else name.name
        if isinstance(name, Path)
        else name()
        if callable(name)
        else name.value
    )
    start = parent(path or os.getcwd())
    latest = None
    while True:
        if getattr(find := start / name, kind.value)():
            if not uppermost:
                return find
            latest = find
        if (start := start.parent) == Path("/"):
            return latest


def flatten(
        data: tuple | list | set, recurse: bool = False, unique: bool = False, sort: bool = True
) -> tuple | list | set:
    """
    Flattens an Iterable

    Examples:
        >>> from ppip.utils.functions import flatten
        >>>
        >>> assert flatten([1, 2, 3, [1, 5, 7, [2, 4, 1, ], 7, 6, ]]) == [1, 2, 3, 1, 5, 7, [2, 4, 1], 7, 6]
        >>> assert flatten([1, 2, 3, [1, 5, 7, [2, 4, 1, ], 7, 6, ]], recurse=True) == [1, 1, 1, 2, 2, 3, 4, 5, 6, 7, 7]
        >>> assert flatten((1, 2, 3, [1, 5, 7, [2, 4, 1, ], 7, 6, ]), unique=True) == (1, 2, 3, 4, 5, 6, 7)

    Args:
        data: iterable
        recurse: recurse
        unique: when recurse
        sort: sort

    Returns:
        Union[list, Iterable]:
    """
    if unique:
        recurse = True

    cls = data.__class__

    flat = []
    _ = [
        flat.extend(flatten(item, recurse, unique) if recurse else item)
        if isinstance(item, list)
        else flat.append(item)
        for item in data
        if item
    ]
    value = set(flat) if unique else flat
    if sort:
        try:
            value = cls(sorted(value))
        except TypeError:
            value = cls(value)
    return value


def getpths() -> dict[str, Path] | None:
    """
    Get list of pths under ``sitedir``

    Examples:
        >>> from ppip.utils.functions import getpths
        >>>
        >>> pths = getpths()
        >>> assert "distutils-precedence" in pths

    Returns:
        Dictionary with pth name and file
    """
    try:
        sitedir = getsitedir()
        names = os.listdir(sitedir)
    except OSError:
        return
    return {
        re.sub("(-[0-9].*|.pth)", "", name): Path(sitedir / name) for name in names if name.endswith(".pth")
    }


def getsitedir(index: bool = 2) -> Path:
    """Get site directory from stack if imported by :mod:`site` in a ``.pth``file or :mod:`sysconfig`

    Examples:
        >>> from ppip.utils.functions import getsitedir
        >>> assert "packages" in str(getsitedir())

    Args:
        index: 1 if directly needed by this function (default: 2), for caller to this function

    Returns:
        Path instance with site directory
    """
    if (sitedir := sys._getframe(index).f_locals.get("sitedir")) is None:
        sitedir = sysconfig.get_paths()["purelib"]
    return Path(sitedir)


def group_user(name: int | str = USER) -> GroupUser:
    """
    Group and User for Name (id if name is str and vice versa).

    Examples:
        >>> import os
        >>> import pathlib
        >>>
        >>> from ppip.utils.functions import group_user
        >>> from ppip.utils.variables import PW_USER, PW_ROOT
        >>>
        >>> s = pathlib.Path().stat()
        >>> gr = group_user()
        >>> assert gr.group == s.st_gid and gr.user == s.st_uid
        >>> gr = group_user(name=PW_USER.pw_uid)
        >>> actual_gname = gr.group
        >>> assert gr.group != PW_ROOT.pw_name and gr.user == PW_USER.pw_name
        >>> gr = group_user('root')
        >>> assert gr.group != s.st_gid and gr.user == 0
        >>> gr = group_user(name=0)
        >>> assert gr.group != actual_gname and gr.user == 'root'

    Args:
        name: usename or id (default: `data.ACTUAL.pw_name`)

    Returns:
        GroupUser.
    """
    if isinstance(name, str):
        struct = (
            struct if name == (struct := PW_USER).pw_name or name == (struct := PW_ROOT).pw_name else pwd.getpwnam(name)
        )
        return GroupUser(group=struct.pw_gid, user=struct.pw_uid)
    struct = struct if name == (struct := PW_USER).pw_uid or name == (struct := PW_ROOT).pw_uid else pwd.getpwuid(name)
    return GroupUser(group=grp.getgrgid(struct.pw_gid).gr_name, user=struct.pw_name)


def logger(fmt: str = LOGGER_DEFAULT_FMT) -> loguru.logger:
    """Returns a new logger"""
    for item in loguru.logger._core.handlers:
        loguru.logger.remove(item)
    log = copy.deepcopy(loguru.logger)
    if fmt:
        log.configure(handlers=[{"sink": sys.stderr, "format": fmt}])
    return log


def parent(path: StrOrBytesPath = Path(__file__), none: bool = True) -> Path | None:
    """
    Parent if File or None if it does not exist.

    Examples:
        >>> from ppip.utils.functions import parent
        >>>
        >>> parent("/bin/ls")
        PosixPath('/bin')
        >>> parent("/bin")
        PosixPath('/bin')
        >>> parent("/bin/foo", none=False)
        PosixPath('/bin')
        >>> parent("/bin/foo")

    Args:
        path: file or dir.
        none: return None if it is not a directory and does not exist (default: True)

    Returns:
        Path
    """
    return (
        path.parent
        if (path := Path(path)).is_file()
        else path
        if path.is_dir()
        else None
        if none
        else path.parent
    )


def returncode(c: str | list[str], shell: bool = True) -> int:
    """
    Runs command in shell and returns returncode showing stdout and stderr

    No exception is raised

    Examples:
        >>> from ppip.utils.functions import returncode
        >>>
        >>> assert returncode("ls /bin/ls") == 0
        >>> assert returncode("ls foo") == 1

    Arguments:
        c: command to run
        shell: run in shell (default: True)

    Returns:
        return code

    """
    return subprocess.call(c, shell=shell)


def stdout(shell: AnyStr, keepends: bool = False, split: bool = False) -> list[str] | str | None:
    """Return stdout of executing cmd in a shell or None if error.

    Execute the string 'cmd' in a shell with 'subprocess.getstatusoutput' and
    return a stdout if success. The locale encoding is used
    to decode the output and process newlines.

    A trailing newline is stripped from the output.

    Examples:
        >>> from ppip.utils.functions import stdout
        >>>
        >>> stdout("ls /bin/ls")
        '/bin/ls'
        >>> stdout("true")
        ''
        >>> stdout("ls foo")
        >>> stdout("ls /bin/ls", split=True)
        ['/bin/ls']

    Args:
        shell: command to be executed
        keepends: line breaks when ``split`` if true, are not included in the resulting list unless keepends
            is given and true.
        split: return a list of the stdout lines in the string, breaking at line boundaries.(default: False)

    Returns:
        Stdout or None if error.
    """

    exitcode, data = subprocess.getstatusoutput(shell)

    if exitcode == 0:
        if split:
            return data.splitlines(keepends=keepends)
        return data
    return None


def superproject(path: Path | str = "") -> Path | None:
    """
    Show the absolute resolved path of the root of the superproject's working tree (if exists) that uses the current
    repository as its submodule (--show-superproject-working-tree) or show the absolute path of the
    top-level directory of the working tree (--show-toplevel).

    Exmples:
        >>> import os
        >>> import pathlib
        >>> import ppip
        >>> from ppip.utils.classes import TempDir
        >>> from ppip.utils.functions import chdir
        >>> from ppip.utils.functions import superproject
        >>> from ppip.utils.functions import supertop
        >>> from ppip.utils.functions import command
        >>>
        >>> supertop(ppip.__file__)  # doctest: +ELLIPSIS
        PosixPath('.../ppip')
        >>>
        >>> with TempDir() as tmp:
        ...     if "site-packages" not in __file__:
        ...         assert superproject() == pathlib.Path(ppip.__file__).parent.parent.parent
        ...     assert superproject(tmp) is None
        ...     rv = command("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert superproject(tmp) == tmp.resolve()
        ...     assert superproject(tmp / "README") == tmp.resolve()
        ...     rv = command("git", "submodule", "add", "https://github.com/octocat/Hello-World.git", cwd=tmp)
        ...     assert rv.returncode == 0
        ...     assert (tmp / ".git").exists()
        ...     assert (tmp / ".git").is_dir()
        ...     with chdir(tmp):
        ...         assert superproject() == tmp.resolve()
        ...     with chdir(tmp /"Hello-World"):
        ...         assert superproject() == tmp.resolve()
        ...         assert superproject(tmp / "Hello-World/README") == tmp.resolve()

    Args:
        path: path inside working tree

    Returns:
        top repository absolute resolved path
    """
    c = f"git -C {parent(path, none=False)} rev-parse --show-superproject-working-tree --show-toplevel"
    if output := stdout(c, split=True):
        return Path(output[0])


supertop = superproject


def suppress(func: Callable[P, T], *args: P.args, exception: ExcType | None = Exception, **kwargs: P.kwargs) -> T:
    """
    Try and supress exception.

    Args:
        func: function to call
        *args: args to pass to func
        exception: exception to suppress (default: Exception)
        **kwargs: kwargs to pass to func

    Returns:
        result of func
    """
    with contextlib.suppress(exception or Exception):
        return func(*args, **kwargs)


def syssudo(user: str = "root") -> subprocess.CompletedProcess | None:
    """
    Rerun Program with sudo ``sys.executable`` and ``sys.argv`` if user is different that the current user

    Arguments:
        user: run as user (Default: False)

    Returns:
        CompletedProcess if the current user is not the same as user, None otherwise
    """
    if not ami(user):
        return cmd(["sudo", "-u", user, sys.executable, *sys.argv])
    return None


def tag_latest(path: AnyPath = None) -> str:
    """
    latest tag

    Examples:
        >>> import ppip
        >>> from ppip.utils.functions import tag_latest
        >>> from ppip.utils.functions import top
        >>> t = top(ppip)
        >>> if t.top:
        ...    assert tag_latest(ppip.__file__) != ""

    """
    c = f"-C {parent(path)}" if path else ""
    return stdout(f"git {c} describe --abbrev=0 --tags") or ""


def toiter(obj: Any, always: bool = False, split: str = " ") -> Any:
    """
    To iter.

    Examples:
        >>> import pathlib
        >>> from ppip.utils.functions import toiter
        >>>
        >>> assert toiter('test1') == ['test1']
        >>> assert toiter('test1 test2') == ['test1', 'test2']
        >>> assert toiter({'a': 1}) == {'a': 1}
        >>> assert toiter({'a': 1}, always=True) == [{'a': 1}]
        >>> assert toiter('test1.test2') == ['test1.test2']
        >>> assert toiter('test1.test2', split='.') == ['test1', 'test2']
        >>> assert toiter(pathlib.Path("/tmp/foo")) == ('/', 'tmp', 'foo')

    Args:
        obj: obj.
        always: return any iterable into a list.
        split: split for str.

    Returns:
        Iterable.
    """
    if isinstance(obj, str):
        obj = obj.split(split)
    elif hasattr(obj, "parts"):
        obj = obj.parts
    elif not isinstance(obj, Iterable) or always:
        obj = [obj]
    return obj


def top(data: types.ModuleType | StrOrBytesPath | None = None) -> Top:
    """
    Get Top Level Package/Module Path.

    Examples:
        >>> import email.mime.application
        >>> from pathlib import Path
        >>> import pytest_cov
        >>> import ppip
        >>> import ppip.utils
        >>> from ppip.utils.enums import PathSuffix, FileName
        >>> from ppip.utils.functions import chdir, findup, parent, top
        >>>
        >>> with chdir(ppip.__file__):
        ...     t_top = top()
        ...     assert "__init__.py" in str(t_top.init_py)
        ...     assert "ppip" == t_top.name
        ...     assert "PPIP_" == t_top.prefix
        ...     assert "ppip.pth" in str(t_top.pth_source)  # doctest: +SKIP
        ...     if t_top.installed:
        ...         assert "site-packages" in str(t_top.init_py)
        ...         assert "site-packages" in str(t_top.path)
        ...         assert "site-packages" in str(t_top.pth_source)
        ...         assert "site-packages" in str(t_top.root)
        ...     else:
        ...         assert t_top.pth is None
        ...         assert "ppip/pyproject.toml" in str(t_top.pyproject_toml)
        ...         assert "ppip/venv" in str(t_top.venv)
        >>>
        >>> t_module = top(ppip)
        >>> with chdir(ppip.utils.__file__):
        ...     t_cwd = top()
        >>> t_cli = top(Path(ppip.utils.__file__).parent)
        >>> assert t_module == t_cwd == t_cli
        >>>
        >>>
        >>> t_pytest_cov = top(pytest_cov)
        >>> t_pytest_cov  # doctest: +ELLIPSIS
        Top(init_py=PosixPath('.../site-packages/pytest_cov/__init__.py'), \
installed=True, name='pytest_cov', \
path=PosixPath('.../site-packages/pytest_cov'), \
prefix='PYTEST_COV_', \
pth=PosixPath('.../site-packages/pytest-cov.pth'), \
pth_source=None, \
pyproject_toml=None, root=PosixPath('.../site-packages/pytest_cov'), \
top=..., \
venv=...)

    Args:
        data: ModuleType, directory or file name (default: None). None for cwd.

    Raises:
        AttributeError: __file__ not found.
    """

    if isinstance(data, types.ModuleType):
        p = data.__file__
    elif isinstance(data, (str, Path, PurePath)):
        p = data
    else:
        p = os.getcwd()

    init_py = installed = path = pth_source = pyproject_toml = None

    start = parent(p)
    root = None
    t = None
    if start and (t := superproject(start)):
        root = Path(t)
    v = root / venv.__name__ if root else None

    if start:
        while True:
            if (rv := start / FileName.INIT()).is_file():
                init_py, path = rv, start
            if (rv := start / FileName.PYPROJECT()).is_file():
                pyproject_toml = rv
            if any(
                [
                    start.name == "dist-packages",
                    start.name == "site-packages",
                    start.name == Path(sys.executable).resolve().name,
                    (start / "pyvenv.cfg").is_file(),
                ]
            ):
                installed, root = True, start
                break
            finish = root.parent if root else None
            if (start := start.parent) == (finish or Path("/")):
                break
    root = pyproject_toml.parent if root is None and pyproject_toml else path
    if pyproject_toml:
        name = toml.load(pyproject_toml)["project"]["name"]
    elif path:
        name = path.name
    else:
        name = data

    name_dash = name.replace("_", "-")

    pths = getpths()

    if path:
        pth_source = (
            pth_source
            if (
                    path
                    and (
                            ((pth_source := path / PathSuffix.PTH(name)).is_file())
                            or ((pth_source := path / PathSuffix.PTH(name.replace("_", "-"))).is_file())
                    )
            )
            else None
        )

    return Top(
        init_py=init_py,
        installed=installed,
        name=name,
        path=path,
        prefix=f"{name.upper()}_",
        pth=pths.get(name, pths.get(name_dash)),
        pth_source=Path(pth_source) if pth_source else None,
        pyproject_toml=pyproject_toml,
        root=root,
        top=t,
        venv=v,
    )


def tox() -> bool:
    """running in tox"""
    return ".tox" in sysconfig.get_paths()["purelib"]


def version(data: types.ModuleType | Path | str | None = None) -> str:
    """
    Package installed version

    Examples:
        >>> from pathlib import Path
        >>> import IPython
        >>> import semver
        >>> import ppip
        >>> from ppip.utils.functions import version
        >>>
        >>> if (ver := version(ppip)) and "dev" not in ver:
        ...     assert semver.VersionInfo.parse(version(ppip))
        >>> assert semver.VersionInfo.parse(version(IPython))  # __version__
        >>> assert version(semver) == version(semver.__file__) == version(Path(semver.__file__).parent) \
            == version("semver")
        >>> assert semver.VersionInfo.parse(version(semver))

    Arguments:
        data: module to search for __version__ or use name, package name oir path.name (Default: `PROJECT`)

    Returns
        Installed version
    """
    if isinstance(data, types.ModuleType) and hasattr(data, "__version__"):
        return data.__version__

    t = top(data)
    if isinstance(data, str) and "/" not in data:
        name = data
    elif isinstance(data, types.ModuleType):
        name = data.__name__
    else:
        name = t.name

    if t.pyproject_toml:
        if (v := toml.load(t.pyproject_toml).get("project", {}).get("version")) is None and t.root:
            v = tag_latest(t.root)
        if t.name == name:
            return v

    if not name:
        raise InvalidArgument(f"name is required: {data=}")

    return suppress(importlib.metadata.version, name, exception=importlib.metadata.PackageNotFoundError)


def which(data="sudo", raises: bool = False) -> str:
    """
    Checks if cmd or path is executable or exported bash function.

    Examples:
        # FIXME: Ubuntu

        >>> from ppip.utils.functions import which
        >>> if which():
        ...    assert "sudo" in which()
        >>> assert which('/usr/local') == ''
        >>> assert which('/usr/bin/python3') == '/usr/bin/python3'
        >>> assert which('let') == 'let'
        >>> assert which('source') == 'source'
        >>> which("foo", raises=True) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ppip.utils.errors.CommandNotFound: foo

    Attribute:
        data: command or path.
        raises: raise exception if command not found

    Raises:
        CommandNotFound:


    Returns:
        Cmd path or ""
    """
    rv = (
            shutil.which(data, mode=os.X_OK)
            or subprocess.run(f"command -v {data}", shell=True, text=True, capture_output=True).stdout.rstrip("\n")
            or ""
    )

    if raises and not rv:
        raise CommandNotFound(data)

    return rv
