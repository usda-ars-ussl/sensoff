import os
from setuptools import setup
from typing import Dict

HERE = os.path.abspath(os.path.dirname(__file__))

about: Dict[str, str] = {}
with open(os.path.join(HERE, "sensoff", "__version__.py")) as f:
    exec(f.read(), about)


LONG = (
    """Corrects GPS transect coordinates to account for sensor offsets on on-the-go
mobile survey platforms
"""
).replace("\n", " ")


SHORT = "Corrects GPS transect coordinates to account for on-the-go sensor offsets"


setup(
    name="sensoff",
    python_requires=">=3.7",
    version=about["__version__"],
    description=SHORT,
    long_description=LONG,
    url="https://github.com/usda-ars-ussl/sensoff",
    author="Todd Skaggs",
    author_email="todd.skaggs@usda.gov",
    license="Public Domain CC0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
    packages=["sensoff"],
    zip_safe=True,
    tests_require=["numpy", "pytest"],
    test_suite="tests",
)
