from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mime-common',
    version='0.0.1',
    description='Some reusable libraries for properties, logging, console, etc',
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=[
        "console",
        "logg",
        "msmb",
    ],
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "blessings ~= 1.7",
        "pysmb ~= 1.2.9.1",
    ],
    extras_require={
        "dev": [
            "pytest>=3.7",
        ],
    },
    url="https://www.vegvesen.no",
    author="Bjørne Malmanger",
    author_email="bjorne.malmanger@vegvesen.no",
)
