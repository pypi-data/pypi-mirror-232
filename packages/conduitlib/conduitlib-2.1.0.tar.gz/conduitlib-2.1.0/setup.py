# Copyright 2021 Software Factory Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    readme = f.read()

with open(os.path.join(here, 'requirements.txt')) as file:
    requires = file.readlines()

with open(os.path.join(here, 'requirements-dev.txt')) as file:
    dev_requires = file.readlines()

setup(
    name='conduitlib',
    version='2.1.0',
    description='A library containing common elements to Conduit and Conduit plugins.',
    long_description=readme,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
    ],
    author='Eric Frechette',
    author_email='eric@softwarefactorylabs.com',
    # url='',
    # keywords='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require={
        'dev': dev_requires,
    },
    python_requires='>=3.8,<4',
)
