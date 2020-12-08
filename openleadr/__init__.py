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

# flake8: noqa

import logging
from .client import OpenADRClient
from .server import OpenADRServer


def enable_default_logging(level=logging.INFO):
    """
    Turn on logging to stdout.
    :param level integer: The logging level you wish to use.
                          Defaults to logging.INFO.
    """
    import sys
    import logging
    logger = logging.getLogger('openleadr')
    handler_names = [handler.name for handler in logger.handlers]
    if 'openleadr_default_handler' not in handler_names:
        logger.setLevel(level)
        logging_handler = logging.StreamHandler(stream=sys.stdout)
        logging_handler.set_name('openleadr_default_handler')
        logging_handler.setLevel(logging.DEBUG)
        logger.addHandler(logging_handler)
