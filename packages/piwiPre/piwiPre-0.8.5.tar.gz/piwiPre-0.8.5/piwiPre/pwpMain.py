# ---------------------------------------------------------------------------------------------------------------
# piwiPre project
# This program and library is licenced under the European Union Public Licence v1.2 (see LICENCE)
# developed by fabien.battini(at)gmail.com
# ---------------------------------------------------------------------------------------------------------------

import sys
import os.path
import pathlib
import re
import pprint
import tempfile
import datetime

from piwiPre.pwpActor import ACTOR
from piwiPre.pwpParser import PwpParser
from piwiPre.pwpConfig import PwpConfig
from piwiPre.pwpJpg import PwpJpg, PwpObject
from piwiPre.pwpMp4 import PwpMp4
from piwiPre.pwpErrors import PwpError, PwpConfigError, LOGGER
from piwiPre.pwpVersion import PwpVersion
from piwiPre.pwpLicence import PwpLicence

# -----------------------------------------------------------------------------------
# Requirements, General behavior
#
# REQ 0001: piwiPre is configured with HOME/.piwiPre.ini and piwiPre.ini files found in the hierarchy of directories
# REQ 0002: piwiPre is also configured by cmdline arguments
# REQ 0003: piwiPre renames .jpg, .mp4, .txt files found in 'triage' (enable-rename) (program_24)
# REQ 0004: piwiPre inserts metadata in .jpg and .mp4 files (enable-metadata)
# REQ 0005: piwiPre generates piwigo metadata (enable-thumbnails)
# REQ 0006: piwiPre synchronizes piwigo albums that were modified (enable-piwigo-sync)
# REQ 0007: piwiPre runs on windows and Linux development stations
# REQ 0008:  --dump-config folder allows to debug the configuration hierarchy (program_2)

# REQ 0009: piwiPre configures automatically album by ADDING piwiPre.ini files (autoconfiguration) (program_6, 7, 8, 9)
# REQ 0010: hand-writing a piwiPre.ini in albums may prevent any modification of files
# REQ 0011: during renaming, the name of .txt files is not changed. They simply go to the appropriate folder
# REQ 0012: tox is run on gitlab, generates html doc and coverage

# REQ 0020: 'enable-XXX' : false: feature is never active
# REQ 0021: 'enable-XXX' : true: feature is done in TRIAGE, and in ALBUMS if the result is not present


# REQ 0049: requirements are parsed from the source and put automatically in doc

# REQ 0050: temporary files are put in a real temporary dir
# REQ 0051: parser: remove trailing / at end of directories, this is common error

# REQ 0100: Renaming is based on the 'names' configuration template
# REQ 0101: Renaming takes into account the date/time of the picture shooting, found in metadata
# REQ 0102: if renaming a file clobber an existing file, piwiPre increments the last numerical field to avoid conflict


# REQ 0200: piwiPre verifies the albums are aligned with configuration (verify-albums)
# REQ 0201: piwiPre realigns pictures rotation
# REQ 0202: piwiPre updates metadata
# REQ 0203: piwiPre generates lacking thumbnails from album
# REQ 0204: album modified pictures are saved in 'BACKUP'
# REQ 0205: piwiPre removes useless thumbnails
# REQ 0206: the albums to verify are specified by 'verify-albums'
# REQ 0207: insert the 'author' metadata
# REQ 0208: use XMP metadata (piwiPre version 2.0)

# REQ 0300: generate an error if HOME/.piwiPre.ini is not protected: CANCELLED, because chmod is limited in windows
# TODO REQ 0301: piwiPre reorders the piwigo directories with the right order !  (future piwiPre version 2.0)

# -----------------------------------------------------------------------------------
# Requirements, Testing

# REQ 3000: autotest available with tox and pytest
# REQ 3001: piwipre> tests\\pwp_test.py -n number # runs the test number n                          # noqa
# REQ 3002: pwp_test -n 0 # runs all the tests
# REQ 3003: pwp_test can run all the autotests
# REQ 3004: PyCharm tests cases are saved in project files
# REQ 3005: all automatic tests run by pwp_test can be run by anyone on any development server
# REQ 3006: pwp_test assumes a valid configuration in HOME/.piwiPre.ini
# REQ 3007: coverage is run automatically by tox
# REQ 3008: coverage > 92 %
# REQ 3009: tests --dryrun, with triage and album
# REQ 3010: test error generation

