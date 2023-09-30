# ---------------------------------------------------------------------------------------------------------------
# piwiPre project
# This program and library is licenced under the European Union Public Licence v1.2 (see LICENCE)
# developed by fabien.battini@gmail.com
# ---------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------
# Management of exceptions for piwiPre
# ---------------------------------------------------------------------------------------------------------------

# raise PwpError(): prints a message and generate an exception


import inspect
import time
import datetime
import sys


class PwpLog:
    def __init__(self):
        logfile_name = time.strftime("piwiPre_%Y_%m_%d.log")
        self.logfile = open(logfile_name, "a", encoding="utf-8")
        self.start_time = datetime.datetime.now()
        self.print_debug = False
        self.msg(f"---- piwiPre start {self.start_time}")
        self.pictures_nb = 0
        self.data = {           # normal logs are not stored
            'info': [],         # logs that are stored for tests
            'Warning': [],      # a problem that do not require stopping the program
            'ERROR': [],        # under normal circumstances, stops the program. Can be trapped for test
        }

    def configure(self, config):
        self.print_debug = config['debug']

    def reset_data(self):
        self.start_time = datetime.datetime.now()
        self.data = {
            'info': [],
            'Warning': [],
            'ERROR': [],
        }
        nb = self.pictures_nb
        self.pictures_nb = 0
        return nb

    def msg_nb(self, level):
        return len(self.data[level])

    def end(self):
        end = datetime.datetime.now()
        self.msg(f"--- end          = {end} ---")
        self.msg(f"--- Nb files     = {self.pictures_nb}")
        self.msg(f"--- duration     = {end - self.start_time}")
        if self.pictures_nb:
            self.msg(f"--- duration/pic = {(end - self.start_time) / self.pictures_nb}")
        self.msg("------------------------------------")

    def incr_picture(self):
        self.pictures_nb += 1

    def do_msg(self, msg, context=None, level='msg', flush=False):
        if context is not None:
            if level not in ['debug', 'info'] or self.print_debug:
                print(f"{level:7} {context}")
                print(f"{level:7} {context}", file=self.logfile)

        if level not in ['debug', 'info'] or self.print_debug:
            print(f"{level:7} {msg}")
            print(f"{level:7} {msg}", file=self.logfile)
            if flush:
                sys.stdout.flush()

        if level != 'msg' and level != 'debug':
            self.data[level].append(msg)

        if level == 'warning' and self.msg_nb('warning') > 20:
            raise PwpError("Too much warnings")

        if level == 'ERROR' and self.msg_nb('ERROR') > 20:
            raise PwpFatal("Too much errors, aborting")

    def warning(self, msg, context=None):        # warning is always kept for test, and ALWAYS printed
        self.do_msg(msg, context=context, level='Warning', flush=True)

    def msg(self, msg, context=None):           # info is NOT kept for test, and ALWAYS printed
        self.do_msg(msg, context=context, level='msg')

    def info(self, msg, context=None):          # info is always kept for test, and printed only if --debug
        self.do_msg(msg, context=context, level='info', flush=True)

    def debug(self, msg, context=None):         # debug is NOT kept for test, and printed only if --debug
        self.do_msg(msg, context=context, level='debug', flush=True)

    # error must NOT be declared, it is mandatory to go through PwpError
    # def error(self, msg, context=None):
    #     self.do_msg(msg, context=context, level='ERROR', flush=True)


class PwpError(Exception):
    def __init__(self, msg, context=None):
        LOGGER.do_msg(msg, level='ERROR', context=context, flush=True)


class PwpInternalError(PwpError):
    def __init__(self, msg: str):
        previous_frame = inspect.currentframe().f_back
        (filename, line_number, _function_name, _lines, _index) = inspect.getframeinfo(previous_frame)
        context = f"{filename}:{line_number:3}"
        super().__init__("INTERNAL " + msg, context=context)


class PwpConfigError(PwpError):
    def __init__(self, msg, context="Cmd-line/configuration "):
        super().__init__(msg, context=context)


# class PwpExit(PwpError):
#     def __init__(self, msg):
#         super().__init__(msg, context="Exiting from main")


class PwpFatal(Exception):  # should not be trapped
    def __init__(self, msg):
        LOGGER.do_msg(msg, level='FATAL', flush=True)


LOGGER = PwpLog()
