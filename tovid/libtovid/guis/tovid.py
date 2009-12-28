# tovid.py

"""A GUI for the ``tovid`` script.
"""

# Get supporting classes from libtovid.metagui
from libtovid.metagui import *

### --------------------------------------------------------------------
### tovid
### --------------------------------------------------------------------

_in = Filename('Input filename', '-in', '',
    'Video file to encode',
    'load', 'Select a video file')
_out = Filename('Output prefix', '-out', '',
    'Name to use for encoded output file (.mpg added automatically)',
    'save', 'Choose an output prefix')

# Standard formats
_dvd = Flag("DVD", '-dvd', True,
    "(720x480 NTSC, 720x576 PAL) DVD-compatible output. May be burned "
    "to a DVD[+/-]R[W] disc. Also known as Digital [Versatile|Video] Disc, "
    "or just DVD depending on who you talk to.")
_svcd = Flag("Super Video CD (SVCD)", '-svcd', False,
    "(480x480 NTSC, 480x576 PAL) Super Video CD format, may be burned "
    "to a CD-R. Like VCD but with better resolution and variable bitrate. "
    " About 1 hour of playing time per disc.")
_vcd = Flag("Video CD (VCD)", '-vcd', False,
    "(320x240 NTSC, 320x288 PAL) Video CD format, may be burned to a CD-R. "
    "About 1 hour of playing time per disc.")

# Extra formats
_dvd_vcd = Flag('VCD-on-DVD', '-dvd-vcd', False,
    '(352x240 NTSC, 352x288 PAL) VCD-on-DVD output')
_half_dvd = Flag('Half-DVD', '-half-dvd', False,
    '(352x480 NTSC, 352x576 PAL) Half-D1-compatible output')
_kvcd = Flag('KVCD', '-kvcd', False,
    '(352x240 NTSC, 352x288 PAL) KVCD-enhanced long-playing video CD')
_kvcdx3 = Flag('KVCDx3', '-kvcdx3', False,
    '(528x480 NTSC, 520x576 PAL) KVCDx3 specification')
_kvcdx3a = Flag('KVCDx3A', '-kvcdx3a', False,
    '(544x480 NTSC, 544x576 PAL) KVCDx3a specification')
_kdvd = Flag('KDVD', '-kdvd', False,
    '(720x480 NTSC, 720x576 PAL) KVCD-enhanced long-playing DVD')
_bdvd = Flag('BDVD', '-bdvd', False,
    '(720x480 NTSC, 720x576 PAL) BVCD-enhanced long-playing DVD')

# Aspect ratio
_full = Flag('4:3 (full-frame)', '-full', True)
_wide = Flag('16:9 (widescreen)', '-wide', False)
_panavision = Flag('2.35:1 (panavision)', '-panavision', False)
_aspect = Text('Aspect ratio', '-aspect', '4:3',
    'Explicit integer aspect ratio (ex. 6:4)')

# TV Systems
_ntsc = Flag("NTSC", '-ntsc', True, "NTSC, US standard, 29.97 fps")
_ntscfilm = Flag("NTSC Film", '-ntscfilm', False, "NTSC Film, 23.976 fps")
_pal = Flag("PAL", '-pal', False, "PAL, European standard, 25.00 fps")

# Video quality/size controls
_quality = Number('Quality', '-quality', 6,
    'Quality of encoding, on a scale of 1-10, with 10 giving the best '
    'quality, at the expense of a larger output file.',
    1, 10)
_vbitrate = Number('Bitrate', '-vbitrate', 0,
    'Target video bit rate, in kilobits per second. Higher bit rates '
    'give better quality, but a larger output file.',
    0, 9000, units='kbits/sec')
_fit = Number('Fit to', '-fit', 0,
    'Fit the output file into the given size in MiB (2^20 bytes). '
    'Video bitrate and quantization are chosen to ensure the target size '
    'is not exceeded. Ignored for VCD, which has constant bitrate.',
    0, 4400, units='MiB')
