from setuptools import setup, find_packages

setup(
    name="appocr",  # Name of your package
    version="0.1",
    packages=find_packages(include=["app"]),  # This only includes the app folder
)