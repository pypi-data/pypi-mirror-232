# Copyright (C) 2023 twyleg
import versioneer
from pathlib import Path
from setuptools import find_packages, setup


def read(fname):
    return open(Path(__file__).parent / fname).read()


setup(
    name="ihk_ausbildungsnachweis_broker",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description="IHK Ausbildungsnachweise workflow broker",
    license="GPL 3.0",
    keywords="ihk ausbildungsnachweis pdf signature",
    url="https://github.com/twyleg/ausbildungsnachweis_utils",
    packages=find_packages(),
    include_package_data=True,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    install_requires=[
        "ihk-ausbildungsnachweis-utilities",
        "PyGithub~=1.59.1",
        "pygit2~=1.13.1",
        "flask~=2.3.3",
        "werkzeug~=2.3.7",
    ],
    entry_points={
        "console_scripts": [
            "ihk_ausbildungsnachweis_broker = ihk_ausbildungsnachweis_broker.app:start",
        ]
    },
)
