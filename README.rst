==================
hypothesis-couchdb
==================

:status: alpha
:license: `Apache 2`_

**hypothesis-couchdb** is a set of `Hypothesis`_ strategies for testing
CouchDB-related projects and tools.


hypothesis_couchdb.example_db
=============================

Hypothesis has `example database`_ feature that stores information about found
bugs from previous test runs in order to reuse them in further checks to make
sure that these bugs are really fixed.

This module provides special backend to store these examples in CouchDB.
To start use it, you need to update Hypothesis settings::

  import hypothesis
  from hypothesis_couchdb.example_db import CouchExampleDB

  # default database url is http://localhost:5984/hypothesis
  settings = hypothesis.setting(database=CouchExampleDB()

  # now you can either register it as own profile to use it global-wide
  hypothesis.settings.register_profile('couchdb', settings)
  hypothesis.settings.load_profile('couchdb')

  # or use it in-place as decorator or context manager in your tests.
  # See Hypothesis documentation about settings and profiles for more.

The `CouchExampleDB` ensures that database is exists and design document too,
so for initial setup may require administrator privileges in order to create
these objects on server.

If you don't want to share with `CouchExampleDB` your admin password (sure you
don't!) then in order to make everything works you need to make two things:

- Create database::

    curl -X PUT http://localhost:5984/hypothesis --user admin

- Create design document (see ``hypothesis_couchdb/example_db.py`` for sources)::

    curl -X PUT http://localhost:5984/hypothesis/_design/hypothesis --user admin -d '{"_id": "_design/hypothesis", "views": { "by_key": {"map": "function(doc){ emit(doc.key, doc.value) }", "reduce": "_count"}}}'

`CouchExampleDB` will not require admin privileges anymore to setup valid
context. Additionally, you may want to have special user that hypothesis will
use to store examples in the target database. To make auth works, specify
credentials on `CouchExampleDB` init like::

  CouchExampleDB('https://couchdb.intranet/hypothesis',
                 basic_auth_credentials=('hypothesis', 'password'))

Make sure you pass authentication over secure HTTPS connection!

The `_design/hypothesis` document provides basic grouping and statistic over
stored examples. You may browse it with Futon/Fauxton CouchDB web UI.

What's the profit from all of this?

Since all the examples are stored on the server, your coworkers and other
developers may share examples in order to reproduce the bugs locally. You may
share your examples by using CouchDB Replication feature with your friends with
easy.


hypothesis_couchdb.json
=======================

CouchDB speaks with JSON over HTTP API, so we need to be able produce suitable
for JSON serialization values. This module provides set of strategies that
completes that goal, producing values for all JSON types:

- ``nulls``: just ``None`` values all the time;
- ``booleans``: generates ``True`` and ``False`` values;
- ``numbers``: generates ``int`` and finite ``float`` values;
- ``strings``: generates ``str`` values;
- ``arrays``: generates ``list``'s of given elements;
- ``objects``: generates ``dict``'s of given elements, may have optional and
  required fields;
- ``values``: union of all JSON strategies that also produces nested
  arrays and objects;


hypothesis_couchdb.document
===========================

Contains strategies to generate CouchDB various documents:

- ``documents``: semantic wrapper around ``json.objects`` to generate JSON
  documents;

Additionally provides strategies to generate valid values for special fields:

- ``id``
- ``rev``
- ``deleted``
- ``revisions``
- ``revs_info``
- ``local_seq``
- ``conflicts``
- ``deleted_conflicts``

CouchDB has these fields prefixed with underscore ``_`` character while
strategies are not (leading underscore has special mean in Python).


.. _Apache 2: http://www.apache.org/licenses/LICENSE-2.0.html
.. _Hypothesis: https://github.com/DRMacIver/hypothesis
.. _example database: http://hypothesis.readthedocs.org/en/master/database.html
