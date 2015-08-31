==================
hypothesis-couchdb
==================

:status: alpha
:license: `Apache 2`_

**hypothesis-couchdb** is a set of `Hypothesis`_ strategies for testing
CouchDB-related projects and tools.


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


.. _Apache 2: http://www.apache.org/licenses/LICENSE-2.0.html
.. _Hypothesis: https://github.com/DRMacIver/hypothesis
