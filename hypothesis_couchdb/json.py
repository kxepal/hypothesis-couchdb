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
from functools import reduce

import hypothesis.strategies as st


__all__ = (
    'nulls',
    'booleans',
    'numbers',
    'strings',
    'arrays',
    'objects',
    'values'
)


def nulls():
    """Generates ``None`` values.

    Basically is a proxy to ``hypothesis.strategies.none()``.
    """
    return st.none()


def booleans():
    """Generates instances of ``bool`` type.

    Basically is a proxy to ``hypothesis.strategies.booleans()``.
    """
    return st.booleans()


def numbers(min_value=None, max_value=None):
    """Generates instances of ``int`` and ``float`` types, except special values
    like ``inf`` and `NaN`.

    `min_value` and `max_value` arguments are applied to both
    ``hypothesis.strategies.integers`` and ``hypothesis.strategies.floats``
     strategies which are used under hood.
    """
    min_value_int = int(min_value) if min_value is not None else None
    max_value_int = int(max_value) if max_value is not None else None
    return (st.integers(min_value=min_value_int, max_value=max_value_int)
            | st.floats(min_value=min_value,
                        max_value=max_value).filter(math.isfinite))


def strings(*, alphabet=None, min_size=None, average_size=None, max_size=None):
    """Generates instances of ``str`` type.

    Basically is a proxy to ``hypothesis.strategies.text()``.
    """
    return st.text(alphabet=alphabet,
                   min_size=min_size,
                   average_size=average_size,
                   max_size=max_size)


def arrays(elements, *,
           min_size=None,
           average_size=None,
           max_size=None,
           unique_by=None):
    """Returns a strategy that generates lists of specified `elements`.
    The `elements` must be valid Hypothesis strategy.

    While choice of elements left here for user side, it's not recommended to
    use anything that produces non-serializable to JSON values.

    Basically is a proxy to ``hypothesis.strategies.lists()``.
    """
    return st.lists(elements,
                    min_size=min_size,
                    average_size=average_size,
                    max_size=max_size,
                    unique_by=unique_by)


def objects(elements=None, *,
            required_fields=None,
            optional_fields=None,
            min_size=None,
            average_size=None,
            max_size=None):
    """Returns a strategy that generates dicts of specified `elements`.

    The `elements` must be valid Hypothesis strategy. The keys are ensured to
    be string only as JSON requires.

    While choice of `elements` left here for user side, it's not recommended to
    use anything that produces non-serializable to JSON values.

    Additionally, it's possible to ensure that some fields with values generated
    by a certain strategy are always exists (`required_fields`) or just optional
    (`optional_fields`).
    """
    def check_type(varname, var, expected):
        if not isinstance(var, expected):
            raise TypeError('{} must be {}, got {}'.format(
                varname, expected, type(var)))

    acc = []
    if required_fields:
        check_type('required_fields', required_fields, dict)
        for key in required_fields:
            check_type('required field name', key, str)
        acc.append(st.fixed_dictionaries(required_fields))

    if optional_fields:
        check_type('optional_fields', optional_fields, dict)
        for key in optional_fields:
            check_type('optional field name', key, str)
        acc.append(st.sets(st.sampled_from(optional_fields)).flatmap(
            lambda keys: st.fixed_dictionaries({key: optional_fields[key]
                                                for key in keys})))
    if elements:
        acc.append(st.dictionaries(strings(), elements,
                                   min_size=min_size,
                                   average_size=average_size,
                                   max_size=max_size))

    if not acc:
        raise RuntimeError('object must have any strategy for fields')

    return st.tuples(*reversed(acc)).map(
        lambda s: reduce(lambda a, d: dict(a, **d), s))


def values():
    """Returns a strategy that unifies all strategies that produced valid JSON
    serializable values."""
    simple_values = nulls() | booleans() | numbers() | strings()
    return (simple_values
            | st.recursive(simple_values,  # noqa
                           lambda children: arrays(children)
                                            | objects(children)))  # noqa