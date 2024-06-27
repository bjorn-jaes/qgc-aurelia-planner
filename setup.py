#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="qgc-aurelia",
    version="0.1.0",  # Set a suitable version
    description="Converts GeoJson files into QGroundControl plans for Aurelia X6 spraying system.",
    long_description=open("README.md").read(),  # Adjust the path if needed
    long_description_content_type="text/markdown",
    author="Bjørn Nødland Fuglestad",
    author_email="bjorn@jaersense.no",
    maintainer="Bjørn Nødland Fuglestad",
    maintainer_email="bjorn@jaersense.no",
    keywords=["ground controller", "geospatial", "drone", "uav", "uas", "uuv", "robotics", 
              "autonomous", "vehicle", "system", "gcs", "qgc", "aurelia", "mavlink", "mavproxy", "mavros", "mavlink-router"],
    license="MIT",  # Adjust the license as needed
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "geopandas",
        "folium",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "qgc-aurelia-cli=qgc_aurelia.__main__:main"
        ],
        "gui_scripts": [
            "qgc-aurelia=qgc_aurelia.app:main"
        ]
    },
    project_urls={
        #"Homepage": ""
    }
)