# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

from . import json


__all__ = (
    'documents',
)


def documents(required_fields=None,
              optional_fields=None,
              random_fields=json.values()):
    """Generates various JSON documents as `dict` instances."""
    return json.objects(required_fields=required_fields,
                        optional_fields=optional_fields,
                        elements=random_fields)
