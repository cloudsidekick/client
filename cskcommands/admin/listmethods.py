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

class ListMethods(cskcommands.cmd.CSKCommand):

    Description = 'Retrieves a list of all REST API methods and their documentation.'
    API = ''
    Examples = '''
_To print a full listing of all api commands with documentation_

    cato-list-methods

_To print only the names with the api commands sorted_

    cato-list-methods -l
'''
    Options = [Param(name='listonly', short_name='l', long_name='listonly',
                     optional=True, ptype='boolean',
                     doc='List the methods without documentation.')]
               

    def main(self):
        # output format for this command is limited to text
        self.output_format = "text"
        
        results = self.call_api(self.API, ['listonly'])
        print(results)