_discsize = Number('Disc size', '-discsize', 0,
    'Size of target media, in MiB (2^20 bytes). Output will be split into '
    'chunks of this size.',
    0, 4400, units='MiB')

# Encoder options
_mplayeropts = SpacedText('mplayer options', '-mplayeropts', '', 'TODO: Tooltip')
_filters = Choice('mplayer filters', '-filters', 'none', 'TODO: Tooltip',
    'none|denoise|deblock|contrast|all', side='top')
_ffmpeg = Flag('Encode using ffmpeg', '-ffmpeg', False)
_parallel = Flag('Parallel video/audio encoding', '-parallel', False,
    "(mpeg2enc only) Rip, encode, and multiplex in parallel.")

# Interlacing
_interlaced = Flag('Interlaced encoding', '-interlaced', False,
    "Do interlaced encoding. Use this if your source material is interlaced.")
_interlaced_bf = Flag('Interlaced (bottom first)', '-interlaced_bf', False,
    "Do interlaced encoding, bottom-field first. Use this if "
    "the -interlaced option produces bad output.")
_deinterlace = Flag('Deinterlace', '-deinterlace', False,
    "Deinterlace the input video, and create a progressive-scan output. "
    "Degrades video quality considerably.")

# Picture manipulation
_safe = Number('Safe area', '-safe', 90,
    'Safe area as a percentage of screen size',
    50, 100, 'scale')
_crop = Text('Crop', '-crop', '', 'TODO: Tooltip')
_slice = Number('Slice', '-slice', 0, 'TODO: Tooltip', 0, 220000)
_fps = Text('FPS', '-fps', '', 'TODO: Tooltip')
_type = Choice('Video type', '-type', 'live', 'TODO: Tooltip',
    'live|animation|bw', side='top')

# Subtitles
_autosubs = Flag('Auto-subtitles', '-autosubs', False,
    'Automatically include subtitle files with the same '
    'name as the input video.')
_mkvsub = Text('mkvsub', '-mkvsub', '',
    'EXPERIMENTAL. Attempt to encode an integrated subtitle stream '
    '(such as may be found in Matroska .mkv files) in the given '
    'language code (eng, jpn, etc.) May work for other formats.')
_subtitles = Filename('subtitles', '-subtitles', '',
    'Get subtitles from FILE and encode them into the video. '
    'WARNING: This hard-codes the subtitles into the video, and you '
    'cannot turn them off while viewing the video. By default, no subtitles '
    'are loaded. If your video is already compliant with the chosen output '
    'format, it will be re-encoded to include the subtitles.',
    'load', 'Select a subtitle file')

# Audio options
_normalize = Flag('Normalize', '-normalize', False,
    'Analyze the audio stream and then normalize the volume of the audio. '
    'This is useful if the audio is too quiet or too loud, or you want to '
    'make volume consistent for a bunch of videos. Similar to running '
    'normalize without any parameters. The default is -12dB average level '
    'with 0dB gain.')
_downmix = Flag('Downmix', '-downmix', False,
    'Encode all audio tracks as stereo. This can save space on your DVD if '
    'your player only does stereo. The default behavior of tovid is to use the '
    'original number of channels in each track. For aac audio, downmixing is '
    'not possible: tovid runs a quick 1 frame test to try to downmix the input '
    'track with the largest number of channels, and if it fails then it will '
    'revert to the default behavior of using the original channels.')
_audiotrack = SpacedText('Audio track', '-audiotrack', '',
    'Encode  the  given  audio  track, if the input video has multiple '
    'audio tracks.  NUM is 1 for the first track, 2 for the second, etc. '
    'You may also provide a list of tracks, separated by spaces or commas, '
    'for example -audiotrack 3,1,2. Use idvid on your source video to '
    'determine which audio tracks it contains. ')
