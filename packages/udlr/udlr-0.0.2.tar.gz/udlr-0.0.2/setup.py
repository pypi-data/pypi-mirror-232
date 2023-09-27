from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np
from pathlib import Path
import sys
import os

if sys.platform == "darwin":
    os.environ["CC"] = "gcc-12"
    os.environ["CXX"] = "g++-12"

if sys.platform == "win32":
    compile_flags = ["/Ox", "/std:c++20"]
else:
    compile_flags = ["-std=c++2a", "-O3"]


this_directory = Path(__file__).parent

cpp_modules = ["gf2sparse"]

c_extensions = []
for module in cpp_modules:
    c_extensions.append(
        Extension(
            name=f"udlr.{module}._{module}",
            sources=[f"src_python/udlr/{module}/_{module}.pyx"],
            libraries=[],
            library_dirs=[],
            include_dirs=[np.get_include(), "src_cpp"],
            extra_compile_args=compile_flags,
            extra_link_args=[],
            language="c++",
        )
    )


setup(
    ext_modules=cythonize(
        c_extensions,
        compiler_directives={
            "boundscheck": False,
            "wraparound": False,
            "initializedcheck": False,
            "cdivision": True,
            "embedsignature": True,
        },
    ),
)
