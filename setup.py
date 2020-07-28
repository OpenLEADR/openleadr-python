from setuptools import setup
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'VERSION')) as file:
    VERSION = file.read().strip()

setup(name="pyopenadr",
      version=VERSION,
      description="Python library for dealing with OpenADR",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://git.finetuned.nl/stan/pyopenadr",
      packages=['pyopenadr', 'pyopenadr.service'],
      include_package_data=True,
      install_requires=['xmltodict', 'aiohttp', 'apscheduler', 'jinja2'])
