#########################################################################
# Copyright 2011 Cloud Sidekick
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################

import os
import setuptools

binscripts = []
for f in os.listdir("bin"):
    binscripts.append("bin/" + f)

setuptools.setup(
    name='cskclient',
    version='1.33',
    description='Cloud Sidekick Client Tools',
    license='Apache License (2.0)',
    author='Patrick Dunnigan',
    author_email='patrick.dunnigan@cloudsidekick.com',
    url='https://github.com/cloudsidekick/client',
    packages=setuptools.find_packages(exclude=['bin']),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: No Input/Output (Daemon)',
    ],
    scripts=binscripts,
    py_modules=[])