# REQ 3100: test jpg files in TRIAGE, with/without rotation and metadata
# REQ 3101: test .txt files in TRIAGE
# REQ 3102: test .mp4 files in TRIAGE with metadata
# REQ 3104: tests end-2-end with piwogo sync (program_13)
# REQ 3105: test --version
# REQ 3106: test --chdir
# REQ 3107: test --licence
# REQ 3108: autotest of PwpPatcher
# REQ 3109: autotest of PwpPatcher should cover 80% of code
# REQ 3110: autotest of PwpMP4
# REQ 3111: There are no explicit remote locations on server, use config instead
# REQ 3112: someone with a valid config would run the same test on a different configuration
# REQ 3113: test --dump-config folder
# REQ 3114: test PwpError generation (program_26)
# REQ 3115: on argument error, raise an exception , not trapped
# REQ 3116: test the insertion of the 'author' metadata


# REQ 3120: test --enable-rename false  (program_27)
# REQ 3122: test dates (all cases) :  program_24
# TODO REQ 3123: test unsupported (e.g. .foo) files in TRIAGE

# TODO REQ 3200: test manual piwiPre.ini in album that prevents from renaming
# TODO REQ 3201: test manual piwiPre.ini in album that prevents from changing metadata
# TODO REQ 3202: test manual piwiPre.ini in album that prevents from rotation


# DONE: test --test-piwigo-synchronization

# DONE: a modified copy of a picture (so same metadata!) is renamed thanks to collision avoiding

# DOC: piwigo user and password in HOME .piwiPre.ini
# Doc:  HOME/.piwiPre.ini contains only server-side information
# Doc: warning: .ini files should be written in UTF8 encoding !
# Doc: usage: photo is accessible or synchronized, not web: this is not an issue, piwigo will generate thumbnails

# REQ 4000: manage remote WEB, accessible with ssh
# REQ 4001: setup ssh/sftp session
# REQ 4002: We assume that thumbnails are always coming from the corresponding file in ALBUM
# REQ 4003: a thumbnail is created only if the file in ALBUM is new, or the thumbnail was non-existent
# REQ 4004: thumbnails are created in WEB, then copied to remote-web

# ----------------------------- FUTURE ROADMAP -------------------------------------
# Future V2.0
#
#
# TODO REQ 9000: piwiPre runs on a synology NAS
# TODO REQ 9001: piwiPre runs on a workstation connected to the piwigo server through ssh, without shared directories
# TODO REQ 9002: piwiPre uses MD5 checksums to compare local and remote files
# TODO REQ 9100: piwiPre generates synology @eaDir thumbnails to speedup processing
# TODO: Parse requirements: reorder by REQ number, yell if duplicate number. non REQ are listed in their arrival order
# TODO: manage several toplevel albums inside piwigo


