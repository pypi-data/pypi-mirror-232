# ---------------------------------------------------------------------------------------------------------------
# piwiPre project
# This program and library is licenced under the European Union Public Licence v1.2 (see LICENCE)
# developed by fabien.battini(at)gmail.com
# ---------------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------
# test_pwp.py
# ---------------------------------------------------------------------------------------------------------------
# This test is intended to be run from piwiPre directory by invoking pytest,
# which will run all files of the form test_*.py or *_test.py in the current directory and its subdirectories.
#
# is called by tox
#
# can be called directly by running, from piwiPre root directory (where tox.ini is):
# prompt> python -I tests/test_pwp.py -n 0 # or other number...

# =============================================================================================================
# CAVEAT:
# =============================================================================================================
#         tox has issues with comodo antivirus when run from PyCharm Terminal window
#         To avoid this, run tox from a native terminal, not within PyCharm
#
#         The origin seems to be that PyCharm creates a temp script which is not assess correctly by comodo
# =============================================================================================================


import sys
import os
import argparse
import inspect
import re
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from piwiPre.pwpActor import ACTOR
from piwiPre.pwpMain import pwp_main, pwp_run, pwp_init
from piwiPre.pwpErrors import PwpConfigError, LOGGER  # , PwpError
from piwiPre.pwpArgsIni import args_ini_main
from piwiPre.pwpPatcher import patcher_main
from piwiPre.pwpParser import pwp_parser_main
from piwiPre.pwpJpg import PwpJpg
from piwiPre.pwpMp4 import mp4_main, PwpMp4
# from piwiPre.pwpConfig import PwpConfig
from piwiPre.pwpParser import PwpParser

from source.parse_requirements import run_requirements


