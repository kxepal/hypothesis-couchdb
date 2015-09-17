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

import base64
import json
import urllib.parse
import urllib.request
import uuid

from hypothesis.database import ExampleDatabase
from hypothesis.database.backend import Backend
from hypothesis.database.formats import Format


__all__ = (
    'CouchExampleDB',
    'BasicFormat',
    'CouchBackend',
)


class CouchExampleDB(ExampleDatabase):
    def __init__(self,
                 dburl: str='http://localhost:5984/hypothesis',
                 basic_auth_credentials: tuple=None):
        backend = CouchBackend(dburl, basic_auth_credentials)
        format = BasicFormat()
        super().__init__(backend, format)


class BasicFormat(Format):
    def data_type(self):
        return list

    def serialize_basic(self, value: list):
        return value

    def deserialize_data(self, data: list):
        return data


class CouchBackend(Backend):
    def __init__(self, dburl: str, basic_auth_credentials: tuple=None):
        assert dburl.startswith(('http://', 'https://'))
        self.url = dburl
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        if basic_auth_credentials:
            self.headers['Authorization'] = basic_auth_header(
                *basic_auth_credentials)
        self._ensured_db_exists = False
        self._ensured_ddoc_exists = False

    def ddoc(self) -> dict:
        return {
            '_id': '_design/hypothesis',
            'validate_doc_update': '''
function(newdoc, olddoc){
  var assert = function(cond) {
    if(!cond) {
      throw({forbidden: 'bad doc'})
    }
  }

  if(newdoc._deleted === true){
    return
  }

  if(newdoc.type !== 'example'){
    return
  }

  assert(isArray(newdoc.key));
  assert(isArray(newdoc.value));
}''',
            'views': {
                'by_key': {
                    'map': 'function(doc){ emit(doc.key, doc.value) }',
                    'reduce': '_count'
                }
            },
            'version': 2
        }

    def data_type(self):
        return list

    def save(self, key: str, value: list):
        self._ensure_setup()

        request(
            method='PUT',
            url=url(self.url, str(uuid.uuid4())),
            data=json.dumps({'key': format_key(key),
                             'value': value,
                             'type': 'example'}).encode(),
            headers=self.headers)

    def delete(self, key: str, value: list):
        self._ensure_setup()

        result = request(
            method='GET',
            url=url(self.url, '_design', 'hypothesis', '_view', 'by_key',
                    reduce='false',
                    include_docs='true',
                    key=json.dumps(format_key(key))),
            headers=self.headers)

        for row in result['rows']:
            if row['value'] != value:
                continue
            request(
                method='DELETE',
                url=url(self.url, row['id'],
                        rev=row['doc']['_rev']),
                headers=self.headers)

    def fetch(self, key: str) -> list:
        self._ensure_setup()

        result = request(
            method='GET',
            url=url(self.url, '_design', 'hypothesis', '_view', 'by_key',
                    reduce='false',
                    key=json.dumps(format_key(key))),
            headers=self.headers)

        return [row['value'] for row in result['rows']]

    def close(self):
        pass

    def _ensure_setup(self):
        self._ensure_db_exists()
        self._ensure_ddoc_exists()

    def _ensure_db_exists(self):
        if self._ensured_db_exists:
            return

        try:
            request('GET', url(self.url), headers=self.headers)
        except urllib.request.HTTPError as err:
            if err.code != 404:
                raise
            request('PUT', url(self.url), headers=self.headers)

        self._ensured_db_exists = True

    def _ensure_ddoc_exists(self):
        if self._ensured_ddoc_exists:
            return

        try:
            remote_ddoc = request('GET',
                                  url(self.url, '_design', 'hypothesis'),
                                  headers=self.headers)
        except urllib.request.HTTPError as err:
            if err.code != 404:
                raise

            request('PUT',
                    url(self.url, '_design', 'hypothesis'),
                    data=json.dumps(self.ddoc()).encode(),
                    headers=self.headers)
        else:
            local_ddoc = self.ddoc()
            if local_ddoc['version'] != remote_ddoc.get('version', 0):
                ddoc = self.ddoc()
                ddoc['_rev'] = remote_ddoc['_rev']
                request('PUT',
                        url(self.url, '_design', 'hypothesis'),
                        data=json.dumps(ddoc).encode(),
                        headers=self.headers)

        self._ensured_ddoc_exists = True


def quote(segment: str, safe: str='') -> str:
    return urllib.parse.quote(segment, safe=safe)


def url(base_url: str, *path: str, **params) -> str:
    rval = base_url
    if path:
        rval += '/' + '/'.join(map(quote, path or []))
    if params:
        rval += '?' + urllib.parse.urlencode(params)
    return rval


def request(method: str, url: str, headers: dict, data: bytes=None) -> dict:
    req = urllib.request.Request(url, method=method, data=data, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))


def basic_auth_header(username: str, password: str) -> str:
    return 'Basic %s' % (
        base64.b64encode(
            ':'.join((username, password)).encode('utf-8')
        ).decode('ascii')
    )


def format_key(key: str) -> list:
    return key.split('.')
