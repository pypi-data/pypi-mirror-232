from __future__ import annotations

__all__ = (
    "Project",
    "PPIP",
    "PROJECT",
)

import dataclasses
import importlib.metadata
import importlib.util
import shutil
import subprocess
import sys
import sysconfig
import types
from pathlib import Path
from typing import ClassVar

import semver
import toml

from ..env import OPENAI_API_KEY
from .classes import FileConfig
from .constants import PYTHON_DEFAULT_VERSION
from .enums import Bump
from .enums import GitSHA
from .enums import ProjectRepos
from .errors import InvalidArgument
from .functions import findfile
from .functions import flatten
from .functions import findup
from .functions import logger
from .functions import stdout
from .functions import suppress
from .functions import toiter
from .repo import Repo

log = logger("<level>{level: <8}</level> <red>|</red> "
             "<cyan>{name}</cyan> <red>|</red> "
             "<green><level>{extra[name]}</level></green> "
             "<red>|</red> <level>{message}</level>")


@dataclasses.dataclass
class Project:
    """Project Class."""
    data: Path | str | types.ModuleType = Path.cwd()
    """File, directory or name of project (default: current working directory)"""
    executable: Path | str = dataclasses.field(default=sys.executable, init=False)
    directory: Path | None = dataclasses.field(default=None, init=False)
    """Parent of data if data is a file or None if it is a name (one word)"""
    git: str = dataclasses.field(default="git", init=False)
    """git -C directory if self.directory is not None"""
    installed: bool = dataclasses.field(default=False, init=False)
    name: str = dataclasses.field(default=None, init=False)
    """Pypi project name from setup.cfg, pyproject.toml or top name or self.data when is one word"""
    repo: Repo | None = dataclasses.field(default=None, init=False)
    """Repo instance"""
    pyproject_toml: FileConfig = dataclasses.field(default_factory=FileConfig, init=False)
    root: Path = dataclasses.field(default=None, init=False)
    """pyproject.toml or setup.cfg parent or superproject or top directory"""
    source: Path | None = dataclasses.field(default=None, init=False)
    """sources directory, parent of __init__.py or module path"""
    clean_match: ClassVar[list[str]] = ["*.egg-info", ".coverage", ".mypy_cache",
                                        ".pytest_cache", ".tox", ".ruff_cache", "build", "dist"]

    def __post_init__(self):
        data = Path(self.data.__file__ if isinstance(self.data, types.ModuleType) else self.data)
        if isinstance(self.data, str) and len(toiter(self.data, split="/")) == 1:
            if r := self.repos(ret=ProjectRepos.DICT).get(self.data):
                self.directory = r
        elif data.is_dir():
            self.directory = data.absolute()
        elif data.is_file():
            self.directory = data.parent.absolute()
        else:
            raise InvalidArgument(f"Invalid argument: {self.data=}")

        if self.directory:
            self.git = f"git -C '{self.directory}'"
            if path := (findup(self.directory, name="pyproject.toml", uppermost=True) or
                        findfile("pyproject.toml", self.directory)):
                path = path[0] if isinstance(path, list) else path
                self.pyproject_toml = FileConfig(path, toml.load(str(path)))
                self.name = self.pyproject_toml.config.get("project", {}).get("name")
                self.root = path.parent

            repo = self.top() or self.superproject()
            self.root = (self.root or repo).absolute()
            if repo:
                self.repo = Repo(repo)
            self.name = self.name if self.name else self.root.name
            self.executable = v / "bin/python" if (v := self.root / "venv").is_dir() else sys.executable
        else:
            self.name = self.data

        try:
            if spec := importlib.util.find_spec(self.name):
                self.source = Path(spec.origin).parent if "__init__.py" in spec.origin else Path(spec.origin)
                self.installed = True
                self.root = self.root if self.root else self.source.parent
                purelib = sysconfig.get_paths()["purelib"]
                self.installed = True if (self.source.is_relative_to(purelib)
                                          or Path(purelib).name in str(self.source)) else False
        except (ModuleNotFoundError, ImportError):
            pass

        self.log = log.bind(name=self.name)

    def _openai(self):
        try:
            openai.api_key = OPENAI_API_KEY  # noqa:
            diff_string = stdout(
                f"{self.git} diff --cached .")
            prompt = (f"What follows '-------' is a git diff for a potential commit. "
                      f"Reply with an appropriate git commit message(a Git "
                      f"commit message should be concise but also try to describe "
                      f"the important changes in the commit) "
                      f"including a conventional commit key/type"
                      f"(fix:, feat:, or BREAKING CHANGE: ), "
                      f"as the first word of your response and don't include"
                      f" any other text but the message in your response. ------- {diff_string}, language=english")
            completions = openai.Completion.create(  # noqa:
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.7,
            )
            messages = [c.text.strip().replace("\n", "") for c in completions.choices]
            return messages
        except (openai.APIError, openai.InvalidRequestError, openai.OpenAIError) as e:  # noqa:
            error_message = f"OpenAI API Error: {e}"
            print(error_message)
            raise openai.APIError(error_message)  # noqa:

    def build(self) -> Path:
        """Build project"""
        self.clean()
        self.venv()
        rv = subprocess.run(f"{self.executable} -m build {self.root} --wheel", stdout=subprocess.PIPE, shell=True, )
        wheel = rv.stdout.splitlines()[-1].decode().split(" ")[2]
        self.log.info(f"{self.build.__name__}: {wheel}")
        return self.root / "dist" / wheel

    def clean(self) -> None:
        """Clean project"""
        for item in self.clean_match:
            for file in Path.cwd().rglob(item):
                if file.is_dir():
                    shutil.rmtree(self.root / item, ignore_errors=True)
                else:
                    file.unlink(missing_ok=True)

    def commit(self, msg: str = None) -> None:
        """
        commit

        Raises:
            CalledProcessError: if  fails
            RuntimeError: if diverged or dirty
        """
        if self.dirty():
            if self.need_pull():
                raise RuntimeError(f"Diverged: {self.name=}")
            if msg is None:
                msg = "fix: "
            subprocess.check_call(f"{self.git} add -A", shell=True)
            subprocess.check_call(f"{self.git} commit -a --quiet -m '{msg}'", shell=True)
            self.log.info(self.commit.__name__)

    def dependencies(self) -> list[str]:
        """dependencies from pyproject.toml or distribution"""
        if self.pyproject_toml.config:
            return self.pyproject_toml.config.get("project", {}).get("dependencies", [])
        elif d := self.distribution():
            return [item for item in d.requires if "; extra" not in item]
        else:
            raise RuntimeWarning(f"Dependencies not found for {self.name=}")

    def distribution(self) -> importlib.metadata.Distribution | None:
        """distribution"""
        return suppress(importlib.metadata.Distribution.from_name, self.name)

    def diverge(self) -> bool:
        """diverge"""
        return (self.dirty() or self.need_push()) and self.need_pull()

    def extras(self) -> dict[str, list[str]]:
        """optional dependencies from pyproject.toml or distribution"""
        if self.pyproject_toml.config:
            return self.pyproject_toml.config.get("project", {}).get("optional-dependencies", {})
        elif d := self.distribution():
            return {item.split("; extra == ")[1].replace('"', ""): item.split("; extra == ")[0]
                    for item in d.requires if "; extra" in item}
        else:
            raise RuntimeWarning(f"Extras not found for {self.name=}")

    def dirty(self) -> bool:
        """is repository dirty  including untracked files"""
        return bool(stdout(f"{self.git} status -s"))

    def latest(self) -> str:
        """"latest tag: git {c} describe --abbrev=0 --tags"""
        latest = stdout(f"{self.git} tag | sort -V | tail -1") or ""
        if not latest:
            latest = "0.0.0"
            self.commit()
            self.tag(latest)
        return latest

    def need_pull(self) -> bool:
        """needs pull"""
        return ((self.sha() != self.sha(GitSHA.REMOTE)) and
                (self.sha() == self.sha(GitSHA.BASE)))

    def need_push(self) -> bool:
        """needs push, commits not been pushed already"""
        return ((self.sha() != self.sha(GitSHA.REMOTE)) and
                (self.sha() != self.sha(GitSHA.BASE)) and
                (self.sha(GitSHA.REMOTE) == self.sha(GitSHA.BASE)))

    def next(self, part: Bump = Bump.PATCH, force: bool = False) -> str:
        """
        Show next version based on fix: feat: or BREAKING CHANGE:

        Args:
            part: part to increase if force
            force: force bump
        """
        latest = self.latest()
        out = stdout(f"git log --pretty=format:'%s' {latest}..@")
        if force:
            if part is Bump.PATCH:
                return semver.bump_patch(latest)
            elif part is Bump.MINOR:
                return semver.bump_minor(latest)
            elif part is Bump.MAJOR:
                return semver.bump_major(latest)
            else:
                raise InvalidArgument(f"Invalid argument: {part=}")
        elif out:
            if "BREAKING CHANGE:" in out:
                return semver.bump_major(latest)
            elif "feat:" in out:
                return semver.bump_minor(latest)
            elif "fix:" in out:
                return semver.bump_patch(latest)
        return latest

    def publish(self, part: Bump = Bump.PATCH, force: bool = False, tox: bool = True):
        """
        Publish package

        Args:
            part: part to increase if force
            force: force bump
            tox: run tox
        """
        if rc := self.tests():
            sys.exit(rc)
        if tox:
            if rc := self.tox() != 0:
                sys.exit(rc)
        self.commit()
        if (n := self.next(part=part, force=force)) != (l :=self.latest()):
            self.tag(n)
            self.push()
            if rc := self.twine() != 0:
                sys.exit(rc)
            self.log.info(f"{self.publish.__name__}: {l} -> {n}")
        else:
            self.log.warning(f"{self.publish.__name__}: {n} -> nothing to do")

        self.clean()

    def pull(self) -> None:
        """pull

        Raises:
            CalledProcessError: if pull fails
            RuntimeError: if diverged or dirty
        """
        if self.diverge():
            raise RuntimeError(f"Diverged: {self.diverge()} or dirty: {self.diverge()} - {self.name=}")
        if self.need_pull():
            subprocess.check_call(f"{self.git} fetch --all  --tags --quiet", shell=True)
            subprocess.check_call(f"{self.git} pull --quiet", shell=True)
            self.log.info(self.pull.__name__)

    def push(self) -> None:
        """push

        Raises:
            CalledProcessError: if push fails
            RuntimeError: if diverged
        """
        self.commit()
        if self.need_push():
            if self.need_pull():
                raise RuntimeError(f"Diverged: {self.name=}")
            subprocess.check_call(f"{self.git} push --quiet", shell=True)
            self.log.info(self.push.__name__)

    @classmethod
    def repos(
            cls,
            ret: ProjectRepos = ProjectRepos.NAMES,
            py: bool = False, sync: bool = False,
    ) -> list[Path] | list[str] | dict[str, Project | str]:
        """
        repo paths, names or Project instances under home and Archive

        Args:
            ret:return names, paths or instances
            py: return only python projects instances
            sync: push or pull all repos

        """
        if py or sync:
            ret = ProjectRepos.INSTANCES
        names = True if ret is ProjectRepos.NAMES else False
        archive = sorted(archive.iterdir()) if (archive := Path.home() / "Archive").is_dir() else []

        rv = [item.name if names else item
              for item in archive + sorted(Path.home().iterdir())
              if item.is_dir() and (item / ".git").exists()]
        if ret == ProjectRepos.DICT:
            return {item.name: item for item in rv}
        if ret == ProjectRepos.INSTANCES:
            rv = {item.name: cls(item) for item in rv}
            if sync:
                for item in rv.values():
                    item.sync()
            if py:
                rv = [item for item in rv.values() if item.pyproject_toml.file]
            return rv
        return rv

    def requirements(self, install: bool = False, upgrade: bool = False) -> list[str] | int:
        """dependencies and optional dependencies from pyproject.toml or distribution"""
        req = sorted(list({*self.dependencies() + flatten(list(self.extras().values()), recurse=True)}))
        if (install or upgrade) and req:
            upgrade = ["--upgrade"] if upgrade else []
            rv = subprocess.check_call([self.executable, "-m", "pip", "install", "-q", *upgrade, *req])
            self.log.info(self.requirements.__name__)

            return rv
        return req

    def sha(self, ref: GitSHA = GitSHA.LOCAL) -> str:
        """has for local, base or remote"""
        if ref is GitSHA.LOCAL:
            args = "rev-parse @"
        elif ref is GitSHA.BASE:
            args = "merge-base @ @{u}"
        elif ref is GitSHA.REMOTE:
            args = "rev-parse @{u}"
        else:
            raise InvalidArgument(f"Invalid argument: {ref=}")
        return stdout(f"{self.git} {args}")

    def sync(self):
        """Sync repository"""
        self.push()
        self.pull()

    def superproject(self) -> Path | None:
        """git rev-parse --show-superproject-working-tree --show-toplevel"""
        if v := stdout(f"{self.git} rev-parse --show-superproject-working-tree --show-toplevel", split=True):
            return Path(v[0])

    def tag(self, tag: str) -> None:
        """
        tag

        Raises:
            CalledProcessError: if push fails
        """
        if (latest := self.latest()) == tag:
            self.log.warning(f"{self.tag.__name__}: {tag} -> nothing to do")
            return
        subprocess.check_call(f"{self.git} tag {tag}", shell=True)
        subprocess.check_call(f"{self.git} push origin {tag} --quiet", shell=True)
        self.log.info(f"{self.tag.__name__}: {latest} -> {tag}")

    # TODO: borrar viejos

    def tests(self) -> int:
        if self.pyproject_toml.file:
            return subprocess.run(f"{self.executable} -m pytest {self.root}", shell=True).returncode

    def top(self) -> Path | None:
        """git rev-parse --show-toplevel"""
        if v := stdout(f"{self.git} rev-parse --show-toplevel"):
            return Path(v)

    def tox(self) -> int:
        if self.pyproject_toml.file:
            return subprocess.run(f"{self.executable} -m tox --root {self.root}", shell=True).returncode
        return 0

    def twine(self, part: Bump = Bump.PATCH, force: bool = False, ) -> int:
        """
        Twine

        Args:
            part: part to increase if force
            force: force bump
        """
        pypi = d.version if (d := self.distribution()) else None

        if (self.pyproject_toml.file and (pypi != self.next(part=part, force=force))
                and "Private :: Do Not Upload"
                not in self.pyproject_toml.config.get("project", {}).get("classifiers", [])):
            return subprocess.run(f"{self.executable} -m twine upload -u __token__  "
                                  f"{self.build()}", shell=True).returncode
        return 0

    def version(self) -> str:
        """Version from pyproject.toml, tag or distribution"""
        if v := self.pyproject_toml.config.get("project", {}).get("version"):
            return v
        elif self.repo and (v := self.latest()):
            return v
        elif d := self.distribution():
            return d.version
        else:
            raise RuntimeWarning(f"Version not found for {self.name=} {self.directory=}")

    def venv(self, version: str = PYTHON_DEFAULT_VERSION, force: bool = False, upgrade: bool = False):
        """venv"""
        if not self.root:
            raise RuntimeError(f"Undefined: {self.root=} for {self.name=} {self.directory=}")
        venv = self.root / 'venv'
        if force:
            shutil.rmtree(venv, ignore_errors=True)
        elif not venv.is_dir():
            subprocess.check_call(f"python{version} -m venv {venv}", shell=True)
            self.log.info(f"{self.venv.__name__}: {venv}")
        self.executable = venv / "bin/python"
        subprocess.check_call([self.executable, "-m", "pip", "install", "--upgrade", "-q",
                               "pip", "wheel", "setuptools", "build"])
        self.requirements(install=True, upgrade=upgrade)


PPIP = Project(__file__)
"""Project instance for Ppip"""
PROJECT = Project()
"""Project instance for cwd"""
# --only-binary=:all:
# [install]
# only-binary = :all:
# no-warn-script-location = false
# PIP_ONLY_BINARY=:all:


if __name__ == '__main__':
    p = Project("/Users/j5pu/ppip")
    print(p.build())
