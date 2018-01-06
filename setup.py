import os
from setuptools import setup
# read __version__
filename = 'pytoolsMH/_version.py'; exec(compile(open(filename, "rb").read(), filename, 'exec'), globals(), locals())

# Utility function to read the README file.  Used for the long_description.  better to use the file than to put a raw string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pytoolsMH",
    version = __version__,
    author = "Mark Histed",
    author_email = "mhisted@gmail.com",
    description = ("misc personal Python utilities"),
    license = "none",
    keywords = "",
    url = "", 
    packages=['pytoolsMH'],
    package_dir={'pytoolsMH': 'pytoolsMH'},
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)

# 0.0.4: dataio
# 0.0.3: convert to package
# 0.0.2: add plotMH
# 0.0.1
