from setuptools import setup, find_packages

setup(
    name='blachnio',
    version='v0.2.0',
    description='Artur Tools for everyday operations',
    author='Artur B',
    author_email='blachnio.artur@gmail.com',
    url='https://github.com/ArturBlachnio/ArturBlachnio.git',
    packages=find_packages(),
    install_requires=[],
)

# To publish packege
# Create setup.py file in root (current file) and put proper name and version
# python setup.py sdist
# pip install twine (if not done)
# twin upload sist/*
