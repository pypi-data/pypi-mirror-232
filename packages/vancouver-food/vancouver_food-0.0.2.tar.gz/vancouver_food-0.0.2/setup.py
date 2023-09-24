from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.2'
DESCRIPTION = 'Help you choose one food in Vancouver.'
LONG_DESCRIPTION = 'Yes, it is help you choose one food in Vancouver.'

# Setting up
setup(
    name="vancouver_food",
    version=VERSION,
    author="LeviLiao",
    author_email="<dlnx38@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'vancouver', 'random'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
