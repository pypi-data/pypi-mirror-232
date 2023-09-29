from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Spatiotemporal data processing for the STELAR project'
LONG_DESCRIPTION = 'This package is part of the EU STELAR project and provides tools for processing spatiotemporal data. The package includes functionality for field delineation (i.e., segmentation) of satellite images, extracting LAI timseries out of the images, and interpolating cloud covers, among others.'


setup(
    name='stelar_spatiotemporal',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="Jens d'Hondt",
    author_email="j.e.d.hondt@tue.nl",
    packages=find_packages(),
    install_requires=[
        "pystac",
        "pystac_client",
        "shapely",
        "opencv-python",
        "numpy",
        "sentinelhub",
        "pandas",
        "rasterio",
        "geopandas>=0.8.1",
        "decorator",
        "scikit-image",
        "fs",
        "fs-s3fs",
        "tqdm",
        "boto3",
        "matplotlib"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
