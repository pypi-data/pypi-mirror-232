# Hello PyPI

This is a simple package to demonstrate publishing a package to PyPI.

# Steps

- 打包代码

```bash
pip install setuptools wheel twine
python setup.py sdist bdist_wheel
```

- 上传到 PyPI

```bash
twine upload dist/*
```

# Misc
