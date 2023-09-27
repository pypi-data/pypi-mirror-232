from setuptools import setup, find_packages

setup(
    name='mmc-jwt-auth',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'djangorestframework',
        'djangorestframework-simplejwt',
    ],
)
