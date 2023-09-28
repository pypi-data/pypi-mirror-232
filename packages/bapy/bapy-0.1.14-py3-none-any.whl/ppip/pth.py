__all__ = (
    "PTHBuildPy",
    "PTHDevelop",
    "PTHEasyInstall",
    "PTHInstallLib",
)

import filecmp
import itertools
from pathlib import Path
from typing import Union

import setuptools.command.build_py
import setuptools.command.develop
import setuptools.command.easy_install
import setuptools.command.install_lib

from .utils.functions import logger

log = logger("<level>{level: <8}</level> <red>|</red> "
             "<cyan>{name}</cyan> <red>|</red> "
             "<blue><level>{message}</level></blue><red>:</red> "
             "<level>{extra[source]}</level> <red>-></red> "
             "<level>{extra[destination]}</level>")


class PTHBuildPy(setuptools.command.build_py.build_py):
    """Build py with pth files installed"""

    def run(self):
        super().run()
        self.outputs = []
        self.outputs = _copy_pths(self, self.build_lib)

    def get_outputs(self, include_bytecode=1):
        return itertools.chain(setuptools.command.build_py.build_py.get_outputs(self, 0), self.outputs)


class PTHDevelop(setuptools.command.develop.develop):
    def run(self):
        super().run()
        _copy_pths(self, self.install_dir)


class PTHEasyInstall(setuptools.command.easy_install.easy_install):
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)
        _copy_pths(self, self.install_dir)


class PTHInstallLib(setuptools.command.install_lib.install_lib):
    def run(self):
        super().run()
        self.outputs = []
        self.outputs = _copy_pths(self, self.install_dir)

    def get_outputs(self):
        return itertools.chain(setuptools.command.install_lib.install_lib.get_outputs(self), self.outputs)


def _copy_pths(self: Union[PTHBuildPy, PTHDevelop, PTHEasyInstall, PTHInstallLib],
               directory: str) -> list[str]:
    outputs = []
    data = self.get_outputs() if isinstance(self, (PTHBuildPy, PTHInstallLib)) else self.outputs
    for source in data:
        if source.endswith(".pth"):
            destination = Path(directory, Path(source).name)
            if not destination.is_file() or not filecmp.cmp(source, destination):
                destination = str(destination)
                log.info(self.__class__.__name__, source=source, destination=destination)
                self.copy_file(source, destination)
                outputs.append(destination)
    return outputs
