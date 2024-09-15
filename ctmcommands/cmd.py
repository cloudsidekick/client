#########################################################################
# Copyright 2019 VersionOne
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
from future.standard_library import install_aliases
install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import requests
from ctmcommands.param import Param

try:
    import xml.etree.cElementTree as ET
except (AttributeError, ImportError):
    import xml.etree.ElementTree as ET

try:
    from requests.packages import urllib3
    urllib3.disable_warnings()
except (ImportError):
    pass


class CSKCommand(object):

    Description = ''
    API = ''
    Examples = ''
    Info = ''
    StandardOptions = [Param(name='url', short_name='U', long_name='url',
                             doc='URL of the REST API endpoint. For example: http://address:port',
                             optional=True),
                       Param(name='token',
                             short_name='T', long_name='token',
                             doc='A valid users API token.',
                             optional=True),
                       Param(name='config_file',
                             short_name='C', long_name='config',
                             doc='Read token and url from the specified json formatted config file.',
                             optional=True),
                       Param(name='output_format', short_name='F', long_name='format',
                             doc='The output format.  (default=text)',
                             optional=True, ptype='string', choices=['text', 'json', 'xml']),
                       Param(name='output_delimiter', short_name='L', long_name='output_delimiter',
                             doc='Delimiter for "text" output format. (default=TAB)',
                             optional=True, ptype='string'),
                       Param(name='debug', short_name='D', long_name='debug',
                             doc='Turn on debugging output.',
                             optional=True, ptype='boolean'),
                       Param(name='help', short_name='H', long_name='help',
                             doc='Display this help message.',
                             optional=True, ptype='boolean'),
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
        self.config_file_name = None
        self.debug = 0
        self.force = False
        self.set_debug(debug)
        self.cmd_name = os.path.basename(sys.argv[0])
        self.token = os.environ.get("CONTINUUM_TOKEN")
        self.url = os.environ.get("CONTINUUM_URL")
        self.process_cli_args()

        # if we can find CONTINUUM_URL and CONTINUUM_TOKEN in the environment, don't bother with the file
        if not self.token or not self.url:
            # if there's a config file, we read it.
            # any required values not explicitly specified on the command line,
            # are read from the config file.
            # there's a default file ".ctmclient.conf", and you can override with the "config_file" argument
            config_doc = None
            cfn = None
            if self.config_file_name:
                cfn = self.config_file_name
            else:
                cfn = "%s/.ctmclient.conf" % os.path.expanduser("~")

            try:
                with open(cfn, 'r') as f_in:
                    if f_in:
                        config_doc = json.loads(f_in.read())
            except IOError:
                # if the file doesn't exist, warn and exit (but continue if there's no default config file).
                if cfn != "%s/.ctmclient.conf" % os.path.expanduser("~"):
                    raise Exception("The specified config file (%s) could not be found." % cfn)
                else:
                    if self.debug:
                        print("The default config file (%s) could not be found." % cfn)

            except ValueError:
                # if the format of either file is bad, bark about it
                print("The specified config file (%s) json format is invalid." % cfn)
                self.error_exit()

            if config_doc:
                # loop through the settings
                # comments because this is a little hard to grok
                # for every key in the config file
                for k, v in config_doc.items():
                    # if 'self' has the key
                    if hasattr(self, k):
                        # and self.key is not set
                        if not getattr(self, k):
                            # set it with the value from the file
                            setattr(self, k, v)

        if not self.url:
            print("URL is required, either via `--url` argument, `CONTINUUM_URL` environment variable or in a config file.")
            self.error_exit()
        if not self.url.endswith("/api"):
            self.url = "%s/api" % (self.url)
        if not self.token:
            print("Token is required, either via `--token`, `CONTINUUM_TOKEN` environment variable or in a config file.")
            self.error_exit()

        if self.debug:
            print("Using CONTINUUM_URL: %s" % self.url)
        if self.debug:
            print("Using CONTINUUM_TOKEN: %s" % self.token)

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
        except getopt.GetoptError as e:
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
                print(self.API)
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
        print(s, lines[0])
        for line in lines[1:]:
            print('%s%s' % (' ' * n, line))

    def usage(self):
        print('    %s\n' % self.Description)
        # self.synopsis()
        self.param_usage([opt for opt in self.Options if not opt.optional],
                         'REQUIRED PARAMETERS')
        self.param_usage([opt for opt in self.Options if opt.optional],
                         'OPTIONAL PARAMETERS')
        self.param_usage([opt for opt in self.StandardOptions],
                         'STANDARD PARAMETERS')

        if self.Info:
            print(self.Info)

    def dumpdoc(self):
        print('<h3 id="{0}" title="Permalink">{0}&nbsp;<a href="#{0}" style="display: margin-left: 1em;">&para;</a></h3>\n'.format(self.cmd_name))
        print('\n%s\n' % self.Description)

        self.param_usage([opt for opt in self.Options if not opt.optional],
                         'REQUIRED PARAMETERS')
        self.param_usage([opt for opt in self.Options if opt.optional],
                         'OPTIONAL PARAMETERS')
        if self.Info:
            print(self.Info)

        if self.Examples:
            print("**Examples**")
            print(self.Examples)

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

    def call_api(self, method, parameters=[], data={}, verb="GET", content_type=None, timeout=10):
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

        args = data
        argstr = ""
        for param in parameters:
            if getattr(self, param, None) is not None:
                args[param] = getattr(self, param)

        # if post then args are a dict, if get args are qs
        if verb == "GET":
            if len(args):
                arglst = ["&%s=%s" % (k, urllib.parse.quote_plus(str(v))) for k, v in args.items()]
                argstr = "".join(arglst)

        url = host

        if method:
            url = "%s/%s" % (host, method)
        if argstr:
            url = "%s/%s?%s" % (host, method, argstr)

        if outdel:
            url = "%s&output_delimiter=%s" % (url, urllib.parse.quote_plus(outdel))

        if noheader:
            url = "%s&header=false" % (url)

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

        if content_type:
            hdrs["Content-Type"] = content_type

        try:
            response = requests.request(verb, url, headers=hdrs, data=args, verify=False, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # 400 level errors don't all raise an exception ... some
            # actually do have a response.
            if response.status_code == 400:
                pass
            elif response.status_code == 401 or response.status_code == 403:
                m = "API connection error. Most likely a credentials problem."
                raise Exception(m, e)
            elif response.status_code == 404:
                m = "API connection error. Requested path not found."
                raise Exception(m, e)
            else:
                m = "API error"
                raise Exception(m, e)
        except requests.exceptions.Timeout as e:
            m = "Timeout attempting to access [%s]" % url
            raise Exception(m, e)
        except requests.exceptions.ConnectionError as e:
            m = "API connection error. Check http or https, server address and port."
            raise Exception(m, e)
        except Exception as e:
            m = "API error."
            raise Exception(m, e)

        if self.debug:
            print(response)

        if response is not None:
            if outfmt == "json":
                try:
                    d = response.json()
                    if d["ErrorCode"]:
                        return json.dumps(d, indent=4)
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
                        return ET.tostring(xRoot)
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
