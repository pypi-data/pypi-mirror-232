import os
from ast import parse
import sysconfig
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py
from Cython.Build import cythonize

EXCLUDE_FILES = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    
with open(os.path.join('hydrotrack', '_version.py')) as f:
    __version__ = parse(next(filter(lambda line: line.startswith('__version__'),
                                     f))).body[0].value.s

def get_ext_paths(root_dir, exclude_files):
    """get filepaths for compilation"""
    paths = []
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if os.path.splitext(filename)[1] != '.py':
                continue        
            file_path = os.path.join(root, filename)
            if file_path in exclude_files:
                continue
            paths.append(file_path)
    return paths

external_modules = cythonize(
        get_ext_paths('hydrotrack', EXCLUDE_FILES),
        compiler_directives={'language_level': 3}
    )

# noinspection PyPep8Naming
class build_py(_build_py):
    def find_package_modules(self, package, package_dir):
        ext_suffix = sysconfig.get_config_var('EXT_SUFFIX')
        modules = super().find_package_modules(package, package_dir)
        filtered_modules = []
        for (pkg, mod, filepath) in modules:
            if os.path.exists(filepath.replace('.py', ext_suffix)):
                continue
            filtered_modules.append((pkg, mod, filepath, ))
        return filtered_modules
    
setup(
    name="hydrotrack",
    version=__version__,
    author="Helvecio B. L. Neto, Alan J. P. Calheiros",
    author_email="hydrotrack.project@gmail.com",
    description="A Python package for track and forecasting.",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    url="https://github.com/hydrotrack-project/hydrotrack",
    packages=find_packages(),
    install_requires=requirements,
    ext_modules=external_modules,
    license="LICENSE",
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    cmdclass={
        'build_py': build_py
    }
)
