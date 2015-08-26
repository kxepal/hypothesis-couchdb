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

import importlib
import os
from os.path import join
from setuptools import setup, find_packages

name = 'hypothesis-couchdb'

setup_dir = os.path.dirname(__file__)
mod = importlib.import_module('{}.version'.format(name.replace('-', '_')))
long_description = open(join(setup_dir, 'README.rst')).read().strip()

setup(
    name=name,
    version=mod.__version__,
    license='Apache 2',
    url='https://github.com/kxepal/hypothesis-couchdb',

    description='Hypothesis strategies for CouchDB',
    long_description=long_description,

    author='Alexander Shorin',
    author_email='kxepal@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        "Topic :: Software Development :: Testing",
    ],

    packages=find_packages(),
    test_suite='nose.collector',
    zip_safe=False,

    install_requires=[
        'hypothesis==1.11.0',
    ],
    extras_require={

    },
    tests_require=[
        'nose==1.3.7',
    ]
)
