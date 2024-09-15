#########################################################################
# Copyright 2019 VersionOne
# All Rights Reserved.
# http://www.versionone.com
#########################################################################

import ctmcommands.cmd
from ctmcommands.param import Param

from builtins import input


class UpdateUser(ctmcommands.cmd.CSKCommand):

    Description = 'Updates a User account, Authentication type will be set to SSO if SSO is enabled in this instance'
    API = 'update_user'
    Examples = '''
    ctm-update-user -u "dave.thomas" -s "disabled"  --force
'''
    Options = [Param(name='user', short_name='u', long_name='user',
                     optional=False, ptype='string',
                     doc='The ID or Name of a User account.'),
               Param(name='name', short_name='n', long_name='name',
                     optional=True, ptype='string',
                     doc='The full name of the user.'),
               Param(name='role', short_name='r', long_name='role',
                     optional=True, ptype='string',
                     doc='The users role.  (Valid values: Administrator, Developer, User)',
                     choices=["Administrator", "Developer", "User"]),
               Param(name='teams', short_name='t', long_name='teams',
                     optional=True, ptype='string',
                     doc='A list of teams the user belongs to, along with a role for each team. Teams and roles are separated by a colon. Team/role pairs are separated by commas.'),
               Param(name='is_system_administrator', long_name='is-sys-admin',
                     optional=True, ptype='string',
                     doc="Whether the user should have system administrator privileges. (Valid values: True or False)"),
               Param(name='is_shared_asset_manager', long_name='is-shared-asset-mgr',
                     optional=True, ptype='string',
                     doc="Whether the user should have shared asset manager privileges. (Valid values: True or False)"),
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
                     doc='Usernames in source control management systems related to an user. Comma delimited list.'),
               Param(name='password', short_name='p', long_name='password',
                     optional=True, ptype='string',
                     doc='The new password.'),
               Param(name='generate', long_name='generate',
                     optional=True, ptype='boolean',
                     doc='Generate a new, random password.')]

    def main(self):
        go = False
        if self.force:
            go = True
        else:
            answer = input("Updating a User could affect their ability to log in and use the system.\n\nAre you sure? ")
            if answer:
                if answer.lower() in ['y', 'yes']:
                    go = True

        if go:
            results = self.call_api(self.API, ['user', 'name', 'role', 'teams', 'email', 'authtype', 'forcechange', 'status', 'expires', 'groups', 'contributors', 'password', 'generate', 'is_system_administrator', 'is_shared_asset_manager'])
            print(results)
