import sys
from contextvars import ContextVar
from pathlib import Path

# noinspection PyCompatibility
import pip._internal.cli.base_command
import pip._internal.operations.install.wheel

from .utils.functions import exec_module_from_file, findfile
from .utils.functions import logger

log = logger("<level>{level: <8}</level> <red>|</red> "
             "<cyan>{name}</cyan> <red>|</red> "
             "<blue><level>{message}</level></blue><red>:</red> "
             "<level>{extra[source]}</level> <red>-></red> "
             "<level>{extra[destination]}</level>")

pip_context: ContextVar[dict[str, Path]] = ContextVar("pip_context", default={})


def _pip_base_command(self: pip._internal.cli.base_command.Command, args: list[str]) -> int:
    """
    Post install pip patch
    """
    try:
        with self.main_context():
            rv = self._main(args)
            if rv == 0 and self.__class__.__name__ == "InstallCommand":
                variable = pip_context.get()
                for key, value in variable.items():
                    for filename in ["_post_install.py", "post_install.py"]:
                        for file in findfile(filename, value):
                            log.info(key, source="executing", destination=file)
                            exec_module_from_file(file)
            return rv
    finally:
        logging.shutdown()  # noqa: F821


def _pip_install_wheel(name, wheel_path, scheme, req_description, pycompile, warn_script_location,
                       direct_url, requested):
    """pip install wheel patch to post install"""
    with ZipFile(wheel_path, allowZip64=True) as z:  # noqa: F821, SIM117
        with req_error_context(req_description):  # noqa: F821
            _install_wheel(  # noqa: F821
                name=name,
                wheel_zip=z,
                wheel_path=wheel_path,
                scheme=scheme,
                pycompile=pycompile,
                warn_script_location=warn_script_location,
                direct_url=direct_url,
                requested=requested,
            )
            variable = pip_context.get()
            variable[name] = Path(scheme["purelib"], name)
            pip_context.set(variable)


pip._internal.operations.install.wheel.install_wheel = _pip_install_wheel
pip._internal.cli.base_command.Command.main = _pip_base_command
