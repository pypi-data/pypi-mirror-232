"""importaciones"""
from pathlib import Path
import setuptools

path = Path("README.md").read_text
setuptools.setup(
    name="primeraquete",
    version="0.0.1",
    long_description="Primera prueba de subida",
    packages=setuptools.find_packages(
        exclude=["mocks", "tests"]
    )
)
