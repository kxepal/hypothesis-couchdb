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

import functools
import math

import hypothesis
import hypothesis.strategies as st

from .. import json


def ensure_serializable(func):
    import json

    @functools.wraps(func)
    def wrapper(value):
        func(value)
        assert value == json.loads(json.dumps(value)), value

    return wrapper


@hypothesis.given(json.nulls())
@ensure_serializable
def test_nulls(value):
    assert value is None


@hypothesis.given(json.booleans())
@ensure_serializable
def test_booleans(value):
    assert value is True or value is False, value


@hypothesis.given(json.numbers())
@ensure_serializable
def test_numbers(value):
    assert isinstance(value, (int, float))
    assert not math.isinf(value)
    assert not math.isnan(value)


@hypothesis.given(json.strings())
@ensure_serializable
def test_strings(value):
    assert isinstance(value, str)


@hypothesis.given(json.arrays(json.numbers()))
@ensure_serializable
def test_arrays(value):
    assert isinstance(value, list)
    for item in value:
        test_numbers(item)


@hypothesis.given(json.objects(json.numbers()))
@ensure_serializable
def test_objects(value):
    assert isinstance(value, dict)
    for key, item in value.items():
        test_strings(key)
        test_numbers(item)


@hypothesis.given(json.objects(required_fields={'test': json.nulls(),
                                                'passed': json.strings()}))
def test_objects_always_contains_required_fields(value):
    assert isinstance(value, dict)
    assert set(value) == {'test', 'passed'}
    test_nulls(value['test'])
    test_strings(value['passed'])


def test_objects_may_contains_optional_fields():
    st = json.objects(optional_fields={'test': json.nulls()})
    assert {} == hypothesis.find(st, lambda _: True)
    assert {'test': None} == hypothesis.find(st, lambda v: 'test' in v)


def test_objects_with_required_and_optional_fields():
    obj = json.objects(required_fields={'always': st.just(True)},
                       optional_fields={'maybe': st.just(False)})
    assert {'always': True} == hypothesis.find(obj, lambda _: True)
    assert {'always': True,
            'maybe': False} == hypothesis.find(obj, lambda v: 'maybe' in v)


def test_objects_requires_any_fields_definition():
    try:
        json.objects()
    except RuntimeError:
        pass
    else:
        assert False, 'exception expected'


def test_objects_required_fields_must_have_string_keys():
    try:
        json.objects(required_fields={42: 24})
    except TypeError:
        pass
    else:
        assert False, 'exception expected'


def test_objects_optional_fields_must_have_string_keys():
    try:
        json.objects(optional_fields={42: 24})
    except TypeError:
        pass
    else:
        assert False, 'exception expected'
