__all__ = (
    "EXECUTABLE",
    "EXECUTABLE_SITE",
    "LINUX",
    "MACOS",
    "PPIP_CONFIG",
    "PPIP_CONFIG_PYPROJECT",
    "PPIP_DATA",
    "PW_ROOT",
    "PW_USER",
    "venv",
)

import os
import pwd
import sys
import venv
from pathlib import Path

import toml

EXECUTABLE = Path(sys.executable)
EXECUTABLE_SITE = Path(EXECUTABLE).resolve()
LINUX = sys.platform == "linux"
"""Is Linux? sys.platform == 'linux'"""
MACOS = sys.platform == "darwin"
"""Is macOS? sys.platform == 'darwin'"""
PPIP_CONFIG = Path(__file__).parent.parent / "config"
"Ppip Config Directory"
PPIP_CONFIG_PYPROJECT = PPIP_CONFIG / "pyproject.toml"
"Ppip Config Logger Directory"
PPIP_DATA = PPIP_CONFIG.parent / "data"
"""Ppip Data Directory"""
PW_ROOT = pwd.getpwnam("root")
PW_USER = pwd.getpwnam(os.environ["USER"])
venv.CORE_VENV_DEPS = sorted({req for extra in
                              toml.load(PPIP_CONFIG_PYPROJECT)["project"]["optional-dependencies"].values()
                              for req in extra})
