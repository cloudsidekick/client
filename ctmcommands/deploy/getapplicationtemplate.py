#########################################################################
# 
# Copyright 2016 VersionOne
# All Rights Reserved.
# http://www.versionone.com
# 
# 
#########################################################################

import ctmcommands.cmd
from ctmcommands.param import Param

class GetApplicationTemplate(ctmcommands.cmd.CSKCommand):

    Description = 'Retrieves the properties of an application template'
    API = 'get_application_template'
    Examples = '''
_To get the high level properties of an application template_

    ctm-get-application-template -t "Spring Petclinic" -v 1

_To get the json formatted definition for the application template and redirect to a file_

    ctm-get-application-template -t "Spring Petclinic" -v 1 -d > petclinic.json

_To get retrieve a base64 encoded icon file for an application template and decode it_

    ctm-get-application-template -t "Spring Petclinic" -v 1 -i | base64 --decode > petclinic.png



'''
    Options = [Param(name='template', short_name='t', long_name='template',
                     optional=False, ptype='string',
                     doc='Name of the Application Template.'),
               Param(name='version', short_name='v', long_name='version',
                     optional=False, ptype='string',
                     doc='The Application Template Version.'),
               Param(name='getdefinition', short_name='d', long_name='desc',
                     optional=True, ptype='boolean',
                     doc='Will only return the JSON definition file.'),
               Param(name='geticon', short_name='i', long_name='icon',
                     optional=True, ptype='boolean',
                     doc='Will only return the Base64 encoded icon.')
               ]

    def main(self):
        results = self.call_api(self.API, ['template', 'version', 'getdefinition', 'geticon'])
        print(results)