from setuptools import setup

setup(
    name='neap',
    version='0.1.2',
    description='A Python wrapper for the NEAP API',
    author='Bard',
    author_email='bard@google.com',
    packages=['neap'],
    py_modules=['neap.ReportCard'],
    install_requires=['requests'],
)