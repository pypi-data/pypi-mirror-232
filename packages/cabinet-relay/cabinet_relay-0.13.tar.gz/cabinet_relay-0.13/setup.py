

from setuptools import setup, find_packages

setup(
    name='cabinet_relay',
    version='0.13',
    description='cabinet cabinet_relay',
    author='hewitt',
    author_email='pypi_user@163.com',
    license='MIT',
    packages=find_packages(),
    install_requires=['uModbus', 'pyserial'],  # List all dependencies here
)
