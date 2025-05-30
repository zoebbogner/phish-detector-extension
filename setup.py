# setup.py
from setuptools import setup, find_packages

setup(
    name="phishing_crawler",
    version="0.1",
    packages=find_packages(),  # will pick up your models/ and phishing_crawler/ dirs
)