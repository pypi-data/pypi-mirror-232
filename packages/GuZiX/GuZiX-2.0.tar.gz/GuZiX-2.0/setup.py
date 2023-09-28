from setuptools import setup, find_packages
import codecs
import os

VERSION = '2.0'
DESCRIPTION = 'intresting stuff, and more'
LONG_DESCRIPTION = ''

setup(
    name="GuZiX",
    version=VERSION,
    author="chanakya ram sai illa",
    author_email="chanakyaramsaiilla@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['GIZ'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
