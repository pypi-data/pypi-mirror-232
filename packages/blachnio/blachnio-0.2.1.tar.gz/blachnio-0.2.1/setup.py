from setuptools import setup, find_packages

setup(
    name='blachnio',
    version='v0.2.1',
    description='Artur Tools for everyday operations',
    author='Artur B',
    author_email='blachnio.artur@gmail.com',
    url='https://github.com/ArturBlachnio/ArturBlachnio.git',
    packages=find_packages(),
    install_requires=[],
)

# To publish package:
# Create setup.py file in root (current file) and put proper name and version
# python setup.py sdist
# pip install twine (if not done)
# twine upload sist/* - set as user __token__ and as password API-token
# (check file token.txt or create new on pypi/account settings/add api token
