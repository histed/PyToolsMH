import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "PytoolsMH",
    version = "0.0.2",
    author = "Mark Histed",
    author_email = "mhisted@gmail.com",
    description = ("A miscellaneous set of python utilities, mainly for neural data analysis"),
    license = "none",
    keywords = "",
    url = "", 
    py_modules=['behaviorLibraryMH', 'mathMH', 'windowsTimingMH', 'macTimingMH', 'crossPlatformMH', 'filesStreamsMH', 'plotMH', 'containersMH'],
    #packages=['an_example_pypi_project', 'tests'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)

# 0.0.2: add plotMH
# 0.0.1
