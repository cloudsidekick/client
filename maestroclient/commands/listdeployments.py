#########################################################################
# 
# Copyright 2013 Cloud Sidekick
# __________________
# 
#  All Rights Reserved.
# 
# NOTICE:  All information contained herein is, and remains
# the property of Cloud Sidekick and its suppliers,
# if any.  The intellectual and technical concepts contained
# herein are proprietary to Cloud Sidekick
# and its suppliers and may be covered by U.S. and Foreign Patents,
# patents in process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from Cloud Sidekick.
#
#########################################################################

import catoclient.catocommand
from catoclient.param import Param

class ListDeployments(catoclient.catocommand.CatoCommand):

    Description = 'Lists Deployments'
    Options = [Param(name='filter', short_name='f', long_name='filter',
                     optional=True, ptype='string',
                     doc='A filter.'),
               Param(name='show_archived', short_name='a', long_name='show_archived',
                     optional=True, ptype='boolean',
                     doc='Include Archived Deployments in the results.')]

    def main(self):
        results = self.call_api('depMethods/list_deployments', ['filter', 'show_archived'])
        print(results)