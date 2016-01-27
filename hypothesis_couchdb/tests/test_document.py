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
import unittest

from hypothesis_couchdb import (
    document,
    json,
)


class DocumentTestCase(unittest.TestCase):

    def test_document(self):
        self.assertEqual(hypothesis.find(document.documents(), lambda _: True),
                         {})

    def test_document_optional_fields(self):
        st = document.documents(optional_fields={'test': json.nulls()})
        self.assertEqual(hypothesis.find(st, lambda _: True),
                         {})
        self.assertEqual(hypothesis.find(st, lambda v: 'test' in v),
                         {'test': None})

    def test_document_required_fields(self):
        st = document.documents(required_fields={'test': json.nulls()})
        self.assertEqual(hypothesis.find(st, lambda _: True), {'test': None})

    @hypothesis.given(document.id())
    def test_id(self, value):
        self.assertIsInstance(value, str)
        self.assertGreater(len(value), 0)

    def test_id_with_bad_min_size(self):
        with self.assertRaises(ValueError):
            document.id(min_size=0)

        with self.assertRaises(ValueError):
            document.id(min_size=None)

    @hypothesis.given(document.rev())
    def test_rev(self, value):
        self.check_rev(value)

    def test_deleted(self):
        self.assertFalse(hypothesis.find(document.deleted(), lambda _: True))
        self.assertTrue(hypothesis.find(document.deleted(), lambda v: v))

    @hypothesis.given(document.revisions())
    def test_revisions(self, value):
        self.assertIsInstance(value, dict)
        self.assertTrue(set(value).issubset({'ids', 'start'}))

        self.assertIsInstance(value['start'], int)
        self.assertGreater(value['start'], 0)

        self.assertIsInstance(value['ids'], list)
        self.assertEqual(len(value['ids']), value['start'])

        for num, hash in zip(range(value['start'], 0, -1), value['ids']):
            rev = str(num) + '-' + hash
            self.check_rev(rev)

    @hypothesis.given(document.revs_info())
    def test_revs_info(self, value):
        self.assertIsInstance(value, list)
        self.assertGreater(len(value), 0)

        for item in value:
            self.assertIsInstance(item, dict)
            self.assertTrue(set(item).issubset({'rev', 'status'}))

            self.check_rev(item['rev'])
            self.assertIn(item['status'], {'available', 'missing', 'deleted'})

    @hypothesis.given(document.local_seq())
    def test_local_seq(self, value):
        self.assertIsInstance(value, int)
        self.assertGreater(value, 0)

    @hypothesis.given(document.conflicts())
    def test_conflicts(self, value):
        self.assertIsInstance(value, list)
        self.assertGreaterEqual(len(value), 0)

        for item in value:
            self.check_rev(item)

    @hypothesis.given(document.deleted_conflicts())
    def test_deleted_conflicts(self, value):
        self.assertIsInstance(value, list)
        self.assertGreaterEqual(len(value), 0)

        for item in value:
            self.check_rev(item)

    def check_rev(self, value):
        self.assertIsInstance(value, str)
        self.assertGreater(len(value), 0)

        self.assertIn('-', value)
        num, hash = value.split('-', 1)

        self.assertTrue(num.isdigit())
        int(num)

        self.assertEqual(len(hash), 32)
        self.assertTrue(set(hash).issubset(string.hexdigits))
