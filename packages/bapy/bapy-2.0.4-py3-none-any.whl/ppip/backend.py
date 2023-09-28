import sys
from pathlib import Path

import setuptools.build_meta
import toml

from .env import Env
from .env import VIRTUAL_ENV

from .utils.constants import PPIP_PROJECT
from .utils.functions import tox

from .utils.variables import PPIP_CONFIG_PYPROJECT
from .utils.variables import venv

for item in sys.argv[1:]:
    directory = Path(item)
    if directory.is_dir():
        break
else:
    directory = Path.cwd()

extras = venv.CORE_VENV_DEPS if tox() or Env.CI or Env.GITHUB_ACTION or VIRTUAL_ENV else []
ppip_deps = toml.load(PPIP_CONFIG_PYPROJECT)["build-system"]["requires"] if PPIP_PROJECT == directory.name else []


class BuildMetaBackend(setuptools.build_meta._BuildMetaBackend):
    def get_requires_for_build_wheel(self, config_settings=None):
        return super().get_requires_for_build_wheel(config_settings) + extras + ppip_deps

    def get_requires_for_build_sdist(self, config_settings=None):
        return super().get_requires_for_build_sdist(config_settings) + extras + ppip_deps

    def prepare_metadata_for_build_wheel(self, metadata_directory,
                                         config_settings=None):
        return super().prepare_metadata_for_build_wheel(metadata_directory,
                                                        config_settings)

    def build_wheel(self, wheel_directory, config_settings=None,
                    metadata_directory=None):
        return super().build_wheel(wheel_directory, config_settings,
                                   metadata_directory)

    def build_sdist(self, sdist_directory, config_settings=None):
        return super().build_sdist(sdist_directory, config_settings)

    def get_requires_for_build_editable(self, config_settings=None):
        return super().get_requires_for_build_editable(config_settings) + extras + ppip_deps

    def prepare_metadata_for_build_editable(self, metadata_directory,
                                            config_settings=None):
        return super().prepare_metadata_for_build_editable(metadata_directory,
                                                           config_settings)

    def build_editable(self, wheel_directory, config_settings=None,
                       metadata_directory=None):
        return super().build_editable(wheel_directory, config_settings,
                                      metadata_directory)


BACKEND = BuildMetaBackend()
get_requires_for_build_wheel = BACKEND.get_requires_for_build_wheel
get_requires_for_build_sdist = BACKEND.get_requires_for_build_sdist
prepare_metadata_for_build_wheel = BACKEND.prepare_metadata_for_build_wheel
build_wheel = BACKEND.build_wheel
build_sdist = BACKEND.build_sdist

if not setuptools.build_meta.LEGACY_EDITABLE:
    get_requires_for_build_editable = BACKEND.get_requires_for_build_editable
    prepare_metadata_for_build_editable = BACKEND.prepare_metadata_for_build_editable
    build_editable = BACKEND.build_editable
