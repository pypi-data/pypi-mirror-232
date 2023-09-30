# ---------------------------------------------------------------------------------------------------------------
# piwiPre project
# This program and library is licenced under the European Union Public Licence v1.2 (see LICENCE)
# developed by fabien.battini(at)gmail.com
# ---------------------------------------------------------------------------------------------------------------


import sys
import os
import pprint
from piwiPre.pwpErrors import LOGGER
from piwiPre.pwpArgsIni import PwpArgsIni


class PwpParser(PwpArgsIni):
    default_ini_file = "piwiPre.ini"

    def __init__(self, arguments=None, with_config=True, program: str = "piwiPre"):
        super().__init__()
        self.config = None  # the config after parsing HOME,& cwd ini files and cmdline args

        self.add_header("""
Commandline Flags and configuration items
#########################################

This file is the default configuration of piwiPre.

Unless stated otherwise, the  configuration items have a command line argument counterpart,
with the same name, starting with - - .

The default value is given as an argument.

The configuration file uses the yaml syntax,
and uses pyYaml  to read/write the configuration file

- *boolean* values are *true* and *false*
- *None* denotes a value which is not set.
- *string* SHOULD single or double quotes to prevent yaml to interpret values.
- *directory* should be a valid path syntax, written as a string.
- *dictionary* read key : value
""")

        self.add_header("""

Configuration hierarchy
=======================

1. Default values are set for all items.

2. By default, configuration data is read from piwiPre.ini,
   but if the cmdline arguments hold a '--ini-file new-value.ini', then the name of the ini file is changed,
   so that the new ini-file is taken into account.

3. In the user HOME directory, as a special case, '.piwiPre.ini' is read instead.
   This file should be protected against reading from others,
   (chmod 500 in the Linux case).
   It is used to store confidential information:

   - piwigo-host
   - piwigo-port
   - piwigo-user
   - piwigo-pwd

   - remote-host
   - remote-port
   - remote-user
   - remote-pwd
   - remote-incoming 
 
   Other configuration items could also be stored there, but should be preferably stored in cwd or in TRIAGE
  
4. in cwd. Here, one usually  sets up the global configuration without the confidential information
   and without details specific to each TRIAGE directory.
   If this file stores confidential information, it should also be chmod 500.
   Once cwd/piwiPre.ini has been read, new values of the confidential configuration 
   are no more taken into account.

5. On cmdLine. In this case, options start with '--', such as '--version' etc.
 
6. When managing TRIAGE, in TRIAGE subdirectories. 

   These .ini files are read only when processing files in TRIAGE.
   Only directory-specific configuration should be stored here.

   To clarify a difficulty: when managing TRIAGE, the configuration files in ALBUM are *not* read
     
   Typically, one stores there 'names', 'authors', 'dates', 'copyright', 'instructions',
   if some of these should be different for a specific directory.
   Each ini file will be copied in the corresponding ALBUM directories.
   If there was a preexisting .ini file in the ALBUM subdir,
   then it is clobbered by the new one.
   

7. When managing ALBUM, in the directory hierarchy of ALBUM.

   These .ini files are read only when processing files in ALBUM.
   
   To clarify a difficulty: when managing ALBUM, the configuration files in TRIAGE are *not* read

   .ini files in ALBUM are usually a copy of an .ini file in the original TRIAGE directory, but they *can* be
   hand-writen by the piwigo administrator.
    
   .ini files in ALBUM are typically used to maintain directory (nested ALBUM) wide settings.
   
   For instance, some sub-ALBUM may hold pictures without shooting date in the Exif data,
   therefore the naming method is different.


8. The later has precedence over the sooner.
 
9. Therefore, cmdLine items do not modify configuration options found in directories of TRIAGE and ALBUM.
   The only way to reset these are:
   
   - To modify the .ini files in TRIAGE, and then run piwiPre to forward the modifications to ALBUM
   - To edit .ini files in ALBUM 
""")

        self.add_header("""
Some vocabulary
===============

- The **piwigo host** is the server where the piwigo service runs. 
  Usually this is a cloud-based host, or a NAS, or a Linux server.

- The **piwiPre host** is the computer where piwiPre runs. 
  Usually this is a desktop PC, but could be also the same machine than piwigo host.

- **cwd** is the directory where piwiPre is run. If a relative path is used, then it starts from there
""")
        self.add_header("""
cmdLine flags only
==================

The following command line arguments do not have configuration counterpart in the .ini file:
""")
        # -h, --help is implicit

        self.add_item('version',
                      action='store_true',
                      help="Prints piwiPre version number and exits.",
                      location='args',
                      config="""
This flag has no value, it is active only when set""")

        self.add_item('licence',
                      action='store_true',
                      help="prints the LICENCE and exits",
                      location='args',
                      config="""
This flag has no value, it is active only when set""")

        self.add_item('debug',
                      action='store_true',
                      help="Increments the level of verbosity of the logs printed on standard output.",
                      location='args',
                      config="""
This flag has no value, it is active only when set""")

        self.add_item('dump-config',
                      pwp_type=str,
                      action='store',
                      help="Dump the configuration for a given directory and exits.",
                      location='args',
                      config="""
The value of this flag is the name of the directory from which the configuration should be dumped.
  
This path starts from cwd, e.g. TRIAGE/Armor""")

        self.add_item('dryrun',
                      action='store_true',
                      help="Prints what should be done, but does not execute actions.",
                      location='args',
                      config="""this flag has no value, it is active only when set""")

        self.add_item('ini-file',
                      help="Changes the default configuration file to something else.",
                      pwp_type=str,
                      default='piwiPre.ini',
                      action='store',
                      location='args',
                      config="""
The value of this flag is the name of the new configuration file, it will be used in all directories""")

        self.add_item('reset-ini',
                      help="Resets to default the ini file in the current directory and exits.",
                      config="""
This flag has no value, it is active only when set
                      
This is useful to build a new configuration file and edit it.

CAVEAT: previous inifile is clobbered!! """,
                      action='store_true',
                      location='args')

        self.add_item('chdir',
                      help="Changes the default directory where piwiPre is run, is always executed BEFORE --ini-file",
                      pwp_type=str,
                      action='store',
                      location='args',
                      config="""
    The value of this flag is the directory to change to""")

        self.add_header("""
Global actions in ALBUM subdirectories
======================================""")

        self.add_item('verify-albums',
                      help='list of directories in ALBUM to be verified ',
                      action='append',
                      default=[],
                      location='args',
                      pwp_type=list,
                      config="""
   
- Value = a directory in ALBUM to be verified
- Default : [].
- may be used several times

If verify-albums is set, triage and verify-thumbnails are unset

Caveat: sub-directories of the target directory are NOT verified.
""")

        self.add_item('verify-thumbnails',
                      help='list of directories in ALBUM where thumbnails are verified',
                      action='append',
                      default=[],
                      location='args',
                      pwp_type=list,
                      config="""

- Value = a directory in ALBUM to be verified
- Default : [].
- may be used several times

If verify-thumbnails is set, triage is unset (and it means that verify-albums is not set)

Caveat: this is RECURSIVE: sub-directories are managed.
""")

        self.add_item('useless-thumbnails-delete',
                      help='Deletion of useless piwigo thumbnails.',
                      action='store_true',
                      location='args',
                      config="""
When doing verify-albums or verify-thumbnails, 
this flag allows to remove thumbnails that are useless because there is no corresponding picture.

This flag has no value, it is active only when set.
   
- It should be tested first with --dryrun
- It cannot be stored in a configuration file
        """)

        self.add_header("""
.. attention::
    The following flags --test-xxx are used when performing self-testing of piwiPre
    They are not intended to be used under normal circumstances""")

        self.add_item('test-piwigo-synchronization',  # album
                      help="tests piwigo sync through http for the album argument, and exits",
                      default=None,
                      action='store',
                      location='args',
                      config="""
argument = album sub-directory to synchronize
                    """)

        self.add_item('test-ssh', help="tests ssh on remote host and exits",
                      action='store_true',
                      location='args')

        self.add_item('test-sftp', help="tests rcp on remote host (by copying a file in HOME and exits",
                      action='store_true',
                      location='args')

        self.add_header("""
Management of directories
=========================""")

        self.add_item('triage',
                      help='Sets the TRIAGE directory where are stored incoming pictures.',
                      action='store',
                      default='TRIAGE',
                      config="""
- value = 'directory': Sets the TRIAGE directory

  This directory is read-only
  
  This directory can be erased once processing is finished.

- value = None: no TRIAGE directory to process
  
  When verify-albums is used, triage is automatically set to None in order to avoid confusion 
  between the configurations of triage and album
  
""")

        self.add_item('album',
                      help='Sets the root directory for ALBUM where piwigo pictures are stored.',
                      action='store',
                      default='ALBUM',
                      config="""
- value = 'directory' : Sets root directory for ALBUM
 
  a typical value is //NAS/photo 
  
- value =  None, the ALBUM directory is not managed, files are not copied from TRIAGE to ALBUM.""")

        self.add_item('backup',
                      help='Sets the modified directory.',
                      action='store',
                      default='BACKUP',
                      config="""
- value = 'directory' : Sets the BACKUPS directory, where unknown files and modified ALBUM files 
  are saved before  any modification.
  
  This directory can be erased once processing is finished.""")

        self.add_item('web',
                      help='Sets the root directory for piwigo thumbnails.',
                      action='store',
                      default='WEB',
                      config="""
- value = 'directory' : Sets the thumbnails directory.

  a typical value is //NAS/web/piwigo/_data/i/galleries/photo
""")

        self.add_item('remote-web',
                      help='Sets the REMOTE directory for piwigo thumbnails.',
                      action='store',
                      default=None,
                      config="""
- value = 'directory' : Sets the thumbnails directory when accessed through ssh/sftp on the remote host
- if value is None, then piwigo thumbnails are NOT accessed through sftp

a typical value is '/volume1/web/piwigo/_data/i/galleries/photo', appropriate for synology NAS """)

        self.add_header("""
Management of piwigo host and users 
===================================""")

        self.add_item('piwigo-user',
                      help='username on remote server, used for https administration',
                      action='store',
                      default=None,
                      config="""
- Value = 'string' :username on remote server, used by https
- Value = None : anonymous https is assumed""")

        self.add_item('piwigo-pwd',
                      help='Sets the password of the piwigo https admin ',
                      action='store',
                      default=None,
                      location='config')

        self.add_item('piwigo-host',
                      help='sets the hostname of the piwigo server, used by https administration',
                      action='store',
                      default=None,
                      config="""
- Value = 'string' : hostname of the host, used by https
- Value = None : https cannot be used""")

        self.add_item('piwigo-port',
                      help='sets the https port the piwigo server',
                      action='store',
                      pwp_type=int,
                      default=443)
        # --------------------------------------
        # ssh/sftp

        self.add_item('remote-user',
                      help='username on remote server, used for ssh/sftp',
                      action='store',
                      default=None,
                      config="""
- Value = 'string' :username on remote server, used by ssh/sftp
- Value = None : anonymous ssh/sftp is assumed""")

        self.add_item('remote-pwd',
                      help='Sets the password of the piwigo ssh/sftp ',
                      action='store',
                      default=None,
                      location='config')

        self.add_item('remote-host',
                      help='sets the hostname of the piwigo server, used by ssh/sftp',
                      action='store',
                      default=None,
                      config="""
- Value = 'string' : hostname of the host, used by ssh
- Value = None : remote ssh cannot be used""")

        self.add_item('remote-port',
                      help='sets the ssh/sftp port the piwigo server',
                      action='store',
                      pwp_type=int,
                      default=42)

        self.add_item('remote-incoming',
                      help='Path, relative to the remote directory where SFTP launches, where files can be written.',
                      action='store',
                      default=None,
                      config="""
If None, the SFTP root should be writable.

'incoming' is another typical value""")

        self.add_header("""
       
remote host configuration
=========================
Modify these settings only if you know exactly what you are doing.
The default values should be ok with any standard Linux remote host.""")

        self.add_item('ls-command',
                      help='The remote shell command to list files.',
                      action='store',
                      default='ls -sQ1 --full-time {file}',
                      location='config')

        self.add_item('ls-output',
                      help='The output of ls-command.',
                      action='store',
                      default=r'.+\s+{size}\s+{Y}-{m}-{d} {H}:{M}:{S}.\d* {z}\s+"{file}"',
                      location='config',
                      config=r"""
        Where flags are taken from 
        https://docs.python.org/3/library/datetime.html?highlight=datetime#strftime-strptime-behavior ,

           - {dir} is 'd' for a directory
           - {size} is the file size in K Bytes
           - {file} is the file name
           - {Y} is the year, with 4 digits
           - {m} is the month number, with 2 digits
           - {d} is the day number with 2 digits
           - {H} is the hour, with 2 digits
           - {M} the minutes, with 2 digits
           - {S} the seconds, with 2 digits
           - {z} the timezone, expressed as the number of hours and minutes of difference with UTC time, 
             eg. +0100 for CET during winter.
           - {am} is AM or PM

        Alternative for ms-dos, see https://www.windows-commandline.com/get-file-modified-date-time/

           - 'dir {file}'
           - '{Y}/{m}/{d} {H}:{M} {am}'\d*\s+{file}'""")

        self.add_header("""
Management of actions on pictures
=================================

enable-XXX flags have 2 values:

- **false**: no action
- **true** : action is enabled if triage or album mode

By default, all actions are enabled, and this is typically done in the configuration files.


The default values enable a regular processing of ALBUM, provided **verify-albums** is not empty.""")

        self.add_item('enable-rename',
                      help='Enables files renaming',
                      action='store',
                      choices=['true', 'false'],
                      default='true',
                      config="""
In album mode, pictures will **not** be moved from a directory to another, only the filename is changed""")

        self.add_item('enable-rotation',
                      help='Enables picture rotation',
                      action='store',
                      choices=['true', 'false'],
                      default='true',
                      config="""
                      
when ALBUM is moved from photostation to piwigo, since piwigo assumes that pictures are not rotated,
enable-rotation should be used at least once per directory if not done when importing pictures.""")

        self.add_item('enable-metadata',
                      help='Enables the generation of metadata in pictures.',
                      action='store',
                      choices=['true', 'false'],
                      default='true')

        self.add_item('enable-thumbnails',
                      help='Enables generation of Piwigo thumbnails',
                      action='store',
                      choices=['true', 'false'],
                      default='true')

        self.add_item('enable-piwigo-sync',
                      help='Enables the piwigo album synchronization.',
                      action='store',
                      choices=['true', 'false'],
                      default='true')

        self.add_item('enable-remote-copy',
                      help='Enables the copy of piwigo thumbnails with ssh/sftp.',
                      action='store',
                      choices=['true', 'false'],
                      default='false')

        self.add_item('enable-auto-configuration',
                      help='Enables configuration of ALBUM from TRIAGE.',
                      action='store',
                      choices=['true', 'false'],
                      default='true',
                      config="""
Enables the copy of piwiPre.ini files found in TRIAGE directory to the corresponding folder of ALBUM,
so that further processing of ALBUM give the same results.""")

        self.add_header("""
configuration only
==================

The following configuration items are not accessible through command line options
and must be specified in a configuration file.""")

        self.add_item('names',
                      help='The format of renamed pictures. This includes the path starting from ALBUM.',
                      action='store',
                      default='{Y}/{Y}-{m}-{month_name}-{d}-{base}/{Y}-{m}-{d}-{H}h{M}-{S}-{base}.{suffix}',
                      location='config',
                      config=r"""

CAVEAT: The value must be enclosed in single or double quotes !                      
                      
Field values:

- {Y} etc are inherited from the IPTC date of the picture.

- {base} is the name of the TRIAGE folder where the picture was originally found.

- {author} is computed according to the camera name in the IPTC metadata, see **authors**

- {count} is the current count of pictures in the directory,
  so that it is 01 for the first picture, 02 for the 2nd etc.

- {suffix}: file suffix, typically jpg, txt, mp4...

- All numeric fields are printed with 2 digits, excepted year which has 4.

When several  different pictures are supposed to have the same filename,
the last numeric field (here {s}) is incremented until a unique filename is found.


Many users prefer names that include the date,
so that name collisions are avoided when pictures are out in a flat folder.

But different schemes are possible.
For instance, "{Y}/{m}/{d}/{base}-{count}", is also a traditional naming.

all characters that are not in 
"a-zA-Z0-9\-_.&@~!,;+°()àâäéèêëïîôöùûüÿçñÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇÑ " will be replaced by '_' 
""")  # noqa

        self.add_item('month-name',
                      help='The name for each month, used to compute month_name.',
                      action='store',
                      pwp_type=list,
                      default=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                      location='config')

        self.add_item('authors',
                      help='A dictionary of mappings between camera model name as found in Exif data, and author name',
                      action='store',
                      pwp_type=dict,
                      default={},
                      location='config',
                      config="""
- example of possible value ::

   Camera1 : author1
   'Camera 2' : 'author 2'
   DEFAULT : 'default value'""")

        self.add_item('copyright',
                      help='A copyright sentence to be written in Exif metadata, with obvious fields.',
                      action='store',
                      default="(C) {author} {Y}",
                      location='config',
                      config="""- The date is taken from the photo metadata, {month} and {day} are also available.'""")

        self.add_item('instructions',
                      help="A sentence to be written in Exif metadata, with {author} coming from the 'authors' section",
                      action='store',
                      default="No copy allowed unless explicitly approved by {author} ",
                      location='config',
                      config="""- adding an email or a phone number may be appropriate.""")

        self.add_item('dates',
                      help='A dictionary of dates corrections',
                      action='store',
                      pwp_type=dict,
                      default='',  # {},
                      location='config',
                      config="""
Date corrections are used only to compute the new name of the picture in the renaming step.
The metadata (notably dates) of the picture is unchanged.

- each toplevel item a dictionary with a unique name
- each date is written as a dictionary with year, month, day, hour, minute, second, some items may be missing

- the dictionary describes each correction with the following fields:

  - 'start', 'end': dates. the correction occurs if the picture date is between these boundaries
  - camera_name: the name of the camera for this correction or 'default' for camera name not in the list
  - 'delta' or 'forced' : a date. 
  
    - If 'delta', the date is added to the picture date. 
    - If  'forced' the picture date is set to this value.

- the specific 'NO-DATE' toplevel item is for pictures without a date.
   - the 'start', 'end', delta dates are not defined
   - this item contains only 'forced' date that will be set to all pictures without a date
- when a date is 'forced', and hour, minute, second are not specified, piwiPre uses the picture creation time.
   
See also the online documentation 
   """)

        self.add_header("""
example ::

    dates:
        USA:                 # this name should be unique within the 'dates'
            start:
                year:  2018
                month:  7
                day: 4
                hour: 20
            end:
                year:  2018
                month:  7
                day: 6
                hour: 23
            D6503:              # camera name
                delta:
                    hour: 9
            TG-320:            # a different camera
                delta:
                    hour: 9
                    minute: 30
        Utah 1:
            start:
                year:  2018
                month:  7
                day: 6
                hour: 23
            end:
                year:  2018
                month:  7
                day: 8
                hour: 23
            TG-320 :
                delta:
                    hours: 8   # CAVEAT: here, hours and not hour ! (and years, etc...)
        NO-DATE:               # CAVEAT: like python, yaml is strict on indentation errors
            forced :
                 year: 2023
                 month: 7
                 day : 24

.. Note:: usually, 'NO-DATE' and  'forced' are not set on a global ALBUM base, 
   but rather in a specific TRIAGE folder where abnormal pictures are known to be stored.


.. Important:: unless enable-auto-configuration false,  
   when a .ini file is stored in a TRIAGE folder, 
   then it  will be copied in the corresponding ALBUM subdirectories, 
   so that further processing of ALBUM give the same results. 
   This is particularly useful for dates management
""")

        self.add_item('piwigo-thumbnails',
                      help="A dictionary of piwigo thumbnails to be built, including formats",
                      action='store',
                      pwp_type=dict,
                      default={
                          "{f}-sq.jpg": {'width': 120, 'height': 120, 'crop': True},
                          "{f}-th.jpg": {'width': 144, 'height': 144, 'crop': False},
                          "{f}-me.jpg": {'width': 792, 'height': 594, 'crop': False},
                          "{f}-cu_e250.jpg": {'width': 250, 'height': 250, 'crop': True},
                      },
                      location='config',
                      config="""
A dictionary if thumbnail specifications,
- {f} is the photo basename
- width = maximum width
- height = maximum height
- crop = the picture will be cropped to a square form factor.

The regular piwigo thumbnails defined in the documentation are as follows ::

    "{f}-sq.jpg" : 120, 120, crop      # SQUARE: mandatory format
    "{f}-th.jpg":  144, 144            # THUMB:  mandatory
    "{f}-me.jpg" : 792, 594            # MEDIUM: mandatory
    "{f}-2s.jpg" : 240, 240            # XXSMALL       # noqa
    "{f}-xs.jpg" : 432, 324            # XSMALL        # noqa
    "{f}-sm.jpg" : 576, 432            # SMALL
    "{f}-la.jpg" : 1008, 756           # LARGE
    "{f}-xl.jpg" : 1224, 918           # XLARGE        # noqa
    "{f}-xx.jpg" : 1656, 1242          # XXLARGE       # noqa
    "{f}-cu_e250.jpg" : 250, 250, crop # CU    : mandatory"""),  # noqa

        # TODO: self.safe_items = ['piwigo-user', 'piwigo-pwd']

        self.config = self.parse_args_and_ini(program, self.default_ini_file, arguments, with_config=with_config)


def build_official_rst(autotest: bool):
    if autotest:
        filename = "tests/results/configuration.rst.autotest"
    else:
        filename = 'source/usage/configuration.rst'
    source = 'piwiPre/pwpParser.py'
    if not autotest and os.path.getmtime(filename) > os.path.getmtime(source):
        LOGGER.msg(f"file '{filename}' is older than source '{source}': patch useless")
        return
    parser = PwpParser(arguments=[], with_config=True, program="autotest")
    LOGGER.msg(f"building official rst '{filename}' from '{source}'")
    parser.build_rst(filename)


def pwp_parser_main(arguments):
    LOGGER.msg('--------------- starting pwp_test_config')
    parser = PwpParser(arguments=arguments, program="parser_autotest", with_config=False)
    config = parser.parse_args_and_ini("test harness", "tests.ini", arguments)
    rst = "../results/test-result.rst"
    ini = "../results/test-result.ini"
    parser.build_rst(rst)
    parser.build_ini_file(ini)
    pprint.pprint(config)
    parser.print_help()
    LOGGER.msg('--------------- end of  pwp_test_config')


if __name__ == "__main__":
    sys.exit(pwp_parser_main(sys.argv[1:]))
