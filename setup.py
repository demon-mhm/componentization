import os
import sys

import setuptools
from setuptools.command.build_py import build_py as _build_py

# google also doing it to access scripts
# https://github.com/grpc/grpc/blob/master/tools/distrib/python/grpcio_tools/setup.py#L38
sys.path.insert(0, os.path.abspath("."))


class GrpcTool(setuptools.Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from utils import generate_proto

        generate_proto.directory("src", "wire")


class BuildPyCmd(_build_py):
    def run(self):
        self.run_command("proto")
        _build_py.run(self)


if __name__ == "__main__":
    setuptools.setup(
        use_calver=True,
        cmdclass={
            "build_py": BuildPyCmd,
            "proto": GrpcTool,
        },
    )
