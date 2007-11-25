#! /usr/bin/env python
# filetypes.py

"""Defines several commonly-used multimedia and image file types.
"""

import mimetypes

image_types = {}
video_types = {}
audio_types = {}

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
 
