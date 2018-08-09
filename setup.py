from setuptools import setup, find_packages
import cv

setup(
    name='cv',
    version=cv.VERSION,
    long_description='CV',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['flask']
)