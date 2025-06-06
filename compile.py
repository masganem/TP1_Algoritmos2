from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import sysconfig

try:
    import pybind11
except ImportError:
    raise RuntimeError("pybind11 is required to build the kd_tree extension. Install it with `pip install pybind11`. ")

from pybind11 import get_include

# Compiler flags for c++17
cxx_flags = ["-std=c++17"]

# On some platforms (especially macOS) you might need to add extra flags,
# but for a standard Linux/g++ setup these are usually sufficient.

ext_modules = [
    Extension(
        "kd_tree",                      # Module name (matches PYBIND11_MODULE)
        ["kd_tree_module.cpp"],         # Source file(s)
        include_dirs=[
            get_include(),              # pybind11 headers
        ],
        language="c++",
        extra_compile_args=cxx_flags,
    )
]

class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""

    c_opts = {
        "msvc": ["/EHsc", "/std:c++17"],
        "unix": ["-std=c++17"],
    }

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == "unix":
            opts.append("-DVERSION_INFO=\"{}\"".format(self.distribution.get_version()))
            if sys.platform == "darwin":
                opts += ["-stdlib=libc++", "-mmacosx-version-min=10.9"]
        elif ct == "msvc":
            opts.append("/DVERSION_INFO=\"{}\"".format(self.distribution.get_version()))

        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)

setup(
    name="kd_tree",
    version="0.0.1",
    author="pybind11",
    description="KD-Tree C++ extension exposed to Python via pybind11",
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExt},
    zip_safe=False,
) 