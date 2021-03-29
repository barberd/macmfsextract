# macmfsextract
Python utility to extract files from Macintosh MFS filesystem images

MFS (https://en.wikipedia.org/wiki/Macintosh_File_System) was the original Macintosh filesystem used with the release of the Macintosh in 1984. It was replaced with HFS a year and a half later after Apple introduced the first Macintosh hard drives. HFS tools and FUSE modules can be found, but not much exists for MFS. Anyone wanting to extract files from images of these early programs often had to load the images into an emulator; with this python script the files can now be extracted directly. Its especially helpful for extracting hidden files or inspecting volume and file dates. Note Macintosh dates are seconds since midnight Jan 1 1904.

Details on MFS were obtained from https://www.macgui.com/news/article.php?t=482

Usage:

To extract all files in the IMAGEFILE MFS image to the current directory

./mfsextract.py IMAGEFILE

To show additional details such as the block mapping and timestamps, run:

./mfsextract.py IMAGEFILE verbose

Conceptually, one could run this directly on a floppy drive such as:

./mfsextract.py /dev/fd0

but as most of these images were on 400k Macintosh floppies, it would only really make sense on an m68k linux install on a Macintosh both new enough to run Linux (68020 or later processor) and old enough to have a floppy drive capable of reading the original 400k floppies....perhaps a SE/30 or Classic II.
