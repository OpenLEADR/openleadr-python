from setuptools import setup

setup(name="pyopenadr",
      version="0.1.2",
      description="Python library for dealing with OpenADR",
      packages=['pyopenadr', 'pyopenadr.service'],
      include_package_data=True,
      install_requires=['xmltodict', 'responder', 'apscheduler'])
