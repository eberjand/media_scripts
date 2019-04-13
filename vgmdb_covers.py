#!/usr/bin/env python3
import os
import sys
import json
import math
import urllib.request

def print_usage():
    print('Usage: %s https://vgmdb.net/album/###')
    sys.exit(1)

if len(sys.argv) < 2:
    print_usage()

url = sys.argv[1]
if not url.startswith('https://vgmdb.net/album/'):
    print_usage()
album_id = int(url[len('https://vgmdb.net/album/'):])

#TODO Using this json api seems to exclude certain scans.
# In particular, it normally excludes all booklet pages, Obi, and Tray.
# Consider scraping HTML instead to actually get every scan.
jso_url = 'https://vgmdb.info/album/%d?format=json' % album_id
req = urllib.request.urlopen(jso_url)
jso = json.load(req)
print(jso['name'])

track_languages = set()
tracks = []
max_track_digits = 2
disc_digits = math.ceil(math.log10(len(jso['discs'])))
multi_disc = len(jso['discs']) > 1
for disc in jso['discs']:
    max_track_digits = max(max_track_digits, math.ceil(math.log10(len(disc['tracks']))))
for disc_idx, disc in enumerate(jso['discs']):
    disc_num = str(disc_idx + 1).zfill(disc_digits)
    disc_track_digits = max(2, math.ceil(math.log10(len(disc['tracks']))))
    for track_idx, track in enumerate(disc['tracks']):
        track_num = str(track_idx + 1).zfill(disc_track_digits)
        track_languages |= track['names'].keys()
        if multi_disc:
            track_num = disc_num + ('-' if max_track_digits > 2 else '') + track_num
        track['num'] = track_num
        tracks.append(track)

nfo = open('vgmdb_%d.nfo' % album_id, 'w')
nfo.write(
    'Album: %s\n' % jso['name'] +
    'Catalog: %s\n' % jso['catalog'] +
    'URL: https://vgmdb.net/album/%s\n' % jso['link'])
for lang in sorted(track_languages):
    nfo.write('Tracks: %s\n' % lang)
    nfo.writelines(['%s. %s\n' % (track['num'], track['names'].get(lang, 'Untitled'))
        for track in tracks])
nfo.close()

os.makedirs('Scans', exist_ok=True)
for cover in jso['covers']:
    print('%s = %s' % (cover['name'], cover['full']))
    img_url = cover['full']
    ext = img_url[img_url.rfind('.'):]
    img_in = urllib.request.urlopen(img_url)
    img_out_path = 'Scans/%s%s' % (cover['name'].replace('/', '_'), ext)
    img_out = open(img_out_path, 'wb')
    img_out.write(img_in.read())
    img_out.close()
    img_in.close()
