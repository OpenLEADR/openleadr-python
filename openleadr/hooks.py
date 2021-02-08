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

import asyncio

HOOKS = {'before_parse': [],
         'before_handle': [],
         'after_handle': [],
         'before_respond': []}


def register(hook_point, callback):
    """
    Call a hook
    """
    if hook_point not in HOOKS:
        raise ValueError(f"""The hook_point must be one of '{', '.join(HOOKS.keys())}', """
                         f"""you provided '{hook_point}'""")
    HOOKS[hook_point].append(callback)


def call(hook_point, *args, **kwargs):
    loop = asyncio.get_event_loop()
    for hook in HOOKS.get(hook_point, []):
        loop.create_task(hook(*args, **kwargs))
