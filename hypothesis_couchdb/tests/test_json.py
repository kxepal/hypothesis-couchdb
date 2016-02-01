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

import math
import unittest

import hypothesis
from hypothesis.errors import (
    NoSuchExample,
)

from hypothesis_couchdb import (
    json,
)


class JsonTestCase(unittest.TestCase):

    def test_nulls(self):
        st = json.nulls()
        value = hypothesis.find(st, lambda _: True)
        self.assertIsNone(value)

    def test_booleans(self):
        st = json.booleans()
        value = hypothesis.find(st, lambda _: True)
        self.assertIsInstance(value, bool)
        self.assertFalse(value)
    
    @hypothesis.given(json.numbers())
    def test_numbers(self, value):
        self.check_number(value)

    def test_strings(self):
        st = json.strings()
        value = hypothesis.find(st, lambda _: True)
        self.assertIsInstance(value, str)
        self.assertFalse('')

    def test_arrays(self):
        st = json.arrays(json.numbers())
        value = hypothesis.find(st, lambda _: True)
        self.assertIsInstance(value, list)
        self.assertEqual(value, [])

    def test_objects(self):
        st = json.objects(json.values())
        value = hypothesis.find(st, lambda _: True)
        self.assertIsInstance(value, dict)
        self.assertEqual(value, {})

    def test_objects_always_contains_required_fields(self):
        st = json.objects(required_fields={'test': json.nulls()})
        with self.assertRaises(NoSuchExample):
            hypothesis.find(st, lambda v: 'test' not in v)

    def test_objects_may_contains_optional_fields(self):
        st = json.objects(optional_fields={'test': json.nulls()})
        self.assertEqual(hypothesis.find(st, lambda v: 'test' not in v),
                         {})
        self.assertEqual(hypothesis.find(st, lambda v: 'test' in v),
                         {'test': None})

    def test_objects_with_required_and_optional_fields(self):
        st = json.objects(required_fields={'always': json.booleans()},
                          optional_fields={'maybe': json.booleans()})
        self.assertEqual(hypothesis.find(
            st,
            lambda v: v['always'] and 'maybe' not in v),
            {'always': True})
        self.assertEqual(hypothesis.find(
            st,
            lambda v: v['always'] and 'maybe' in v),
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

    def check_number(self, value):
        self.assertIsInstance(value, (int, float))
        self.assertFalse(math.isinf(value))
        self.assertFalse(math.isnan(value))
