__version__ = '3.5.4' # Keep this on the first line so it's easy for __init__.py to grab.


from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="spinmob",
    version=__version__,
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
