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

import cskcommands.cmd
from cskcommands.param import Param

class TagObject(cskcommands.cmd.CSKCommand):

    Description = 'Applies a security Tag to an object.'
    API = 'add_object_tag'
    Examples = '''
_To tag a task using task uuid and the task object type_
    
    cato-tag-object -t "development" -o "7f17e600-794f-11e3-bb4c-c8bcc89d4845" -y 3
'''
    Options = [Param(name='tag', short_name='t', long_name='tag',
                     optional=False, ptype='string',
                     doc='The name of the Tag.'),
               Param(name='object_id', short_name='o', long_name='object_id',
                     optional=False, ptype='string',
                     doc='The uuid of the object to Tag.'),
               Param(name='object_type', short_name='y', long_name='object_type',
                     optional=False, ptype='string',
                     doc='''The numeric object type of the object to Tag. (User = 1, Asset = 2, Task = 3)''')]

    def main(self):
        results = self.call_api(self.API, ['tag', 'object_id', 'object_type'])
        print(results)
