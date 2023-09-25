from setuptools import find_packages, setup

setup(packages=find_packages())

# Build package:
#   Increase version number in pyproject.toml
#   delete dist folder, coziepy.egg-info folder
#   python -m build

# Upload package to pypi:
#   python -m twine upload --repository testpypi dist/*
#   python -m twine upload --repository pypi dist/*