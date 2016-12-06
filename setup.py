"""Eny command setup"""

from setuptools import setup, find_packages
from eny import __version__

setup(
    name='eny',
    py_modules=['eny'],
    version=__version__,
    description='Tool for eny button',
    url='https://github.com/quantum-inc/eny-devkit',
    author='@asus4',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': ['eny = eny:main'],
    }
)
