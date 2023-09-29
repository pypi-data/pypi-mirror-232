from setuptools import setup, find_packages

setup(
    name="hello-pypi-tyronexj",
    use_scm_version=True,
    packages=find_packages(),
    setup_requires=["setuptools_scm"],
    description="A simple greeting package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jie Xu",
    author_email="tyronexj@gmail.com",
    url="https://github.com/tyronexj/hello-pypi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
