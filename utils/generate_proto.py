import os
import site
from pathlib import Path

import pkg_resources
from grpc_tools import protoc


def directory(*dirs):
    for dir in dirs:
        run(dir, dirs)


def run(source, includes):
    inline_protos = list(Path(f"./{source}").rglob("*.proto"))
    google_protos = pkg_resources.resource_filename("grpc_tools", "_proto")
    for count, proto in enumerate(inline_protos, start=1):
        print(f"{count}) {proto}")
        protoc.main(
            (
                "grpc_tools.protoc",
                *(f"-I./{inc}" for inc in includes),
                *(f"-I{sp}" for sp in site.getsitepackages() if os.path.exists(sp)),
                f"-I{google_protos}",
                f"--python_out=./{source}",
                f"--pyi_out=./{source}",
                f"{proto}",
            )
        )


if __name__ == "__main__":
    directory("src", "wire")
