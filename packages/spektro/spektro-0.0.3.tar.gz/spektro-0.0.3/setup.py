from setuptools import setup, find_packages

setup(
    name="spektro",
    version="0.0.3",
    description="A Python package for hyperspectral/multispectral imaging research.",
    author="Yannis Kalfas",
    packages=find_packages(),
    install_requires=[
        "h5py>=3.9.0",
        "matplotlib>=3.8.0",
        "numpy>=1.26.0",
    ],
)