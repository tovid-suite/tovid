#! /usr/bin/env python
# filetypes.py

"""Defines several commonly-used multimedia and image file types.
"""

__all__ = ['match_types']

import mimetypes

image_types = {}
video_types = {}
audio_types = {}

def match_types(containing):
    """Return a list of (type, extensions) tuples for matching mimetypes.
    
        containing: String or list of strings to match, for example:
                match_types('image/jpeg')
            Uses a "contains" search, so you can do:
                match_types(['image', 'mpeg'])
            to match any mimetype containing 'image' or 'mpeg'.

    The returned tuples are suitable for use as the 'filetypes' argument of
    Tkinter file dialogs (askopenfilename etc.).
    """
    if type(containing) == str:
        containing = [containing]
    elif type(containing) != list:
        raise TypeError("match_types requires a string or list argument.")

    types = {}
    # Check for matching types and remember their extensions
    for ext, typename in mimetypes.types_map.items():
        for substr in containing:
            if substr in typename:
                # Append or insert extension
                if typename in types:
                    types[typename] += ' *' + ext
                else:
                    types[typename] = '*' + ext

    # Convert to tuple-list form
    return types.items()
    
    

# Get all known image, video, and audio types/extensions
for ext, typename in mimetypes.types_map.items():
    if typename.startswith('image/'):
        image_types[ext] = typename
    elif typename.startswith('video/'):
        video_types[ext] = typename
    elif typename.startswith('audio/'):
        audio_types[ext] = typename


all_files = ('All files', '*.*')

# image files
jpeg = ('JPEG files', '*.jpg')
png = ('PNG files', '*.png')
tga = ('TGA files', '*.tga')
gif = ('GIF files', '*.gif')
bmp = ('BMP files', '*.bmp')
image_files = ('Image files', '*.jpg *.png *.tga *.bmp *.gif')

# video files
mpeg = ('MPEG files', '*.mpg')
avi = ('AVI files', '*.avi')
mov = ('MOV files', '*.mov')
mp4 = ('MPEG4 files', '*.mp4')
rm = ('Realmedia files', '*.rm')
mkv = ('Matroska files', '*.mkv')
video_files = ('Video files', '*.mpg *.avi *.rm *.mkv *.mp4')

# audio files
wav = ('WAV files', '*.wav')
mp3 = ('MP3 files', '*.mp3')
ac3 = ('AC3 files', '*.ac3')
ra = ('Realaudio files', '*.ra')
flac = ('FLAC files', '*.flac')
aac = ('AAC files', '*.aac')
m4a = ('M4A files', '*.m4a')
mp2 = ('MPEG audio files', '*.mp2 *.mpa')
ogg = ('OGG files', '*.ogg')
mka = ('Matroska audio files', '*.mka')
audio_files = ('Audio files', '*.wav *.mp3 *.ac3 *.mp2 *.ra *.flac *.aac *.m4a *.ogg *.mka')
 
