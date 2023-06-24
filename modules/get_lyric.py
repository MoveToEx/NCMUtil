import re
from .api import NCMAPI
from argparse import ArgumentParser

ap = ArgumentParser()

ap.add_argument('id', type=int)
ap.add_argument('-o', '--output')
ap.add_argument('-t', '--translation', action='store_false')
ap.add_argument('-l', '--lrc', action='store_false')

api = NCMAPI()

# [ms,en] => [mm:ss.MM]
# (ms,en,?) => <mm:ss.MM>
def ts_conv(s: str):
    bracket = '[]' if s.startswith('[') else '<>'
    ms = int(re.search(r'(\d+),\d+,?\d*', s).group(1))
    second = ms // 1000
    minute = second // 60
    ms %= 1000
    second %= 60
    return "%c%02d:%02d.%03d%c" % (bracket[0], minute, second, ms, bracket[1])

def ylc_to_elrc(s):
    pl = '\n'.join(filter(lambda x: x.startswith('['), s.split('\n')))
    a = re.split(r'([\[\(]\d+,\d+,?\d*[\]\)])', pl)
    res = []
    for i in a:
        if re.match(r'[\[\(]\d+,\d+,?\d*[\]\)]', i):
            res.append(ts_conv(i))
        else:
            res.append(i)
    return ''.join(res)

def main(argv):
    args = ap.parse_args(argv)
    res = ""

    s = api.lyric(args.id)

    if s.get('yrc', {}).get('lyric', '') and args.lrc:
        res += ylc_to_elrc(s['yrc']['lyric']) + '\n'
    elif s.get('lrc', {}).get('lyric', ''):
        res += '\n'.join(filter(lambda x: x.startswith('['), s['lrc']['lyric'].split('\n'))) + '\n'

    if args.translation:
        if s.get('ytlrc', {}).get('lyric'):
            res += '\n'.join(filter(lambda x: re.match(r'\[\d+', x), s['ytlrc']['lyric'].split('\n'))) + '\n'
        elif s.get('tlyric', {}).get('lyric'):
            res += '\n'.join(filter(lambda x: re.match(r'\[\d+', x), s['tlyric']['lyric'].split('\n'))) + '\n'

    if args.output:
        with open(args.output, 'w') as f:
            f.write(res)
    else:
        print(res)