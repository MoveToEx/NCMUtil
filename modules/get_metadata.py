import subprocess
import json
import inquirer
from functools import reduce
from datetime import datetime
from argparse import ArgumentParser

from .api import NCMAPI

ap = ArgumentParser()
api = NCMAPI()

ap.add_argument('file')
ap.add_argument('-id', type=int)
ap.add_argument('-o', '--output')


def search(file):
    raw = subprocess.check_output(['ffprobe', '-i', file, '-show_format',
                                  '-hide_banner', '-loglevel', 'error', '-print_format', 'json'])
    info = json.loads(raw.decode())
    tags = info['format']['tags']

    _ = {}
    for i in tags:
        if i.islower():
            _[i.upper()] = tags[i]

    tags.update(_)

    if not (tags['TITLE'] or tags['ARTIST']):
        raise Exception("Both TITLE and ARTIST are missing. ID required")

    qs = tags['ARTIST'] + ' ' + tags['TITLE']
    res = api.search(qs.strip())
    qt = [
        inquirer.List('id', message="Select an ID from search result", choices=[
            f"{','.join([r['name'] for r in x['ar']])} - {x['name']} #{x['id']}" for x in res['result']['songs']
        ])
    ]
    ua = inquirer.prompt(qt)['id']
    return int(ua.split('#')[-1])


def main(argv):
    args = ap.parse_args(argv)

    if not args.output:
        out = '.'.join(args.file.split(
            '.')[:-1]) + '.out.' + args.file.split('.')[-1]
    else:
        out = args.output

    if not args.id:
        id = search(args.file)
    else:
        id = args.id

    info = api.detail(id)['songs'][0]

    metadata = {
        'TITLE': info['name'],
        'ARTIST': '/'.join([r['name'] for r in info['ar']]),
        'COMMENT': ''
    }

    if info['al']['id']:
        album_info = api.album(info['al']['id'])
        album_songs = [x['name'] for x in album_info['songs']]
        pub_time = datetime.fromtimestamp(album_info['album']['publishTime'] / 1000)
        metadata['DATE'] = pub_time.strftime('%Y/%m/%d')
        metadata['ALBUM'] = info['al']['name']
        metadata['ALBUM_ARTIST'] = '/'.join([x['name'] for x in album_info['album']['artists']])
        metadata['DISC'] = info['cd']
        metadata['TRACKTOTAL'] = album_info['album']['size']
        metadata['TRACK'] = album_songs.index(info['name']) + 1

    metadata = [[
        '-metadata', f'{x}={metadata[x]}'
    ] for x in metadata]

    subprocess.call([
        'ffmpeg',
        '-i', args.file,
        '-i', info['al']['picUrl'],
        '-map:a', '0:a',
        '-map:v', '1:v',
        '-id3v2_version', '4',
        '-disposition:1', 'attached_pic',
        '-c', 'copy',
        *reduce(lambda a, b: a + b, metadata),
        '-metadata:s:v', 'comment=Cover (front)',
        out,
        '-hide_banner', '-y'
    ])
