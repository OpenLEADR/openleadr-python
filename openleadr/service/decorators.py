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

def handler(message_type):
    """
    Decorator to mark a method as the handler for a specific message type.
    """
    def _actual_decorator(decorated_function):
        decorated_function.__message_type__ = message_type
        return decorated_function
    return _actual_decorator


def service(service_name):
    """
    Decorator to mark a class as an OpenADR Service for a specific endpoint.
    """
    def _actual_decorator(decorated_function):
        decorated_function.__service_name__ = service_name
        return decorated_function
    return _actual_decorator
