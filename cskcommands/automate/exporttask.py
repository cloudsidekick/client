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

class ExportTask(cskcommands.cmd.CSKCommand):

    Description = 'Exports a Task that can be checked into version control or imported elsewhere.'
    API = 'export_task'
    Examples = '''
_To export the default version of a task in the default xml format_

    cato-export-task -t "mytask01"

_To export a specific version of a task in json format_

    cato-export-task -t "mytask01" -v "2.000" -F "json"

_To export the default version of a task and redirect to a file_

    cato-export-task -t "mytask01" > mytask01.xml

_To export the default version of a task, include all subtask references and put results in a file_

    cato-export-task -t "mytask01" -r -f "~/mytask01.xml"
'''
    Options = [Param(name='task', short_name='t', long_name='task',
                     optional=False, ptype='string',
                     doc='The ID or Name of the Task to export.'),
               Param(name='version', short_name='v', long_name='version',
                     optional=True, ptype='string',
                     doc='An optional specific Task Version. (Default if omitted.)'),
               Param(name='include_refs', short_name='r', long_name='include_refs',
                     optional=True, ptype='boolean',
                     doc='If provided, will include all referenced subtasks.'),
               Param(name='output_file', short_name='f', long_name='output_file',
                     optional=True, ptype='string',
                     doc='Save the exported Task(s) to the specified file.')
               ]

    def main(self):
        try:
            results = self.call_api(self.API, ['task', 'version', 'include_refs'])

            if self.output_file:
                import os
                fn = os.path.expanduser(self.output_file)
                with open(fn, 'w') as f_out:
                    if not f_out:
                        print("Unable to open file [%s]." % fn)
                    f_out.write(results)
            else:
                print(results)
        except ValueError:
            # the results could not be parsed as JSON, just return them
            print(results)
        except Exception as ex:
            raise ex
