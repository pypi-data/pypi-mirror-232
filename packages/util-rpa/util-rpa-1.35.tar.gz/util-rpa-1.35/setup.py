from setuptools import (
    setup,
    find_packages,
)

from util_rpa import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="util-rpa",
    version=__version__,
    author="Jonathan Bolo",
    author_email="jonathan.bolo@telefonica.com",
    description="Utilitarios usados por RPA Python",
    python_requires='>=3.9.0',
    install_requires=required,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(exclude=['tests*', '*.tests*']),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Utilities"
    ],
)