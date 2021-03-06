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

import hypothesis.strategies as st

from . import json


__all__ = (
    'documents',
    'id',
    'rev',
    'deleted',
    'local_seq',
)


HEXDIGITS = '1234567890abcdef'


def documents(required_fields=None,
              optional_fields=None,
              random_fields=json.values()):
    """Generates various JSON documents as `dict` instances."""
    return json.objects(required_fields=required_fields,
                        optional_fields=optional_fields,
                        elements=random_fields)


def id(*, alphabet=None, min_size=1, average_size=None, max_size=None):
    """Generates document ids.

    This strategy doesn't ensures that produced values are always unique.
    """
    if min_size is None or min_size < 1:
        raise ValueError('Document ID must not be empty')
    return json.strings(alphabet=alphabet,
                        min_size=min_size,
                        average_size=average_size,
                        max_size=max_size)


def rev():
    """Generates document revisions."""
    return st.tuples(rev_pos(), rev_id()).map('-'.join)


def deleted():
    """Generates values for `_deleted` field."""
    return json.booleans()


def local_seq():
    """Generates values for `_local_seq` field."""
    return st.integers(min_value=1)


def rev_pos():
    return st.integers(min_value=0).map(str)


def rev_id():
    return json.strings(alphabet=HEXDIGITS, min_size=32, max_size=32)
