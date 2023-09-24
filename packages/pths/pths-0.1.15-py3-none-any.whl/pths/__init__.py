__all__ = (
    "exec_module_from_file",
    "find_file",
    "PostInstall",
    "PTHBuildPy",
    "PTHDevelop",
    "PTHEasyInstall",
    "PTHInstallLib",
)

import filecmp
import fnmatch
import importlib.util
import inspect
import itertools
import os
import sys
import types
import warnings
from contextvars import ContextVar
from pathlib import Path
from typing import Optional, Union

import setuptools.command.build_py
import setuptools.command.develop
import setuptools.command.easy_install
import setuptools.command.install
import setuptools.command.install_lib
from loguru import logger
from loguru_config import LoguruConfig

_config = {
    "handlers": [
        {
            "sink": "ext://sys.stderr",
            "format": "<level>{level: <8}</level> <red>|</red> "
                      "<cyan>{name}</cyan> <red>|</red> "
                      "<blue><level>{message}</level></blue><red>:</red> <level>{extra[source]}</level> "
                      "<red>-></red> <level>{extra[destination]}</level>",
        },
    ],
    "extra": {
        "source": "source",
        "destination": "destination",
    }
}

LoguruConfig.load(_config)

pip_context: ContextVar[dict[str, Path]] = ContextVar("pip_context", default={})


def find_file(pattern, path: Optional[Union[Path, str]] = None) -> list[Path]:
    """
    Find file with pattern"

    Examples:
        >>> from pathlib import Path
        >>> import pths
        >>> from pths import find_file
        >>>
        >>> assert Path(pths.__file__) in find_file("*.py")

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


def exec_module_from_file(file: Union[Path, str], name: Optional[str] = None) -> types.ModuleType:
    """
    executes module from file location

    Examples:
        >>> import pths
        >>> m = pths.exec_module_from_file(pths.__file__)
        >>> assert m.__name__ == pths.__name__

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


class PostInstall(setuptools.command.install.install):
    """Runs "post_install.py" after install"""

    def run(self):
        super().run()
        for f in inspect.stack():
            print(f.filename)

        # self.build_lib = build/lib
        # self.get_outputs() = ['build/bdist.macosx-12-x86_64/wheel/huti/functions.py'...
        for file in self.get_outputs():
            file = Path(file)
            if file.name in ["_post_install.py", "post_install.py"]:
                logger.info(self.__class__.__name__, source="executing", destination=file)
                exec_module_from_file(file)


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
                logger.info(self.__class__.__name__, source=source, destination=destination)
                self.copy_file(source, destination)
                outputs.append(destination)
    return outputs


warnings.filterwarnings("ignore", category=UserWarning, message="Setuptools is replacing distutils.")
# UserWarning: Distutils was imported before Setuptools,
# but importing Setuptools also replaces the `distutils` module in `sys.modules`.
# noinspection PyCompatibility
import pip._internal.cli.base_command  # noqa: E402
import pip._internal.operations.install.wheel  # noqa: E402


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
                        for file in find_file(filename, value):
                            logger.info(key, source="executing", destination=file)
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
setuptools.command.build_py._IncludePackageDataAbuse.warn = lambda x=None, y=None: None
