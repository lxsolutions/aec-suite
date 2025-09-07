
from setuptools import setup, find_packages

setup(
    name="aec-shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.4.0",
    ],
)
