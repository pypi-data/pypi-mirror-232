# ---------------------------------------------------------------------------------------------------------------
# piwiPre project
# This program and library is licenced under the European Union Public Licence v1.2 (see LICENCE)
# developed by fabien.battini(at)gmail.com
# ---------------------------------------------------------------------------------------------------------------

import argparse
import re
import sys
import os
import pprint
import datetime

from piwiPre.pwpConfig import PwpConfig
from piwiPre.pwpErrors import PwpConfigError, LOGGER


class ArgHeader:
    def __init__(self, config: str):
        self.config = config

    @staticmethod
    def is_in_config():
        return False

    def write_rst(self, stream):
        stream.write("\n")
        for line in self.config.splitlines():
            stream.write(line + '\n')
        stream.write("\n")

    def write_ini_file(self, stream):
        stream.write("\n")
        for line in self.config.splitlines():
            stream.write('# ' + line + '\n')
        stream.write("\n")


class ArgIniItem:
    def __init__(self, name: str, config: str, location: str, help_str: str, default, arg, i_type):
        self.name = name
        self.config = config
        self.location = location
        self.help = help_str
        self.default = default
        self.arg = arg
        self.i_type = i_type
        if self.i_type == dict and self.default == '':
            self.default = {}
        if not isinstance(self.default, self.i_type) and self.default is not None:
            raise PwpConfigError(f"Parameter '{name}' default value {default} should have type {str(i_type)} ")

    def is_in_config(self):
        return self.location != 'args'

    def write_rst(self, stream):

        default = self.get_ini_value(self.default, "   ", ini_file=False)
        # default = 'false' if default is False else 'true' if default is True else default

        location = 'configration files only' if self.location == 'config' else \
            'cmd-line arguments only' if self.location == 'args' else 'both configuration files and cmd-line arguments'
        stream.write(f"\n**{self.name}** : {default}\n\n")
        stream.write(f"   where: {location}\n\n")
        stream.write(f"   {self.help}\n")
        for line in self.config.splitlines():
            stream.write(f"   {line}\n")
        stream.write("\n")

    def get_ini_value(self, item, prefix, level=0, ini_file=True):
        if item is False:
            return 'false'
        if item is True:
            return 'true'
        if isinstance(item, str):
            if re.search(r'[+\-/]', item):
                return "'" + item + "'"
            return item

        if type(item) is dict:
            if len(item.keys()) == 0:
                return ""
            if level == 0:
                if ini_file:
                    res = '\n'
                else:
                    res = '\n ::\n\n'
            else:
                res = '\n'
            for key, value in item.items():
                k = self.get_ini_value(key, "", level=level+1, ini_file=ini_file)
                val = self.get_ini_value(value, prefix + "   ", level=level+1, ini_file=ini_file)
                res += f"{prefix}   {k} : {val}\n"
            if level == 0:
                if not ini_file:
                    res += "\n\n#  *(end of the structure)*\n"
            return res

        return str(item)

    def write_ini_file(self, stream):
        default = self.get_ini_value(self.default, "   ", ini_file=True)

        location = 'configration files only' if self.location == 'config' else \
            'cmd-line arguments only' if self.location == 'args' else 'both configuration files and cmd-line arguments'
        if self.location == 'args':
            header = '# '
            name = '--' + self.name
        else:
            header = ''
            name = self.name

        stream.write(f"\n{header}{name} : {default}\n")
        stream.write(f"#   where: {location}\n\n")
        stream.write(f"#   {self.help}\n")
        for line in self.config.splitlines():
            stream.write(f"#   {line}\n")
        stream.write("\n")


