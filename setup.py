from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="pyopenadr",
      version="0.2.2",
      description="Python library for dealing with OpenADR",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://git.finetuned.nl/stan/pyopenadr",
      packages=['pyopenadr', 'pyopenadr.service'],
      include_package_data=True,
      install_requires=['xmltodict', 'responder', 'apscheduler', 'uvloop==0.12'])
