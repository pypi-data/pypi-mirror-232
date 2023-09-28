__all__ = (
    "CONSOLE",
)

import os
import warnings

import rich.pretty
import rich.traceback

CONSOLE = rich.console.Console(force_interactive=True, color_system='256')

rich.pretty.install(CONSOLE, expand_all=True)
rich.traceback.install(show_locals=True)

warnings.filterwarnings("ignore", category=UserWarning, message="Setuptools is replacing distutils.")
os.environ["PYTHONDONTWRITEBYTECODE"] = ""
os.environ["PY_IGNORE_IMPORTMISMATCH"] = "1"
