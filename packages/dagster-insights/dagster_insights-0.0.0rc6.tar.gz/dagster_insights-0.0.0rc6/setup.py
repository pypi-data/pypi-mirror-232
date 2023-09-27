from pathlib import Path
from typing import Dict

from setuptools import find_packages, setup


def get_version() -> str:
    version: Dict[str, str] = {}
    with open(Path(__file__).parent / "dagster_insights/version.py", encoding="utf8") as fp:
        exec(fp.read(), version)

    return version["__version__"]


setup(
    name="dagster_insights",
    version="0.0.0rc6",
    author_email="hello@elementl.com",
    packages=find_packages(exclude=["dagster_insights_tests*"]),
    include_package_data=True,
    install_requires=[
        "dagster",
        "dagster_cloud",
        "gql[requests]>=3.0.0",
    ],
    extras_require={"tests": ["freezegun"]},
    author="Elementl",
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points={},
)
