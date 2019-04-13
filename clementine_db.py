#!/usr/bin/env python3
import configparser
import sqlite3
import sys
import os
import urllib.parse
import shutil
HOME = os.environ.get('HOME')
sql = sqlite3.connect(HOME + '/.config/Clementine/clementine.db')

def open_config():
    HOME_DIR = os.environ.get('HOME')
    CONFIG_DIR = os.path.join(
        os.environ.get('XDG_CONFIG_HOME', os.path.join(HOME_DIR, '.config')), 'eberjand')

    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_DIR, 'scripts.cfg'))
    return config['clementine_db']

if sys.argv[1] in ('mv', 'move', 'rename'):
    if len(sys.argv) < 4:
        print('Need more arguments')
        sys.exit(1)
    c = sql.cursor()
    src = os.path.abspath(sys.argv[2])
    dst = os.path.abspath(sys.argv[3])
    if not os.path.exists(src):
        print('Path not found:', src)
        sys.exit(1)
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    print('mv "%s" "%s"' % (src, dst))
    c.execute('''UPDATE songs SET filename = 
        CAST(replace(CAST(filename as text), :src, :dst) as blob)
        WHERE CAST(filename as text) LIKE :src || "%"''',
        {
            'src': 'file://' + urllib.parse.quote(src, safe='/;!@$&()+=,[]') + '/',
            'dst': 'file://' + urllib.parse.quote(dst, safe='/;!@$&()+=,[]') + '/'
        })
    print('Modified: ', c.rowcount)
    sql.commit()
    shutil.move(src, dst)
elif sys.argv[1] in ('ratings'):
    config = open_config()
    min_rating = sys.argv[2] if len(sys.argv) > 2 else config['min_rating']
    rating_file_list = sys.argv[3] if len(sys.argv) > 3 else config['rating_file_list']
    file_list = open(rating_file_list, 'w')
    numsongs = 0
    c = sql.cursor()
    sql_cmd = 'select filename from songs WHERE rating>?'
    for row in c.execute(sql_cmd, (float(min_rating) - 0.01,)):
        fname = urllib.parse.unquote(row[0].decode('utf-8'))
        if fname.startswith('file:///'):
            fname = fname[len('file://'):]
            if os.path.isfile(fname):
                file_list.write(fname + '\n')
                numsongs += 1
    file_list.close()
    print('Songs:', numsongs)

#c = sql.cursor()
#c.execute('SELECT filename, rating from songs')
#c.execute('UPDATE songs SET rating = ? WHERE )
