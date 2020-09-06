from setuptools import setup, find_packages
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="spinmob",
    version=get_version("src/spinmob/__init__.py"),
    author="Jack Sankey",
    author_email="jack.sankey@gmail.com",
    description="Data handling, plotting, analysis, and GUI building for scientific labs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Spinmob/spinmob",
    project_urls={
        "Source Code": "https://github.com/Spinmob/spinmob",
        "Bug Tracker": "https://github.com/Spinmob/spinmob/issues",
        "Wiki": "https://github.com/Spinmob/spinmob/wiki",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires='>=3,<4',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    install_requires=[
        "scipy",
        "matplotlib",
        "lmfit",
        "pyqtgraph>=0.11,<1",
    ],
)
