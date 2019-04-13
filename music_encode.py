#!/usr/bin/env python3
# This script takes a list of music files that should be synced to a mobile device and prepares
# a directory containing only those files by re-encoding FLAC files into a more compact format,
# hard-linking anything else of interest, and removing any existing unneeded files in that
# directory.
# The resulting directory can be uploaded with rsync. For example, to a Termux sshd:
# $ rsync -rv --size-only --delete $OUTPUT_ROOT $ANDROID_HOST:/sdcard/Music/
# Note: The above example uses --size-only because Android hosts can have problems with mtime.
# Android's media library normally needs a forced rescan after this kind of sync.
import os
import configparser
import subprocess
import tempfile
import time


def read_config():
    home_dir = os.environ.get('HOME')
    config_dir = os.path.join(
        os.environ.get('XDG_CONFIG_HOME', os.path.join(home_dir, '.config')), 'eberjand')
    parser = configparser.ConfigParser()
    parser.read(os.path.join(config_dir, 'scripts.cfg'))
    return parser['music_encode']

CONFIG = read_config()
# Path to a file containing a list of newline-delimited input filenames that should be reencoded
ENCODING_LIST = CONFIG['encoding_list']
# All encoded output files are placed relative to this directory
OUTPUT_ROOT = CONFIG['output_root']
# This directory should contain all (or most) of the files in encoding_list.
INPUT_ROOT = CONFIG['input_root']

def convert_flac_to_ogg(src, dst):
    # TODO avoid creating incomplete files if Ctrl+C is pressed
    # TODO reduce the size of large artwork files by downscaling or converting png->jpg
    # TODO resample any 96kHz music files down to 48kHz
    subprocess.run(['oggenc', '-Q', '-o', dst, '-q5', src])
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close()
    cp = subprocess.run(['metaflac', '--export-picture-to=' + temp.name, src])
    if cp.returncode == 0:
        subprocess.run(['oggart.sh', dst, temp.name])
    os.remove(temp.name)

class FilesToEncodeIterator:
    def __init__(self):
        self.src_file_arr = [line.rstrip('\n\r') for line in open(ENCODING_LIST)]
        self.src_file_arr.sort()
        self.dst_file_arr = [
            os.path.join(root, f)
            for root, dirs, files in os.walk(OUTPUT_ROOT)
            for f in files]
        self.dst_file_arr.sort()

    def __iter__(self):
        self.src_idx = 0
        self.dst_idx = 0
        return self

    def __next__(self):
        # TODO pick a better naming scheme for these variables
        # src: The next file path read from ENCODING_LIST
        # dst: The next file that already exists in OUTPUT_ROOT
        # out: The corresponding output file in OUTPUT_ROOT for this src
        while True:
            # Determine the next file that already exists in OUTPUT_ROOT
            if self.dst_idx < len(self.dst_file_arr):
                dst_path = self.dst_file_arr[self.dst_idx]
                dst_rel = dst_path
                if dst_path.startswith(OUTPUT_ROOT + '/'):
                    dst_rel = dst_path[len(OUTPUT_ROOT) + 1:]
            else:
                dst_path = None
                dst_rel = None

            if self.src_idx >= len(self.src_file_arr):
                if dst_path is not None:
                    self.dst_idx += 1
                    return None, dst_path
                else:
                    raise StopIteration

            # Determine the next source file and its corresponding output file's path
            src_path = self.src_file_arr[self.src_idx]
            if not os.path.isfile(src_path):
                self.src_idx += 1
                continue
            src_rel = src_path[len(INPUT_ROOT) + 1:] \
                if src_path.startswith(INPUT_ROOT + '/') else src_path
            out_rel = src_rel[:-4] + 'ogg' if src_rel.endswith('.flac') else src_rel
            out_path = os.path.join(OUTPUT_ROOT, out_rel)

            if out_rel == dst_rel:
                # The same file exists in the ENCODING_LIST and OUTPUT_ROOT
                self.src_idx += 1
                self.dst_idx += 1
                # Keep the existing file unless the source has newer modified timestamp
                if os.path.getmtime(src_path) <= os.path.getmtime(dst_path):
                    continue
                return src_path, out_path
            elif dst_rel is not None and out_rel > dst_rel:
                # This file exists in OUTPUT_ROOT but isn't in the ENCODING_LIST
                self.dst_idx += 1
                return None, dst_path
            else: # if dst_rel is None or out_rel < dst_rel:
                # This file exists in the ENCODING_LIST but isn't in OUTPUT_ROOT
                self.src_idx += 1
                return src_path, out_path

def main():
    for src_path, out_path in FilesToEncodeIterator():
        if src_path is None:
            print('rm ' + out_path)
            os.remove(out_path)
            continue
        if os.path.exists(out_path):
            print('update', out_path)
            os.remove(out_path)
        else:
            print('add', out_path)
        out_dir = os.path.dirname(out_path)
        os.makedirs(out_dir, exist_ok=True)
        if src_path.endswith('.flac'):
            convert_flac_to_ogg(src_path, out_path)
        else:
            os.link(src_path, out_path)


if __name__ == '__main__':
    main()