class PwpMain:
    allowed_chars = r"a-zA-Z0-9\-_.&@~!,;+°()àâäéèêëïîôöùûüÿçñÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇÑ "    # noqa

    def __init__(self, arguments=None):
        self.initial_cwd = os.getcwd()
        self.parser = PwpParser(arguments=arguments, program="piwiPre", with_config=True)
        self.parser_config = self.parser.config
        self.dumped_config = None      # The config reached by --dump-config, used for test only
        self.dirs_to_synchronize = []
        self.expected_thumbnails = []  # list of expected thumbnails, when processing ALBUM. reset for each dir.
        # self.cached_dirs = {}

    @staticmethod
    def get_base_from_dir(dir_name, p_config):
        base = re.sub(r".jpg$", "", dir_name)
        base = re.sub(r'[^' + PwpMain.allowed_chars + ']', "_", base, re.IGNORECASE)

        # Maybe we are processing a directory which is already the result of a renaming process
        # so its format should be the same then the directory part of 'names'

        template = os.path.basename(os.path.dirname(p_config['names']))
        res = ACTOR.get_info_from_format(template, dir_name)
        if res and res['base'] is not None and res['base'] != '':
            return res['base']
        return base

    @staticmethod
    def build_path(base, common_path: str, path):
        if base is None:
            return None
        result = base + '/' + common_path + ('' if common_path == '' else '/') + path
        if result[-1] == '/':
            result = result[:-1]
        return result

    # @staticmethod
    # def increment_last_number(filename):
    #     m = re.match(r"(.*)(\d+)(\D*)\.jpg", filename)
    #     if m is not None:
    #         prefix = m.group(1)
    #         number = int(m.group(2))
    #         postfix = m.group(3)
    #         return prefix + str(number+1) + postfix + '.jpg'
    #     else:
    #         LOGGER.msg(f"file {filename} has no integer to increment")
    #         return filename[:-4] + '01.jpg'

    def build_all_thumbs(self, target: str, config: PwpConfig, common_path: str, stage: str,
                         allow_clobber: bool):
        # returns the description of work done
        if config['enable-thumbnails'] is False:
            LOGGER.debug(f"{stage} {target} enable-thumbnails is False")
            return ''

        f = os.path.basename(target)[:-4]  # skip .jpg

        thumbs_base = config['web'] + '/' + common_path

        im = PwpJpg(target)
        thumbs = config['piwigo-thumbnails']

        summary = ''
        for name, values in thumbs.items():
            width = values['width']
            height = values['height']
            crop = values['crop']
            thumb_name = name.format(f=f)
            local_name = thumbs_base + '/' + thumb_name

            self.expected_thumbnails.append(local_name)
            remote_file = PwpJpg.get_remote_web_filename(config, local_name)
            if remote_file:
                self.expected_thumbnails.append(remote_file)

            if config['dryrun']:
                # CAVEAT: conflict management has NOT occurred, because the files are not created in ALBUM
                #         So we do *not* know te exact thumbnail name
                #         hence the message is not accurate
                LOGGER.info(f"Would create Thumbnail {width}x{height} crop={crop} for {target}")
            else:
                im.thumbnail(local_name, width, height, crop, config, allow_clobber)
            if summary == '':
                summary = ' Thumbs('
            summary += name[4:-4] + ', '
        if summary != '':
            summary = summary[:-2] + ') '

        index_base = 'index.htm'
        local_name = thumbs_base + '/' + index_base
        if local_name not in self.expected_thumbnails:
            self.expected_thumbnails.append(local_name)

        remote_name = PwpJpg.get_remote_web_filename(config, local_name)
        if remote_name and remote_name not in self.expected_thumbnails:
            self.expected_thumbnails.append(remote_name)

        if os.path.isfile(local_name) or (remote_name and ACTOR.remote_isfile(remote_name)):
            pass  # index is already there
        else:
            if config['dryrun']:
                LOGGER.info(f"would create thumbnail html index '{local_name}'")
            else:
                LOGGER.info(f"Create thumbnail html index '{local_name}'")
                with open(local_name, 'w', encoding="utf-8") as f:
                    print("Not allowed!", file=f)
                summary += 'Index '
                if remote_name:
                    remote_path = os.path.dirname(remote_name)
                    LOGGER.info(f"Index file {local_name} sftp to {remote_path}")
                    ACTOR.remote_put(local_name, remote_path)
        return summary

    @staticmethod
    def get_cached_folder(path) -> [str]:
        # if path in self.cached_dirs:
        #     # update_with_dir has already been done, no need to update again
        #     return self.cached_dirs[path]
        album_folder = []
        if os.path.isdir(path):
            album_folder = [f for f in os.listdir(path) if os.path.isfile(path+'/'+f)]
        # self.cached_dirs[path] = album_folder
        return album_folder

    @staticmethod
    def same_file(f1, f2):
        with open(f1, 'rb') as f:
            c1 = f.read()
        with open(f2, 'rb') as f:
            c2 = f.read()
        return c1 == c2

    @staticmethod
    def rename_allowed(_stage, config):
        if config['enable-rename'] is False:
            return False
        return True

    @staticmethod
    def build_auto_config(src, dst, base):
        # we want to change the {base} component of names to base
        # because this value cannot be guessed from the directory name in ALBUM
        with open(src, 'r') as s:
            lines = s.readlines()
        with open(dst, 'w') as d:
            d.write(f"# file generated by --enable-auto-configuration on {datetime.datetime.now()}\n")
            for li in lines:
                m = re.match(r"names\s*:(.*)", li)
                if m:
                    li = li.replace('{base}', base)
                d.write(li)

    def run_stage_file(self, stage: str, config: PwpConfig, common_path: str, old_filename: str, base: str):
        LOGGER.incr_picture()

        LOGGER.debug('')
        LOGGER.debug(f"{stage} file path='{common_path}' old_filename='{old_filename}' base='{base}'")
        summary = f'{stage:6} {old_filename:31}: '  # will hold a 1 line summary of actions taken
        suffix = pathlib.Path(old_filename).suffix[1:]

        path = config[stage] + '/' + common_path
        file_path = path + "/" + old_filename
        backup = self.build_path(config['backup'], common_path, old_filename)

        if old_filename == 'Thumbs' or suffix in ["pl", "py", "log", "ini"]:   # FIXME: why Thumbs ???
            if stage == 'triage':
                LOGGER.info(f"backup {old_filename} to {backup}")
                LOGGER.msg(f"{summary} file type not managed COPY TO '{backup}'")
                ACTOR.copy(file_path, backup)
            return

        if suffix in ("bak", "md5"):
            if stage == 'triage':
                ACTOR.copy(file_path, backup)
            # silently avoid
            return

        move_to_album = (stage == 'triage')
        # if True, we need to move the file to album
        # in album stage, we move again to album only if the fle has been modified
        copy_file_path = config['tmp_dir'] + '/' + common_path + '/' + old_filename

        if suffix in ("mp4", "MP4", "txt", "TXT"):
            author = config.default_author()
            ACTOR.copy(file_path, copy_file_path, forced=True)

            summary += f"author({author+')':18} "

            suffix = suffix.lower()
            if suffix == "mp4":
                copy_object = PwpMp4(copy_file_path)
                new_date = copy_object.creation or PwpJpg.guess_file_date(file_path, config)
            else:
                copy_object = PwpObject(copy_file_path)
                new_date = PwpJpg.guess_file_date(file_path, config)

            summary += f"date({new_date}) "

        elif suffix not in ("jpg", "jpeg", "JPG", "JPEG"):
            LOGGER.msg(f"{summary} file type *** UNKNOWN *** : COPY TO '{backup}' ")
            ACTOR.copy(old_filename, backup)
            return
        else:
            suffix = "jpg"
            jpg = PwpJpg(file_path)
            new_date, author = jpg.get_jpg_new_date(config)
            summary += f"author({author+')':18} date({new_date}) "
            jpg.close()
            ACTOR.copy(file_path, copy_file_path, forced=True)
            copy_object = PwpJpg(copy_file_path)

        # here, the original file has been copied to a temporary file, copy_file_path
        # copy_file_path has not been modified.

        if copy_object.rotate(stage, config):
            if config['dryrun']:
                LOGGER.info(f"Would rotate/flip '{file_path}'")
            else:
                LOGGER.info(f"rotate/flip '{file_path}'")
            move_to_album = True  # picture was modified

            summary += "rot "
        else:
            summary += "    "
        if copy_object.set_metadata(stage, config, date=new_date, new_author=author):
            if config['dryrun']:
                LOGGER.info(f"Would insert metadata in '{file_path}'")
            else:
                LOGGER.info(f"metadata inserted in '{file_path}'")
            summary += "meta "
            move_to_album = True  # picture was modified
        else:
            summary += "     "
        copy_object.close()

        file_format = config.format('names')
        file_dico = config.format_dict(new_date, author, base=base, suffix=suffix)

        if self.rename_allowed(stage, config):
            new_filepath = file_format.format(**file_dico)
        else:
            # we do not change the name
            new_filepath = common_path + '/' + os.path.basename(file_path)

        # CAVEAT: in ALBUM, the path between ALBUM and the picture is reset by file_format !!!
        # so, common_path is NOT part of new_filepath !

        target = config['album'] + '/' + new_filepath
        target_rel_path = os.path.dirname(new_filepath)
        new_filename = os.path.basename(new_filepath)
        if suffix == 'txt':
            new_filename = old_filename
            new_filepath = target_rel_path + '/' + new_filename
            target = config['album'] + '/' + new_filepath

        to_increment = ACTOR.get_last_numerical_field(config['names'])
        album_folder = self.get_cached_folder(os.path.dirname(target))

        if new_filename not in album_folder:
            move_to_album = True  # it is not here, we need to put it

        if os.path.abspath(target) != os.path.abspath(file_path):
            move_to_album = True

        while new_filename in album_folder:
            if self.same_file(copy_file_path, target):
                if target == file_path:
                    LOGGER.info(f"File '{file_path}' has not changed")
                else:
                    LOGGER.info(f"New file '{file_path}' is already in album as '{target}'")
                move_to_album = False
                break
            elif target == file_path:
                # the file has been modified, so we need to clobber the existing file
                # message about modification was already done
                LOGGER.debug(f"Update '{file_path}' due to modifications")
                move_to_album = True
                break
            elif self.rename_allowed(stage, config):
                file_dico[to_increment] += 1
                new_filepath = file_format.format(**file_dico)
                target = config['album'] + '/' + new_filepath
                new_filename = os.path.basename(new_filepath)

                if suffix == 'txt':
                    new_filename = old_filename
                    new_filepath = target_rel_path + '/' + new_filename
                    target = config['album'] + '/' + new_filepath
                move_to_album = True
            else:
                LOGGER.debug(f"Clobber '{file_path}' with '{old_filename}' because rename not allowed")
                move_to_album = True
                break

        summary += f"-->({target}) "

        target_dir = os.path.dirname(target)
        if move_to_album:
            if stage == 'album':
                LOGGER.info(f"backup {old_filename} to {backup}")
                ACTOR.copy(file_path, backup)
                summary += f"backup({backup}) "
                ACTOR.delete(file_path)  # if dryrun, does nothing :-)

            if config['dryrun']:
                if file_path == target:
                    LOGGER.info(f"Would update '{file_path}'")
                else:
                    LOGGER.info(f"Would rename '{file_path}' : '{target}'")
                    # otherwise message is misleading: in reality, we do not rename to itself,
                    # we rename the copy that has been changed
                #  BUG:  target = file_path
            else:
                ACTOR.move(copy_file_path, target)
                if file_path == target:
                    LOGGER.info(f"Update '{file_path}'")
                else:
                    LOGGER.info(f"RENAME: '{file_path}' : '{target}'")

            # Put in cache if it was not there
            album_folder.append(new_filename)
            # self.cached_dirs[target_dir] = album_folder # in case album_folder was empty

            # here, target is always in ALBUM

            if config['enable-piwigo-sync'] and target_rel_path not in self.dirs_to_synchronize:
                self.dirs_to_synchronize.append(target_rel_path)  # for piwigo

        # even if the picture is unchanged, maybe the thumbs are not done

        if suffix == "jpg":
            if config['dryrun']:
                # we have to cheat, because target is NOT build !
                summary += self.build_all_thumbs(file_path, config, target_rel_path, stage, move_to_album)
            else:
                summary += self.build_all_thumbs(target, config, target_rel_path, stage, move_to_album)

        if not move_to_album and copy_file_path != file_path:
            ACTOR.delete(copy_file_path, forced=True)

        if stage != 'triage':
            LOGGER.msg(summary)
            return

        if config['enable-auto-configuration'] is False:
            LOGGER.msg(summary)
            return

        this_ini = path + '/' + config['ini-file']
        album_ini = target_dir + '/' + config['ini-file']

        if suffix == "jpg" and os.path.isfile(this_ini) and not os.path.isfile(album_ini):
            if config['dryrun']:
                LOGGER.info(f"Would Auto-configure '{this_ini}' to '{album_ini}'")
            else:
                LOGGER.info(f"Auto-configure '{this_ini}' to '{album_ini}'")
                self.build_auto_config(this_ini, album_ini, base)
            summary += "autoconf() "
        LOGGER.msg(summary)

    def verify_thumbnails(self, config: PwpConfig, common_path: str, old_filename: str):
        # path = config['album'] + '/' + common_path
        if old_filename[-4:] != '.jpg':
            return
        file_path = common_path + "/" + old_filename
        target_rel_path = os.path.dirname(file_path)
        target = config['album'] + '/' + file_path
        self.build_all_thumbs(target, config, target_rel_path, 'album', False)

    @staticmethod
    def synchronize(path, p_config):
        if p_config['dryrun'] or p_config['enable-piwigo-sync'] is False:
            return
        LOGGER.msg(f"synchronize '{path}'")
        if path[0] == '/':
            path = path[1:]
        all_dirs = os.path.dirname(path).split('/')

        done = ''
        for item in all_dirs:
            ACTOR.synchronize_piwigo_dir(done + item, with_files=False)
            done = done + item + '/'
        ACTOR.synchronize_piwigo_dir(path, with_files=True)

    # @staticmethod
    # def is_album_to_process(common_path, verify_albums):
    #     """
    #     test if the album needs to be processed
    #     :param common_path:
    #     :param verify_albums: True, False, or a list
    #     :return: bool
    #     """
    #     if isinstance(verify_albums, bool):
    #         raise PwpConfigError('verify-albums must be a list, not a bool')
    #
    #     if True in verify_albums:
    #         raise PwpConfigError('true is illegal in verify-albums')
    #     if False in verify_albums:
    #         raise PwpConfigError('false is illegal in verify-albums')
    #
    #     for d in verify_albums:
    #         if d.startswith(common_path):
    #             return True
    #     return False

    # @staticmethod
    # def allow_process_files_in_album(common_path, verify_albums):
    #     if isinstance(verify_albums, bool):
    #         raise PwpConfigError('verify-albums must be a list, not a bool')
    #
    #     if True in verify_albums:
    #         raise PwpConfigError('true is illegal in verify-albums')
    #     if False in verify_albums:
    #         raise PwpConfigError('false is illegal in verify-albums')
    #
    #     for d in verify_albums:
    #         if d == common_path:
    #             return True
    #     return False

    def remove_useless_thumbnails(self, path, config):
        if config['enable-thumbnails'] is False:
            LOGGER.debug(f" {path} enable-thumbnails is False")
            return
        if config['useless-thumbnails-delete'] is False:
            LOGGER.debug(f" {path} useless-thumbnails-delete is False")
            return

        if config['remote-web'] is None:
            thumbs_base = config['web'] + '/' + path
            if not os.path.isdir(thumbs_base):
                LOGGER.debug(f"remove_useless_thumbnails {path} is empty")
                # this can happen, if there are no pictures in the corresponding album
                return
            all_files = os.listdir(thumbs_base)

            for file in all_files:
                file_path = thumbs_base + '/' + file
                if os.path.isfile(file_path):
                    if file_path in self.expected_thumbnails:
                        pass  # this is normal
                    elif config['dryrun']:
                        LOGGER.msg(f"would remove '{file_path}'")
                    else:
                        LOGGER.info(f"Removing extra thumbnail {file_path}")
                        ACTOR.delete(file_path)

        else:
            thumbs_base = config['remote-web'] + '/' + path
            if not ACTOR.remote_isfile(thumbs_base):
                LOGGER.debug(f"remove_useless_thumbnails {path} (remote) is empty")
                # this can happen, if there are no pictures in the corresponding album
                return

            all_files = ACTOR.remote_ls(thumbs_base)

            for file in all_files.keys():
                file_path = thumbs_base + '/' + file
                if ACTOR.remote_isfile(file_path):
                    if file_path in self.expected_thumbnails:
                        pass  # this is normal
                    elif config['dryrun']:
                        LOGGER.msg(f"would remove '{file_path}'")
                    else:
                        LOGGER.info(f"Removing extra thumbnail {file_path}")
                        ACTOR.remote_delete(file_path)

        return  # because the debugger sometimes has issues with tail return

    def run_stage_dir(self, stage: str, p_config: PwpConfig, common_path: str, base: str, recursive=True):
        """
        stage: triages or albums
        common_path: the path, starting from TRIAGE, of the directory to run,
            it will be added to other roots
        base: the part of renamed files inherited from common_path
        """

        cur_dir = os.path.basename(common_path)

        if re.match(r'(.picasaoriginals.*|.idea.*|@eaDir)', cur_dir):
            # nothing to do here, this directory should not be managed
            return

        if stage == 'triage' and p_config['triage'] is None:
            LOGGER.msg("No TRIAGE directory")
            return

        if (stage == 'album' or stage == 'thumbnails') and p_config['album'] is None:
            LOGGER.msg("No ALBUM directory")
            return

        if stage == "thumbnails":
            path = p_config['album'] + ('' if common_path == '' else '/' + common_path)
        else:
            path = p_config[stage] + ('' if common_path == '' else '/' + common_path)

        new_conf_file = path + '/' + os.path.basename(p_config['ini-file'])
        new_conf = p_config.push_local_ini(new_conf_file)

        # if stage == 'album':
        #     if not self.is_album_to_process(common_path, p_config['verify-albums']):
        #         return

        LOGGER.msg('')
        LOGGER.msg(f"------ {stage} dir: common_path='{common_path}' base='{base}'")

        self.expected_thumbnails = []

        new_base = self.get_base_from_dir(cur_dir, p_config)

        if new_base and new_base != "":
            base = new_base

        all_files = os.listdir(path) if os.path.isdir(path) else []
        # self.cached_dirs = {}
        if recursive:
            for item in all_files:
                if os.path.isdir(path + '/' + item):
                    new_dir = common_path + ('' if common_path == '' else '/') + item
                    self.run_stage_dir(stage, new_conf, new_dir, base)

        self.expected_thumbnails = []

        for item in all_files:
            if os.path.isfile(path + '/' + item):
                # if stage == 'album' and not self.allow_process_files_in_album(common_path, p_config['verify-albums']):
                #     LOGGER.debug("Skipping file in album not leaf", common_path)
                # else:
                #     self.run_stage_file(stage, new_conf, common_path, item, base)
                if stage == 'thumbnails':
                    self.verify_thumbnails(new_conf, common_path, item)
                else:
                    self.run_stage_file(stage, new_conf, common_path, item, base)

        if stage == 'album' or stage == "thumbnails":
            self.remove_useless_thumbnails(common_path, p_config)

        if common_path == '':
            # we are back in the initial directory
            for path in self.dirs_to_synchronize:
                self.synchronize(path, p_config)

    def combined_config(self, path: str, p_config, prologue="", caller="dump_config"):
        # prologue is what we have already traversed, must end with '/' if not empty
        # path MUST be a relative path
        # the code here does NOT manage absolute paths

        if prologue == '':
            abs_path = os.path.abspath(path)
            if p_config["triage"] and abs_path.startswith(os.path.abspath(p_config["triage"])):
                rel_path = os.path.relpath(abs_path, os.path.abspath(p_config["triage"]))

                new_conf_file = p_config["triage"] + '/' + os.path.basename(p_config['ini-file'])
                new_conf = p_config.push_local_ini(new_conf_file)

                return self.combined_config(rel_path, new_conf, prologue=p_config["triage"] + '/', caller=caller)

            if p_config["album"] and abs_path.startswith(os.path.abspath(p_config["album"])):
                rel_path = os.path.relpath(abs_path, os.path.abspath(p_config["album"]))
                new_conf_file = p_config["album"] + '/' + os.path.basename(p_config['ini-file'])
                new_conf = p_config.push_local_ini(new_conf_file)
                return self.combined_config(rel_path, new_conf, prologue=p_config["album"] + '/', caller=caller)

            raise PwpConfigError(f"argument of {caller} must exist must be a subdirectory of triage or album",
                                 path)

        if path == '':
            self.dumped_config = p_config  # just for test
            return p_config

        if path[-1] != '/':
            path += '/'

        first = path.split('/')[0]
        if os.path.isdir(prologue + first):
            new_conf_file = prologue + first + '/' + os.path.basename(p_config['ini-file'])
            new_conf = p_config.push_local_ini(new_conf_file)
            new_path = path.replace(first + '/', '')
            new_prologue = prologue + '/' + first + '/' if prologue != '' else first + '/'
            return self.combined_config(new_path, new_conf, prologue=new_prologue, caller=caller)
        raise PwpConfigError(f"argument of --{caller} must exist", path)

    def dump_config(self, path, p_config):
        conf = self.combined_config(path, p_config, caller="dump_config")
        LOGGER.info(f"dump_config({path}): {conf['ini-filename-parsed']}")
        pprint.pprint(conf)

    def reset_ini(self):
        ini_file = self.parser_config['ini-file']
        if os.path.isfile(ini_file):
            ACTOR.move(ini_file, ini_file+'.bak')
        self.parser.build_ini_file(ini_file)
        LOGGER.msg(f"Reset '{ini_file}' to default")

    def run(self):
        do_exit = False  # exit is delayed until we have managed all --flag that generate exit

        # We do it HERE because we want to have read the 1st .ini in cwd

        ACTOR.configure(self.parser_config)
        LOGGER.configure(self.parser_config)

        # done automatically by argparse
        # if self.config['help']:
        #     self.parser.print_help()
        #     do_exit = True

        if self.parser_config['version']:
            version = PwpVersion()
            LOGGER.msg(f"current version: PyxlSql '{version.help}' ")
            do_exit = True

        if self.parser_config['licence']:
            licence = PwpLicence()
            licence.print()
            do_exit = True

        # -------------------------------------------------------------
        # SSH CONNECT !
        #
        # has already been done in ACTOR.configure

        remote, uname, cause, is_error = ACTOR.connect_ssh(self.parser_config)

        if self.parser_config['test-ssh']:
            LOGGER.msg("Testing ssh ")
            LOGGER.msg(f"remote host : '{ACTOR.remote_host}'")
            LOGGER.msg(f"remote port : '{ACTOR.remote_port}'")
            LOGGER.msg(f"remote user : '{ACTOR.remote_user}'")
            LOGGER.msg(f"uname       : '{uname}'")
            if remote:
                result = ACTOR.remote_ls(".")
                LOGGER.info(f"test-ssh OK: ls -l       : '{result}'")
            else:
                LOGGER.info(f"Cannot ssh : {cause}")
            do_exit = True

        if self.parser_config['test-sftp']:
            if not remote:
                LOGGER.msg("sftp test OK : skipped because no remote configuration")
                LOGGER.info("sftp test OK : skipped because no remote configuration")
            else:
                dummy = "dummy.txt"
                dummy_timestamp = ACTOR.build_timestamp(dummy)
                base = os.path.basename(dummy)
                LOGGER.debug("Testing sftp")

                dst = self.parser_config['remote-web']
                ACTOR.remote_put(dummy, dst)
                result = ACTOR.remote_ls(dst)
                if base not in result:
                    LOGGER.info(f"sftp failed      : '{result}'")
                    LOGGER.msg("sftp test failed")
                else:
                    remote_stamp = ACTOR.timestamp_from_ls(result[base])
                    if remote_stamp == dummy_timestamp:
                        LOGGER.info(f"sftp test OK          : '{result[base]}'")
                        LOGGER.msg("sftp test OK")
                    else:
                        LOGGER.info(f"sftp set time failed      : '{dummy_timestamp}'  '{remote_stamp}")
                        LOGGER.msg("sftp test failed")

                ACTOR.remote_delete(dst + '/' + dummy)
            do_exit = True

        src = self.parser_config['test-piwigo-synchronization']
        if src is not None:
            LOGGER.msg(f"Testing piwigo synchronization of '{src}'")
            ACTOR.synchronize_piwigo_dir(src, with_files=False)
            do_exit = True

        if self.parser_config['reset-ini']:
            self.reset_ini()
            do_exit = True

        if self.parser_config['dump-config']:
            self.dump_config(self.parser_config['dump-config'], self.parser_config)
            do_exit = True

        if do_exit:
            LOGGER.msg("Exiting due to cmdline options")
        else:
            with tempfile.TemporaryDirectory() as tmp_dir:
                self.parser_config['tmp_dir'] = tmp_dir

                if self.parser_config['verify-albums']:
                    if self.parser_config['triage']:
                        self.parser_config['triage'] = None
                        LOGGER.warning(f"removing target --triage {self.parser_config['triage']} " +
                                       "because --verify-album not empty")

                    if self.parser_config['verify-thumbnails']:
                        self.parser_config['verify-thumbnails'] = None
                        LOGGER.warning("removing target --verify-thumbnails " +
                                       f"{self.parser_config['verify-thumbnails']} " +
                                       "because --verify-album not empty")

                    for item in self.parser_config['verify-albums']:
                        item_father = os.path.dirname(item)
                        common_path = self.parser_config['album'] + ('/' + item_father if item_father else "")
                        cur_dir = os.path.basename(item)
                        p_config = self.combined_config(common_path, self.parser_config, caller="verify-albums")
                        new_base = self.get_base_from_dir(cur_dir, p_config)
                        self.run_stage_dir('album', p_config, item, new_base, recursive=False)

                elif self.parser_config['verify-thumbnails']:
                    if self.parser_config['triage']:
                        self.parser_config['triage'] = None
                        LOGGER.warning(f"removing target --triage {self.parser_config['triage']} " +
                                       "because --verify-thumbnails not empty")

                    for item in self.parser_config['verify-thumbnails']:
                        item_father = os.path.dirname(item)
                        common_path = self.parser_config['album'] + ('/' + item_father if item_father else "")
                        cur_dir = os.path.basename(item)
                        p_config = self.combined_config(common_path, self.parser_config, caller='verify-thumbnails')
                        new_base = self.get_base_from_dir(cur_dir, p_config)
                        self.run_stage_dir('thumbnails', p_config, item, new_base, recursive=True)
                else:
                    self.run_stage_dir('triage', self.parser_config, '', '', recursive=True)

            LOGGER.msg("End of processing")

        LOGGER.end()
        os.chdir(self.initial_cwd)


def pwp_init(arguments=None):
    """used for tests, when the test harness in test_pwp needs to use the ssh connection
    initializes PwpMain"""

    main = PwpMain(arguments)
    return main


def pwp_run(main: PwpMain):
    """used for tests, when the test harness in test_pwp needs to use the ssh connection"""
    if main is None:
        raise PwpError("main is None")
    main.run()
    return main.parser_config if main is not None else None


def pwp_main(arguments=None):
    main = PwpMain(arguments)
    if main.parser_config is None:
        return None
    return pwp_run(main)


if __name__ == "__main__":
    pwp_main(sys.argv[1:])
