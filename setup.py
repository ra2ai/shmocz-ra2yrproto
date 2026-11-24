import os
import shutil
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist

try:
    from setuptools.command.editable_wheel import editable_wheel
except ImportError:
    editable_wheel = None

SETUP_DIR = os.path.dirname(os.path.abspath(__file__))
PROTO_DIR = os.path.join(SETUP_DIR, "ra2yrproto")


def get_proto_sources(path):
    for directory, _, files in os.walk(path):
        for name in files:
            if name.endswith(".proto"):
                yield os.path.join(directory, name)


def ensure_protoc():
    candidates = []
    if os.environ.get("PROTOC_EXE"):
        candidates.append(os.environ["PROTOC_EXE"])
    found = shutil.which("protoc")
    if found:
        candidates.append(found)
    candidates.append(os.path.join(SETUP_DIR, "protoc", "bin", "protoc"))
    for exe in candidates:
        if os.path.isfile(exe):
            return exe
    raise RuntimeError(
        "protoc is required to build ra2yrproto. "
        "Install protoc 25.1, set PROTOC_EXE, or run ./ensure_protoc.sh."
    )


def compile_protos():
    protoc = ensure_protoc()
    sources = sorted(get_proto_sources(PROTO_DIR))
    if not sources:
        raise RuntimeError(f"no .proto files found in {PROTO_DIR}")
    command = [
        protoc,
        f"--python_out={SETUP_DIR}",
        f"--pyi_out={SETUP_DIR}",
        f"--proto_path={SETUP_DIR}",
    ]
    include = os.path.join(os.path.dirname(os.path.dirname(protoc)), "include")
    if os.path.isdir(include):
        command.append(f"--proto_path={include}")
    command.extend(sources)
    if subprocess.call(command) != 0:
        raise RuntimeError("protoc failed")
    missing = []
    for source in sources:
        relative = os.path.splitext(os.path.relpath(source, SETUP_DIR))[0] + "_pb2.py"
        output = os.path.join(SETUP_DIR, relative)
        if not os.path.isfile(output):
            missing.append(output)
    if missing:
        raise RuntimeError("protoc did not write:\n" + "\n".join(missing))


class _Sdist(sdist):
    def add_defaults(self):
        super().add_defaults()
        self.filelist.extend(sorted(get_proto_sources(PROTO_DIR)))


class BuildProto(build_py):
    def run(self):
        compile_protos()
        super().run()


cmdclass = {"sdist": _Sdist, "build_py": BuildProto}
if editable_wheel is not None:

    class EditableWheel(editable_wheel):
        def run(self):
            compile_protos()
            super().run()

    cmdclass["editable_wheel"] = EditableWheel


setup(
    cmdclass=cmdclass,
    packages=find_packages(include=["ra2yrproto"]),
    package_data={"ra2yrproto": ["*.proto", "*.pyi"]},
)
