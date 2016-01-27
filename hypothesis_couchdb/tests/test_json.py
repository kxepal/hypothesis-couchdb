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
import unittest

import hypothesis
import hypothesis.strategies as st

from hypothesis_couchdb import (
    json,
)


class JsonTestCase(unittest.TestCase):

    @hypothesis.given(json.nulls())
    def test_nulls(self, value):
        self.assertIsNone(value)
    
    @hypothesis.given(json.booleans())
    def test_booleans(self, value):
        self.assertIsInstance(value, bool)
    
    @hypothesis.given(json.numbers())
    def test_numbers(self, value):
        self.assertIsInstance(value, (int, float))
        self.assertFalse(math.isinf(value))
        self.assertFalse(math.isnan(value))

    @hypothesis.given(json.strings())
    def test_strings(self, value):
        self.assertIsInstance(value, str)

    @hypothesis.given(json.arrays(json.numbers()))
    def test_arrays(self, value):
        self.assertIsInstance(value, list)
        for item in value:
            self.test_numbers(item)

    @hypothesis.given(json.objects(json.numbers()))
    def test_objects(self, value):
        self.assertIsInstance(value, dict)
        for key, item in value.items():
            self.test_strings(key)
            self.test_numbers(item)

    @hypothesis.given(json.objects(
        required_fields={'test': json.nulls(),
                         'passed': json.strings()}))
    def test_objects_always_contains_required_fields(self, value):
        self.assertIsInstance(value, dict)
        self.assertEqual(set(value), {'test', 'passed'})
        self.test_nulls(value['test'])
        self.test_strings(value['passed'])

    def test_objects_may_contains_optional_fields(self):
        st = json.objects(optional_fields={'test': json.nulls()})
        self.assertEqual(hypothesis.find(st, lambda _: True), {})
        self.assertEqual(hypothesis.find(st, lambda v: 'test' in v),
                         {'test': None})

    def test_objects_with_required_and_optional_fields(self):
        obj = json.objects(required_fields={'always': st.just(True)},
                           optional_fields={'maybe': st.just(False)})
        self.assertEqual(hypothesis.find(obj, lambda _: True),
                         {'always': True})
        self.assertEqual(hypothesis.find(obj, lambda v: 'maybe' in v),
                         {'always': True, 'maybe': False})

    def test_objects_requires_any_fields_definition(self):
        with self.assertRaises(RuntimeError):
            json.objects()
    
    def test_objects_required_fields_must_have_string_keys(self):
        with self.assertRaises(TypeError):
            json.objects(required_fields={42: 24})

    def test_objects_optional_fields_must_have_string_keys(self):
        with self.assertRaises(TypeError):
            json.objects(optional_fields={42: 24})
