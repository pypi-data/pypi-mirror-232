from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'nester-test-abcxyz',
    version= '1.0.0',
    py_modules= ['nester'],
    author='Long Nguyen',
    author_email='test@gmail.com',
    description="Im testing a module"
)