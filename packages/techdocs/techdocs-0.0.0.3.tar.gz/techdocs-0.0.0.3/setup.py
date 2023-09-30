import setuptools
from setuptools import setup

setup(
	name='techdocs',
	version='0.0.0.3',
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'techdocs=techdocs.cli:main',
            'techdocs run tests=techdocs.tests.test_get_version.TestGetVersion.test_get_version'
        ]
    },

    packages=setuptools.find_packages(exclude=['tests']),
)