# ---------------------------------------------------------------------------------------------------------------
# piwiPre project
# This program and library is licenced under the European Union Public Licence v1.2 (see LICENCE)
# developed by fabien.battini(at)gmail.com
# ---------------------------------------------------------------------------------------------------------------

import os
import datetime
# pip install pyyaml
import yaml
import yaml.parser

from piwiPre.pwpActor import ACTOR
from piwiPre.pwpErrors import PwpInternalError, PwpConfigError, LOGGER

# DONE: specifications are imported form code, not from doc
# DONE: parse also the list of possible values, so that we can do a verification


class PwpConfig(dict):
    format_dico = {
        'author': '{author}',
        'base': '{base}',
        'Y': '{Y:04}',
        'm': '{m:02}',
        'd': '{d:02}',
        'H': '{H:02}',
        'M': '{M:02}',
        'S': '{S:02}',
        'month_name': '{month_name}',
        'count': '{count:03}',
        'suffix': '{suffix}',
    }
    legal_items = None

    def __init__(self, content_str: str = None, filename: str = None, dico=None):
        super().__init__()
        LOGGER.msg(f"Reading configuration from '{filename}'")
        self.format_cached = {}

        if content_str is not None:
            try:
                dico = yaml.safe_load(content_str)
            except yaml.parser.ParserError as error:
                error: yaml.parser.ParserError
                context = f"in file {filename}: line : {error.problem_mark.line}"
                msg = "Yaml parsing error : " + error.args[0] + ' ' + error.args[2]
                raise PwpConfigError(msg, context=context)
        elif type(dico) is not dict:
            raise PwpInternalError("illegal PwpConfig")

        dico['ini-filename-parsed'] = filename
        # postprocessing
        for key, value in dico.items():
            self[PwpConfig.normalize(key)] = PwpConfig.normalize(value)

        if PwpConfig.legal_items is None:
            PwpConfig.legal_items = list(self.keys())   # better to do an explicit copy here

    @staticmethod
    def normalize(val):
        if val == 'True' or val == 'true':
            return True
        if val == 'False' or val == 'false':
            return False
        if val == 'Forced':
            return 'forced'
        if val == 'None' or val == 'none':
            return None
        if val is None or val is True or val is False:
            return val
        if val == '':
            return val
        if isinstance(val, str) and val[0] == "'" and val[-1] == "'":
            return PwpConfig.normalize(val[1:-1])
        if isinstance(val, str) and val[0] == '"' and val[-1] == '"':
            return PwpConfig.normalize(val[1:-1])
        if isinstance(val, int):
            return val
        if isinstance(val, str):
            if val[-1:] == '/':  # remove trailing / for ALL items.
                return PwpConfig.normalize(val[:-1])
            else:
                return val
        if isinstance(val, list):
            nl = [PwpConfig.normalize(x) for x in val]
            return nl
        if isinstance(val, dict):
            nd = {}
            for k, v in val.items():
                nd[PwpConfig.normalize(k)] = PwpConfig.normalize(v)
            return nd
        raise PwpInternalError("Normalize illegal type")

    @staticmethod
    def parse_ini_file(filename):
        if not os.path.isfile(filename):
            return PwpConfig(content_str="", filename=filename)

        with ACTOR.open(filename, "r") as ini:
            content = ini.readlines()
        content_str = "".join(content)
        conf = PwpConfig(content_str=content_str, filename=os.path.abspath(filename))
        legals = PwpConfig.legal_items
        for key, value in conf.items():
            if key not in legals:
                raise PwpConfigError(f"Illegal configuration item '{key} : {value}' in '{filename}'")
            conf[key] = None if value == 'None' else value
        return conf

    def merge_ini(self, old):
        LOGGER.debug(f"merging ini files '{old['ini-filename-parsed']}' and '{self['ini-filename-parsed']}'")
        for key in self.keys():
            if key not in old:
                # the old is the default, so it has all the keys.
                PwpConfigError(f"ERROR: illegal argument {key}")

        for key, value in old.items():
            if key not in self:
                self[key] = value

            # otherwise, we keep the new value.
        return self

    # def get(self, flag, default=None):
    #     if flag in self.keys():
    #         return self[flag]
    #     return default
    #
    # @staticmethod
    # def has_flag(args, flag):
    #     try:
    #         args.__getattribute__(flag)
    #         return True
    #     except AttributeError:
    #         return False

    @staticmethod
    def args_to_dict(args):
        args_dict = vars(args)

        for key, value in args_dict.items():
            args_dict[key] = PwpConfig.normalize(value)

        return args_dict

    def merge_ini_args(self, args, arguments: list):
        """
        merges self and args
        :param args: arguments after parsing by argparse, takes default value into account
        :param arguments: argument list BEFORE parsing by argparse
        :return: self
        """
        LOGGER.debug("merging ini with cmdline args")

        args_dict = self.args_to_dict(args)

        for key, value in self.items():
            flag = key.replace('-', '_')
            expected = '--' + key
            if flag in args_dict and expected in arguments:
                # if key not in arguments, then args contains the default value
                # so the .ini file has higher priority
                self[key] = args_dict[flag]  # or value

        # manage items that are in args but not in config (aka self)
        for flag in args_dict.keys():
            key = flag.replace('_', '-')
            if key not in self:
                self[key] = args_dict[flag]
        return self

    def push_local_ini(self, filename):
        if os.path.isfile(filename):
            new_ini = PwpConfig.parse_ini_file(filename)
            new_ini.merge_ini(self)
            return new_ini
        return self

    def author(self, apn, _date):
        # TODO: add a date trigger to authors, so that different photographers can share the same camera
        author = 'Photographer'
        authors = self['authors']
        if apn in authors:
            author = authors[apn]
        elif 'DEFAULT' in authors:
            author = authors['DEFAULT']
        LOGGER.info(f"apn '{apn}'  => author '{author}'")
        return author

    def default_author(self):
        authors = self['authors']
        if 'DEFAULT' in authors:
            return authors['DEFAULT']
        return 'Photographer'

    @staticmethod
    def absolute_date(photo_date: datetime, absolute: dict):
        if 'hour' not in absolute:
            absolute['hour'] = photo_date.hour
        if 'minute' not in absolute:
            absolute['minute'] = photo_date.minute
        if 'second' not in absolute:
            absolute['second'] = photo_date.second

        LOGGER.debug(f"absolute-date {absolute}")
        abs_datetime = datetime.datetime(**absolute)
        return abs_datetime

    def fix_date(self, filename, photo_date, apn):
        all_dates = self['dates']
        if not isinstance(all_dates, dict):
            all_dates = {}

        if photo_date is None:
            if 'NO-DATE' in all_dates.keys:
                nd = all_dates['NO-DATE']
                return self.absolute_date(photo_date, nd)
            else:
                LOGGER.warning("picture without a date and without a correction")
                return None

        for key, descr in all_dates.items():
            if key == 'NO-DATE':
                continue
            start = datetime.datetime(**descr['start'])
            end = datetime.datetime(**descr['end'])

            found_apn = apn if apn in descr else 'default' if 'default' in descr else None
            if found_apn and start <= photo_date <= end:
                update = descr[found_apn]
                if 'delta' in update:
                    new_date = photo_date + datetime.timedelta(**update['delta'])
                    LOGGER.msg(f"DATE correction: {filename}:{apn} (delta) {photo_date} -> {new_date}")
                    return new_date
                if 'forced' in update:
                    nd = update['forced'].copy()
                    new_date = self.absolute_date(photo_date, nd)
                    LOGGER.msg(f"DATE correction: {filename}:{apn} (forced) {photo_date} -> {new_date}")
                    return new_date

                LOGGER.warning(f"date correction start:{start} end:{end} camera:{apn} " +
                               "without a delta or forced statement")

        return photo_date

    def format(self, field):
        if field not in self.format_cached:
            self.format_cached[field] = self[field].format(**self.format_dico)
        return self.format_cached[field]

    def format_dict(self, date, author, base='', count=1, suffix='.jpg'):
        """
        :param date: inherited from the IPTC date of the picture.
        :param author: picture author from IPTC data
        :param base: is the name of the TRIAGE folder where the picture was originally found.
        :param count:
        :param suffix: file suffix
        :return: the dictionary used to format a file or document
        """
        month = self['month-name']
        month_name = month[date.month-1]
        dico = {
            'author': author,
            'base': base,
            'Y': date.year,
            'm': date.month,
            'd': date.day,
            'H': date.hour,
            'M': date.minute,
            'S': date.second,
            'month_name': month_name,
            'count': count,
            'suffix': suffix,
        }
        return dico
