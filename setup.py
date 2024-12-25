# -*- coding: utf-8 -*-

import glob
import os
import shutil
import sys

import pybind11
import setuptools
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext

here = os.path.abspath(os.path.dirname(__file__))
about = {}

with open(os.path.join(here, "src", "pdftopng", "__version__.py"), "r") as f:
    exec(f.read(), about)

with open("README.md", "r") as f:
    readme = f.read()

requires = [
    "Click>=7.0",
]
dev_requires = ["Pillow>=8.2.0", "pytest>=6.2.3", "pytest-cov>=2.11.1"]
dev_requires = dev_requires + requires

poppler_dir = os.path.join(os.getcwd(), "lib", "poppler")
build_dir = os.path.join(poppler_dir, "build")
library_dirs = []
libraries = []

if sys.platform in ["linux", "darwin"]:
    library_dirs.extend([build_dir])
    libraries.extend(["poppler"])

if sys.platform == "win32":
    # https://docs.python.org/3/library/platform.html#platform.architecture
    x = "x64" if sys.maxsize > 2**32 else "x86"

    poppler_dir = os.path.join(os.getcwd(), "lib", "poppler")
    build_dir = os.path.join(poppler_dir, f"build_win_{x}")

    # set VCPKG_INSTALLATION_ROOT=C:\dev\vcpkg
    vcpkg_lib_dir = os.path.join(
        os.environ["VCPKG_INSTALLATION_ROOT"], "installed", f"{x}-windows", "lib"
    )
    poppler_lib_dir = os.path.join(build_dir, "Release")

    library_dirs.extend([vcpkg_lib_dir, poppler_lib_dir])
    libraries.extend(
        ["freetype", "fontconfig", "libpng16", "jpeg", "advapi32", "poppler"]
    )

include_dirs = [
    poppler_dir,
    os.path.join(poppler_dir, "fofi"),
    os.path.join(poppler_dir, "goo"),
    os.path.join(poppler_dir, "utils"),
    os.path.join(poppler_dir, "poppler"),
    build_dir,
    os.path.join(build_dir, "utils"),
    os.path.join(build_dir, "poppler"),
    pybind11.get_include(),
]

ext_modules = [
    Extension(
        "pdftopng.pdftopng",
        # Sort input source files to ensure bit-for-bit reproducible builds
        # (https://github.com/pybind/python_example/pull/53)
        sorted([os.path.join("src", "pdftopng", "pdftopng.cpp")]),
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        language="c++",
    ),
]


# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import os
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".cpp", delete=False) as f:
        f.write("int main (int argc, char **argv) { return 0; }")
        fname = f.name
    try:
        compiler.compile([fname], extra_postargs=[flagname])
    except setuptools.distutils.errors.CompileError:
        return False
    finally:
        try:
            os.remove(fname)
        except OSError:
            pass
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14/17] compiler flag.
    The newer version is prefered over c++11 (when it is available).
    """
    flags = ["-std=c++14", "-std=c++11"]

    for flag in flags:
        if has_flag(compiler, flag):
            return flag

    raise RuntimeError("Unsupported compiler -- at least C++11 support " "is needed!")


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""

    c_opts = {
        "msvc": ["/MD", "/EHsc", "/std:c++14"],
        "unix": ["-O3", "-Wall", "-shared", "-fPIC"],
    }

    l_opts = {
        "msvc": [],
        "unix": [],
    }

    if sys.platform == "darwin":
        darwin_opts = ["-stdlib=libc++", "-mmacosx-version-min=10.7"]
        c_opts["unix"] += darwin_opts
        l_opts["unix"] += darwin_opts

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])

        if ct == "unix":
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, "-fvisibility=hidden"):
                opts.append("-fvisibility=hidden")

        for ext in self.extensions:
            ext.define_macros = [
                ("VERSION_INFO", '"{}"'.format(self.distribution.get_version()))
            ]
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts

        build_ext.build_extensions(self)


def setup_package():
    metadata = dict(
        name=about["__title__"],
        version=about["__version__"],
        description=about["__description__"],
        long_description=readme,
        long_description_content_type="text/markdown",
        url=about["__url__"],
        author=about["__author__"],
        author_email=about["__author_email__"],
        license=about["__license__"],
        packages=find_packages(where="src", exclude=("tests",)),
        package_dir={"": "src"},
        ext_modules=ext_modules,
        include_package_data=True,
        install_requires=requires,
        extras_require={"dev": dev_requires},
        entry_points={
            "console_scripts": [
                "pdftopng = pdftopng.cli:cli",
            ],
        },
        classifiers=[
            # Trove classifiers
            # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
            "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
        ],
        cmdclass={"build_ext": BuildExt},
    )

    setup(**metadata)


if __name__ == "__main__":
    setup_package()