_abitrate = Number('Audio bitrate', '-abitrate', 224,
   'Encode audio at NUM kilobits per second. Reasonable values include 128, '
    '224,  and  384.  The default is 224 kbits/sec, good enough for most '
    'encodings. The value must be within the allowable range for the chosen '
    'disc format; Ignored for VCD, which must be 224.',
    128, 384, units='kbits/sec')
_amplitude = Text('Amplitude', '-amplitude', '',
    'In addition to analyzing and normalizing, apply the gain to the audio '
    'such that the "average" (RMS) sound level is NUM. Valid values range '
    '0.0 - 1.0, with  0.0  being  silent and 1.0 being full scale. Use NUMdB '
    'for a decibel gain below full scale '
    '(the default without -amplitude is -12dB).')
_async = Number('Audio sync', '-async', 0, 'Adjust audio synchronization',
    -600, 600, units='secs')

# File-related
_keepfiles = Flag('Keep temporary files', '-keepfiles')
_overwrite = Flag('Overwrite files', '-overwrite')
_nofifo = Flag('No FIFO', '-nofifo', False,
    "Don't use a FIFO (pipe) when encoding. Instead, write "
    "intermediate conversion files to disk. May take "
    "up lots of space!")

# Runtime behavior
_config = Filename('Configuration file', '-config', '', 'TODO: Tooltip',
    'load', 'Select tovid configuration file')
_priority = Choice('Process priority', '-priority', 'high', 'TODO: Tooltip',
    'low|medium|high')
_update = Number('Update interval', '-update', 5, 'TODO: Tooltip', 1, 20)
_quiet = Flag('Quiet', '-quiet')
_fake = Flag('Fake encoding', '-fake')
_force = Flag('Force encoding', '-force')

# Prompting
_noask = Flag('No prompts',  '-noask', False, 'TODO: Tooltip')
_from_gui = Flag('From GUI', '-from-gui', True)

### ---------------------------------------------------------------------------
### Higher-level groups and panels
### ---------------------------------------------------------------------------

IN_OUT = VPanel('Filenames', _in, _out)
FORMAT = FlagGroup('Disc format', 'exclusive',
    _dvd, _svcd, _vcd,
    _dvd_vcd, _half_dvd, _kvcd,
    _kvcdx3a, _kdvd, _bdvd,
    side='top',
    columns=3)

BASIC_OPTS = VPanel('Basic options',
    FORMAT,
    HPanel('Output file size', _quality, _vbitrate, _fit, _discsize),
    HPanel('',
        FlagGroup('TV System', 'exclusive', _ntsc, _ntscfilm, _pal),
        FlagGroup('Aspect ratio', 'exclusive', _full, _wide, _panavision),
        FlagGroup('Interlacing', 'exclusive',
                  _interlaced, _interlaced_bf, _deinterlace)
    ),
)

MAIN = VPanel('Main',
    IN_OUT,
    BASIC_OPTS,
)

VIDEO = HPanel('Video',
    VPanel('Encoder options',
        FlagGroup('', 'exclusive', _ffmpeg, _parallel),
        _filters,
        _mplayeropts,
        _force,
    ),
    VPanel('Picture manipulation',
        _safe, _crop, _slice, _fps, _type),
)

AUDIO = VPanel('Audio & Subtitles',
    _normalize,
    _downmix,
    _audiotrack,
    _abitrate,
    _amplitude,
    _async,
    _autosubs,
    _mkvsub,
    _subtitles,
)

BEHAVIOR = VPanel('Behavior',
    _config,
    _priority,
    VPanel('File output', _fake, _overwrite, _keepfiles, _nofifo),
    VPanel('Prompts and output options', _quiet, _noask, _from_gui, _update)
)

### --------------------------------------------------------------------
### main GUI
### --------------------------------------------------------------------

def run():
    app = Application('tovid', MAIN, VIDEO, AUDIO, BEHAVIOR)
    gui = GUI("tovid metagui", 640, 720, app)
    gui.run()

if __name__ == '__main__':
    run()