class PwpArgsIni(argparse.ArgumentParser):

    def __init__(self, **_kwargs):
        super().__init__(prog='piwiPre', allow_abbrev=False, exit_on_error=False)
        self.args_dico = {}
        # self.args = None # the actual args passed on cmd line
        self.items_list = []
        self.home_config = None

    def add_header(self, prologue: str):
        item = ArgHeader(prologue)
        self.items_list.append(item)

    def add_item(self, name_or_flags: str, **kwargs):
        # location should be 'config' or 'args'. any other value = 'both'. default = 'both'
        location = 'both'
        if 'location' in kwargs:
            location = kwargs['location']
            kwargs.pop('location')
        config = ''
        if 'config' in kwargs:
            config = kwargs['config']
            kwargs.pop('config')
        help_str = '' if 'help' not in kwargs else kwargs['help']
        default = '' if 'default' not in kwargs else kwargs['default']
        if 'pwp_type' in kwargs:
            i_type = kwargs['pwp_type']
            kwargs.pop('pwp_type')
        else:
            i_type = str

        arg = super().add_argument('--'+name_or_flags, **kwargs) if location != 'config' else None
        item = ArgIniItem(name_or_flags, config, location, help_str, default, arg, i_type)
        self.args_dico[name_or_flags] = item
        self.items_list.append(item)

    def build_rst(self, filename: str):
        abs_path = os.path.abspath(filename)
        LOGGER.debug(f"Build RST file {abs_path}")
        with open(filename, 'w', encoding="utf-8") as f:
            start = datetime.datetime.now()
            f.write(f".. comment : CAVEAT: This text is automatically generated by pwpPatcher.py on {start}\n")
            f.write(".. comment :         from the code in pwpParser.py\n")
            for item in self.items_list:
                item.write_rst(f)

    def build_ini_file(self, filename: str):
        with open(filename, 'w', encoding="utf-8") as f:
            for item in self.items_list:
                item.write_ini_file(f)

    def build_initial_config(self):
        dico = {}
        for v in self.items_list:
            if v.is_in_config():
                dico[v.name] = v.default
        dico['help'] = None
        res = PwpConfig(content_str=None, filename="INITIAL VALUES", dico=dico)
        return res

    def parse_args_and_ini(self, program: str, ini_to_parse, arguments, with_config=True):
        initial_config = None
        real_args = arguments if arguments is not None else []

        # check if actual arguments prevent from using the default .ini
        skip_next = False
        for i in range(len(real_args)):
            if skip_next:
                skip_next = False

            elif real_args[i] == '--ini-file':
                if i >= len(real_args):
                    raise PwpConfigError("ERROR: --ini-file without a value")
                new_ini_to_parse = real_args[i + 1]
                ini_to_parse = os.path.basename(new_ini_to_parse)
                skip_next = True

            elif real_args[i] == '--chdir':
                if i >= len(real_args):
                    raise PwpConfigError("ERROR: --chdir without a value")
                new_dir = real_args[i + 1]
                if not os.path.isdir(new_dir):
                    raise PwpConfigError(f"--chdir '{new_dir}' : non existing directory")

                LOGGER.msg(f"chdir '{new_dir}'")
                os.chdir(new_dir)
                skip_next = True
            elif real_args[i] == '--help':
                self.print_usage()
                # FIXME: if we do exit(0) or raisePwpConfigError, (on program_3) on test 400, Paramiko exits on error!
                #        msg is:  'ValueError: I/O operation on closed file'
                #        this seems to be an issue with stdin.
                # Trick: We return None, so that the program is ended gracefully
                return None
            else:
                skip_next = False

        if with_config:
            initial_config = self.build_initial_config()

        home_ini_path = os.path.expanduser("~") + '/.' + ini_to_parse
        config = initial_config

        if with_config and os.path.isfile(home_ini_path):
            first_ini = PwpConfig.parse_ini_file(home_ini_path)
            # if not ACTOR.is_mode_protected(home_ini_path):
            #    raise PwpError(f"HOME ini file {home_ini_path} MUST be protected by chmod 0x600 o 0x400")
            # chmod has limited meaning in windows universe
            config = first_ini.merge_ini(initial_config)

        self.home_config = config

        if with_config and os.path.isfile(ini_to_parse):
            first_ini = PwpConfig.parse_ini_file(ini_to_parse)
            config = first_ini.merge_ini(config)

        LOGGER.msg(f"{program}: reading configuration from cmd-line arguments")
        try:
            args = super().parse_args(args=real_args)
        except argparse.ArgumentError:
            super().print_help()
            raise PwpConfigError("Error on arguments, internal")
        except SystemExit:
            super().print_help()
            # return None
            raise PwpConfigError("Error on arguments")

        if with_config:
            config = config.merge_ini_args(args, real_args)
        else:
            config = PwpConfig.args_to_dict(args)

        return config


