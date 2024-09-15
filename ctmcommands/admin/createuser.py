#########################################################################
# Copyright 2019 VersionOne
# All Rights Reserved.
# http://www.versionone.com
#########################################################################

import ctmcommands.cmd
from ctmcommands.param import Param


class CreateUser(ctmcommands.cmd.CSKCommand):

    Description = 'Creates a new User, Authentication type will be set to SSO if SSO is enabled in this instance'
    API = 'create_user'
    Examples = '''
    ctm-create-user -u "dave.thomas" -n "Dave Thomas" -r "User" -t "dev" -e "dave.thomas@example.com" -p "passw0rd" -a "local" -s "enabled"
'''
    Options = [Param(name='user', short_name='u', long_name='user',
                     optional=False, ptype='string',
                     doc='A login name for the user.'),
               Param(name='name', short_name='n', long_name='name',
                     optional=False, ptype='string',
                     doc='The full name of the user.'),
               Param(name='teams', short_name='t', long_name='teams',
                     optional=False, ptype='string',
                     doc='A list of teams the user belongs to, along with a role for each team. Teams and roles are separated by a colon. Team/role pairs are separated by commas.'),
               Param(name='role', short_name='r', long_name='role',
                     optional=False, ptype='string',
                     doc='The users role.  (Valid values: Administrator, Developer, User)',
                     choices=["Administrator", "Developer", "User"]),
               Param(name='password', short_name='p', long_name='password',
                     optional=True, ptype='string',
                     doc='Password for the user. If "password" is not provided, a random password will be generated.'),
               Param(name='email', short_name='e', long_name='email',
                     optional=True, ptype='string',
                     doc='Email address for the user.  Required if "password" is omitted.'),
               Param(name='authtype', short_name='a', long_name='authtype',
                     optional=True, ptype='string',
                     doc='"local" or "ldap".  Default is "local" if omitted.',
                     choices=["local", "ldap"]),
               Param(name='forcechange', short_name='f', long_name='forcechange',
                     optional=True, ptype='integer',
                     doc='Require user to change password. Default is "true" (1) if omitted. (Valid values: 0 or 1).',
                     choices=[0, 1], default=1),
               Param(name='status', short_name='s', long_name='status',
                     optional=True, ptype='string',
                     doc='Status of the new account. Default is "enabled" if omitted. (Valid values: enabled, disabled, locked)',
                     choices=["enabled", "disabled", "locked"]),
               Param(name='expires', short_name='x', long_name='expires',
                     optional=True, ptype='string',
                     doc='Expiration date for this account.  Must be in mm/dd/yyyy format.'),
               Param(name='groups', short_name='g', long_name='groups',
                     optional=True, ptype='string',
                     doc='A list of groups the user belongs to. Group names cannot contain spaces. Comma delimited list.'),
               Param(name='contributors', short_name='c', long_name='contributors',
                     optional=True, ptype='string',
                     doc='A list of contributors the user is mapped to. Contributors cannot contain spaces. Comma delimited list.'),
               Param(name='get_token', long_name='get_token',
                     optional=True, ptype='boolean',
                     doc='Include a login token in the response. (Used for passthru login.)')
               ]

    def main(self):
        results = self.call_api(self.API, ['user', 'name', 'role', 'teams', 'password', 'email', 'authtype', 'forcechange', 'expires', 'status', 'groups', 'contributors', 'get_token'])
        print(results)
