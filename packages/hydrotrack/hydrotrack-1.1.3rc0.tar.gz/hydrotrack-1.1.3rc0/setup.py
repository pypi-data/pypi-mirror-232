import setuptools
from hydrotrack import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="hydrotrack",
    version=__version__,
    author="Helvecio B. L. Neto, Alan J. P. Calheiros",
    author_email="hydrotrack.project@gmail.com",
    description="A Python package for track and forecasting.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hydrotrack-project/hydrotrack",
    packages=setuptools.find_packages(),
    install_requires=[
        'geopandas==0.14.0',
        'rasterio==1.3.8',
        'scikit_learn==1.3.1',
        'tqdm==4.66.1',
        'opencv-python==4.8.0.76',
        'pyarrow==13.0.0',
        'xarray==2023.8.0',
        'netcdf4==1.6.4'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