def args_ini_main(arguments):
    parser = PwpArgsIni()
    parser.add_header('Unified parser for .ini files and cmdline flags')
    parser.add_header('===============================================')
    parser.add_header('\nParameters when executing pwpArgsIni as a program\n')
    parser.add_item('build-ini-file',
                    help='builds the ini-file argument',
                    action='store_true',
                    location='args')
    parser.add_item('ini-file',
                    help='sets the ini-file to build',
                    action='store',
                    default="test.ini")
    parser.add_item('build-rst-file',
                    help='builds the rst-file argument',
                    action='store_true',
                    location='args')
    parser.add_item('rst-file',
                    help='sets the rst-file to build',
                    action='store',
                    default="test.rst")
    parser.add_item('dump-config',
                    help='dumps the configuration and exits',
                    action='store_true',
                    location='args')
    parser.add_item('auto-test',
                    help='performs the auto-test and exits',
                    action='store_true',
                    location='args')

    # check if actual arguments ask for new configuration items just for test

    if '--auto-test' in arguments:
        # The following data is fake, just to test if args-ini works OK
        parser.add_header("""
#######################
Flags and configuration
#######################""")
        parser.add_header("""
File usage
==========

This file is the default configuration of piwiPre.

Unless stated otherwise, the  configuration items have a command line argument counterpart, 
with the same name, starting with -- .

The default value is given as an argument.

The configuration file uses the yaml syntax,
and uses pyYaml  to read/write the configuration file""")
        parser.add_item('version', help="Prints piwiPre version number and exits.",
                        action='store_true', location='args')

        parser.add_header("""
Management of directories
=========================""")

        parser.add_item('triage',
                        help='Sets the root directory for TRIAGE pictures to manage.',
                        action='store',
                        default='TRIAGE',
                        config="""
- value = 'directory': Sets the root directory for TRIAGE pictures to manage
- value = None: renaming  has already been done, so the TRIAGE directory is not processed
""")

        parser.add_item('month-name',
                        help='The name for each month, used to compute month_name.',
                        action='store',
                        pwp_type=list,
                        default=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                        location='config')

        parser.add_item('piwigo-thumbnails',
                        help='A dictionary if thumbnail specifications',
                        pwp_type=dict,
                        default={
                            "{f}-sq.jpg": {'width': 120, 'height': 120, 'crop': True},
                            "{f}-th.jpg": {'width': 144, 'height': 144, 'crop': False},
                            "{f}-me.jpg": {'width': 792, 'height': 594, 'crop': False},
                            "{f}-cu_e250.jpg": {'width': 250, 'height': 250, 'crop': True},
                        },
                        location='config')
        parser.add_item('dates',
                        help='A dictionary of dates corrections',
                        action='store',
                        pwp_type=dict,
                        default={},
                        location='config')
        parser.add_item('verify-albums',
                        help='true/false/list of directories in ALBUMS to be processed ',
                        action='append',
                        pwp_type=list,
                        default=[])
        parser.add_item('process-rename',  # is used to test ambiguous arguments
                        help='Enables files renaming',
                        action='store',
                        choices=['true', 'false'],
                        default='false')
    # end of auto-test case
    config = parser.parse_args_and_ini("autotest", "tests.ini", arguments)

    if config['auto-test']:
        rst = config['rst-file'] or "../results/test-result.rst"
        ini = config['ini-file'] or "../results/test-result.ini"
        parser.build_rst(rst)
        parser.build_ini_file(ini)
        pprint.pprint(config)
        parser.print_help()
        return
    if config['build-rst-file']:
        parser.build_rst(config['rst-file'])
    if config['build-ini-file']:
        parser.build_ini_file(config['ini-file'])
    if config['help']:
        parser.print_help()


# by default, --auto-test is launched from the tests/argsini directory  # noqa

if __name__ == "__main__":
    sys.exit(args_ini_main(sys.argv[1:]))
