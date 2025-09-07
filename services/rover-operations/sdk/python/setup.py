








from setuptools import setup, find_packages

setup(
    name="rover-operations-sdk",
    version="0.1.0",
    description="Python SDK for Rover Operations tele-operation platform",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        "grpcio>=1.32.0",
        "numpy>=1.19.0",
    ],
    entry_points={
        'console_scripts': [
            'rover-sdk=rover_operations.cli:main',
        ],
    },
)






