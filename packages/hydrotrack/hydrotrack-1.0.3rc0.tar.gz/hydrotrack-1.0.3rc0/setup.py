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
        'joblib==1.2.0',
        'numpy==1.24.3',
        'scikit-learn==1.2.2',
        'opencv-python==4.7.0.72',
        'geopandas==0.13.2',
        'rasterio==1.3.7',
        'xarray==2023.5.0',
        'pyarrow==12.0.0',
        'netcdf4==1.6.4',
        'tqdm==4.65.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
