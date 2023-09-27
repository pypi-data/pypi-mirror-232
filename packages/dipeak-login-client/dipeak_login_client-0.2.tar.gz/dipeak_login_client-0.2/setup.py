from setuptools import setup, find_packages

setup(
    name='dipeak_login_client',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'requests>=2.0.0',
    ],
)