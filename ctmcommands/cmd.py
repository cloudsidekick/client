#########################################################################
# Copyright 2016 VersionOne
# All Rights Reserved.
# http://www.versionone.com
#########################################################################

# This file is a derived work from Eucalyptus
# euca2ools/euca2ools/commands/eucacommands.py
# released under the BSD license
# original copyright:
#        (c) 2009-2011, Eucalyptus Systems, Inc.`
# original authors:
#       Neil Soman neil@eucalyptus.com
#       Mitch Garnaat mgarnaat@eucalyptus.com

import getopt
import os
import sys
import textwrap
import hashlib
import base64
import hmac
import urllib
import json
import requests
from datetime import datetime
from param import Param

try:
    import xml.etree.cElementTree as ET
except (AttributeError, ImportError):
    import xml.etree.ElementTree as ET


class CSKCommand(object):

    Description = ''
    API = ''
    Examples = ''
    Info = ''
    StandardOptions = [Param(name='access_key',
                             short_name='A', long_name='access-key',
                             doc="A defined username.",
                             optional=True),
                       Param(name='secret_key',
                             short_name='S', long_name='secret-key',
                             doc="A valid password.",
                             optional=True),
                       Param(name='token',
                             short_name='T', long_name='token',
                             doc="A defined user UUID 'token'.",
                             optional=True),
                       Param(name='config_file',
                             short_name='C', long_name='config',
                             doc="""Read credentials and URL from the specified json formatted config file. If a config file and 
                                    -A, -U or -S flags are used on the same command, the flag option parameters take precendence""",
                             optional=True),
                       Param(name='output_format', short_name='F', long_name='format',
                             doc='The output format.  (default=text, values=xml/json.)',
                             optional=True, ptype='string', choices=['text', 'json', 'xml']),
                       Param(name='output_delimiter', short_name='L', long_name='output_delimiter',
                             doc='Delimiter for "Text" output format. (Default is TAB)',
                             optional=True, ptype='string'),
                       Param(name='debug', short_name='D', long_name='debug',
                             doc='Turn on debugging output.',
                             optional=True, ptype='boolean'),
                       Param(name='help', short_name='H', long_name='help',
                             doc='Display this help message.',
                             optional=True, ptype='boolean'),
                       Param(name='url', short_name='U', long_name='url',
                             doc='URL of the REST API endpoint. E.g.: http://address:port',
                             optional=True),
                       Param(name='force', long_name='force',
                             doc='Force "yes" on "Are you sure?" prompts.',
                             optional=True, ptype='boolean'),
                       Param(name='noheader', long_name='noheader',
                             doc='For "text" output format, omit the column header.',
                             optional=True, ptype='boolean'),
                       Param(name='dumpdoc', long_name='dumpdoc',
                             doc='Writes documentation for the command in Markdown format.',
                             optional=True, ptype='boolean'),
                       Param(name='api', long_name='api',
                             doc='Identifies the API endpoint associated with this command.',
                             optional=True, ptype='boolean')]
    Options = []
    Args = []

    def __init__(self, debug=False):
        self.token = None
        self.url = None
        self.config_file_name = None
        self.debug = 0
        self.force = False
        self.set_debug(debug)
        self.cmd_name = os.path.basename(sys.argv[0])
        self.process_cli_args()

        # if there's a config file, we read it.
        # any required values not explicitly specified on the command line,
        # are read from the config file.
        # there's a default file ".cclclient.conf", and you can override with the "config_file" argument
        configargs = None
        cfn = None
        if self.config_file_name:
            cfn = self.config_file_name
        else:
            cfn = "%s/.cclclient.conf" % os.path.expanduser("~")

        try:
            # VERSION 1.33+ - we renamed the catoclient.conf file.
            # if the old name is encountered, rename it
            if os.path.isfile("%s/.catoclient.conf" % os.path.expanduser("~")):
                print("INFO - encountered '.catoclient.conf'.  This version uses '.cclclient.conf'.  The file has been renamed as a convenience, and this message should not appear again.")
                try:
                    old = "%s/.catoclient.conf" % os.path.expanduser("~")
                    os.rename(old, old.replace("cato", "ccl"))
                except Exception as ex:
                    # trying to rename the conf file failed... write a nice warning
                    print("Unable to rename .catoclient.conf.  Please check the permissions and/or rename it manually.")
                    print(ex.__str__())
                    self.error_exit()

            with open(cfn, 'r') as f_in:
                if f_in:
                    configargs = json.loads(f_in.read())
        except IOError:
            # if the file doesn't exist, warn and exit (but continue if there's no default config file).
            if cfn != "%s/.cclclient.conf" % os.path.expanduser("~"):
                print("The specified config file (%s) could not be found." % cfn)
                self.error_exit()
            else:
                if self.debug:
                    print("The default config file (%s) could not be found." % cfn)

        except ValueError:
            # if the format of either file is bad, bark about it
            print("The specified config file (%s) json format is invalid." % cfn)
            self.error_exit()

        if configargs:
            # loop through the settings
            for k, v in configargs.items():
                if hasattr(self, k):
                    if not getattr(self, k):
                        setattr(self, k, v)

        # since the args can come from different sources, we have to explicitly check the required ones.
        if not self.url:
            print("URL is required, either via --url or in a config file.")
            self.error_exit()
        if not self.url.endswith("/api"):
            # 9-3-15 per Patrick
            self.url = "%s/api" % (self.url)
        # token is required
        if not self.token:
            print("Token is required, either via --token or in a config file.")
            self.error_exit()

    def set_debug(self, debug=False):
        if debug:
            self.debug = 2

    def set_force(self, force=True):
        if force:
            self.force = True

    def process_cli_args(self):
        try:
            (opts, args) = getopt.gnu_getopt(sys.argv[1:],
                                             self.short_options(),
                                             self.long_options())
        except getopt.GetoptError, e:
            print(e)
            sys.exit(1)
        for (name, value) in opts:
            if name in ('-H', '--help'):
                self.usage()
                sys.exit()
            elif name == '--dumpdoc':
                self.dumpdoc()
                sys.exit()
            elif name == '--api':
                print self.API
                sys.exit()
            elif name in ('-D', '--debug'):
                self.set_debug(True)
            elif name in ('-C', '--config'):
                self.config_file_name = value
            else:
                option = self.find_option(name)
                if option:
                    try:
                        value = option.convert(value)
                    except:
                        msg = '%s should be of type %s' % (option.long_name,
                                                           option.ptype)
                        self.display_error_and_exit(msg)

                    if option.choices:
                        if value not in option.choices:
                            msg = '%s value must be one of: %s' % (option.long_name, '|'.join(["%s" % str(x) for x in option.choices]))
                            self.display_error_and_exit(msg)
                    if option.cardinality in ('*', '+'):
                        if not hasattr(self, option.name):
                            setattr(self, option.name, [])
                        getattr(self, option.name).append(value)
                    else:
                        setattr(self, option.name, value)
        self.handle_defaults()
        self.check_required_options()

        for arg in self.Args:
            if not arg.optional and len(args) == 0:
                self.usage()
                msg = 'Argument (%s) was not provided' % arg.name
                self.display_error_and_exit(msg)
            if arg.cardinality in ('*', '+'):
                setattr(self, arg.name, args)
            elif arg.cardinality == 1:
                if len(args) == 0 and arg.optional:
                    continue
                try:
                    value = arg.convert(args[0])
                except:
                    msg = '%s should be of type %s' % (arg.name,
                                                       arg.ptype)
                setattr(self, arg.name, value)
                if len(args) > 1:
                    msg = 'Only 1 argument (%s) permitted' % arg.name
                    self.display_error_and_exit(msg)

    def find_option(self, op_name):
        for option in self.StandardOptions + self.Options:
            if option.synopsis_short_name == op_name or option.synopsis_long_name == op_name:
                return option
        return None

    def short_options(self):
        s = ''
        for option in self.StandardOptions + self.Options:
            if option.short_name:
                s += option.getopt_short_name
        return s

    def long_options(self):
        l = []
        for option in self.StandardOptions + self.Options:
            if option.long_name:
                l.append(option.getopt_long_name)
        return l

    def required(self):
        return [opt for opt in self.StandardOptions + self.Options if not opt.optional]

    def required_args(self):
        return [arg for arg in self.Args if not arg.optional]

    def optional(self):
        return [opt for opt in self.StandardOptions + self.Options if opt.optional]

    def optional_args(self):
        return [arg for arg in self.Args if arg.optional]

    def handle_defaults(self):
        for option in self.Options + self.Args:
            if not hasattr(self, option.name):
                value = option.default
                if value is None and option.cardinality in ('+', '*'):
                    value = []
                elif value is None and option.ptype == 'boolean':
                    value = False
                elif value is None and option.ptype == 'integer':
                    value = 0
                setattr(self, option.name, value)

    def check_required_options(self):
        missing = []
        for option in self.required():
            if not hasattr(self, option.name) or getattr(self, option.name) is None:
                missing.append(option.long_name)
        if missing:
            msg = 'These required options are missing: %s' % ','.join(missing)
            self.display_error_and_exit(msg)

    def param_usage(self, plist, label, n=25):
        nn = 80 - n - 13
        if plist:
            print('    %s' % label)
            for opt in plist:
                names = []
                if opt.short_name:
                    names.append(opt.synopsis_short_name)
                if opt.long_name:
                    names.append(opt.synopsis_long_name)
                if not names:
                    names.append(opt.name)
                doc = textwrap.dedent(opt.doc)
                doclines = textwrap.wrap(doc, nn)
                if opt.choices:
                    vv = 'Valid Values: %s' % '|'.join(["%s" % str(x) for x in opt.choices])
                    doclines += textwrap.wrap(vv, nn)
                if doclines:
                    print('        %s%s' % (','.join(names).ljust(n), doclines[0]))
                    for line in doclines[1:]:
                        print('%s%s' % (' ' * (n + 13), line))

    def option_synopsis(self, options):
        s = ''
        for option in options:
            names = []
            if option.short_name:
                names.append(option.synopsis_short_name)
            if option.long_name:
                names.append(option.synopsis_long_name)
            if option.optional:
                s += '['
            s += ', '.join(names)
            if option.ptype != 'boolean':
                if option.metavar:
                    n = option.metavar
                elif option.name:
                    n = option.name
                else:
                    n = option.long_name
                s += ' <%s> ' % n
            if option.optional:
                s += ']'
        return s

    def synopsis(self):
        s = '%s ' % self.cmd_name
        n = len(s) + 1
        t = ''
        t += self.option_synopsis(self.required())
        t += self.option_synopsis(self.optional())
        if self.Args:
            t += ' '
            arg_names = []
            for arg in self.Args:
                name = arg.name
                if arg.optional:
                    name = '[ %s ]' % name
                arg_names.append(name)
            t += ' '.join(arg_names)
        lines = textwrap.wrap(t, 80 - n)
        print s, lines[0]
        for line in lines[1:]:
            print '%s%s' % (' ' * n, line)

    def usage(self):
        print '    %s\n' % self.Description
        # self.synopsis()
        self.param_usage([opt for opt in self.Options if not opt.optional],
                         'REQUIRED PARAMETERS')
        self.param_usage([opt for opt in self.Options if opt.optional],
                         'OPTIONAL PARAMETERS')
        self.param_usage([opt for opt in self.StandardOptions],
                         'STANDARD PARAMETERS')

        if self.Info:
            print self.Info

    def dumpdoc(self):
        print '## %s' % self.cmd_name
        print '{:#%s}' % self.cmd_name
        print '\n%s\n' % self.Description

        self.param_usage([opt for opt in self.Options if not opt.optional],
                         'REQUIRED PARAMETERS')
        self.param_usage([opt for opt in self.Options if opt.optional],
                         'OPTIONAL PARAMETERS')
        if self.Info:
            print self.Info

        if self.Examples:
            print "**Examples**"
            print self.Examples

    def display_error_and_exit(self, exc):
        try:
            print('\n%s: %s, %s\n' % (exc.error_code, exc.error_message, exc.error_detail))
        except:
            print('\n%s\n' % exc)
        finally:
            self.usage()
            sys.exit(1)

    def error_exit(self):
        sys.exit(1)

    def call_api(self, method, parameters, verb="GET"):
        host = self.url
        outfmt = "text"
        outdel = ""
        noheader = None
        # was a different output format specified?
        # we limit the values to xml or json.
        if hasattr(self, "output_format"):
            x = getattr(self, "output_format")
            if x:
                if x == "xml" or x == "json":
                    outfmt = x
        # are we using a custom delimiter?
        if hasattr(self, "output_delimiter"):
            x = getattr(self, "output_delimiter")
            if x is not None:
                outdel = x
        # hide the headers in text mode?
        if outfmt == "text":
            noheader = getattr(self, "noheader", None)

        args = {}
        argstr = ""
        for param in parameters:
            if getattr(self, param, None):
                args[param] = getattr(self, param)

            # if post then args are a dict, if get args are qs
        if verb == "GET":
            if len(args):
                arglst = ["&%s=%s" % (k, urllib.quote_plus(str(v))) for k, v in args.items()]
                argstr = "".join(arglst)

        od = "&output_delimiter=%s" % urllib.quote_plus(outdel)
        nh = "&header=false" if noheader else ""
        url = "%s/%s?%s%s%s" % (host, method, argstr, od, nh)

        if not url:
            return "URL not provided."

        if self.debug:
            print("Trying an HTTP %s to %s" % (verb, url))

        hdrs = {
            "Authorization": "Token %s" % (self.token)
        }
        if outfmt == "json":
            hdrs["Accept"] = "application/json"
        elif outfmt == "xml":
            hdrs["Accept"] = "application/xml"
        else:
            hdrs["Accept"] = "text/plain"

        try:
            response = requests.request(verb, url, headers=hdrs, data=args, verify=False, timeout=10)
        except requests.exceptions.Timeout as e:
            m = "Timeout attempting to access [%s]" % url
            raise Exception(m, e)
        except requests.exceptions.ConnectionError as e:
            m = "HTTP connection error. Check http or https, server address and port"
            raise Exception(m, e)

        if self.debug:
            print(response)

        if response:
            if outfmt == "json":
                try:
                    d = response.json()
                    if d["ErrorCode"]:
                        code = d["ErrorCode"]
                        detail = d["ErrorDetail"]
                        message = d["ErrorMessage"]
                        msg = "%s, %s, %s" % (code, message, detail)
                        self.display_error_and_exit(msg)
                    else:
                        # JSON is a bit confusing...
                        # the entire 'payload' is json formatted, so by using json.loads above,
                        # we've converted THE WHOLE PAYLOAD to a python object
                        # However, we need to return a JSON *string* of the stuff *inside* the 'Response' property.
                        return json.dumps(d["Response"], indent=4)
                except ValueError:
                    print("Response JSON could not be parsed.")
                    return response.content
                except Exception as ex:
                    raise ex
            elif outfmt == "xml":
                try:
                    xRoot = ET.fromstring(response.content)
                    if xRoot.findtext("error/code", None):
                        code = xRoot.findtext("error/code", "")
                        detail = xRoot.findtext("error/detail", "")
                        message = xRoot.findtext("error/message", "")

                        msg = "%s, %s, %s" % (code, message, detail)
                        self.display_error_and_exit(msg)
                    else:
                        # the response might have inner content, or it might have just text
                        try:
                            innercontent = list(xRoot.find("response"))[0]
                            return ET.tostring(innercontent)
                        except IndexError:
                            return xRoot.findtext("response", "")
                except ValueError:
                    print("Response XML could not be parsed.")
                except Exception as ex:
                    raise ex
            else:
                return response.content

    def get_relative_filename(self, filename):
        return os.path.split(filename)[-1]

    def get_file_path(self, filename):
        # relative_filename = self.get_relative_filename(filename)
        file_path = os.path.dirname(filename)
        if len(file_path) == 0:
            file_path = '.'
        return file_path