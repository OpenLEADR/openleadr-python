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

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(name='openleadr',
      version='0.5.26',
      description='Python3 library for building OpenADR Clients (VENs) and Servers (VTNs)',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://openleadr.org',
      project_urls={'GitHub': 'https://github.com/openleadr/openleadr-python',
                    'Documentation': 'https://openleadr.org/docs'},
      packages=['openleadr', 'openleadr.service'],
      python_requires='>=3.7.0',
      include_package_data=True,
      install_requires=['xmltodict', 'aiohttp', 'apscheduler', 'jinja2', 'signxml-openadr==2.9.1'],
      entry_points={'console_scripts': ['fingerprint = openleadr.fingerprint:show_fingerprint']})
