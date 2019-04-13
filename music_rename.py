#!/usr/bin/env python3
import mutagen
import sys
import shutil
from mutagen.easyid3 import EasyID3
src = sys.argv[1]
ext = src[src.rfind('.'):]
disc = None
title = 'Untitled'
track = None

if ext.lower() == '.mp3':
    f = EasyID3(src)
elif ext.lower() in ['.flac', '.opus', '.ogg']:
    f = mutagen.File(src)
elif ext.lower() in ['.m4a', '.aac']:
    f = mutagen.File(src)
    title = f['\xa9nam'][0]
    track = f['trkn'][0][0]
    disc = f['disk'][0][0]
else:
    print('Unrecognized extension:', src)
    sys.exit(1)

if 'title' in f:
    title = f['title'][0]
if 'discnumber' in f:
    # "Disc 1 of 2" may either have a value of "1" or "1/2" here
    disc = f['discnumber'][0]
    if '/' in disc:
        disc = disc[0:disc.find('/')]
    disc = int(disc)
if 'tracknumber' in f:
    track = f['tracknumber'][0]
    if '/' in track:
        track = track[0:track.find('/')]
    track = int(track)

title = title\
    .replace('/', '_')\
    .replace('\\', '_')\
    .replace('|', '_')\
    .replace(':', ' -')\
    .replace('?', '')\
    .replace('*', '')\
    .replace('"', '')\
    .replace('<', '[')\
    .replace('>', ']')

if disc is not None:
    dst = '%d%02d. %s%s' % (disc, track, title, ext)
else:
    dst = '%02d. %s%s' % (track, title, ext)
if src == dst:
    print('Unchanged:', src)
else:
    shutil.move(src, dst)
    print(dst)
