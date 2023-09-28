from setuptools import setup, find_packages

setup(
    name="hello-pypi-tyronexj",
    version="0.1",
    packages=find_packages(),
    description="A simple greeting package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/tyronexj/hello-pypi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
