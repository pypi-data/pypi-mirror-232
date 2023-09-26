from setuptools import setup, find_packages

setup(
    name='neap',
    version='0.1.4',
    description='A Python wrapper for the NEAP API',
    author='Bard',
    author_email='bard@google.com',
    packages=find_packages(),
    install_requires=['requests'],
)