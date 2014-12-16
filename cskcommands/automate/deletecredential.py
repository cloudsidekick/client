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

class DeleteCredential(cskcommands.cmd.CSKCommand):

    Description = 'Deletes a Shared Credential.'
    API = 'delete_credential'
    Examples = '''
    csk-delete-credential -c "adminuser"
'''
    Options = [Param(name='credential', short_name='c', long_name='credential',
                     optional=False, ptype='string',
                     doc='ID or Name of the Credential.')
               ]

    def main(self):
        go = False
        if self.force:
            go = True
        else:
            answer = raw_input("WARNING: This is a utility function.\n\nDeleting a Credential may affect automation connectivity and cannot be undone.\n\nAre you sure? ")
            if answer:
                if answer.lower() in ['y', 'yes']:
                    go = True

        if go:
            results = self.call_api(self.API, ['credential'])
            print(results)
