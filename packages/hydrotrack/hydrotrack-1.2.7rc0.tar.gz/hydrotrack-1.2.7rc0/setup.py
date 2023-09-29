import os
import sysconfig
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py
from hydrotrack import __version__

try:
    from Cython.Build import cythonize
except ImportError:
    raise RuntimeError(
        "Cython required for running the package installation\n"
        + "Try installing it with:\n"
        + "$> pip install cython"
    )

EXCLUDE_FILES = []
requirements = [
    'ipykernel',
    'pandas==2.1.1',
    'numpy==1.24.3',
    'geopandas==0.14.0',
    'rasterio==1.3.8',
    'scikit_learn==1.3.1',
    'tqdm==4.66.1',
    'opencv-python==4.8.0.76',
    'pyarrow==13.0.0',
    'xarray==2023.8.0',
    'netcdf4==1.6.4'
    ]

def get_ext_paths(root_dir, exclude_files):
    """get filepaths for compilation"""
    paths = []
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if os.path.splitext(filename)[1] != '.py':
                # delete non-python files
                os.remove(os.path.join(root, filename))
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
    ext_modules=external_modules,
    setup_requires=requirements,
    install_requires=requirements,
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
