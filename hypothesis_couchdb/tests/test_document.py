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

import string
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


@hypothesis.given(document.id())
def test_id(value):
    assert isinstance(value, str)
    assert len(value) > 0


def test_id_with_bad_min_size():
    try:
        document.id(min_size=0)
    except ValueError:
        pass
    else:
        assert False, 'value error expected'

    try:
        document.id(min_size=None)
    except ValueError:
        pass
    else:
        assert False, 'value error expected'


@hypothesis.given(document.rev())
def test_rev(value):
    assert isinstance(value, str)
    assert len(value) > 0

    assert '-' in value
    num, hash = value.split('-', 1)

    assert num.isdigit()
    int(num)

    assert len(hash) == 32
    assert set(hash).issubset(string.hexdigits)


def test_deleted():
    value = hypothesis.find(document.deleted(), lambda _: True)
    assert value is False

    value = hypothesis.find(document.deleted(), lambda v: v)
    assert value is True


@hypothesis.given(document.revisions())
def test_revisions(value):
    assert isinstance(value, dict)
    assert set(value).issubset({'ids', 'start'})

    assert isinstance(value['start'], int)
    assert value['start'] > 0

    assert isinstance(value['ids'], list)
    assert len(value['ids']) == value['start']

    for num, hash in zip(range(value['start'], 0, -1), value['ids']):
        rev = str(num) + '-' + hash
        test_rev(rev)


@hypothesis.given(document.revs_info())
def test_revisions(value):
    assert isinstance(value, list)
    assert len(value) > 0

    for item in value:
        assert isinstance(item, dict)
        assert set(item).issubset({'rev', 'status'})

        test_rev(item['rev'])
        assert item['status'] in ('available', 'missing', 'deleted')


@hypothesis.given(document.local_seq())
def test_local_seq(value):
    assert isinstance(value, int)
    assert value > 0


@hypothesis.given(document.conflicts())
def test_conflicts(value):
    assert isinstance(value, list)
    assert len(value) >= 0

    for item in value:
        test_rev(item)


@hypothesis.given(document.deleted_conflicts())
def test_deleted_conflicts(value):
    assert isinstance(value, list)
    assert len(value) >= 0

    for item in value:
        test_rev(item)
