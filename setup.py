# -*- coding: utf-8 -*-

import os
import sys

import pybind11
from setuptools.command.build_ext import build_ext
from setuptools import setup, Extension, find_packages


here = os.path.abspath(os.path.dirname(__file__))
about = {}

with open(os.path.join(here, "src", "pdftopng", "__version__.py"), "r") as f:
    exec(f.read(), about)

with open("README.md", "r") as f:
    readme = f.read()


requires = [
    "Click>=7.0",
]
dev_requires = ["Sphinx>=2.2.1"]
dev_requires = dev_requires + requires
ext_includes = [
    "lib/poppler",
    "lib/poppler/fofi",
    "lib/poppler/goo",
    "lib/poppler/poppler",
    "lib/poppler/build",
    "lib/poppler/build/poppler",
    "lib/poppler/utils",
    "lib/poppler/build/utils",
    pybind11.get_include(),
]

ext_modules = [
    Extension(
        "pdftopng.pdftopng",
        # Sort input source files to ensure bit-for-bit reproducible builds
        # (https://github.com/pybind/python_example/pull/53)
        sorted(["src/pdftopng/pdftopng.cpp"]),
        include_dirs=ext_includes,
        language="c++",
    ),
]


# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    import os

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
        "msvc": ["/EHsc"],
        "unix": ["-O3", "-Wall", "-shared", "-fPIC"],
    }

    if sys.platform == "linux":
        soname = "libpoppler.so"
    elif sys.platform == "darwin":
        soname = "libpoppler.dylib"

    l_opts = {
        "msvc": [],
        "unix": ["-Wl,-rpath,lib/poppler/build", f"lib/poppler/build/{soname}"],
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
        package_dir={"": "src"},
        packages=find_packages(where="src", exclude=("tests",)),
        ext_modules=ext_modules,
        include_package_data=True,
        install_requires=requires,
        extras_require={"dev": dev_requires},
        classifiers=[
            # Trove classifiers
            # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
            "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
        ],
        cmdclass={"build_ext": BuildExt},
    )

    setup(**metadata)


if __name__ == "__main__":
    setup_package()
