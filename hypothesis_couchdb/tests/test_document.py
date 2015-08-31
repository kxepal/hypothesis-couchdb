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

import hypothesis

from .. import document
from .. import json


def test_document():
    assert {} == hypothesis.find(document.documents(), lambda _: True)


def test_document_optional_fields():
    st = document.documents(optional_fields={'test': json.nulls()})
    assert {} == hypothesis.find(st, lambda _: True)
    assert {'test': None} == hypothesis.find(st, lambda v: 'test' in v)


def test_document_required_fields():
    st = document.documents(required_fields={'test': json.nulls()})
    assert {'test': None} == hypothesis.find(st, lambda _: True)
