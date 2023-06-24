# NCMUtil


## Usage

```sh
$ pip install -r requirements.txt
$ python main.py MODULE ARGUMENTS...
```

## Modules

### `get_lyric`

Required parameters:

```
id (positional): int
o|output (optional): str
t|translation (switch): Whether not to output translated lyric
l|lrc (switch): Whether to prefer lrc to yrc (elrc)
```

### `get_metadata`

Fill metadata using information from server.  
Requires `ffmpeg` to run.

Required parameters:

```
file (positional): str
id (optional): int, specifies the song id. Will ask for choice if this is missing
o|output (optional): str, specifies the output file(the one with proper metadata), default set to FILE.out.EXTENSION
```

---

Thanks to [Binaryify/NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi) for encryption details