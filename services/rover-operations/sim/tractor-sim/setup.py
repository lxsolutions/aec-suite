





from setuptools import setup, find_packages

setup(
    name="tractor-sim",
    version="0.1.0",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        "grpcio-tools>=1.32.0",
        "numpy>=1.19.0",
        "opencv-python-headless>=4.5.0",  # For frame generation
    ],
    entry_points={
        'console_scripts': [
            'tractor-sim=simulator.main:main',
        ],
    },
)





