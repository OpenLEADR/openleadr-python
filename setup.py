# SPDX-License-Identifier: Apache-2.0

# Copyright 2020 Contributors to OpenLEADR

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup
import os

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'VERSION')) as file:
    VERSION = file.read().strip()

setup(name='openleadr',
      version=VERSION,
      description='Python library for dealing with OpenADR',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://openleadr.elaad.io',
      packages=['openleadr', 'openleadr.service'],
      include_package_data=True,
      install_requires=['xmltodict', 'aiohttp', 'apscheduler', 'jinja2', 'signxml-openadr==2.9.1'],
      entry_points={'console_scripts': ['fingerprint = openleadr.fingerprint:show_fingerprint']})
