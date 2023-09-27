from setuptools import setup, find_packages

setup(
    name='dipeak_login_client',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'json',
        'requests>=2.0.0',
    ],
)