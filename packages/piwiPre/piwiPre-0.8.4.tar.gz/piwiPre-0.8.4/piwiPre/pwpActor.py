# ---------------------------------------------------------------------------------------------------------------
# piwiPre project
# This program and library is licenced under the European Union Public Licence v1.2 (see LICENCE)
# developed by fabien.battini(at)gmail.com
# ---------------------------------------------------------------------------------------------------------------

import re
import os
import shutil
import time
import datetime

# pip install fabric
# doc: https://docs.fabfile.org/en/stable/
# doc: https://www.paramiko.org/
# doc: https://help.ubuntu.com/community/SSH/OpenSSH/Keys
import fabric


# pip install requests
# doc: https://requests.readthedocs.io/en/latest/
import requests
import requests.cookies

import urllib3.exceptions
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Remove useless warning on https certificates

from piwiPre.pwpErrors import LOGGER, PwpError


class PwpActor:
    allowed_chars = r"a-zA-Z0-9\-_.&@~!,;+°()àâäéèêëïîôöùûüÿçñÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇÑ "  # noqa
    tmp_dir = '.piwiPre.tmp'

    def __init__(self):
        self.dryrun = False
        # values that are cached from the 1st config used
        self.print_debug = False
        self.piwigo_user = None
        self.piwigo_pwd = None
        self.piwigo_host = None
        self.piwigo_port = None

        # management of ssh/sftp
        self.remote_user = None
        self.remote_pwd = None
        self.remote_host = None
        self.remote_port = None
        self.ls_command = None
        self.ls_output = None
        self.connection = None
        self.session = None
        self.remote_uname = None

        # end of cache
        self.piwigo_session = None
        self.dir_made = []
        self.dir_numbers = {}

        self.remote_ls_cache = {}

    def configure(self, config):
        self.piwigo_host = config['piwigo-host']
        self.piwigo_port = int(config['piwigo-port'])
        self.piwigo_user = config['piwigo-user']
        self.piwigo_pwd = config['piwigo-pwd']
        self.print_debug = config['debug']
        self.dryrun = config['dryrun']

        self.connect_ssh(config)

    def reset_data(self):
        self.dryrun = False
        # values that are cached from the 1st config used
        self.print_debug = False
        self.piwigo_user = None
        self.piwigo_pwd = None
        self.piwigo_host = None
        self.piwigo_port = None
        # end of cache
        self.piwigo_session = None
        self.dir_made = []
        self.dir_numbers = {}

        self.connection = None
        self.session = None
        self.remote_ls_cache = {}

    def mkdirs(self, dir_name, forced=False):
        dir_name = dir_name.rstrip('/')
        dir_name = dir_name or '.'
        if os.path.isdir(dir_name) or os.path.ismount(dir_name):
            return
        if self.dryrun and not forced:
            LOGGER.debug(f"Would makedirs '{dir_name}'")
            return

        os.makedirs(dir_name, exist_ok=True)
        if os.path.isdir(dir_name):
            LOGGER.debug(f"makedirs '{dir_name}'")
        else:
            LOGGER.debug(f"FAIL: makedirs '{dir_name}'")

    def copy(self, src, dst, forced=False):
        """
        copy src to dst, unless dryrun is True
        :param src: file to copy
        :param dst: destination
        :param forced: if True, copy is always done, if False, do not copy if dryrun is True
        :return: None
        """
        base = os.path.dirname(dst)
        self.mkdirs(base, forced)

        if not os.path.isfile(src):
            raise PwpError(f"FAILED copy '{src}' ->  '{dst}' : non existing source")

        if self.dryrun and not forced:
            LOGGER.debug(f"Would copy '{src}' ->  '{dst}'")
            return

        shutil.copy2(src, dst)  # preserve metadata
        if os.path.isfile(dst):
            LOGGER.debug(f"copy '{src}' ->  '{dst}'")
        else:
            LOGGER.debug(f"FAIL:copy '{src}' ->  '{dst}'")

    def copytree(self, src, dst):

        if self.dryrun:
            LOGGER.debug(f"Would copytree'{src}' ->  '{dst}'")
            return

        shutil.copytree(src, dst, dirs_exist_ok=True)
        if os.path.isdir(dst):
            LOGGER.debug(f"copytree '{src}' ->  '{dst}'")
        else:
            LOGGER.debug(f"FAIL:copytree '{src}' ->  '{dst}'")

    def move(self, src, dst, forced=False):
        if self.dryrun and not forced:
            LOGGER.debug(f"Would move file '{src}' -> '{dst}'")
            return

        # src_stamp = self.timestamp(src)

        base = os.path.dirname(dst)
        self.mkdirs(base)

        if os.path.isfile(dst):
            os.remove(dst)

        shutil.move(src, dst)
        if os.path.isfile(dst):
            LOGGER.debug(f"move file '{src}' -> '{dst}'")
            # dst_stamp = self.timestamp(dst)
            # if dst_stamp != src_stamp:
            #    self.msg(f"TIMESTAMPS '{src_stamp}' -> '{dst_stamp}'")
        else:
            LOGGER.debug(f"FAIL:move file '{src}' -> '{dst}'")

    def delete(self, src, forced=False):
        if not os.path.isfile(src):
            LOGGER.debug(f"Delete '{src}' non existing file")
            return

        if self.dryrun and not forced:
            LOGGER.debug(f"Would delete '{src}' ")
            return

        os.remove(src)
        if os.path.isfile(src):
            LOGGER.debug(f"FAIL:  delete '{src}'")
        else:
            LOGGER.debug(f"delete file '{src}'")

    def rmtree(self, src):
        if not os.path.isdir(src):
            LOGGER.debug(f"rmtree '{src}' : non existing directory")
            return

        if self.dryrun:
            LOGGER.debug(f"would remove tree '{src}' ")
            return

        shutil.rmtree(src)
        if os.path.isdir(src):
            raise PwpError(f"FAIL:  remove tree '{src}'")
        else:
            LOGGER.debug(f"remove tree  '{src}'")

    # @staticmethod
    # def is_mode_protected(path):
    #     if os.path.isfile(path):
    #         mode = stat.S_IMODE(os.stat(path).st_mode)
    #         return mode & (stat.S_IRWXO | stat.S_IRWXG) == 0
    #    return False
    # chmod has limited meaning in windows universe

    @staticmethod
    def open(filename: str, mode: str):
        # if self.dryrun:
        #     LOGGER.debug(f"open '{filename}' ")
        #     return

        if mode == 'r' and not os.path.isfile(filename):
            raise PwpError(f"ERROR reading non-existing file {filename}")
        if mode == 'rb':
            return open(filename, mode)
        return open(filename, mode, encoding="utf-8")

    @staticmethod
    def get_last_numerical_field(template: str):
        items_list = re.findall('{[^}]*}', template)
        non_numerical = ['{a', '{month_name}', '{base}', '{author}', '{suffix}', '{file}']
        while items_list:
            res = items_list.pop()
            if res not in non_numerical:
                return res[1:-1]  # skip {}
        return None

    def get_info_from_format(self, template: str, src: str):
        """
        Extract information from src according to the descriptor
        :param template: a string that describes the information format
        :param src: the source with information
        :return: a dictionary

        Assuming that template is a reasonably simple format,
        notably that the same field does not occur 2 times.

        Assuming also that the possible items within template are all known,
        which is the case in piwiPre.

        If src is the result of formatting template with some values,
        then we can find back the values, provided the string is simple enough.
        This can even been done independently of the order of the fields in the template,
        because we can find the order by analysing template.
        """
        items_list = re.findall('{[^}]*}', template)  # the list of all items to find, e.g. '{Y}'
        # here, we have all items possibly found in piwiPre
        trans = {
            'size': r"(\d+)",      # noqa
            'Y': r"(\d\d\d\d)",
            'm': r"(\d\d)",
            'd': r"(\d\d)",
            'H': r"(\d\d)",
            'M': r"(\d\d)",
            'S': r"(\d\d)",
            'count': r"(\d+)",
            'z': r"(\+?\-?\d\d\d\d)",
            'a': r"(am|pm)",
            'month_name': '([' + self.allowed_chars + ']+)',
            'base': '([' + self.allowed_chars + ']+)',
            'author': r'(\.*)',
            'suffix': r'(\.*)',
            'file': r"(.*?)",  # noqa
        }
        str_format = template.format(**trans)
        res = re.match(str_format, src)
        dico = None
        if res:
            dico = {}
            for field in trans.keys():
                ff = '{'+field+'}'
                dico[field] = res.group(items_list.index(ff) + 1) if ff in items_list else None
        return dico

    def authenticate_piwigo(self, forced=False):
        if self.piwigo_session is not None and forced is None:
            return
        LOGGER.debug(f"Authenticate to piwigo, host = '{self.piwigo_host}' user = '{self.piwigo_user}'")
        redirect = '/piwigo/admin.php?page=site_update&site=1'
        piwigo_url = "https://" + self.piwigo_host + "/piwigo/identification.php"
        post_info = {
            'username': self.piwigo_user,
            'password': self.piwigo_pwd,
            'remember_me': "1",
            'redirect': redirect,
            'login': 'To Validate',
        }
        # https://requests.readthedocs.io/en/latest/user/advanced/
        self.piwigo_session = requests.Session()
        required_args = {
            'name': 'pwg_id',
            'value': 'A fake value to start the process'
        }
        optional_args = {}
        my_cookie = requests.cookies.create_cookie(**required_args, **optional_args)
        self.piwigo_session.cookies.set_cookie(my_cookie)
        self.piwigo_session.post(piwigo_url, data=post_info, verify=False)

    def maybe_authenticate(self, req):
        if '<a href="identification.php?redirect=' in req.text:
            # piwigo asks for authentication
            self.authenticate_piwigo(forced=True)
            req = self.piwigo_session.get(req.url, verify=False)
        return req

    def get_piwigo_dirs(self):
        self.authenticate_piwigo()
        LOGGER.debug("get_piwigo_dirs")
        piwigo_url = "https://" + self.piwigo_host + "/piwigo/admin.php?page=site_update&site=1"
        req = self.piwigo_session.get(piwigo_url, verify=False)
        req = self.maybe_authenticate(req)
        seen = False
        dico = {}
        # CAVEAT: the number of &nbsp; gives the level of the directory
        # O: Root dir, typically photo
        # 3: first level
        # 6: 2nd level etc
        path = []
        level = 0
        for line in req.text.splitlines():
            if seen:
                res = re.search(r'<option value="(\d+)">((&nbsp;)*)- (.*)</option>', line)
                if res:
                    item = res.group(4)
                    new_level = int(res.group(2).count("&nbsp;")/3) + 1
                    if new_level == level+1:
                        pass
                        # entered a deeper directory
                    elif new_level > level+1:
                        LOGGER.warning("INTERNAL ERROR: jump between directories")
                    else:  # new_level <= level
                        for i in range(0, level - new_level+1):
                            path.pop()
                    d = ''
                    for f in path:
                        d += f + '/'
                    dico[d + item] = res.group(1)
                    path.append(item)
                    level = new_level

                else:
                    if re.search(r'</select>', line) is not None:
                        seen = False
            else:
                seen = re.search(r'<select class="categoryList" name="cat"', line) is not None
        return dico

    def synchronize_piwigo_dir(self, src: str, with_files: bool):
        # https://fr.piwigo.org/forum/viewtopic.php?id=16532
        LOGGER.debug(f"synchronize_piwigo_dir '{src}'")
        if self.dryrun:
            return
        if self.piwigo_host is None or self.piwigo_user is None:
            LOGGER.info(f"synchronize_piwigo_dir '{src}' impossible : no host configuration")
            return
        self.dir_numbers = self.get_piwigo_dirs()
        dirs = self.dir_numbers
        if 'photo/' + src not in dirs.keys():
            LOGGER.info(f"dir '{src}' not in piwigo managed directories")
            return
        dir_nb = dirs['photo/' + src]

        post_info = {
            'sync': 'files' if with_files else 'dirs',
            'display_info': 1,
            'privacy_level': 4,
            'sync_meta': 1,  # Value is unclear
            "cat": dir_nb,
            "subcats-included": 1,  # noqa
            "submit": "submit",
        }
        piwigo_url = "https://" + self.piwigo_host + "/piwigo/admin.php?page=site_update&site=1"
        req = self.piwigo_session.post(piwigo_url, data=post_info, verify=False)
        # TODO: parse here to get new directories and verify src is in the list
        t = req.text
        LOGGER.info(f"dir '{src}' synchronized with piwigo")
        return t

    @staticmethod
    def create(filename):
        with open(filename, 'w') as f:
            f.write(f"Fake file created for test {datetime.datetime.now()}\n")

    # ----------------------------------------------------------------------
    # management of ssh/sftp

    @staticmethod
    def build_timestamp(filename: str):
        file_time = os.path.getmtime(filename)
        timestamp = time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime(file_time))
        return timestamp

    @staticmethod
    def timestamp_from_ls(d: dict):
        timestamp = f"{d['Y']}/{d['m']}/{d['d']}-{d['H']}:{d['M']}:{d['S']}"
        return timestamp

    def remote_run(self, cmd: str, forced=False):
        if self.dryrun and not forced:
            return None

        if self.connection:
            res = self.connection.run(cmd, hide=True, warn=True, encoding='utf8')
            if not res.ok:
                LOGGER.info(f"CAVEAT remote '{cmd}' returned {res.stderr}")
                LOGGER.msg(f"CAVEAT remote '{cmd}' returned {res.stderr}")
            return res
        raise PwpError("trying to run a ssh command without a ssh connection", cmd)

    @staticmethod
    def my_decode(item: str) -> str:
        """
        Manages the unknown encoding used by ls - paramiko - fabfile  
        returns the decoded string
        only chars in 'allowed_chars' are processed
        
        :param item: string to be decoded 
        :return: the decoded string"""    # noqa

        # only allowed chars
        table = {'\\302\\260': '°', '\\303\\240': 'à', '\\303\\242': 'â', '\\303\\244': 'ä', '\\303\\251': 'é',
                 '\\303\\250': 'è', '\\303\\252': 'ê', '\\303\\253': 'ë', '\\303\\257': 'ï', '\\303\\256': 'î',
                 '\\303\\264': 'ô', '\\303\\266': 'ö', '\\303\\271': 'ù', '\\303\\273': 'û', '\\303\\274': 'ü',
                 '\\303\\277': 'ÿ', '\\303\\247': 'ç', '\\303\\261': 'ñ', '\\303\\200': 'À', '\\303\\202': 'Â',
                 '\\303\\204': 'Ä', '\\303\\211': 'É', '\\303\\210': 'È', '\\303\\212': 'Ê', '\\303\\213': 'Ë',
                 '\\303\\217': 'Ï', '\\303\\216': 'Î', '\\303\\224': 'Ô', '\\303\\226': 'Ö', '\\303\\231': 'Ù',
                 '\\303\\233': 'Û', '\\303\\234': 'Ü', '\\305\\270': 'Ÿ', '\\303\\207': 'Ç', '\\303\\221': 'Ñ'}
        new_val = ''
        i = 0
        while i < len(item):
            s = item[i:i+8]
            if s in table:
                new_val += table[s]
                i += 8
            elif item[i:i+2] == '\\\\':
                new_val += '\\'
                i += 2
            else:
                new_val += item[i]
                i += 1
        return new_val

    def remote_ls(self, directory, forced=False):
        directory = directory or '.'
        LOGGER.debug(f"ssh ls '{directory}' ")
        if not forced and self.dryrun:
            return None

        if directory in self.remote_ls_cache.keys():
            return self.remote_ls_cache[directory]

        # TODO: parse also directory / file

        ls_cmd = self.ls_command.format(file=directory)
        try:
            result = self.remote_run(ls_cmd, forced=forced)
        except FileNotFoundError:
            return {}
        res = self.my_decode(result.stdout)
        all_lines = res.split('\n')
        all_files: dict = {}
        for line in all_lines:
            dico = self.get_info_from_format(self.ls_output, line)
            if dico:
                all_files[dico["file"]] = dico

        self.remote_ls_cache[directory] = all_files
        return all_files

    def remote_create(self, filename):
        self.remote_run(f"touch {filename}")
        self.remote_invalidate_cache(os.path.dirname(filename))

    def remote_invalidate_cache(self, directory):
        if directory in self.remote_ls_cache.keys():
            del self.remote_ls_cache[directory]

    def remote_isfile(self, filepath, forced=False):
        if self.dryrun and not forced:
            return None
        all_files = self.remote_ls(os.path.dirname(filepath), forced=forced)
        if all_files is not None and os.path.basename(filepath) in all_files.keys():
            LOGGER.debug(f"ssh file_exists '{filepath}' : YES")
            return True
        LOGGER.debug(f"ssh file_exists '{filepath}' : NO")
        return False

        # all_files = self.ls(config, os.path.dirname(filepath))   # noqa
        # return os.path.basename(filepath) in all_files.keys()

    def remote_mkdir(self, directory):
        if directory in self.dir_made:
            return
        LOGGER.debug(f"remote mkdir '{directory}'")
        self.remote_run('mkdir -p ' + directory)
        self.dir_made.append(directory)

    def remote_put(self, src, directory):
        LOGGER.debug(f"remote put '{src}' '{directory}'")
        if self.dryrun:
            return
        tmp_file = self.tmp_dir + '/' + src
        if self.connection:
            tmp_path = os.path.dirname(tmp_file)
            self.remote_mkdir(tmp_path)
            self.remote_mkdir(directory)
            sftp = self.connection.sftp()
            sftp.put(src, tmp_file, confirm=True)
            f_a_time = os.path.getatime(src)
            f_m_time = os.path.getmtime(src)
            sftp.utime(tmp_file, (f_a_time, f_m_time))

            # FIXME: is it possible there is a race condition with sftp.put ?

        self.remote_run('mv -vf ' + tmp_file + '  ' + directory)
        if directory in self.remote_ls_cache.keys():
            base = os.path.basename(src)
            dico = {"file": base}  # the only info we have so far, we could add more if necessary
            all_files = self.remote_ls_cache[directory]
            all_files[base] = dico
            self.remote_ls_cache[directory] = all_files  # actually this is useless because the object is shared.

    def remote_get(self, remote_file, local_file):
        LOGGER.debug(f"remote get '{remote_file}' -> '{local_file}'")
        # assuming  directory for local exists
        if self.dryrun:
            return
        if self.connection:
            self.remote_mkdir(self.tmp_dir)
            tmp_file = self.tmp_dir + '/' + os.path.basename(local_file)
            # -p: preserve date -v: verbose -f: force (clobbers)
            self.remote_run(f'cp -pvf {remote_file} {tmp_file}')
            sftp = self.connection.sftp()
            local_dir = os.path.dirname(local_file)
            self.mkdirs(local_dir)
            sftp.get(tmp_file, local_file)
        else:
            self.remote_run(f'mv -vf {remote_file}  {local_file}')

    def remote_delete(self, filename: str):
        LOGGER.debug(f"remote rm '{filename}'")
        self.remote_run(f'rm -f {filename}')            # if no connection, falls into remote_run() error raise
        self.remote_invalidate_cache(os.path.dirname(filename))

    def remote_move(self, src: str, dst: str):
        LOGGER.debug(f"remote mv '{src}' -> '{dst}'")
        # assuming  directory for remote exists
        self.remote_run(f'mv -vf {src}  {dst}')     # if no connection, falls into remote_run() error raise
        self.remote_invalidate_cache(os.path.dirname(src))
        self.remote_invalidate_cache(os.path.dirname(dst))

    def remote_copy(self, src: str, dst: str):
        LOGGER.debug(f"remote mv '{src}' -> '{dst}'")
        # assuming  directory for remote exists
        self.remote_run(f'cp -vf {src}  {dst}')     # if no connection, falls into remote_run() error raise
        self.remote_invalidate_cache(os.path.dirname(src))
        self.remote_invalidate_cache(os.path.dirname(dst))

    def remote_rmtree(self, src: str):
        LOGGER.debug(f"remote rmdir '{src}'")
        self.remote_run(f'rm -rf {src}')            # if no connection, falls into remote_run() error raise
        self.remote_invalidate_cache(os.path.dirname(src))

    def connect_ssh(self, config: dict):
        """

        :param config: configuration
        :return: Connection_done: bool, uname: str, cause:str, Error: bool
        """
        self.remote_host = config['remote-host']
        self.remote_port = int(config['remote-port'])
        self.remote_user = config['remote-user']
        self.remote_pwd = config['remote-pwd']
        self.ls_output = config['ls-output']
        self.ls_command = config['ls-command']

        if self.connection is not None:
            return True, self.remote_uname, None, False

        remote = (config['enable-remote-copy'] and config['remote-web'] and
                  config['remote-host'] and config['remote-port'])
        if not remote:
            return False, None, 'No remote parameters', False   # not connecting is not error here

        LOGGER.info(f"connect host='{self.remote_host}' port='{self.remote_port}' user='{self.remote_user}'")
        if self.dryrun:
            self.connection = 1  # just to avoid doing connect every time
            return False, None, "Dryrun", False  # not connecting is not error here

        self.connection = fabric.Connection(self.remote_host, self.remote_user, self.remote_port)
        if self.connection is None:
            LOGGER.info("SSH error while Connecting")
            return False, None, "SSH error Connecting", True

        result = self.remote_run('echo $PATH')
        if not result.ok:
            LOGGER.info(f"ssh error {result.exited}")
            return False, None, f"SSH error {result.exited}", True
        res = result.stdout.strip()
        if res == "$PATH":
            return True, "Windows", None, False
        else:
            result = self.remote_run('uname -rsvm')  # noqa

        uname = result.stdout.strip()
        sftp = self.connection.sftp()
        af = sftp.listdir('.')
        if self.tmp_dir in af:
            self.remote_rmtree(self.tmp_dir)
        sftp.mkdir(self.tmp_dir)
        self.remote_uname = uname
        return True, uname, None, False


ACTOR = PwpActor()
