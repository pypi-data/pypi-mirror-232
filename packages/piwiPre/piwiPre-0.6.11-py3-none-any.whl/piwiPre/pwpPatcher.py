# ---------------------------------------------------------------------------------------------------------------
# piwiPre project
# This program and library is licenced under the European Union Public Licence v1.2 (see LICENCE)
# developed by fabien.battini(at)gmail.com
# ---------------------------------------------------------------------------------------------------------------
import sys
# pip install GitPython
import git
import re
import os
import argparse
import datetime

# this file is run by tox.
# All installation commands are executed using {toxinidir} (the directory where tox.ini resides) as CWD # noqa
# to test without tox, run: 'cd .. ; python piwiPre/pwpPatcher.py  '                                    # noqa
# the following line is mandatory to execute from shell
# tox does it automatically, so not necessary if running only from tox.
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from piwiPre.pwpParser import build_official_rst


class PwpPatcher:
    def __init__(self, arguments=None, standalone=True):
        if not standalone:
            return
        self.parser = argparse.ArgumentParser(description='manages tags and modifies accordingly files that want it ')
        self.parser.add_argument('--Major', '-M', help="Promotes as Major release i.e. X++.",
                                 action='store_true')
        self.parser.add_argument('--minor', '-m', help="Promotes as minor version ie x.Y++",
                                 action='store_true')
        self.parser.add_argument('--patch', '-p', help="Increments patch version ie x.y.Z++",
                                 action='store_true')
        self.parser.add_argument('--commit', '-c', help="Commits, implicit if -M, -m, -p",
                                 action='store_true')
        self.parser.add_argument('--full-help', help="more explanations",
                                 action='store_true')
        self.parser.add_argument('--print', help="prints the last tag spec and exits",
                                 action='store_true')
        self.parser.add_argument('--download', '-d', help="patches download.rst",
                                 action='store_true')
        self.parser.add_argument('--autotest', help="autotest, no real action",
                                 action='store_true')

        self.repo = git.Repo('.')
        tags = sorted(self.repo.tags, key=lambda t: t.commit.committed_datetime)
        if len(tags) > 0:
            latest_tag = tags[-1]
            tag_version = str(latest_tag)
        else:
            latest_tag = None
            tag_version = "0.0.0"

        full_tag = re.sub(r"[^\d.]*", '', tag_version)
        m = re.match(r"(\d+)\.*(\d*)\.*(\d*)", full_tag)
        self.release = int(m.group(1)) if m.group(1) else 0
        self.version = int(m.group(2)) if m.group(2) else 0
        self.patch = int(m.group(3)) if m.group(3) else 0
        self.spec = full_tag
        if latest_tag:
            self.date = latest_tag.commit.committed_datetime.strftime("%m/%d/%Y %H:%M:%S")
        else:
            self.date = datetime.datetime.now()
        self.update_spec()
        self.args = self.parser.parse_args() if arguments is None else self.parser.parse_args(arguments)

    def update_spec(self):
        self.spec = str(self.release)
        if self.version != 0 or self.patch != 0:
            self.spec += '.' + str(self.version)
            if self.patch != 0:
                self.spec += '.' + str(self.patch)

    def manage_tags(self):

        if self.args.patch:
            self.patch += 1

        if self.args.minor:
            self.version += 1
            self.patch = 0

        if self.args.Major:
            self.release += 1
            self.version = 0
            self.patch = 0

        if self.args.Major or self.args.minor or self.args.patch:
            n = datetime.datetime.now()
            self.date = n.strftime("%m/%d/%Y %H:%M:%S")
            self.update_spec()

            print(f"msg     new tag '{self.spec}'")
            return True
        return False

    @staticmethod
    def open(file_name, mode):
        try:
            ins = open(file_name, mode, encoding="utf-8")
        except OSError as error:
            print(f"FATAL ERROR: Cannot open('{file_name}',{mode}) : {str(error)}, aborting")
            exit(-1)
        return ins

    @staticmethod
    def rename(old, new):
        try:
            os.rename(old, new)
        except OSError as error:
            print(f"FATAL ERROR: Cannot rename('{old}','{new}') : {str(error)}, aborting")
            exit(-1)
        return

    def update_file(self, filename: str, dico: dict, duplicate=False, autotest=False):

        if autotest:
            new_file = f"tests/results/{os.path.basename(filename)}.autotest"
        else:
            new_file = filename+'.new'
        old_file = filename+'.bak'

        ins = self.open(filename, "r")
        content = ins.readlines()
        ins.close()

        outs = self.open(new_file, "w")
        useful = False
        previous = []
        for line in content:
            modified = line
            for before, after in dico.items():
                modified = re.sub(before, after, modified)
            if modified not in previous:
                previous.append(modified)
            else:
                # we have already done that modification once, we do not do it twice
                modified = line
            outs.writelines(modified)

            if modified != line:
                useful = True
                if duplicate:
                    outs.writelines(line)

        outs.close()

        if autotest:
            print(f"msg     autotest file '{new_file}' generated")
            return

        if not useful:
            os.remove(new_file)
            print(f"msg     file '{filename}' does not need patch")
            return

        if os.path.isfile(old_file):
            os.remove(old_file)
        self.rename(filename, old_file)
        self.rename(new_file, filename)
        print(f"msg     file '{filename}' patched")

    # @staticmethod
    # def update_from_py(filename, source):
    #     if os.path.getmtime(filename) > os.path.getmtime(source):
    #         print(f"msg     file '{filename}' is older than source '{source}': patch useless")
    #         return
    #     args_ini_main(['--build-rst-file', '--rst-file', filename])

    def update_from_source(self, filename, source, autotest: bool):

        if not autotest and os.path.getmtime(filename) > os.path.getmtime(source):
            print(f"msg     file '{filename}' is older than source '{source}': patch useless")
            return

        with self.open(source, "r") as ins:
            content = ins.readlines()

        if autotest:
            new_file = f"tests/results/{os.path.basename(filename)}.autotest"
        else:
            new_file = filename + '.new'
        old_file = filename + '.bak'

        outs = self.open(new_file, "w")
        do_add = True
        with self.open(filename, "r") as ins:
            for line in ins:
                if do_add:
                    outs.write(line)

                    if re.match(r' *def print\(.*\):\n', line):
                        for cl in content:
                            patched = re.sub('"', '\\"', cl[:-1])
                            outs.write(f'        print("{patched}")\n') # add \t\t\t # noqa ???
                        outs.write('    # End of patched text\n')
                        do_add = False
                else:
                    if re.match(r' +# End of patched text\n', line):
                        do_add = True
        outs.close()

        if autotest:
            print(f"msg     autotest file '{new_file}' generated")
            return

        if os.path.isfile(old_file):
            os.remove(old_file)
        self.rename(filename, old_file)
        self.rename(new_file, filename)
        print(f"msg     file '{filename}' patched")

    def run(self):
        if self.args.autotest:
            self.args.full_help = True

        if self.args.print:
            print(self.spec)
            return

        print(f"msg     initial tag '{self.spec}' at '{self.date}'")

        if self.args.full_help:
            print("if -M, -m or -p, updates the current tag")
            print("verifies that the current tag is writen in piwiPre/pwpVersion.py")
            print("verifies that piwiPre/pwpLicence.py is up to date vs source")
            print("if ")
            print("   - the new tag is a Major or a minor (but *not* a patch), then the corresponding exe and module")
            print("     will be published, assuming here that they have been tested OK)")
            print("     therefore download.rst is also modified")
            print("   - or -d")
            print("then download.rst is updated")

            print("if a new tag or -c, commits ALL modified files")
            print("if a new tag puts the tag LOCALLY on git, but *not* remotely on GitLab")

        new_tag = self.manage_tags()
        if self.args.autotest:
            self.args.Major = True
            self.manage_tags()
            self.args.Major = False
            self.args.minor = True
            self.manage_tags()
            self.args.minor = False
            self.args.patch = True
            new_tag = self.manage_tags()

        self.update_from_source('piwiPre/pwpLicence.py', 'LICENCE', self.args.autotest)

        # self.update_from_source('piwiPre/pwpIniFile.py', 'source/usage/configuration.rst', config=True)

        self.update_file('piwiPre/pwpVersion.py',
                         {r"help = '([^']*)'": f"help = '{self.spec} at {self.date}'",
                          r"spec = '([^']*)'": f"spec = '{self.spec}'",
                          r"release = (\d*)": f"release = {self.release}",
                          r"version = (\d*)": f"version = {self.version}",
                          r"patch = (\d*)": f"patch = {self.patch}",
                          r"date = '([^']*)'": f"date = '{self.date}'",
                          }, autotest=self.args.autotest)

        # - Windows one-file exe on gitlab artifacts:
        # `piwiPre-1.8.3.exe
        # <https://gitlab.com/api/v4/projects/22464405/packages/generic/piwiPre/1.8.3/piwiPre-1.8.3.exe>`_

        prologue = '- Windows one-file exe on gitlab artifacts:'
        epilogue = '<https://gitlab.com/api/v4/projects/22464405/packages/generic/piwiPre'

        if self.args.download or (new_tag and self.patch == 0) or self.args.autotest:
            self.update_file('source/download.rst',
                             {
                                 r".*Windows one-file exe.*": f"{prologue} `piwiPre-{self.spec}.exe " +
                                                              f"{epilogue}/{self.spec}/piwiPre-{self.spec}.exe>`_"
                             },
                             duplicate=True, autotest=self.args.autotest)

        self.update_file('version.txt', {r"(.+)":  self.spec}, autotest=self.args.autotest)
        build_official_rst(self.args.autotest)

        if self.args.autotest:
            print(f"msg     final tag '{self.spec}' at '{self.date}'")
            return

        if new_tag or self.args.commit:
            commit = self.repo.git.commit('-a', '-m', f'set tag {self.spec}', '--date', self.date)
            print(f"msg     DONE: git commit '{str(commit)}' ")

        if new_tag:
            self.repo.git.tag(self.spec)
            print(f"msg     DONE: git tag '{self.spec}'")


def patcher_main(arguments):
    arguments = arguments or []
    print('msg     --------------- starting patcher_main')
    my_patcher = PwpPatcher(arguments=arguments)
    my_patcher.run()
    print('msg     --------------- ending patcher_main')


if __name__ == "__main__":
    sys.exit(patcher_main(sys.argv[1:]))