class PwpTester:
    def __init__(self):
        self.programs_done = {'program_0': False}
        self.programs = {'program_0': self.program_0}
        self.run_file = "tests/sources/run.txt"
        self.asserts = 0
        self.start_time = datetime.datetime.now()
        self.pictures_nb = 0

        parser = PwpParser(arguments=[], program="test_harness", with_config=True)
        self.home_config = parser.home_config

        # initial_config = parser.build_initial_config()
        # home_ini_path = os.path.expanduser("~") + '/.piwiPre.ini'
        # first_ini = PwpConfig.parse_ini_file(home_ini_path)
        # self.home_config = first_ini.merge_ini(initial_config)

        members = inspect.getmembers(self)
        last = 0
        for m in members:
            r = re.match(r"program_\d+", m[0])
            if r:
                name = m[0]
                number = int(name[8:])  # because we want them ordered
                last = max(number, last)
                self.programs_done[name] = False
                self.programs[name] = m[1]
        self.last = last

    @staticmethod
    def get_assert_context():
        previous_frame = inspect.currentframe().f_back.f_back
        (filename, line_number, _function_name, _lines, _index) = inspect.getframeinfo(previous_frame)
        context = f"'{filename}':{line_number:03}\n               "
        return context

    def assert_dir(self, dir_path: str):
        msg = f"{self.get_assert_context()} directory {dir_path} should exist"
        self.asserts += 1
        assert os.path.isdir(dir_path), msg

    def assert_no_dir(self, dir_path: str):
        msg = f"{self.get_assert_context()} directory {dir_path} should not exist"
        self.asserts += 1
        assert not os.path.isdir(dir_path), msg

    def assert_file(self, filepath: str):
        msg = f"{self.get_assert_context()} file {filepath} should exist"
        self.asserts += 1
        assert os.path.isfile(filepath), msg

    def assert_remote_file(self, filepath: str):
        msg = f"{self.get_assert_context()} remote file {filepath} should exist"
        self.asserts += 1
        assert ACTOR.remote_isfile(filepath, forced=True), msg  # forced = bypass --dryrun

    def assert_no_file(self, filepath: str):
        msg = f"{self.get_assert_context()} file {filepath} should not exist"
        self.asserts += 1
        assert not os.path.isfile(filepath), msg

    def assert_no_remote_file(self, filepath: str):
        msg = f"{self.get_assert_context()} remote file {filepath} should not exist"
        self.asserts += 1
        assert not ACTOR.remote_isfile(filepath), msg

    def assert_file_contains(self, filepath: str, line: str):
        msg = f"{self.get_assert_context()} file {filepath} should exist"
        self.asserts += 1
        assert os.path.isfile(filepath), msg
        with open(filepath, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        msg = f"{self.get_assert_context()} file {filepath} should contain '{line}'"
        for la in lines:
            if line in la:
                return
        assert False, msg

    def assert_file_not_contains(self, filepath: str, line: str):
        msg = f"{self.get_assert_context()} file {filepath} should exist"
        self.asserts += 1
        assert os.path.isfile(filepath), msg
        with open(filepath, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        msg = f"{self.get_assert_context()} file {filepath} should not contain '{line}'"
        for la in lines:
            assert line not in la, msg

    def assert_config(self, config, item, value):
        msg = f"{self.get_assert_context()} config[{item}] should be '{value}' and not '{str(config[item])}'"
        self.asserts += 1
        assert str(config[item]) == str(value), msg

    def assert_not_config(self, config, item, value):
        msg = f"{self.get_assert_context()} config[{item}] should not be '{value}'"
        self.asserts += 1
        assert str(config[item]) != str(value), msg

    def assert_error_number(self, level: str, err_nb: int):
        nb = LOGGER.msg_nb(level)
        msg = f"Line:{str(inspect.currentframe().f_lineno)}: {level}[{err_nb}] is not the max[{nb}]"
        self.asserts += 1
        assert nb == err_nb, msg

    def assert_error_contains(self, level: str, err_nb: int, start: str):
        nb = LOGGER.msg_nb(level)
        self.asserts += 1
        previous_frame = inspect.currentframe().f_back
        (filename, line_number, _function_name, _lines, _index) = inspect.getframeinfo(previous_frame)
        context = f"{filename}:{line_number:3}"
        msg = f"{context}: Error[{err_nb}] not reached"
        assert nb >= err_nb, msg
        if nb < err_nb:
            return
        err = LOGGER.data[level][err_nb]
        msg = f"{context}: Error[{err_nb}] '{err[:40]}' != '{start[:40]}' "
        assert start in err, msg

    def assert_info(self, value: str):
        msg = f"{self.get_assert_context()} debug info log should contain <{value}>"
        self.asserts += 1
        all_info = LOGGER.data['info']
        for err in all_info:
            if value in err:
                return
        assert False, msg

    def assert_info_or(self, values: [str]):
        msg = f"{self.get_assert_context()} debug info log should contain <{values[0]}> or ..."
        self.asserts += 1
        all_info = LOGGER.data['info']
        for err in all_info:
            for v in values:
                if v in err:
                    return True
        assert False, msg

    def assert_not_info(self, value: str):
        msg = f"{self.get_assert_context()} debug info log should contain '{value}'"
        self.asserts += 1
        for err in LOGGER.data['info']:
            assert value not in err, msg

    def assert_orientation(self, jpg: PwpJpg, rot: int):
        val = jpg.orientation
        msg = f"{self.get_assert_context()} orientation should be {rot} not {val}"
        self.asserts += 1
        assert val == rot, msg

    def assert_no_orientation(self, jpg: PwpJpg, rot: int):
        val = jpg.orientation
        msg = f"{self.get_assert_context()} orientation should not be {rot} "
        self.asserts += 1
        assert val != rot, msg

    def assert_copyright(self, jpg: PwpJpg, expected: str):
        val = jpg.copyright
        msg = f"{self.get_assert_context()} copyright '{val}' should contain '{expected}' "
        self.asserts += 1
        assert expected in str(val), msg

    def assert_author(self, jpg: PwpJpg, expected: str):
        val = jpg.author
        msg = f"{self.get_assert_context()} author '{val}' should contain '{expected}' "
        self.asserts += 1
        assert expected in str(val), msg

    def assert_mp4_copyright(self, mp4: PwpMp4, expected: str):
        val = mp4.copyright
        msg = f"{self.get_assert_context()} copyright '{val}' should contain '{expected}' "
        self.asserts += 1
        assert expected in str(val), msg

    def assert_no_copyright(self, jpg: PwpJpg, expected: str):
        val = jpg.copyright
        msg = f"{self.get_assert_context()} copyright '{val}' should not contain '{expected}' "
        self.asserts += 1
        assert expected not in str(val), msg

    def assert_special(self, jpg: PwpJpg, expected: str):
        val = jpg.special
        msg = f"{self.get_assert_context()} special instructions '{val}' should contain '{expected}' "
        self.asserts += 1
        assert expected in str(val), msg

    @staticmethod
    def done(name):
        ACTOR.mkdirs("tests/results")
        ACTOR.create(f"tests/results/{name}_done.txt")

    @staticmethod
    def check_done(name: str):
        return os.path.isfile(f"tests/results/{name}_done.txt")

    @staticmethod
    def reset_done(name: str):
        ACTOR.delete(f"tests/results/{name}_done.txt", forced=True)

    def reset_data(self):
        ACTOR.reset_data()
        self.pictures_nb += LOGGER.reset_data()

    # --------------------------------------- Testing cmd line flags and configuration
    def program_1(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('testing chdir, reset-ini, dump-config')
        LOGGER.msg('')

        ACTOR.rmtree("tests/results")
        ACTOR.mkdirs("tests/results/TRIAGE/Armor")
        ACTOR.copy('tests/sources/piwiPre-fake.ini', "tests/results/piwiPre.ini")
        ACTOR.copy('tests/sources/piwiPre-alt-Armor.ini', "tests/results/TRIAGE/Armor/piwiPre.ini")

        pwp_main(['--reset-ini',  '--chdir', 'tests/results/TRIAGE'])
        self.assert_file('tests/results/TRIAGE/piwiPre.ini')  # the file is there, it should overwrite info in cwd

        LOGGER.msg('')
        LOGGER.msg('Step 2 in the same program, --chdir')
        LOGGER.msg('')

        main = pwp_init(['--chdir', 'tests/results', '--dump-config', 'TRIAGE/Armor'])  # , '--debug'])
        pwp_run(main)

        armor_conf = main.dumped_config
        # the hierarchy should be:
        # cwd (aka tests/results): piwiPre-fake.ini
        # cwd/TRIAGE:              --reset-ini
        # cwd/TRIAGE/Armor:        piwiPre-alt-Armor.ini

        # album is written by cwd/piwiPre.ini and reset in cwd/TRIAGE
        self.assert_config(armor_conf, 'album', 'ALBUM')

        # piwigo-user should be set in cwd/TRIAGE, but overwritten by cwd/TRIAGE/Armor
        self.assert_config(armor_conf, 'piwigo-user', 'unknown-user')
        self.assert_config(armor_conf, 'remote-user', 'None')

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_2(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')

        LOGGER.msg('testing --licence etc')
        pwp_main(['--chdir', 'tests/results', '--licence', '--version'])
        # PwpLicence.print()
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        # verify visual output, mainly to get coverage higher
        self.done(mn)

    def program_3(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        ACTOR.mkdirs('tests/results')
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('testing  --help')
        LOGGER.msg('')
        pwp_main(['--chdir', 'tests/results', '--help'])
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_4(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')

        LOGGER.msg('')
        LOGGER.msg('testing --ini-file, all behaviors')
        LOGGER.msg('')
        ACTOR.rmtree("tests/results")
        ACTOR.copytree("tests/sources/TRIAGE2/Armor-cup", "tests/results/TRIAGE/Armor-cup")
        ACTOR.copy('tests/sources/piwiPre-alt.ini', "tests/results")
        ACTOR.copy('tests/sources/piwiPre-alt-Armor.ini', "tests/results/TRIAGE/Armor-cup/piwiPre-alt.ini")
        ACTOR.copy('tests/sources/piwiPre.ini', "tests/results")

        config = pwp_main(['--chdir', 'tests/results', '--ini-file', 'piwiPre-alt.ini'])  # , '--debug'])

        # let's verify the alternative .ini has been used, even in subdirectories.
        # the album and web changes are in cwd
        # the date change is in Armor-cup

        self.assert_config(config, 'album', 'LOCAL-ALBUM')
        self.assert_config(config, 'piwigo-user', 'Foo')
        self.assert_no_file('tests/results/ALBUM/2023/2023-06-Juin-11-Forêt-de-la-Corbière/' +  # noqa
                            '2023-06-11-17h02-26-Forêt-de-la-Corbière.jpg')  # noqa
        self.assert_no_file('tests/results/ALBUM/2023/2023-06-Juin-11-Forêt-de-la-Corbière/' +  # noqa
                            '2023-06-11-17h02-26-Forêt-de-la-Corbière.jpg')  # noqa

        LOGGER.msg(f"cwd  = '{os.getcwd()}' ")

        self.assert_dir('tests/results')  # noqa
        self.assert_dir('tests/results/LOCAL-ALBUM')  # noqa
        self.assert_dir('tests/results/LOCAL-ALBUM/2023')  # noqa
        self.assert_dir('tests/results/LOCAL-ALBUM/2023/2023-08-Aug-30-Armor-cup')  # noqa

        self.assert_file('tests/results/LOCAL-ALBUM/2023/2023-08-Aug-30-Armor-cup/' +  # noqa
                         '2023-08-30-11h05-44-Armor-cup.jpg')  # noqa
        self.assert_file('tests/results/LOCAL-ALBUM/2023/2023-08-Aug-30-Armor-cup/' +  # noqa
                         '2023-08-30-11h13-50-Armor-cup.jpg')  # noqa
        self.assert_file('tests/results/LOCAL-ALBUM/2023/2023-08-Aug-30-Armor-cup/' +  # noqa
                         '2023-08-30-11h31-28-Armor-cup.jpg')  # noqa
        self.assert_file('tests/results/LOCAL-WEB/2023/2023-08-Aug-30-Armor-cup/' +  # noqa
                         '2023-08-30-11h05-44-Armor-cup-cu_e250.jpg')  # noqa
        LOGGER.msg(f'--------------- end of  {mn}')
        self.done(mn)

    def program_10(self):
        initial_cwd = os.getcwd()
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('autotest of ArgsIni')
        os.chdir('tests/argsini')    # noqa
        args_ini_main(['--auto-test', '--verify-albums', 'fifi', '--verify-albums', 'toto'])
        os.chdir(initial_cwd)
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_11(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('autotest of pwpPatcher')
        ACTOR.rmtree("tests/results")
        ACTOR.mkdirs("tests/results")
        # this test must be executed, like pwpPatcher, from piwPre root
        patcher_main(['--autotest'])
        self.assert_file_contains('tests/results/pwpLicence.py.autotest', 'EUROPEAN UNION PUBLIC LICENCE')
        self.assert_file_contains('tests/results/pwpVersion.py.autotest', 'class PwpVersion:')
        self.assert_file('tests/results/version.txt.autotest')
        self.assert_file_contains('tests/results/configuration.rst.autotest', '**enable-rotation** : true')
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def get_first_album(self):
        LOGGER.msg('')
        LOGGER.msg('if run by the developer, will verify album "2023/2023-01-Janvier-08-Ballade"')  # noqa
        LOGGER.msg("if run in a different context, will run the first sub-album in album")
        LOGGER.msg("If no piwigo-host/user defined, will abort")
        LOGGER.msg('')

        if self.home_config['piwigo-host'] is None or self.home_config['piwigo-user'] is None:
            LOGGER.msg("No piwigo-host/user defined, aborting")
            return None
        album = self.home_config['album']
        if os.path.isdir(album):
            return "2023/2023-01-Janvier-08-Ballade"  # noqa

        if not os.path.isdir(album):
            return None

        all_files = os.listdir(album)
        for it in all_files:
            if os.path.isdir(album + '/' + it):
                return it
        return None

    def program_12(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('autotest of piwigo synchronisation')
        ACTOR.rmtree("tests/results")
        ACTOR.mkdirs("tests/results")
        # fallback to HOME for piwigo information

        src = self.get_first_album()
        if src:
            pwp_main(['--chdir', 'tests/results', '--test-piwigo-synchronization', src])
            self.assert_info(f"dir '{src}' synchronized with piwigo")
        else:
            LOGGER.msg("aborting test")

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')

        self.done(mn)

    def program_13(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('autotest of PwpParser')
        os.chdir('tests/argsini')    # noqa
        pwp_parser_main([])
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        # self.done(mn) useless, and test/results does not exist

    def program_14(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('autotest of mp4 management')
        LOGGER.msg('')
        ACTOR.rmtree("tests/results")
        ACTOR.mkdirs("tests/results")
        mp4_main(['-p'])
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_15(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('Error generation')
        seen = False
        try:
            pwp_main(['--chdir', '--ini-file', 'piwiPre-alt.ini'])
        except PwpConfigError:
            seen = True
        assert seen, "program_26 should have generated a PwpConfigError"

        LOGGER.msg(f'--------------- end of  {mn}')
        self.done(mn)

    def program_16(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('autotest of of parse_requirements')
        run_requirements([])
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_17(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('Errors in parse_requirements')
        ACTOR.copytree("tests/sources/TRIAGE", "tests/results/TRIAGE")
        ACTOR.copy("tests/sources/piwiPre-error.ini", "tests/results/piwiPre.ini")
        initial_cwd = os.getcwd()

        done = False
        try:
            main = pwp_init(['--chdir', 'tests/results'])
            pwp_run(main)
        except PwpConfigError:
            done = True
            LOGGER.msg("Correctly generated 'ERROR Illegal configuration item'")
            os.chdir(initial_cwd)  # otherwise self.done does not work

        assert done, "test program should have generated an error"

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    # =====================================================================================================
    # ==================================  30 : Starting tests for TRIAGE Stage, with local ALBUM

    def program_30(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('sources/TRIAGE -> ALBUM, WEB')
        self.reset_data()
        ACTOR.rmtree("tests/results")
        ACTOR.copytree("tests/sources/TRIAGE", "tests/results/TRIAGE")
        ACTOR.copy("tests/sources/piwiPre-local.ini", "tests/results/piwiPre.ini")

        main = pwp_init(['--chdir', 'tests/results'])  # , '--debug'])
        pwp_run(main)
        self.assert_file('tests/results/ALBUM/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg')     # noqa
        jpg = PwpJpg('tests/results/ALBUM/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg')  # noqa
        self.assert_copyright(jpg, "(C) 2023 by Agnes BATTINI, for test")  # noqa
        self.assert_author(jpg,  "Agnes BATTINI")
        self.assert_special(jpg, "No copy allowed unless explicitly approved by Agnes BATTINI")

        self.assert_orientation(jpg, 1)

        self.assert_file('tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup-me.jpg')  # noqa
        self.assert_file('tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup-sq.jpg')  # noqa
        self.assert_file('tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup-th.jpg')  # noqa
        self.assert_file('tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup-cu_e250.jpg')  # noqa
        self.assert_file('tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/index.htm')                             # noqa

        self.assert_file('tests/results/ALBUM/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup.jpg')     # noqa
        self.assert_no_file('tests/results/ALBUM/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-46-Armor-cup.jpg')  # noqa

        LOGGER.msg('')
        LOGGER.msg('------- end of Step 1 of pwp_test(1)')
        LOGGER.msg('')
        # 2d run of pwp_main.
        # we keep the ALBUM etc but change TRIAGE
        # we add new files
        #       Armor-cup/20230617_111349-new.jpg
        #       Armor-cup/20230617_113128-new.jpg
        #       Forêt-de-la-Corbière/IMG20230611164005-new.jpg    # noqa
        #       Forêt-de-la-Corbière/IMG20230611163210-new.jpg    # noqa
        # and keep some old ones
        #       Armor-cup/20230617_110544-copy
        #       Forêt-de-la-Corbière/20230611_170225-copy.jpg     # noqa
        #       Forêt-de-la-Corbière/IMG20230611162736-copy.jpg   # noqa

        self.reset_data()  # before any action, e.g. rmtree

        ACTOR.rmtree("tests/results/Triages")
        ACTOR.copytree("tests/sources/TRIAGE2/", "tests/results/TRIAGE")
        main = pwp_init(['--chdir', 'tests/results'])  # , '--debug'])
        pwp_run(main)
        # if the following file was present, it means that same file detection  is broken
        self.assert_no_file('tests/results/ALBUM/2023/2023-06-Juin-11-Forêt-de-la-Corbière/' +  # noqa
                       '2023-06-11-17h02-26-Forêt-de-la-Corbière.jpg')                          # noqa
        # if the following file was present,
        # it would mean that same file detection with albums is broken
        self.assert_no_file('tests/results/ALBUM/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-46-Armor-cup.jpg')  # noqa
        # the 2 new files should be there
        self.assert_file('tests/results/ALBUM/2023/2023-06-Juin-11-Forêt-de-la-Corbière/' +     # noqa
                    '2023-06-11-16h32-10-Forêt-de-la-Corbière.jpg')                             # noqa
        self.assert_file('tests/results/ALBUM/2023/2023-06-Juin-11-Forêt-de-la-Corbière/' +     # noqa
                    '2023-06-11-16h40-05-Forêt-de-la-Corbière.jpg')                             # noqa

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')

        self.done(mn)

    def program_31(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('sources/TRIAGE -> ALBUM, WEB --enable-rename FALSE')
        LOGGER.msg('')

        self.reset_data()
        ACTOR.rmtree("tests/results")
        ACTOR.copytree("tests/sources/TRIAGE", "tests/results/TRIAGE")
        ACTOR.copy("tests/sources/piwiPre-local.ini", "tests/results/piwiPre.ini")

        main = pwp_init(['--chdir', 'tests/results', '--enable-rename', 'false'])  # , '--debug'])
        pwp_run(main)
        self.assert_no_file('tests/results/ALBUM/2023/2023-06-Juin-17-Armor-cup/' +                  # noqa
                            '2023-06-17-11h05-44-Armor-cup.jpg')                                     # noqa
        self.assert_file('tests/results/ALBUM/Armor-cup/20230617_110544.jpg')
        jpg = PwpJpg('tests/results/ALBUM/Armor-cup/20230617_110544.jpg')
        self.assert_orientation(jpg, 1)
        self.assert_copyright(jpg, '2023')
        self.assert_special(jpg, 'No copy allowed unless explicitly approved by')

        LOGGER.msg('')
        LOGGER.msg(f'--------------- end of  {mn}')
        self.done(mn)

    def program_32(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()   # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('management of mp4 in TRIAGE, including copyright set')
        LOGGER.msg(f"cwd = {os.getcwd()}")
        ACTOR.rmtree("tests/results")

        ACTOR.copytree(f"tests/sources/TRIAGE3/Vendée", f"tests/results/TRIAGE/Vendée")                     # noqa
        ACTOR.copy("tests/sources/piwiPre-local.ini", "tests/results/piwiPre.ini")                          # noqa
        pwp_main(['--chdir', 'tests/results'])                                                              # noqa
        photo= "tests/results/ALBUM/2023"                                                                   # noqa
        self.assert_file(f"{photo}/2023-07-Juillet-04-Vendée/2023-07-04-12h53-07-Vendée.jpg")               # noqa
        self.assert_file(f"{photo}/2023-07-Juillet-02-Vendée/2023-07-02-14h00-00-Comments.txt")             # noqa
        self.assert_file(f"{photo}/2023-01-Janvier-27-Vendée/2023-01-27-17h59-39-Vendée.mp4")             # noqa

        mp4 = PwpMp4(f"{photo}/2023-01-Janvier-27-Vendée/2023-01-27-17h59-39-Vendée.mp4")              # noqa
        self.assert_mp4_copyright(mp4, "(C) 2023 by Famille BATTINI, for test")

        web = "tests/results/WEB/2023/2023-07-Juillet-04-Vendée"                                     # noqa
        self.assert_file(f"{web}/2023-07-04-12h53-07-Vendée-th.jpg")                                 # noqa
        self.assert_file(f"{web}/2023-07-04-12h53-07-Vendée-me.jpg")                                 # noqa
        self.assert_file(f"{web}/2023-07-04-12h53-07-Vendée-cu_e250.jpg")                            # noqa

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_33(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('Verifying dates, from TRIAGE2/Forêt-de-la-Corbière')                        # noqa
        LOGGER.msg('')

        ACTOR.rmtree("tests/results")
        ACTOR.copytree("tests/sources/TRIAGE2/Forêt-de-la-Corbière",                            # noqa
                       "tests/results/TRIAGE/Forêt-de-la-Corbière")                             # noqa
        ACTOR.copytree("tests/sources/TRIAGE4/Thabor",                                          # noqa
                   "tests/results/TRIAGE/Forêt-de-la-Corbière")                                 # noqa

        ACTOR.copy("tests/sources/piwiPre-dates.ini", "tests/results/piwiPre.ini")
        pwp_main(['--chdir', 'tests/results'])

        # Forest, SM-A336B: +4h
        self.assert_file("tests/results/ALBUM/2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +      # noqa
                         "2023-06-11-21h02-25-Forêt-de-la-Corbière.jpg")                         # noqa
        # noqa Thabor, C4100Z,C4000Z: absolute date
        self.assert_file("tests/results/ALBUM/2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +      # noqa
                         "2023-06-11-14h24-38-Forêt-de-la-Corbière.jpg")                         # noqa
        self.assert_file("tests/results/ALBUM/2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +      # noqa
                         "2023-06-11-14h25-06-Forêt-de-la-Corbière.jpg")                         # noqa
        # NO-DATE
        self.assert_file("tests/results/ALBUM/2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +      # noqa
                         "Comments.txt")
        # Forest OPPOReno2 : -6h
        self.assert_file("tests/results/ALBUM/2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +      # noqa
                         "2023-06-11-10h32-10-Forêt-de-la-Corbière.jpg")                         # noqa

        LOGGER.msg(f'--------------- end of  {mn}')
        self.done(mn)

    def program_34(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('dryrun, sources/TRIAGE -> ALBUM, WEB, album')
        ACTOR.rmtree("tests/results")
        ACTOR.copytree("tests/sources/TRIAGE", "tests/results/TRIAGE")
        ACTOR.copy("tests/sources/piwiPre-local.ini", "tests/results/piwiPre.ini")
        ACTOR.copy("tests/sources/piwiPre-corse.ini", "tests/results/TRIAGE/Corse/piwiPre.ini")         # noqa

        main = pwp_init(['--chdir', 'tests/results', '--dryrun'])  # , '--debug'])
        pwp_run(main)
        self.assert_no_dir("tests/results/ALBUM")
        self.assert_no_dir("tests/results/WEB")
        self.assert_no_dir("tests/results/BACKUP")
        self.assert_info("Would rename 'TRIAGE/Armor-cup/20230617_110544.jpg' : " +
                    "'ALBUM/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg'")        # noqa

        # CAVEAT: conflict management has NOT occurred, because the files are not created in ALBUM thanks to dryrun
        #         So we do *not* know te exact thumbnail name
        #         hence the message is not accurate
        self.assert_info("Would create Thumbnail 120x120 crop=True " +
                    "for TRIAGE/Armor-cup/20230617_110544")                                    # noqa

        self.assert_info("Would create Thumbnail 120x120 crop=True " +
                         "for TRIAGE/Corse/IMG-20200517-WA0000.jpg")                           # noqa
        self.assert_info("Would create Thumbnail 120x120 crop=True " +
                         "for TRIAGE/Corse/IMG-20210818-WA0000.jpg")                           # noqa
        self.assert_info("Would create Thumbnail 120x120 crop=True " +
                         "for TRIAGE/Corse/IMG-20210819-WA0004 - Copie.jpg")                   # noqa
        self.assert_info("Would create Thumbnail 120x120 crop=True " +
                         "for TRIAGE/Corse/IMG-20210819-WA0004.jpg")                           # noqa

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_35(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('sources/TRIAGE -> ALBUM, WEB + corse.ini')      # noqa
        ACTOR.rmtree("tests/results")
        ACTOR.copytree("tests/sources/TRIAGE", "tests/results/TRIAGE")
        ACTOR.copy("tests/sources/piwiPre-local.ini", "tests/results/piwiPre.ini")
        ACTOR.copy("tests/sources/piwiPre-corse.ini", "tests/results/TRIAGE/Corse/piwiPre.ini")  # noqa

        main = pwp_init(['--chdir', 'tests/results'])  # , '--debug'])
        pwp_run(main)
        self.assert_dir("tests/results/ALBUM")
        self.assert_dir("tests/results/WEB")
        self.assert_dir("tests/results/BACKUP")
        self.assert_file("tests/results/ALBUM/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg")  # noqa
        self.assert_file("tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup-sq.jpg")  # noqa

        self.assert_file("tests/results/ALBUM/Corsica/2020-05-17-12h00-00-Corsica.jpg")
        self.assert_file("tests/results/ALBUM/Corsica/2021-08-18-12h00-00-Corsica.jpg")
        self.assert_file("tests/results/ALBUM/Corsica/2021-08-19-12h04-00-Corsica.jpg")
        self.assert_file("tests/results/ALBUM/Corsica/2021-08-19-12h04-01-Corsica.jpg")

        self.assert_file("tests/results/WEB/Corsica/2021-08-19-12h04-00-Corsica-sq.jpg")
        self.assert_file("tests/results/WEB/Corsica/2021-08-19-12h04-00-Corsica-me.jpg")

        self.assert_file("tests/results/WEB/Corsica/2021-08-19-12h04-01-Corsica-th.jpg")
        self.assert_file("tests/results/WEB/Corsica/2021-08-19-12h04-01-Corsica-cu_e250.jpg")

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_36(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('sources/TRIAGE -> ALBUM, WEB + autoconfig, prepare program_37')  # noqa
        ACTOR.rmtree("tests/results")
        ACTOR.copytree("tests/sources/TRIAGE/Armor-cup", "tests/results/TRIAGE/Armor-cup")
        ACTOR.copytree("tests/sources/TRIAGE/Corse", "tests/results/TRIAGE/Corse")              # noqa

        ACTOR.copy("tests/sources/piwiPre-autoconfig.ini", "tests/results/TRIAGE/Armor-cup/piwiPre.ini")
        ACTOR.copy("tests/sources/piwiPre-autoconfig.ini", "tests/results/TRIAGE/Corse/piwiPre.ini") # noqa

        pwp_main(['--chdir', 'tests/results'])

        # we verify that all renamed images, most thumbnails and most piwiPre.ini autoconf files are there.

        self.assert_file("tests/results/ALBUM/2023/06/17/Armor-cup-001.jpg")     # noqa
        self.assert_file("tests/results/WEB/2023/06/17/Armor-cup-001-sq.jpg")    # noqa
        self.assert_file("tests/results/ALBUM/2023/06/17/piwiPre.ini")           # noqa

        self.assert_file("tests/results/ALBUM/2023/06/17/Armor-cup-002.jpg")     # noqa
        self.assert_file("tests/results/WEB/2023/06/17/Armor-cup-002-sq.jpg")    # noqa

        self.assert_no_file("tests/results/ALBUM/2023/06/17/Armor-cup-003.jpg")  # noqa

        self.assert_file("tests/results/ALBUM/2020/05/17/Corse-001.jpg")         # noqa
        self.assert_file("tests/results/WEB/2020/05/17/Corse-001-sq.jpg")        # noqa
        self.assert_file("tests/results/ALBUM/2020/05/17/piwiPre.ini")           # noqa

        self.assert_file("tests/results/ALBUM/2021/08/18/Corse-001.jpg")         # noqa
        self.assert_file("tests/results/WEB/2021/08/18/Corse-001-th.jpg")        # noqa
        self.assert_file("tests/results/ALBUM/2021/08/18/piwiPre.ini")         # noqa

        self.assert_file("tests/results/ALBUM/2021/08/19/Corse-001.jpg")         # noqa
        self.assert_file("tests/results/WEB/2021/08/19/Corse-001-me.jpg")        # noqa

        self.assert_file("tests/results/ALBUM/2021/08/19/Corse-002.jpg")         # noqa

        # verify that the.ini files have been modified with the right base:

        self.assert_file_contains("tests/results/ALBUM/2023/06/17/piwiPre.ini",
                                  "names: '{Y}/{m}/{d}/Armor-cup-{count}.{suffix}'")

        self.assert_file_contains("tests/results/ALBUM/2020/05/17/piwiPre.ini",
                                  "names: '{Y}/{m}/{d}/Corse-{count}.{suffix}'")           # noqa

        self.done(mn)

    def program_37(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        if not self.check_done('program_36'):
            self.program_36()

        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('sources/TRIAGE -> ALBUM, WEB + autoconfig')  # noqa

        # remove a thumbnail, do a verify-albums and check
        # files have not changed
        # thumbnail is there again

        ACTOR.delete("tests/results/WEB/2023/06/17/Armor-cup-001-sq.jpg")

        pwp_main(['--chdir', 'tests/results',
                  '--album', 'ALBUM',
                  '--verify-albums', '2023/06/17'])

        self.assert_file("tests/results/ALBUM/2023/06/17/Armor-cup-001.jpg")  # noqa
        self.assert_file("tests/results/WEB/2023/06/17/Armor-cup-001-sq.jpg")  # noqa
        self.assert_file("tests/results/ALBUM/2023/06/17/piwiPre.ini")  # noqa

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')

    # =====================================================================================================
    # ================================= 100: Managing the real 'network share' location

    def runner_100(self, album, web, remote_web=None, delete=True):

        ACTOR.rmtree("tests/results")
        assert album[-5:] == 'tests'
        ACTOR.rmtree(album)
        assert web[-5:] == 'tests'
        ACTOR.rmtree(web)

        ACTOR.copy("tests/sources/piwiPre-mount.ini", "tests/results/piwiPre.ini")
        ACTOR.copytree("tests/sources/TRIAGE/Armor-cup", "tests/results/TRIAGE/Armor-cup")

        LOGGER.msg(f"album         = {album}")
        LOGGER.msg(f"web           = {web}")
        LOGGER.msg(f"remote web    = {remote_web}")

        remote = "true" if remote_web else 'false'

        pwp_main(['--chdir', 'tests/results', '--album', album, '--web', web, '--remote-web', str(remote_web),
                  '--enable-remote-copy', remote,
                  '--enable-piwigo-sync', 'false'])

        if album[0] != '/':
            # album is a path relative to cwd, which was changed to 'tests/results'
            album = 'tests/results/' + album
        self.assert_file(album + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup.jpg')  # noqa
        self.assert_file(album + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg')  # noqa
        self.assert_no_file(album + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-46-Armor-cup.jpg')  # noqa

        if web[0] != '/':
            # album is a path relative to cwd, which was changed to 'tests/results'
            web = 'tests/results/' + web
        self.assert_file(web + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup-me.jpg')  # noqa
        self.assert_file(web + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup-me.jpg')  # noqa
        self.assert_file(web + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup-th.jpg')  # noqa
        self.assert_file(web + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup-th.jpg')  # noqa
        self.assert_file(web + '/2023/2023-06-Juin-17-Armor-cup/index.htm')  # noqa

        if remote_web:
            # always an absolute path
            self.assert_remote_file(remote_web + '/2023/2023-06-Juin-17-Armor-cup/' +           # noqa
                                            '2023-06-17-11h05-45-Armor-cup-me.jpg')
            self.assert_remote_file(remote_web + '/2023/2023-06-Juin-17-Armor-cup/' +           # noqa
                                            '2023-06-17-11h05-44-Armor-cup-me.jpg')
            self.assert_remote_file(remote_web + '/2023/2023-06-Juin-17-Armor-cup/' +           # noqa
                                            '2023-06-17-11h05-45-Armor-cup-th.jpg')
            self.assert_remote_file(remote_web + '/2023/2023-06-Juin-17-Armor-cup/' +           # noqa
                                            '2023-06-17-11h05-44-Armor-cup-th.jpg')
            self.assert_remote_file(remote_web + '/2023/2023-06-Juin-17-Armor-cup/' +           # noqa
                                            'index.htm')

        if delete:
            ACTOR.rmtree(album)
            ACTOR.rmtree(web)
            if remote_web:
                assert remote_web[-5:] == 'tests'
                ACTOR.rmtree(remote_web)

    def program_100(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')

        album = 'ALBUM/tests'
        web = 'WEB/tests'

        self.runner_100(album, web)

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_101(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        # the same test as the previous, but we use the real location home_config['album']

        LOGGER.msg(f'--------------- starting {mn}')

        album = self.home_config['album'] + '/tests'
        web = self.home_config['web'] + '/tests'
        LOGGER.msg("")
        LOGGER.msg(f"tests/sources/ to '{album}' which is read from HOME/.piwiPre.ini")
        LOGGER.msg("piwigo http admin information (login, password...) SHOULD be available from there")
        LOGGER.msg("")

        self.runner_100(album, web)

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def reset_102(self):
        if os.path.isfile(self.run_file):
            ACTOR.delete(self.run_file)

        album = self.home_config['album'] + '/2023'
        if os.path.isdir(album):
            all_files = os.listdir(album)
            for f in all_files:
                m = re.match(r"2023-06-Juin-17-Armor\d+", f)
                if m:
                    ACTOR.rmtree(album + '/' + f)

        web = self.home_config['web'] + '/2023'
        if os.path.isdir(web):
            all_files = os.listdir(web)
            for f in all_files:
                m = re.match(r"Armor\d+", f)
                if m:
                    ACTOR.rmtree(web + '/' + f)

    def runner_102(self, piwigo_sync: bool):
        album = self.home_config['album']
        web = self.home_config['web']

        LOGGER.msg(f"TRIAGE3 -> {album}, piwigo sync {piwigo_sync}")
        LOGGER.msg("")
        LOGGER.msg(f"album='{album}' is read from HOME/.piwiPre.ini")
        LOGGER.msg("This SHOULD be your remote server used for test")
        LOGGER.msg("and other remote information (login, password...) SHOULD be available from there")
        LOGGER.msg("")

        if piwigo_sync and (self.home_config['piwigo-host'] is None or self.home_config['piwigo-user'] is None):
            LOGGER.msg("piwigo-host or piwigo-user not set, aborting test")
            return

        # run_file is used for debugging purposes
        # we can run runner_102 several times, it will generate files in separate directories
        # if we run program_0, e.g. for tox, then everything is reset
        if os.path.isfile(self.run_file):
            with open(self.run_file, 'r', encoding="utf-8") as f:
                all_lines = f.readlines()
            first = all_lines[0].strip()
        else:
            first = 0
        number = int(first) + 1
        with open(self.run_file, 'w', encoding="utf-8") as f:
            f.write(f"{number}\n")
            f.write("# Run number for test program 102\n")
        LOGGER.msg(f"Run number = '{number}'")
        self.reset_data()
        ACTOR.rmtree("tests/results")
        ACTOR.copytree(f"tests/sources/TRIAGE/Armor-cup", f"tests/results/TRIAGE/Armor{number}")               # noqa
        ACTOR.copy("tests/sources/piwiPre-mount.ini", "tests/results/piwiPre.ini")                           # noqa
        pwp_main(['--chdir', 'tests/results', '--enable-piwigo-sync', 'true' if piwigo_sync else 'false',     # noqa
                  '--album', album, '--web', web])

        if album[0] != '/':
            # album is a path relative to cwd, which was changed to 'tests/results'
            album = 'tests/results/' + album

        photo= f"{album}/2023/2023-06-Juin-17-Armor{number}"                                                  # noqa
        self.assert_file(f"{photo}/2023-06-17-11h05-44-Armor{number}.jpg")                                    # noqa
        self.assert_file(f"{photo}/2023-06-17-11h05-45-Armor{number}.jpg")                                    # noqa

        if web[0] != '/':
            # album is a path relative to cwd, which was changed to 'tests/results'
            web = 'tests/results/' + web

        web=f"{web}/2023/2023-06-Juin-17-Armor{number}"                                                       # noqa
        self.assert_file(f"{web}/2023-06-17-11h05-44-Armor{number}-th.jpg")                                   # noqa
        self.assert_file(f"{web}/2023-06-17-11h05-44-Armor{number}-me.jpg")                                   # noqa
        self.assert_file(f"{web}/2023-06-17-11h05-44-Armor{number}-cu_e250.jpg")                              # noqa
        self.assert_not_info("not in piwigo managed directories")
        if piwigo_sync:
            self.assert_info(f"dir '2023/2023-06-Juin-17-Armor{number}' synchronized ")                    # noqa
        return number

    def program_102(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        self.runner_102(False)
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_103(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        self.runner_102(True)
        self.done(mn)

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.reset_done('program_102')

    # =====================================================================================================
    # ------------ 200 : Starting tests for --verify-albums

    def assert_complete(self, config, album, web, remote_web, dst: str, year, src=None):
        if album[0] != '/':
            # album is a path relative to cwd, which was changed to 'tests/results'
            abs_album = 'tests/results/' + album
        else:
            abs_album = album

        self.assert_file(abs_album + '/' + dst)
        if src:
            self.assert_info("RENAME: '" + src + "' : '" +  album + "/" + dst + "'")  # noqa

        jpg = PwpJpg(abs_album + '/' + dst)  # noqa
        self.assert_orientation(jpg, 1)
        self.assert_copyright(jpg, year)
        self.assert_special(jpg, 'No copy allowed unless explicitly approved by')

        if web[0] != '/':
            # web is a path relative to cwd, which was changed to 'tests/results'
            abs_web = 'tests/results/' + web
        else:
            abs_web = web

        thumbs = config['piwigo-thumbnails']

        base = dst[:-4]   # remove .jpg
        for name, values in thumbs.items():
            thumb_name = name.format(f=base)
            self.assert_file(abs_web + '/' + thumb_name)
            if remote_web:
                ACTOR.remote_isfile(remote_web + '/' + dst)

    def verify_200(self, album: str, web: str, with_src: bool, remote_web=None):
        self.assert_complete(self.home_config, album, web, remote_web,
                             "2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg", '2023')  # noqa
        self.assert_complete(self.home_config, album, web, remote_web,
                             "2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup.jpg", '2023')  # noqa

        self.assert_complete(self.home_config, album, web, remote_web,
                             "Corsica/2020-05-17-12h00-00-Corsica.jpg", '2020',
                             src='TRIAGE/Corse/IMG-20200517-WA0000.jpg' if with_src else None)                   # noqa
        self.assert_complete(self.home_config, album, web, remote_web,
                             "Corsica/2021-08-18-12h00-00-Corsica.jpg", '2021',   # noqa
                             src='TRIAGE/Corse/IMG-20210818-WA0000.jpg' if with_src else None)                   # noqa
        self.assert_complete(self.home_config, album, web, remote_web,
                             "Corsica/2021-08-19-12h04-00-Corsica.jpg", '2021',   # noqa
                             src='TRIAGE/Corse/IMG-20210819-WA0004 - Copie.jpg' if with_src else None)           # noqa
        self.assert_complete(self.home_config, album, web, remote_web,
                             "Corsica/2021-08-19-12h04-01-Corsica.jpg", '2021',   # noqa
                             src='TRIAGE/Corse/IMG-20210819-WA0004.jpg' if with_src else None)                   # noqa

        self.assert_complete(self.home_config, album, web, remote_web,
                             "2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +                # noqa
                             "2023-06-11-16h28-04-Forêt-de-la-Corbière.jpg", '2023',  # noqa
                             src='TRIAGE/Forêt-de-la-Corbière/20230611_162803.jpg' if with_src else None)        # noqa
        self.assert_complete(self.home_config, album, web, remote_web,
                             "2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +                # noqa
                             "2023-06-11-16h28-11-Forêt-de-la-Corbière.jpg", '2023',  # noqa
                             src='TRIAGE/Forêt-de-la-Corbière/20230611_162811.jpg' if with_src else None)        # noqa
        self.assert_complete(self.home_config, album, web, remote_web,
                             "2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +                # noqa
                             "2023-06-11-16h28-17-Forêt-de-la-Corbière.jpg", '2023',  # noqa
                             src='TRIAGE/Forêt-de-la-Corbière/20230611_162816.jpg' if with_src else None)        # noqa
        self.assert_complete(self.home_config, album, web, remote_web,
                             "2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +                # noqa
                             "2023-06-11-17h02-16-Forêt-de-la-Corbière.jpg", '2023',  # noqa
                             src='TRIAGE/Forêt-de-la-Corbière/20230611_170215.jpg' if with_src else None)        # noqa
        self.assert_complete(self.home_config, album, web, remote_web,
                             "2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +                # noqa
                             "2023-06-11-17h02-25-Forêt-de-la-Corbière.jpg", '2023',  # noqa
                             src='TRIAGE/Forêt-de-la-Corbière/20230611_170225.jpg' if with_src else None)        # noqa
        self.assert_complete(self.home_config, album, web, remote_web,
                             "2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +                  # noqa
                             "2023-06-11-16h27-36-Forêt-de-la-Corbière.jpg", '2023',    # noqa
                             src='TRIAGE/Forêt-de-la-Corbière/IMG20230611162736.jpg' if with_src else None)        # noqa

    def runner_200(self, album, web, with_src: bool, remote_web=None, _delete=False):
        LOGGER.msg(f"album         = {album}")
        LOGGER.msg(f"web           = {web}")
        LOGGER.msg(f"remote web    = {remote_web}")

        ACTOR.copytree("tests/sources/TRIAGE", "tests/results/TRIAGE")
        ACTOR.copy("tests/sources/piwiPre-mount.ini", "tests/results/piwiPre.ini")
        ACTOR.copy("tests/sources/piwiPre-corse.ini", "tests/results/TRIAGE/Corse/piwiPre.ini")  # noqa

        remote = "true" if remote_web else 'false'

        main = pwp_init(['--chdir', 'tests/results', '--album', album, '--web', web, '--remote-web', str(remote_web),
                         '--enable-remote-copy', remote,  # '--debug',
                         '--enable-piwigo-sync', 'false'])
        pwp_run(main)

        # OR: depends on the order of files processing

        self.assert_info_or(["RENAME: 'TRIAGE/Armor-cup/20230617_110544.jpg' : '" +  # noqa
                            album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg'",  # noqa
                            "RENAME: 'TRIAGE/Armor-cup/20230617_110544.jpg' : '" +  # noqa
                            album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup.jpg'",  # noqa
                            "New file 'TRIAGE/Armor-cup/20230617_110544.jpg' is already in album as '" +
                            album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg'",  # noqa
                            "New file 'TRIAGE/Armor-cup/20230617_110544.jpg' is already in album as '" +
                            album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup.jpg'"])  # noqa

        self.assert_info_or(["RENAME: 'TRIAGE/Armor-cup/20230617_110544-copy.jpg' : '" +  # noqa
                             album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg'",  # noqa
                             "RENAME: 'TRIAGE/Armor-cup/20230617_110544-copy.jpg' : '" +  # noqa
                             album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup.jpg'",  # noqa
                             "New file 'TRIAGE/Armor-cup/20230617_110544-copy.jpg' is already in album as '" +
                             album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg'",  # noqa
                             "New file 'TRIAGE/Armor-cup/20230617_110544-copy.jpg' is already in album as '" +
                             album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup.jpg'"])  # noqa

        self.assert_info_or(["RENAME: 'TRIAGE/Armor-cup/20230617_110544-bis.jpg' : '" +  # noqa
                             album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg'",  # noqa
                             "RENAME: 'TRIAGE/Armor-cup/20230617_110544-bis.jpg' : '" +  # noqa
                             album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup.jpg'",  # noqa
                             "New file 'TRIAGE/Armor-cup/20230617_110544-bis.jpg' is already in album as '" +
                             album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg'",  # noqa
                             "New file 'TRIAGE/Armor-cup/20230617_110544-bis.jpg' is already in album as '" +
                             album + "/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup.jpg'"])  # noqa

        self.verify_200(album, web, with_src, remote_web=remote_web)

    def program_200(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('------------ Starting tests for --verify-albums, local config')
        LOGGER.msg('')
        LOGGER.msg('sources/TRIAGE -> ALBUM, WEB')
        LOGGER.msg('')

        album = 'ALBUM/tests'
        web = 'WEB/tests'
        remote_web = None
        ACTOR.rmtree('tests/results')

        ACTOR.copy("tests/sources/piwiPre-local.ini", "tests/results/piwiPre.ini")
        ACTOR.copy("tests/sources/piwiPre-corse.ini", "tests/results/TRIAGE/Corse/piwiPre.ini")  # noqa

        self.runner_200(album, web, with_src=True, remote_web=remote_web)

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def runner_201(self, album, web, remote_web=None, _delete=False):
        LOGGER.msg(f"album         = {album}")
        LOGGER.msg(f"web           = {web}")
        LOGGER.msg(f"remote web    = {remote_web}")
        remote = "true" if remote_web else 'false'

        main = pwp_init(['--chdir', 'tests/results', '--triage', 'None',
                         '--album', album, '--web', web, '--remote-web', str(remote_web),
                         '--enable-remote-copy', remote,  # , '--debug'
                         '--verify-albums', '2023/2023-06-Juin-11-Forêt-de-la-Corbière',   # noqa
                         '--verify-albums', '2023/2023-06-Juin-17-Armor-cup',   # noqa
                         '--verify-albums', 'Corsica'])
        pwp_run(main)

        # nothing should have changed
        self.assert_info("File '" + album + "/2023/2023-06-Juin-11-Forêt-de-la-Corbière" +  # noqa
                         "/2023-06-11-16h27-36-Forêt-de-la-Corbière.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/2023/2023-06-Juin-11-Forêt-de-la-Corbière" +  # noqa
                         "/2023-06-11-16h28-04-Forêt-de-la-Corbière.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/2023/2023-06-Juin-11-Forêt-de-la-Corbière" +  # noqa
                         "/2023-06-11-16h28-11-Forêt-de-la-Corbière.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/2023/2023-06-Juin-11-Forêt-de-la-Corbière" +  # noqa
                         "/2023-06-11-16h28-17-Forêt-de-la-Corbière.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/2023/2023-06-Juin-11-Forêt-de-la-Corbière" +  # noqa
                         "/2023-06-11-17h02-16-Forêt-de-la-Corbière.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/2023/2023-06-Juin-11-Forêt-de-la-Corbière" +  # noqa
                         "/2023-06-11-17h02-25-Forêt-de-la-Corbière.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/2023/2023-06-Juin-17-Armor-cup" +  # noqa
                         "/2023-06-17-11h05-44-Armor-cup.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/2023/2023-06-Juin-17-Armor-cup" +  # noqa
                         "/2023-06-17-11h05-45-Armor-cup.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/Corsica/2020-05-17-12h00-00-Corsica.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/Corsica/2021-08-18-12h00-00-Corsica.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/Corsica/2021-08-19-12h04-00-Corsica.jpg' has not changed")  # noqa
        self.assert_info("File '" + album + "/Corsica/2021-08-19-12h04-01-Corsica.jpg' has not changed")  # noqa

        self.verify_200(album, web, with_src=False, remote_web=remote_web)

    def program_201(self):
        if not self.check_done('program_200'):
            self.program_200()
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('must be executed AFTER pwp_test(200)')
        LOGGER.msg('--verify-albums, without modifications of ALBUM')
        album = 'ALBUM/tests'
        web = 'WEB/tests'
        remote_web = None

        self.runner_201(album, web, remote_web=remote_web)

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def runner_202(self, album, web, remote_web=None, _delete=False):
        LOGGER.msg(f"album         = {album}")
        LOGGER.msg(f"web           = {web}")
        LOGGER.msg(f"remote web    = {remote_web}")
        remote = "true" if remote_web else 'false'

        # directories may be absolute (//NAS/...) or relative to tests/results
        abs_album = album if album[0] == '/' else 'tests/results/' + album
        abs_web = web if web[0] == '/' else 'tests/results/' + web

        # next picture has a bad name
        ACTOR.move(abs_album + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg',  # noqa
                   abs_album + '/2023/2023-06-Juin-17-Armor-cup/P1.jpg')                             # noqa
        # next picture has a bad copyright information, without '2023'
        ACTOR.delete(abs_album + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/' +                     # noqa
                     '2023-06-11-16h27-36-Forêt-de-la-Corbière.jpg')                                              # noqa
        ACTOR.copy('tests/sources/Modified/2023-06-11-16h27-36-Forêt-de-la-Corbière.jpg',                         # noqa
                   abs_album + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/')                        # noqa
        # next picture has a wrong rotation
        ACTOR.delete(abs_album + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/' +                     # noqa
                     '2023-06-11-16h28-17-Forêt-de-la-Corbière.jpg')                                        # noqa
        ACTOR.copy('tests/sources/Modified/2023-06-11-16h28-17-Forêt-de-la-Corbière.jpg',                   # noqa
                   abs_album + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/')                        # noqa
        if remote_web is not None:
            ACTOR.remote_delete(remote_web + "/Corsica/2020-05-17-12h00-00-Corsica-sq.jpg")
        else:
            ACTOR.delete(abs_web + "/Corsica/2020-05-17-12h00-00-Corsica-sq.jpg")                        # noqa

        pwp_main(['--chdir', 'tests/results', '--triage', 'None', '--dryrun',
                 '--album', album, '--web', web, '--remote-web', str(remote_web),
                 '--enable-remote-copy', remote,  # , '--debug'
                 '--verify-albums', '2023/2023-06-Juin-11-Forêt-de-la-Corbière',                   # noqa
                 '--verify-albums', '2023/2023-06-Juin-17-Armor-cup',                              # noqa
                 '--verify-albums', 'Corsica'])                                                    # noqa

        # verify files modified have not been reset to their normal value, because --dryrun

        self.assert_no_file(abs_album + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg')  # noqa
        if remote_web is not None:
            self.assert_no_remote_file(remote_web + '/Corsica/2020-05-17-12h00-00-Corsica-sq.jpg')  # noqa
        else:
            self.assert_no_file(abs_web + '/Corsica/2020-05-17-12h00-00-Corsica-sq.jpg')  # noqa

        jpg = PwpJpg(abs_album + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/' +  # noqa
                     "2023-06-11-16h27-36-Forêt-de-la-Corbière.jpg")  # noqa
        self.assert_no_copyright(jpg, '2023')
        self.assert_no_file("tests/results/BACKUP/2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +  # noqa
                            "2023-06-11-16h27-36-Forêt-de-la-Corbière.jpg")  # noqa

        jpg = PwpJpg(abs_album + "/2023/2023-06-Juin-11-Forêt-de-la-Corbière/" +  # noqa
                     "2023-06-11-16h28-17-Forêt-de-la-Corbière.jpg")  # noqa
        self.assert_no_orientation(jpg, 1)
        self.assert_no_file('tests/results/BACKUP/2023/2023-06-Juin-11-Forêt-de-la-Corbière/' +  # noqa
                            '2023-06-11-16h28-11-Forêt-de-la-Corbière.jpg')  # noqa                                          # noqa

    def program_202(self):
        if not self.check_done('program_200'):
            self.program_200()
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('--verify-albums, --dryrun, with some modifications')
        LOGGER.msg('must be executed AFTER pwp_test(200), or pwp_test(201)')
        LOGGER.msg('')
        ACTOR.rmtree("tests/results/BACKUP")

        album = 'ALBUM/tests'
        web = 'WEB/tests'
        remote_web = None

        self.runner_202(album, web, remote_web=remote_web, _delete=False)

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def runner_203(self, album, web, remote_web=None, _delete=False):
        LOGGER.msg(f"album         = {album}")
        LOGGER.msg(f"web           = {web}")
        LOGGER.msg(f"remote web    = {remote_web}")
        remote = "true" if remote_web else 'false'

        pwp_main(['--chdir', 'tests/results', '--triage', 'None',
                 '--album', album, '--web', web, '--remote-web', str(remote_web),
                 '--enable-remote-copy', remote,  # , '--debug'
                 '--verify-albums', '2023/2023-06-Juin-11-Forêt-de-la-Corbière',                   # noqa
                 '--verify-albums', '2023/2023-06-Juin-17-Armor-cup',                              # noqa
                 '--verify-albums', 'Corsica'])                                                    # noqa

        self.verify_200(album, web, with_src=False, remote_web=remote_web)

    def program_203(self):
        if not self.check_done('program_202'):
            self.program_202()
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('--verify-albums, with some modifications, without dryrun')
        LOGGER.msg('MUST be executed AFTER pwp_test(202)')
        LOGGER.msg('')

        album = 'ALBUM/tests'
        web = 'WEB/tests'
        remote_web = None

        self.runner_203(album, web, remote_web=remote_web)

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def runner_204(self, album, web, remote_web=None, _delete=False):
        LOGGER.msg(f"album         = {album}")
        LOGGER.msg(f"web           = {web}")
        LOGGER.msg(f"remote web    = {remote_web}")
        remote = "true" if remote_web else 'false'

        # directories may be absolute (//NAS/...) or relative to tests/results
        abs_web = web if web[0] == '/' else 'tests/results/' + web

        if remote_web is not None:
            ACTOR.remote_create(remote_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/foo-sq.jpg')  # noqa
            ACTOR.remote_create(remote_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/bat-th.jpg')  # noqa
        else:
            ACTOR.create(abs_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/foo-sq.jpg')     # noqa
            ACTOR.create(abs_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/bat-th.jpg')     # noqa

        pwp_main(['--chdir', 'tests/results', '--triage', 'None', '--dryrun',
                  '--album', album, '--web', web, '--remote-web', str(remote_web),
                  '--enable-remote-copy', remote,  # , '--debug'
                  '--verify-albums', '2023/2023-06-Juin-11-Forêt-de-la-Corbière',  # noqa
                  '--useless-thumbnails-delete'])  # noqa

        if remote_web is not None:
            self.assert_remote_file(remote_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/foo-sq.jpg')  # noqa
            self.assert_remote_file(remote_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/bat-th.jpg')  # noqa
        else:
            self.assert_file(abs_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/foo-sq.jpg')      # noqa
            self.assert_file(abs_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/bat-th.jpg')      # noqa

    def program_204(self):
        if not self.check_done('program_200'):
            self.program_200()
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')

        LOGGER.msg('must be executed AFTER pwp_test(200), CAN be executed after 201/202/203')
        LOGGER.msg('--verify-album --useless-thumbnails-delete, with modification, --dryrun')

        album = 'ALBUM/tests'
        web = 'WEB/tests'
        remote_web = None

        self.runner_204(album, web, remote_web=remote_web)

        LOGGER.msg(f'--------------- end of  {mn}')
        self.done(mn)

    def runner_205(self, album, web, remote_web=None, _delete=False):
        LOGGER.msg(f"album         = {album}")
        LOGGER.msg(f"web           = {web}")
        LOGGER.msg(f"remote web    = {remote_web}")
        remote = "true" if remote_web else 'false'

        # directories may be absolute (//NAS/...) or relative to tests/results
        abs_web = web if web[0] == '/' else 'tests/results/' + web

        pwp_main(['--chdir', 'tests/results', '--triage', 'None',
                  '--album', album, '--web', web, '--remote-web', str(remote_web),
                  '--enable-remote-copy', remote,
                  '--verify-albums', '2023/2023-06-Juin-11-Forêt-de-la-Corbière',  # noqa
                  '--useless-thumbnails-delete'])

        if remote_web is not None:
            self.assert_no_remote_file(remote_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/foo-sq.jpg')  # noqa
            self.assert_no_remote_file(remote_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/bat-th.jpg')  # noqa
        else:
            self.assert_no_file(abs_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/foo-sq.jpg')      # noqa
            self.assert_no_file(abs_web + '/2023/2023-06-Juin-11-Forêt-de-la-Corbière/bat-th.jpg')      # noqa
        self.verify_200(album, web, with_src=False, remote_web=remote_web)

    def program_205(self):
        if not self.check_done('program_204'):
            self.program_204()
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')

        LOGGER.msg('must be executed AFTER pwp_test(204)')
        LOGGER.msg('--verify-album, with modification, WITHOUT dryrun')

        album = 'ALBUM/tests'
        web = 'WEB/tests'
        remote_web = None

        self.runner_205(album, web, remote_web=remote_web)

        # main2 = pwp_init(['--chdir', 'tests/results', '--triage', 'None',
        #                   '--verify-albums', '2023/2023-06-Juin-11-Forêt-de-la-Corbière',                 # noqa
        #                   '--useless-thumbnails-delete'])
        # pwp_run(main2)
        # self.assert_no_file('tests/results/WEB/2023/2023-06-Juin-11-Forêt-de-la-Corbière/foo-sq.jpg')     # noqa
        # self.assert_no_file('tests/results/WEB/2023/2023-06-Juin-11-Forêt-de-la-Corbière/bat-th.jpg')     # noqa
        self.reset_done('program_204')
        self.reset_done('program_203')
        self.reset_done('program_202')
        self.reset_done('program_201')
        self.reset_done('program_200')
        LOGGER.msg(f'--------------- end of  {mn}')
        self.done(mn)

    def program_206(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')

        LOGGER.msg('')
        LOGGER.msg('--building the test case with tests/sources/TRIAGE/Armor-cup ')
        LOGGER.msg('')
        ACTOR.rmtree("tests/results")
        ACTOR.copytree("tests/sources/TRIAGE/Armor-cup", "tests/results/TRIAGE/Armor-cup")
        ACTOR.copy("tests/sources/piwiPre-local.ini", "tests/results/piwiPre.ini")

        # first, we generate the test pattern in ALBUM
        pwp_main(['--chdir', 'tests/results', '--enable-rename', 'true'])

        self.assert_file('tests/results/ALBUM/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup.jpg')  # noqa
        self.assert_file('tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/' +                                    # noqa
                         '2023-06-17-11h05-44-Armor-cup-sq.jpg')                                                  # noqa

        self.assert_file('tests/results/ALBUM/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup.jpg')  # noqa
        self.assert_no_file('tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/' +                                 # noqa
                            '2023-06-17-11h05-46-Armor-cup.jpg')                                                  # noqa

        LOGGER.msg(f'--------------- end of  {mn}')
        self.done(mn)

    def program_207(self):
        if not self.check_done('program_206'):
            self.program_206()
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('--verify-album --enable-rename , with a different names ')
        LOGGER.msg('')

        ACTOR.copy('tests/sources/piwiPre-names.ini', 'tests/results/piwiPre.ini')
        self.reset_done('program_206')

        pwp_main(['--chdir', 'tests/results', '--triage', 'None',
                  '--verify-albums', '2023/2023-06-Juin-17-Armor-cup',                      # noqa
                  '--useless-thumbnails-delete'])

        self.assert_no_file('tests/results/ALBUM/2023/2023-06-Juin-17-Armor-cup/' +         # noqa
                            '2023-06-17-11h05-44-Armor-cup.jpg')                            # noqa
        self.assert_no_file('tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/' +           # noqa
                         '2023-06-17-11h05-44-Armor-cup-sq.jpg')                            # noqa

        self.assert_file('tests/results/ALBUM/2023/06/17/Armor-cup-002.jpg')                # noqa

        LOGGER.msg(f'--------------- end of  {mn}')
        self.done(mn)

    def program_210(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('--verify-album --dryrun in real life')

        album = self.home_config['album']
        target = self.get_first_album()
        if target is None:
            LOGGER.msg(f"album '{album}' is empty, no test to do")
        else:
            LOGGER.msg(f"verifying album '{target}' --dryrun")

            ACTOR.rmtree("tests/results")
            ACTOR.mkdirs("tests/results")
            ACTOR.copy("tests/sources/piwiPre-mount.ini", "tests/results/piwiPre.ini")
            pwp_main(['--chdir', 'tests/results',
                      '--verify-albums', target, "--dryrun"])
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    # ====================================================================
    # --verify-thumbnails

    def program_300(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        if not self.check_done('program_30'):
            self.program_30()

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('verify-thumbnails')

        ACTOR.delete("tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/" +                               # noqa
                     "2023-06-17-11h05-44-Armor-cup-cu_e250.jpg")                                        # noqa
        ACTOR.delete("tests/results/WEB/2021/2021-08-Août-19-Corse/2021-08-19-12h04-00-Corse-sq.jpg")    # noqa
        ACTOR.create("tests/results/WEB/2021/2021-08-Août-19-Corse/2021-08-19-12h04-00-Corse-foo.jpg")    # noqa
        ACTOR.create("tests/results/WEB/2020/2020-05-Mai-17-Corse/2021-08-19-12h04-00-Corse-sq.jpg")      # noqa
        ACTOR.create("tests/results/WEB/2020/2020-05-Mai-17-Corse/foo.txt")                               # noqa

        pwp_main(['--chdir', 'tests/results',
                  '--verify-thumbnails', "2020",
                  '--verify-thumbnails', "2021",
                  '--verify-thumbnails', "2023",
                  '--useless-thumbnails-delete'])  # noqa

        self.assert_file("tests/results/WEB/2023/2023-06-Juin-17-Armor-cup/" +              # noqa
                         "2023-06-17-11h05-44-Armor-cup-cu_e250.jpg")                       # noqa
        self.assert_file("tests/results/WEB/2021/2021-08-Août-19-Corse/" +                  # noqa
                         "2021-08-19-12h04-00-Corse-sq.jpg")                                # noqa
        self.assert_no_file("tests/results/WEB/2021/2021-08-Août-19-Corse/" +               # noqa
                         "2021-08-19-12h04-00-Corse-foo.jpg")                               # noqa
        self.assert_no_file("tests/results/WEB/2020/2020-05-Mai-17-Corse/" +                # noqa
                         "2021-08-19-12h04-00-Corse-sq.jpg")                                # noqa
        self.assert_no_file("tests/results/WEB/2020/2020-05-Mai-17-Corse/foo.txt")          # noqa

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    # ====================================================================
    # ssh/sftp

    def program_400(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('ssh')

        ACTOR.rmtree("tests/results")
        ACTOR.copy("tests/sources/piwiPre-mount.ini", "tests/results/piwiPre.ini")
        ACTOR.create("tests/results/dummy.txt")

        pwp_main(['--chdir', 'tests/results', '--test-ssh', '--test-sftp', '--enable-remote-copy', 'true'])  # noqa

        self.assert_not_info("SSH error")
        self.assert_info("sftp test OK")

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def clean_program_401(self):
        album = self.home_config['album'] + '/tests'
        web = 'WEB/tests'
        remote_web = self.home_config['remote-web'] + '/tests'
        ACTOR.rmtree(album)
        ACTOR.rmtree(web)
        ACTOR.rmtree(remote_web)
        ACTOR.rmtree('tests/results')

    def program_401(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('remote web, with TRIAGE')

        ACTOR.rmtree("tests/results")

        # always add + '/tests', otherwise rm is a disaster!

        if self.home_config['remote-web']:
            album = self.home_config['album'] + '/tests'
            web = 'WEB/tests'
            remote_web = self.home_config['remote-web'] + '/tests'

            self.runner_100(album, web, remote_web=remote_web, delete=False)
        else:
            LOGGER.msg("Empty test because no 'remote-web' configuration")
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_402(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        if not self.check_done('program_401'):
            self.program_401()

        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('--verify-thumbnails remote web')

        if self.home_config['remote-web']:
            remote_web = self.home_config['remote-web'] + '/tests'
            self.home_config['enable-remote-copy'] = True  # simulates --enable-remote-copy on cmd-line
            ACTOR.configure(self.home_config)  # enable ssh for the test harness

            # always add + '/tests', otherwise rm is a disaster!

            ACTOR.remote_delete(remote_web + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup-me.jpg')  # noqa
            ACTOR.remote_delete(remote_web + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup-me.jpg')  # noqa
            ACTOR.remote_delete(remote_web + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-45-Armor-cup-th.jpg')  # noqa
            ACTOR.remote_move(remote_web + '/2023/2023-06-Juin-17-Armor-cup/2023-06-17-11h05-44-Armor-cup-th.jpg',  # noqa
                              remote_web + '/2023/2023-06-Juin-17-Armor-cup/fake-thumbnail.jpg')                    # noqa
            ACTOR.remote_delete(remote_web + '/2023/2023-06-Juin-17-Armor-cup/index.htm')                             # noqa

            pwp_main(['--chdir', 'tests/results',    # '--dryrun', '--debug',
                      '--verify-thumbnails', "tests/2023/2023-06-Juin-17-Armor-cup", '--useless-thumbnails-delete'])  # noqa

            # always an absolute path
            ACTOR.remote_isfile(remote_web + '/2023/2023-06-Juin-17-Armor-cup/' +  # noqa
                                            '2023-06-17-11h05-45-Armor-cup-me.jpg')
            ACTOR.remote_isfile(remote_web + '/2023/2023-06-Juin-17-Armor-cup/' +  # noqa
                                            '2023-06-17-11h05-44-Armor-cup-me.jpg')
            ACTOR.remote_isfile(remote_web + '/2023/2023-06-Juin-17-Armor-cup/' +  # noqa
                                            '2023-06-17-11h05-45-Armor-cup-th.jpg')
            ACTOR.remote_isfile(remote_web + '/2023/2023-06-Juin-17-Armor-cup/' +  # noqa
                                            '2023-06-17-11h05-44-Armor-cup-th.jpg')
            ACTOR.remote_isfile(remote_web + '/2023/2023-06-Juin-17-Armor-cup/' +  # noqa
                                            'index.htm')

            self.clean_program_401()
        else:
            LOGGER.msg("Empty test because no 'remote-web' configuration")
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    # --------------------------------------------
    # the same tests as program_200, but with sftp
    def program_500(self):
        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree

        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('------------ Starting tests for --verify-albums, sftp configuration')
        LOGGER.msg('')
        LOGGER.msg('sources/TRIAGE -> ALBUM, WEB, remote')
        LOGGER.msg('')
        ACTOR.rmtree("tests/results")
        ACTOR.copytree("tests/sources/TRIAGE", "tests/results/TRIAGE")
        ACTOR.copy("tests/sources/piwiPre-mount.ini", "tests/results/piwiPre.ini")
        ACTOR.copy("tests/sources/piwiPre-corse.ini", "tests/results/TRIAGE/Corse/piwiPre.ini")  # noqa

        # always add + '/tests', otherwise rm is a disaster!

        album = self.home_config['album'] + '/tests'
        web = 'WEB/tests'

        if self.home_config['remote-web']:
            remote_web = self.home_config['remote-web'] + '/tests'
            self.home_config['enable-remote-copy'] = True  # simulates --enable-remote-copy on cmd-line
            ACTOR.configure(self.home_config)  # enable ssh for the test harness
            ACTOR.rmtree(album)
            ACTOR.remote_rmtree(remote_web)

            self.runner_200(album, web, with_src=True, remote_web=remote_web)
        else:
            LOGGER.msg("Empty test because no 'remote-web' configuration")

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_501(self):
        if not self.check_done('program_500'):
            self.program_500()

        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('must be executed AFTER pwp_test(500)')
        LOGGER.msg('--verify-albums, without modifications of ALBUM')

        album = self.home_config['album'] + '/tests'
        web = 'WEB/tests'

        if self.home_config['remote-web']:
            remote_web = self.home_config['remote-web'] + '/tests'
            self.home_config['enable-remote-copy'] = True  # simulates --enable-remote-copy on cmd-line
            ACTOR.configure(self.home_config)  # enable ssh for the test harness

            self.runner_201(album, web, remote_web=remote_web)
        else:
            LOGGER.msg("Empty test because no 'remote-web' configuration")
        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_502(self):
        if not self.check_done('program_500'):
            self.program_500()

        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('must be executed AFTER pwp_test(500)')
        LOGGER.msg('--verify-albums, --dryrun, with some modifications')
        LOGGER.msg('must be executed AFTER pwp_test(500), or pwp_test(501)')
        LOGGER.msg('')
        ACTOR.rmtree("tests/results/BACKUP")

        album = self.home_config['album'] + '/tests'
        web = 'WEB/tests'

        if self.home_config['remote-web']:
            remote_web = self.home_config['remote-web'] + '/tests'
            self.home_config['enable-remote-copy'] = True  # simulates --enable-remote-copy on cmd-line
            ACTOR.configure(self.home_config)  # enable ssh for the test harness

            self.runner_202(album, web, remote_web=remote_web, _delete=False)
        else:
            LOGGER.msg("Empty test because no 'remote-web' configuration")

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_503(self):
        if not self.check_done('program_502'):
            self.program_502()

        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('must be executed AFTER pwp_test(502)')
        LOGGER.msg('--verify-albums, with some modifications')
        LOGGER.msg('')
        ACTOR.rmtree("tests/results/BACKUP")

        album = self.home_config['album'] + '/tests'
        web = 'WEB/tests'

        if self.home_config['remote-web']:
            remote_web = self.home_config['remote-web'] + '/tests'
            self.home_config['enable-remote-copy'] = True  # simulates --enable-remote-copy on cmd-line
            ACTOR.configure(self.home_config)  # enable ssh for the test harness

            self.runner_203(album, web, remote_web=remote_web, _delete=False)
        else:
            LOGGER.msg("Empty test because no 'remote-web' configuration")

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_504(self):
        if not self.check_done('program_500'):
            self.program_500()

        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('must be executed AFTER pwp_test(500), CAN be executed after 501/502/503')
        LOGGER.msg('--verify-album --useless-thumbnails-delete, with modification, --dryrun')
        LOGGER.msg('')

        album = self.home_config['album'] + '/tests'
        web = 'WEB/tests'

        if self.home_config['remote-web']:
            remote_web = self.home_config['remote-web'] + '/tests'
            self.home_config['enable-remote-copy'] = True  # simulates --enable-remote-copy on cmd-line
            ACTOR.configure(self.home_config)  # enable ssh for the test harness

            self.runner_204(album, web, remote_web=remote_web, _delete=False)
        else:
            LOGGER.msg("Empty test because no 'remote-web' configuration")

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.done(mn)

    def program_505(self):
        if not self.check_done('program_504'):
            self.program_504()

        mn = inspect.getframeinfo(inspect.currentframe()).function
        self.reset_data()  # before any action, e.g. rmtree
        LOGGER.msg(f'--------------- starting {mn}')
        LOGGER.msg('')
        LOGGER.msg('must be executed AFTER pwp_test(504),')
        LOGGER.msg('--verify-album --useless-thumbnails-delete, with modification')
        LOGGER.msg('')

        album = self.home_config['album'] + '/tests'
        web = 'WEB/tests'

        if self.home_config['remote-web']:
            remote_web = self.home_config['remote-web'] + '/tests'
            self.home_config['enable-remote-copy'] = True  # simulates --enable-remote-copy on cmd-line
            ACTOR.configure(self.home_config)  # enable ssh for the test harness

            self.runner_205(album, web, remote_web=remote_web, _delete=False)
        else:
            LOGGER.msg("Empty test because no 'remote-web' configuration")

        LOGGER.msg(f'--------------- end of  {mn}')
        LOGGER.msg('')
        self.reset_done('program_504')
        self.reset_done('program_503')
        self.reset_done('program_502')
        self.reset_done('program_501')
        self.reset_done('program_500')

        self.done(mn)

    # ====================================================================

    def run_number(self, number, running_all):
        initial_cwd = os.getcwd()
        name = f"program_{number}"

        try:
            if name in self.programs:
                self.programs[name]()
            else:
                if not running_all:
                    LOGGER.msg('')
                    LOGGER.msg(f'---- No program {name}')
                    LOGGER.msg('')
        # except PwpError:  # traps all errors and subclasses
        #    LOGGER.msg("continuing tests after PwpError")
        except SystemExit:
            LOGGER.msg("continuing tests after SystemExit")
        os.chdir(initial_cwd)

    def program_0(self):
        LOGGER.msg('----------------------------- starting program_0')
        LOGGER.msg(f"cwd  = '{os.getcwd()}' ")
        LOGGER.msg(f"HOME = '{os.path.expanduser('~')}' ")

        self.reset_102()
        for i in range(1, self.last+1):  # in [400]:  # for i in [3, 400]:  # for i in [3, 15, 17, 400]
            self.run_number(i, running_all=True)

        LOGGER.msg('----------------------------- end program_0')
        LOGGER.msg('')
        LOGGER.msg('End of ALL TESTS')
        LOGGER.msg('')
        end = datetime.datetime.now()

        LOGGER.msg(f"--- asserts      = {self.asserts}")
        LOGGER.msg(f"--- end          = {end} ---")
        LOGGER.msg(f"--- files        = {self.pictures_nb}")
        LOGGER.msg(f"--- duration     = {end - self.start_time}")
        if self.pictures_nb:
            LOGGER.msg(f"--- duration/pic = {(end - self.start_time) / self.pictures_nb}")
        LOGGER.msg("------------------------------------")


def test_all_programs():  # because it is called test_XXX, tox runs it
    all_tests = PwpTester()
    all_tests.program_0()


def run_pwp(arguments):
    LOGGER.msg('--------------- starting run_pwp()')
    parser = argparse.ArgumentParser(description='testing piwiPre ')
    parser.add_argument('--number', '-n', help='test number', action='store')
    args = parser.parse_args() if arguments is None else parser.parse_args(arguments)

    number = int(args.number) if args.number else 0

    all_tests = PwpTester()
    all_tests.run_number(number, running_all=False)


if __name__ == '__main__':
    run_pwp(sys.argv[1:])
