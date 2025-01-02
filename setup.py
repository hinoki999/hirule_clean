from setuptools import setup, find_packages

setup(
    name="trading_system",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pytest",
        "pytest-asyncio"
    ]
)


