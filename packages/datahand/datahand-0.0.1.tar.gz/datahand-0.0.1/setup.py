import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datahand",
    version="0.0.1",
    author="cnavarreteliz",
    author_email="cnavarreteliz@gmail.com",
    description="DataHandler is a collection of algorithms to read and handle data for research (e.g., Web of Science, USPTO) in Python.",
    license_files=("LICENSE.md",),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cnavarreteliz/polapy",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
)
