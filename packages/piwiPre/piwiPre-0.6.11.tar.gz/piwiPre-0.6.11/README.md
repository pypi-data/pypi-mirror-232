# piwiPre

piwiPre is a python/windows tool to prepare pictures for piwigo, 
and maintain the piwigo album 

It was initially developed for a piwigo instance running on a remote server such as a Synology NAS, 
while the 'photo' and 'web' directories are accessible from a PC where piwiPre is run, 
but it can run on many other configurations. 

Some of its features can be useful even when piwigo is not used.

piwiPre executes the following tasks:

1. Read configuration files and command-line argument to insure a high level of configuration.

2. Process new pictures on the local host in the TRIAGE directory 
   - process copy of pictures and leave original unmodified 
   - realign picture rotation
   - insert metadata (copyright, instructions)
   - correct picture dates
   - rename pictures
   - avoid collision of filenames
   - put updated copies into ALBUM
   - build piwigo thumbnails
   - copy thumbnails to a remote location through ssh/sftp
   - self-configure ALBUM for maintenance 
   
3. Maintain  ALBUM 
   - work only on selected directories
   - Ensure the directory is aligned with the current configuration
   
4. log intensively the actions

## what piwiPre does *not*

piwiPre does not manage synology thumbnails created by synology filestation,
which is not a concern because those thumbnails are small (less than 500KB).

piwiPre does not copy pictures to piwogo albums that are accessible only through ssh.
This is a future feature in version 2.

However, piwiPre DOES copy *thumbnails* to the piwigo server through ssh/sftp.

## How to get piwiPre

- Python module on Pypi : https://pypi.org/project/piwiPre
- Python source on gitlab: https://gitlab.com/fabien_battini/piwiPre
- Windows on-file exe on gitlab artifacts: https://fabien_battini.gitlab.io/piwipre/html/download.html


# How to use piwiPre (short)

1. Copy new pictures and videos from your cameras to the TRIAGE directory.

2. Create subdirectories is TRIAGE according to your taste
   - The name of the subdirectory will be a base for the new filename of pictures
   - move files into one of those.

3. Optionally edit the pictures in TRIAGE with digiKam, gimp or other image processing tool.

4. If you want managed files to be written to a remote piwigo server, then you need a piwiPre.ini configuration file.
   - If it does not exist, create one by running 'piwiPre --reset-ini' and edit it. 
   - At least, the following items should be  updated: piwigo-user, piwigo-pwd, piwigo-host. 
   - An alternative is to not use the configuration file and use the corresponding --xxx command-line items

5. Run piwiPre

6. Results:
   - pictures have metadata inserted
   - picture rotation is reset to default
   - Files are renamed according to directories, dates
   - the thumbnails are generated
   - files have been copied to ALBUM
   - piwiPre.log holds an exhaustive log
   
# piwiPre as a tool

piwiPre is also a command-line tool, with command-line options.
For more information:

``piwiPre.py --help 
``

# Documentation

Documentation is built using Sphinx https://www.sphinx-doc.org/

Documentation is generated in https://fabien_battini.gitlab.io/piwipre/html/
This process is achieved automatically through gitlab CI pipelines.

gitlab: https://gitlab.com/fabien_battini/piwipre

doc : https://fabien_battini.gitlab.io/piwipre/html/ 

test coverage: https://fabien_battini.gitlab.io/piwipre/html/htmlcov/index.html  

pypi: https://pypi.org/project/piwipre/

LinkedIN: https://www.linkedin.com/in/fabien-battini-supelec/
