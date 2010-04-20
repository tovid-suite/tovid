# todisc.py

"""A GUI for the todisc command-line program.
"""

import os

# Get supporting classes from libtovid.metagui
from libtovid.metagui import *
from libtovid.util import filetypes
import os
import fnmatch
from libtovid.cli import Command

# Define a few supporting functions
def to_title(filename):
    basename = os.path.basename(filename)
    firstdot = basename.find('.')
    return basename[0:firstdot]

def strip_all(filename):
    return ''

def find_masks(dir, pattern):
    file_list=[]
    ext = pattern.replace('*', '')
    for path, dirs, files in os.walk(os.path.abspath(dir)):
        for filename in fnmatch.filter(files, pattern):
            file_list+=[ filename.replace(ext, '') ]
    return file_list

def nodupes(seq):
    noDupes = []
    [noDupes.append(i) for i in seq if not noDupes.count(i)]
    return noDupes

# List of file-type selections for Filename controls
image_filetypes = [filetypes.image_files]
image_filetypes.append(filetypes.all_files)
#image_filetypes.extend(filetypes.match_types('image'))  # confusing
# video file-types from filetypes needs some additions
v_filetypes = 'm2v vob ts '
v_filetypes += filetypes.get_extensions('video').replace('*.', '')
v_filetypes += ' mp4 mpeg4 mp4v divx mkv ogv ogm ram rm rmvb wmv'
vid_filetypes = filetypes.new_filetype('Video files', v_filetypes)
video_filetypes = [vid_filetypes]
video_filetypes += [filetypes.all_files]

# some selectors can use video or audio
av_filetypes = [ filetypes.all_files, filetypes.audio_files, vid_filetypes ]

# some selectors can use image or video
visual_filetypes = [ filetypes.all_files, filetypes.image_files, vid_filetypes ]

# DVD video
dvdext = 'vob mpg mpeg mpeg2'
dvd_video_files = [ filetypes.new_filetype('DVD video files', dvdext) ]

# Users can use their own thumb masks.  Add to thumb mask control drop-down
masks = [ 'none', 'normal', 'oval', 'vignette', 'plectrum', 'arch', 'spiral', \
'blob', 'star', 'flare' ]
# $PREFIX/lib/tovid is already added to end of PATH
os_path = os.environ['PATH'].rsplit(':')
sys_dir = os_path[-1] + '/masks'
home_dir = os.path.expanduser("~") + '/.tovid/masks'
for dir in sys_dir, home_dir:
    masks.extend(find_masks(dir, '*.png'))
thumb_masks =  '|'.join(nodupes(masks))

"""Since todisc has a large number of options, it helps to store each
one in a variable, named after the corresponding command-line option.

Below are defined all the todisc options that will appear in the GUI.
The actual GUI layout comes afterwards...
"""

### --------------------------------------------------------------------
### Main todisc options
### --------------------------------------------------------------------

_menu_title = Text('Menu title', '-menu-title', 'My video collection',
    'Title text displayed on the main menu. Use \\n for a new line '
     'in a multi-line title.')

_files = List('Video files', '-files', None,
    'List of video files to include on the disc',
    Filename('', filetypes=video_filetypes))

_titles = List('Video titles', '-titles', None,
    'Titles to display in the main menu, one for each video file on the disc',
    Text())

_group = List('Grouped videos', '-group', None,
    'Video files to group together. Select the video in the list ' \
    'on the left, and add files to group with it by using the file ' \
    'selector on the right',
    Filename('', filetypes=video_filetypes))

_ntsc = Flag('NTSC', '-ntsc', True, 'NTSC, US standard')

_pal = Flag('PAL', '-pal', False, 'PAL, European standard')

_out = Filename('Output name', '-out', '',
    'Name to use for the output directory where the disc will be created.',
    'save', 'Choose an output name')


### --------------------------------------------------------------------
### Showcase options
### --------------------------------------------------------------------

_non_showcase = Label(
    'Default is centered thumbnail menu links.\nOr choose '
    'from the following "Edge aligned styles".\n'
    '( see tooltips )')

_showcase = FlagOpt('Showcase', '-showcase', False,
    'Arrange menu links along the outside edges, to leave room for'
    ' an optional "showcase" image or video.  The file entry box'
    ' is for an optional image or video file to be showcased in a'
    ' large central frame',
    Filename('', action='load', desc='Select an image or video file.',
    filetypes=visual_filetypes))

_showcase_seek = Number('Showcase seek', '-showcase-seek', 2,
    'Play showcase video from the given seek time. '
    'Note: switched menus uses the value(s) from the '
    ' "Thumbnail seek(s)" option, not this one',
    0, 3600, 'secs')

_textmenu = FlagOpt("Textmenu", '-textmenu', False,
    'A menu using just text for links instead of image AND text, arranged at '
    'outside edges.  Optionally use a "showcase" image/video, or '
    'static/animated background.  Use the "columns" option to set the number '
    'of titles in column 1 (column 2 will use the remainder).  Note that '
    'column 2 titles are aligned right. '
    'See also "Quick menu" and "Switched menus".',
    Number('Columns', '', 13, '', 0, 13))

_quick_menu = Flag('Quick menu (may need a menu video)',
    '-quick-menu', False, 'Note: may not be available in your ffmpeg '
    'as the needed "vhooks" have been deprecated. Ten times faster than '
    'normal showcase animation.  A showcase or background video is required '
    'unless doing switched menus.  Menu links are text only.  Not compatible '
    'with wave or rotate options.')

_switched_menus = Flag('Switched menus (try with "Quick menu" !)',
    '-switched-menus', False,
    'This makes a showcase style menu with text menu '
    'links.  The showcased VIDEO or IMAGE will be of each '
    'video "title", and will change as you press the '
    'up/down keys on your remote.  Do not select a '
    'showcase file for this option.  Use with '
    '"Quick menu" option for a huge speed up !')

_showcase_framestyle = Choice('', '-showcase-framestyle', 'default',
    'This option is only for menu styles with a "showcase" image.  '
    'The "none" option will use the default frame method, using imagemagick.  '
    'The "glass" option will use mplayer to make frames, giving an animated '
    'effect.  The glass style can be much faster - especially if used without '
    '-rotate and -wave options',
    'default|glass')

_showcase_framesize = Number('Frame size', '-showcase-framesize', 4,
    'Width of the showcase image/video frame in pixels',
    0, 20, 'pixels')

_showcase_frame_color = Color('Frame color', '-showcase-frame-color',
    '#6E6E6E', 'Color of the showcase frame. ')

_thumb_framesize = Number('Frame size', '-thumb-frame-size', 4,
    'Width of the thumbnail link frame in pixels',
    0, 20, 'pixels')

_thumb_frame_color = Color('Frame color', '-thumb-frame-color',
    '#6E6E6E', 'Color of the thumbnail link frame. ')

_showcase_shape = Choice('Showcase shape', '-showcase-shape', 'none',
    'Apply a shaped transparency mask to showcase videos or images. '
    'Leave at "none" to not use a feathered shape.',
    thumb_masks, 'dropdown')

_showcase_geo = Text('Image position', '-showcase-geo', '',
    'Enter the position of the top left corner of the showcase image: '
    'e.g. "200x80".  This value is applied to the video *before* is is scaled.')

_showcase_titles_align = Choice('Title alignment',
    '-showcase-titles-align', 'none',
    'This option is only for showcase style menus with video thumbnails and '
    'text.  Default is to center the text above the thumbnails.  This option '
    'will align the titles either to the left (west), center, or right '
    '(east).  Leave at "none" to let todisc sort it out for you.',
    'none|west|center|east')

# Menu settings
_bg_color = Color('', '-bg-color', '#101010',
    'Color of the menu background. Default (#101010) is NTSC color-safe black. '
    'Note: the color turns out MUCH lighter than the one you choose, '
    'so pick a VERY dark version of the color you want.')

_background = Filename('File', '-background', '',
    'Image or video displayed in the background of the main menu',
    'load', 'Select an image or video file',
    filetypes=visual_filetypes)

_bgaudio = Filename('File', '-bgaudio', '',
    'Audio file to play while the main menu plays.  '
    'Static menus use default audio length of 20 seconds.  '
    'Change with "Menu length" on "Menu" tab.  '
    'Use almost any filetype containing audio.',
    'load', 'Select a file containing audio', filetypes=av_filetypes)

_bgvideo_seek = Number('Seek', '-bgvideo-seek', 2,
    'Play background video from the given seek time (seconds)',
    0, 3600, 'secs')

_bgaudio_seek = Number('Seek', '-bgaudio-seek', 2,
    'Play background audio from the given seek time.',
    0, 3600, 'secs')

_menu_audio_fade = Number('Fade in', '-menu-audio-fade', 1,
    'Number  of  sec to fade given menu audio in and out '
    '(default: 1.0 seconds). Use a fade of "0" for no fade.',
    0, 10, 'secs')

_menu_fade = FlagOpt('Menu fade (in/out)', '-menu-fade', False,
    'Fade the menu in and out. The background will fade in first, then '
    'the title (and mist if called for), then the menu thumbs and/or titles.  '
    'The fadeout is in reverse order.  The optional numerical argument '
    'is the length of time the background will play before the menu '
    'begins to fade in.  To disable the fadeout portion, set the '
    '"Pause indefinitely" flag on the "Playback" tab.',
    Number('Start', '', 1, '', 0, 60, 'secs'))

_transition_to_menu = Flag('Transition to menu', '-transition-to-menu', False,
    'A convenience option for animated backgrounds using a menu fadein: the '
    'background will become static at the exact point the thumbs finish '
    'fading in.  This menu does not loop '
    'unless you enable "Menu looping" on the "Playback" tab).')

_intro = Filename('Intro video', '-intro', '',
    'Video to play before showing the main menu.  At present this must '
    'be a DVD compatible video at the correct resolution etc.  Only 4:3 '
    'aspect is supported.',
    'load', 'Select a video file',
    filetypes=[('DVD video', dvd_video_files)])

_menu_length = Number('Menu length', '-menu-length', 20,
    'Duration of menu. The length of the menu will also set '
    'the length of background audio for a static menu',
    0, 120, 'secs')


# Static/animated main menu
_static = Flag('Static menu', '-static', False,
    'Create still-image menus; takes less time. For duration of background '
    'audio for static menus, use "Menu length" on this tab.  See "Main menu" '
    'tab for other menu styles and options.')

_animated = Flag('Animated', '', True,
    'Create animated menus.  See "Main menu" tab for other menu styles and '
    'options.')

# Static/animated submenus
_submenus = Flag('Static submenus', '-submenus', False,
    'Create a submenu for each video title.  Submenu links lead to '
    ' chapter points.  See "Submenus" tab for more submenu options.')

_ani_submenus = Flag('Animated', '-ani-submenus', False,
    'Create an animated submenu for each video.  Submenu links lead to '
    'chapter points.  See "Submenus" tab for more submenu options.')


_submenu_length = Number('Submenu length', '-submenu-length', 14,
    'The length of the submenu. If doing static submenus and using audio '
    'for the submenu, this will be the length of the submenu audio',
    0, 80, 'secs')

_submenu_audio_fade = Number('Audio fade', '-submenu-audio-fade', 1,
    'Number of seconds to fade given submenu audio in and out.',
    0, 10, 'secs')

_submenu_audio = List('Audio', '-submenu-audio', None,
    'File(s) that will play as background audio for each submenu.  '
    'Use a single file for all submenus, or 1 file per submenu.  '
    'Any file containing audio (that ffmpeg can handle) can be used.',
    Filename('', filetypes=av_filetypes))

_submenu_background = List('Image(s)', '-submenu-background', None,
    'Background image(s) for the submenus(s). Single value or list',
    Filename('', filetypes=image_filetypes))

_submenu_titles = List('Submenu titles', '-submenu-titles', None,
        'Submenu titles for each video.  '
        'Use \\n for a new line in a multi-line title.', Text())

_chapter_titles = RelatedList('Chapter titles', '-files', '1:*',
    List('Chapter titles', '-chapter-titles', None,
        'Chapter titles for each video.  Use \\n for a new line in '
        'a multi-line title.  Number of titles given must equal the '
        'number of chapters given for that video.  HINT: If you '
        'click on a video title in the list to the left, then click '
        '"Add" repeatedly until you reach the desired number of '
        'chapters, you can then edit the titles from the keyboard using '
        'the Enter key to cycle through them. '),
    side='left',
    repeat=False)

_title_gap = Number('Space between titles', '-title-gap', 10,
    'Leave this much vertical gap between titles.  '
    'Default is 10 for line buttons, 15 for text-rect buttons.  '
    'This value is applied before the menu is scaled.',
    0, 400, 'pixels')

_text_start = Number('Start titles at', '-text-start', 50,
    'Titles will start at this pixel in the vertical axis.  '
    'This value is applied before the menu is scaled.',
    0, 460, 'pixels')



### --------------------------------------------------------------------
### Runtime behavior
### --------------------------------------------------------------------

_jobs = Number('Number of jobs to run simultaneously', '-jobs', 0,
    'Leave this value at 0 if you wish the default, which is to run '
    'as many jobs as processors found. Use this option if you wish '
    'to limit or increase this number.', 0, 32)
_keep_files = Flag('Keep intermediate files on exit', '-keep-files', False)
_no_ask = Flag('No prompts for questions', '-no-ask', False)
_no_warn = Flag('No pause at warnings', '-no-warn', False)
_grid = Flag('Grid preview', '-grid', False,
    'Show a second preview image with a grid and numbers that will help in '
    'finding coordinates for options that might use them')

_no_menu = Flag('No menu', '-no-menu', False,
    'Create a DVD with no menu. This creates a DVD with no menu '
    'which will jump to the first video, and play all videos provided '
    'in sequence.  Chapters provided with the -chapters option will be '
    'the chapter interval in minutes, or alternatively you can provide '
    'a single chapter list in HH:MM:SS format.')

_slides = List('Images for slideshow one', '-slides', None,
    "Image files for the slideshow",
    Filename('', filetypes=image_filetypes))

_submenu_slide_total = SpacedText('Number of slides shown on submenu',
    '-submenu-slide-total', '',
    'Use this many slides for making the slideshow submenus. '
    'The default is to use all the slides given.  '
    'For multiple slideshows or slideshow(s) mixed with video(s) only.  '
    'Select a submenu option on the "Basic" tab to use this option. '
    'Use a single value for all or list one value per submenu.')

_slide_transition = Choice('Transition type', '-slide-transition', 'crossfade',
    'The type of fade transition between slides in an '
    'animated slideshow menu.  Be sure  the  menu  length '
    'is long enough to support the 1 second transitions '
    'between the slides.  The length is determined by  '
    '1)  the length  of  the -bgaudio AUDIO  2) the '
    'length given with -menu-length DURATION.  '
    '* See "Basic" tab for menu length option *.',
    'crossfade|fade')

_slide_border = FlagOpt('Slide border', '-slide-border', False,
    'Use a border around animated slideshow slides (default: 100 pixels).',
    Number('width', '', 100, '', 0, 200, 'pixels'))

_slide_frame = FlagOpt('Slide frame', '-slide-frame', False,
    'Use a frame around the animated slideshow slides (default: 12).',
    Number('width', '', 12, '', 0, 20, 'pixels'))

_no_confirm_backup = Flag('No reminder prompt to  backup your slideshow files',
    '-no-confirm-backup', False, 'Todisc prompts you for a "yes" '
    ' to show you have taken backup precations.  This option '
    'disables that prompt.')

### --------------------------------------------------------------------
### Slideshows
### --------------------------------------------------------------------

_background_slideshow = Flag("Background", '-background-slideshow', False,
    'This option is only for multiple slideshows, '
    '(or mixed video and slideshow menus). It uses the '
    'animated slideshow as the background video')

_showcase_slideshow = Flag("Showcase", '-showcase-slideshow', False,
    'This option is only for multiple slideshows, '
    '(or mixed video and slideshow menus).  It uses the '
    'animated slideshow as the showcase video')

_slideshow_menu_thumbs = List('Menu slide thumbs', '-slideshow-menu-thumbs', None,
    'Slides for the menu thumbnail.  For multiple slideshows or '
    'mixed slideshows/videos only.',
    Filename('', filetypes=image_filetypes))


_use_dvd_slideshow = FlagOpt('Use dvd-slideshow program', '-use-dvd-slideshow', False,
    'Use the "dvd-slideshow" program to make the animated '
    'slideshow. You need of course to have installed this program '
    'to use this. You only need this for special effects like the '
    '"Ken Burns effect" otherwise todisc can do the job well '
    'and fast on its own. The optional file is the dvd-slideshow '
    'file you would need for non-todisc options, otherwise '
    'todisc will make the file for you. Using this option will '
    'void many todisc slideshow options.',
    Filename('', action='load', help='Select the dvd-author configuration file.'))

_slides_to_bin = List('Slides to "bin"', '-slides-to-bin', None,
    '"Binning" resizes the image to 640x480 using a "box" '
    'filter, which reduces "signal to noise ratio"'
    'Use in conjuction with the next option for burring, '
    'to achieve stronger denoising',
    Filename('', filetypes=image_filetypes))

_slides_to_blur = List('Slides to blur', '-slides-to-blur', None,
    'Blurring the image can reduce noise such as "ringing" '
    'effects.  Use values between 0x0.1 and 0x0.9 for best '
    'results.  Enter a single value or 1 value for each slide '
    'to be blurred.',
    Filename('', filetypes=image_filetypes))

_slide_blur = SpacedText('Slide blur amount', '-slide-blur', '',
    'How much to blur each slide given with "Slides to blur".  '
    'Use a single value, or a list with one value per slide given'
    'The format is {radius}x{sigma} and the default is 0x0.2.  Using '
    'values between 0x0.1 and 0x0.9 is probably the best range.')


### --------------------------------------------------------------------
### Thumbnail images
### --------------------------------------------------------------------

_thumb_shape = Choice('Thumb shape', '-thumb-shape', 'none',
    'Apply a shaped transparency mask to thumbnail videos or images.  These '
    '"feathered" shapes look best against a plain background or used with '
    '**-thumb-mist** [COLOR].  To use a "mist" background behind each thumb, '
    'see "Thumb mist" section.  Leave at "none" to not use a feathered shape.',
    thumb_masks, 'dropdown')

_thumb_columns =  Choice('Thumb columns', '-thumb-columns', 'none',
    'Use a montage tile of 3x1 or 4x1 instead of the usual 2x2 for 3 videos.  '
    'If you want 1 row with 3 thumbs choose "3", or for 1 row with 4 thumbs '
    'choose "4".',
    'none|3|4', 'dropdown')

_opacity = Number('Opacity', '-opacity', 100,
    'Opacity  of thumbnail videos as a percentage. '
    'Less than 100(%) is semi-transparent. '
    'Not recommended with dark backgrounds.',
    1, 100, '%')

_blur = Text('Blur', '-thumb-blur', "",
    'The amount of feather blur to apply to the thumb shape.  '
    'Default is 1.0 which will more or less keep the shape, creating "soft" '
    'edges.  Use float or integer values between 0.1 and 2.0')

_showcase_blur = Text('Blur', '-showcase-blur', "",
    'The amount of feather blur to apply to the showcase thumb shape.  '
    'Default is 1.0 which will more or less keep the shape, creating "soft" '
    'edges.  Use float or integer values between 0.1 and 2.0')

_3dthumbs = Flag('3D thumbs', '-3d-thumbs', False,
    'This will give an illusion of 3D to the thumbnails: '
    'dynamic lighting on rounded thumbs, and a  raised '
    ' effect on rectangular thumbs')

_rotate_thumbs = SpacedText('Rotate Thumbs (list)', '-rotate-thumbs', '',
    'Rotate  thumbs  the  given amount in degrees - can be positive or '
    'negative.  There must be one value for each file given with files.  If '
    'the values are not the same distance from zero, the thumbs will be of '
    'different sizes as images are necessarily resized *after* rotating.  '
    'Note: this will not change a portrait image into a landscape image!')

_wave = Flag('Wave effect', '-wave', False,
    'Wave effect for showcase image|video.  Alters thumbs along a sine '
    'wave.  This will pass a wave arg of -20x556, producing a gentle '
    'wave with a small amount of distortion.  To use other values you '
    'will need to use "-wave VALUE" in the "todiscopts" box on the "Behavior" '
    'tab.  See man todisc for details.')

_3dshowcase = Flag('3D thumb', '-3d-showcase', False,
    'This will give an illusion of 3D to the thumbnails: '
    'dynamic lighting on rounded thumbs, and a  raised '
    ' effect on rectangular thumbs')

_rotate = Number('Rotate thumb', '-rotate', 0,
    'Rotate the showcase image|video clockwise by this number of degrees.'
    'Note: this will not change a portait image into a landscape image!',
    -30, 30, 'degrees')

_thumb_mist = FlagOpt('Use thumb mist', '-thumb-mist', False,
    'Use a mist behind shaped thumbnails for contrast with the background.  '
    'The Color option is the color of the mist.  With some font and mist '
    'color combos you may need to use a large bold font for readability.',
    Color('', '', '#ffffff', ''))

_tile3x1 = Flag('1 row of 3 thumbs', '-tile3x1', False,
    'Use a montage tile of 3x1 instead of the usual 2x2 '
    '(3 videos only).  Not a showcase option.')

_tile4x1 = Flag('1 row of 4 thumbs', '-tile4x1', False,
    'Use a montage tile of 4x1 instead of the usual 2x2 '
    '(4 videos only).  Not a showcase option.')

_align = Choice('Align', '-align', 'north',
    'Controls positioning of the thumbnails and their titles.  '
    'With some arrangements this will have limited effects however.',
    'north|south|east|west|center', 'dropdown')

_seek = SpacedText('Thumbnail seek(s)', '-seek', '',
    'Play thumbnail videos from the given seek time (seconds).  '
    'A single value or space separated list, 1 value per video.  '
    'Also used for seeking in switched menus.')


### --------------------------------------------------------------------
### Fonts and font colors
### --------------------------------------------------------------------

# Menu title font
_menu_font = Font('', '-menu-font', 'Helvetica',
    'The font to use for the menu title')

_menu_fontsize = Number('Size', '-menu-fontsize', 24,
    'The font size to use for the menu title',
    0, 80, 'pixels', toggles=True)

_title_color = Color('', '-title-color', '#eaeaea',
    'The font color to use for the menu title')

_title_opacity = Number('Opacity', '-title-opacity', 100,
    'The opacity of the menu title.',
    0, 100, '%')

_title_stroke = Color('Stroke', '-title-stroke', None,
    'Outline color for the main menu font.')

menu_title_font = HPanel('Menu title font',
    _menu_font,
    _menu_fontsize,
    _title_color,
    _title_opacity,
    _title_stroke,
)

# Video title font
_titles_font = Font('', '-titles-font', 'Helvetica',
    'The font to use for the video titles')

_titles_fontsize = Number('Size', '-titles-fontsize', 12,
    'The font size to use for the video titles.  '
    'Default size varies depending on options chosen.',
    0, 80, 'pixels', toggles=True)

_titles_color = Color('', '-titles-color', None,
    'The font color to use for the video titles')

_titles_opacity = Number('Opacity', '-titles-opacity', 100,
    'The opacity of the video titles.',
    0, 100, '%')

_titles_stroke = Color('Stroke', '-titles-stroke', None,
    'The color to use for the video titles font outline (stroke)')

video_title_font = HPanel('Video title font',
    _titles_font,
    _titles_fontsize,
    _titles_color,
    _titles_opacity,
    _titles_stroke,
)

# Submenu font
_submenu_font = Font('', '-submenu-font', 'Helvetica',
    'The font to use for the Submenu menu titles')

_submenu_fontsize = Number('Size', '-submenu-fontsize', 24,
    'The font size to use for the submenu title',
     0, 80, toggles=True)

_submenu_title_color = Color('', '-submenu-title-color', '#eaeaea',
    'The font color to use for submenu title(s)')

_submenu_title_opacity = Number('Opacity',
    '-submenu-title-opacity', 100,
    'The opacity of the submenu title.',
    0, 100, '%')

_submenu_stroke = Color('Stroke', '-submenu-stroke', None,
    'The color for the submenu font outline (stroke).')

submenu_title_font = HPanel('Submenu title font',
    _submenu_font,
    _submenu_fontsize,
    _submenu_title_color,
    _submenu_title_opacity,
    _submenu_stroke,
)

# Submenu chapter font
_chapter_font = Font('', '-chapter-font', 'Helvetica',
    'The font to use for the chapter titles')

_chapter_fontsize = Number('Size', '-chapter-fontsize', 12,
    'The font size to use for the chapter titles',
    0, 80, 'pixels', toggles=True)

_chapter_color = Color('', '-chapter-color', None,
    'The color for the chapters font.')

_chapter_title_opacity = Number('Opacity',
    '-chapter-title-opacity', 100,
    'The opacity of the chapter titles.',
    0, 100, '%')

_chapter_stroke = Color('Stroke', '-chapter-stroke', None,
    'The color for the chapters font outline (stroke).')

submenu_chapter_font = HPanel('Submenu chapter font',
    _chapter_font,
    _chapter_fontsize,
    _chapter_color,
    _chapter_title_opacity,
    _chapter_stroke,
)

# Other stuff
_menu_title_geo = Choice('Title position', '-menu-title-geo', 'none',
    'The position of the menu title',
    'north|south|west|east|center|none', 'dropdown')

_menu_title_offset = Text('Title offset', '-menu-title-offset', '+0+50',
    'Menu title position as an offset (in pixels) from '
    'the N/S/E/W "Title position".  Use +X+Y syntax.  This '
    'value is applied to the video *before* is is scaled.')

_text_mist = Flag('Text mist', '-text-mist', False,
    'Use "mist" behind the menu title (helps with contrast).',
    enables=['-text-mist-color', '-text-mist-opacity'])

_text_mist_color = Color('', '-text-mist-color', '#ffffff',
    'Color of the mist behind the menu title.')

_text_mist_opacity = Number('Opacity', '-text-mist-opacity', 60,
    'The opacity of the mist behind the menu title.',
    1, 100, '%')




### --------------------------------------------------------------------
### Menu buttons (spumux)
### --------------------------------------------------------------------

_button_style = Choice('Style', '-button-style', 'none',
    'Style or shape of the buttons seen when playing the DVD '
    'menu.  "rect": rectangle around the thumbs, "text": uses '
    'the title text, "text-rect": rectangle around the title text, '
    '"line": line underneath title.  The "line" style is showcase only'
    ', and the "text" buttons can not be used with "showcase" menus.'
    'Leave at "none" to let todisc pick the most appropriate style. ',
    'none|rect|line|text|text-rect', 'dropdown')

_highlight_color = Color('Highlight', '-highlight-color', '#266cae',
    'Color for the menu buttons the dvd remote uses to navigate.')

_select_color = Color('Selection', '-select-color', '#de7f7c',
    'Color for the menu buttons the dvd remote uses to select.')

_outlinewidth = Number('Outlinewidth', '-outlinewidth', 14,
    'For spumux outlinewidth variable.  This option helps if spumux '
    'fails because of a large gap between button words or characters.',
    0, 20, 'pixels')

_playall = Flag('"Play all" button', '-playall', False,
    'Create a "Play All" button that jumps to the 1st title and plays '
    'all the videos in succession before returning to the main menu.')

_chapters = List('Chapters', '-chapters', None,
    'Number of chapters or HH:MM:SS string for each video. '
    'If only one value is given, use that for all videos. '
    'For grouped videos, use a "+" separator for joining '
    'the chapter string of each grouped video. '
    'An example chapter string using HH:MM:SS format: '
    '00:00:00,00:05:00,00:10:00.  An example of 2 grouped videos: '
    '00:00:00,00:05:00+00:05:00,00:10:00.  '
    'When using HH:MM:SS format the 1st chapter MUST be 00:00:00.  '
    'If using -no-menu and passing just integer(s), then the value '
    'represents the chapter INTERVAL not the number of chapters',
    Text())

_loop = FlagOpt('Menu looping (pause)', '-loop', False,
    'Pause before looping playback of the main menu.  Set the number spinbox '
    'to the pause desired.  Default pause varies depending on other options '
    'chosen.  Use -1 to disable looping',
    Number('', '', '', '', -1, 30, 'secs'))

_chain_videos = FlagOpt('Chain videos', '-chain-videos', False,
    'This option will "chain" videos so they play '
    'sequentially until the last, which will return to '
    'the menu.  You can also specify individual videos to '
    'behave like this by using the text box at the right. '
    'You can use single integers or indicate a range with a '
    '"-" separator. Example of a range: "1-2 4-6" (no quotes). '
    'This will play video 1 through video 3 before returning '
    'to the menu, and the same for video 4 through video 6.',
    Text(''))

_videos_are_chapters = Flag('Each video is a chapter',
    '-videos-are-chapters', False,
    'A button will be made on the main menu for each video which You '
    'can use as a chapter button .  Selecting any video will play '
    'them all in order starting with the selected one.' )


### --------------------------------------------------------------------
### Authoring / burning
### --------------------------------------------------------------------

# Burning options
_burn = Flag('Burn project on completion', '-burn', False)

_speed = Number('Speed', '-speed', 8,
    'Speed for burning',
    0, 30)

_device = Text('Device', '-device', '/dev/dvdrw',
    'Type your burning device (default: /dev/dvdrw)')

# Authoring
_widescreen = Choice('Widescreen', '-widescreen', 'none',
    'This will output a <video widescreen=nopanscan /> tag '
    '(for example) for the dvdauthor xml file.  It affects all '
    'videos in the titleset.  Use in conjunction with "Video aspect ratio" '
    'if your dvd player is cropping your videos.  '
    'Leave this at "none" to not output a widescreen tag',
    'none|nopanscan|noletterbox')

_aspect = Choice('Video aspect ratio', '-aspect', 'none',
    'This will output a <video aspect WIDTH:HEIGHT /> tag for the '
    'dvdauthor xml file.  It will affect all videos in the titleset.  '
    'This also has the effect of forcing a thumb aspect ratio for the menu, '
    'which is otherwise determined automatically. '
    'Leave this at "none" to let todisc and dvdauthor figure it out for you.',
    '4:3|16:9|none')

_audio_lang = SpacedText('Audio', '-audio-lang', '',
    'Single value or list of language codes for audio')

_subtitles = SpacedText('Subtitles', '-subtitles', '',
    'Single value or list')


### ---------------------------------------------------------------------------
### Main GUI layout and panel construction
### ---------------------------------------------------------------------------
"""The todisc GUI is laid out using panels and tabs for logical grouping.
"""

main =  VPanel('Basic',
    Label('You can author (and burn) a DVD with a simple menu '
          'using ONLY this "Basic" pane', 'center'),
    RelatedList('', _files, '1:1', _titles, filter=to_title),
    VPanel('',
        HPanel('',
            VPanel('Menu options',
                FlagGroup('', 'exclusive',
                    _static, _animated, _no_menu, side='left'),
                FlagGroup('', 'exclusive',
                    _submenus, _ani_submenus, side='left')
            ),
            FlagGroup('TV System', 'exclusive', _ntsc, _pal),
            VPanel('Burning',
                _burn,
                HPanel('',
                    _speed,
                    _device,
                ),
            ),
        ),
        HPanel('',
            HPanel('Video or image background', _background),
            HPanel('Audio background', _bgaudio),
        ),
        HPanel('', _menu_title, _menu_length),
        _out,
    ),
)

main_menu = Tabs('Main menu',
    HPanel('Basic settings',
        VPanel('',
            HPanel('Default style',  _non_showcase),
            VPanel('Edged aligned styles',
                _showcase,
                _textmenu,
                _quick_menu,
                _switched_menus,
            ),
        ),
        VPanel('',
            VPanel('Special menu style options',
                _menu_fade,
                _transition_to_menu,
                _intro,
            ),
            VPanel('Backgrounds',
                VPanel('Image or video options',
                    _bgvideo_seek,
                    _bg_color),
                VPanel('Audio options',
                    HPanel('',  _bgaudio_seek, _menu_audio_fade)),
            ),
        ),
    ),

    VPanel('Menu title',
        menu_title_font,
        HPanel('Layout',
            _menu_title_geo,
            _menu_title_offset,
        ),
        HPanel('Mist',
            _text_mist,
            _text_mist_color,
            _text_mist_opacity,
        ),
    ),

    VPanel('Video titles',
        video_title_font,
        HPanel('Layout',
            VPanel('For textmenu style titles',
            _text_start,
            _title_gap),
            VPanel('For showcase style menu with thumbs',
            _showcase_titles_align)),
        HPanel('DVD buttons',
            Label('Configure the style and color for the menu link '
            '"buttons" on the "Playback" tab')),
    ),
)

submenus = Tabs('Submenus',
    VPanel('Settings',
        Label('Enable a submenu option on the "Basic" tab to use submenus',
        'center'),
        _submenu_length,
        _submenu_audio_fade,
        HPanel('Backgrounds',
            _submenu_audio,
            _submenu_background,
        ),
    ),

    VPanel('Submenu titles',
        submenu_title_font,
        RelatedList('Submenu titles',
                    '-files', '1:1', _submenu_titles, filter=strip_all),
    ),

    VPanel('Chapter titles',
        submenu_chapter_font,
        _chapter_titles,
    ),
)


tab_list = []
slideshow_panel = Tabs('Slideshow',
    VPanel('General options',
        Label('Make a single slideshow on this tab.  Add slideshows using '
        'numbered tabs.  On the\n"Basic" tab: mix with videos if desired, '
        'and please set "Output name" before executing.', 'center'),
        Text('Title', '-titles', '', 'Title for this slideshow.  '
        'Use a title ONLY for multiple slideshows '
        'or slideshow(s) mixed with videos'),
        _slides,
        FlagGroup("", 'exclusive',
            Flag('Animated with transitions', '', True,
                'This is the default if you are not doing a static '
                'menu.  The slides transition one to the next, using '
                'the type of transition selected in "Transition type"'),
            Flag('Static with "Polaroid stack" menu', '-static', False,
                'This puts the  slides  onto  the  background in '
                '"random" locations with random rotations, making it '
                'look like a scattered stack of photos. This is the '
                'same as setting -static on the Main tab.'), side='left'
        ),
        VPanel('Animated slideshow options',
            HPanel('',
                _slide_transition,
                HPanel('', _slide_border, _slide_frame),
            ),
        ),
        HPanel('',
            Number('Number of slides shown on menu', '-menu-slide-total', 0,
                'Use this many slides for making the slideshow menu. '
                'The default is to use all the slides given.',
                0, 100),
            _submenu_slide_total,
        ),
    ),
    VPanel('Advanced options',
        FlagGroup('Use slideshow as background or showcase video ',
            'exclusive',
            _background_slideshow, _showcase_slideshow
        ),
        _slideshow_menu_thumbs,
        _use_dvd_slideshow,
    ),
    VPanel('Denoising options',
        HPanel('', _slides_to_bin, _slides_to_blur),
        _slide_blur),
)

tab_list.append(slideshow_panel)

for num in range(2,  13):
    title_str = 'Images for slideshow ' + str(num)
    next_panel = VPanel(str(num),
        Text('Title', '-titles', '',
            'Title for this slideshow. Leave empty if doing a single slideshow.'),
        List(title_str, '-slides', None,
            'Image files for the slideshow.',
            Filename('')),
        )
    tab_list.append(next_panel)

slideshows = Tabs('Slideshows', *tab_list)


thumbnails = VPanel("Thumbnails",
    HPanel('',
        VPanel('Menu link thumbnails',
            HPanel('Seeking', _seek),
            VPanel("Effects",
                HPanel('',_opacity, Label('(Also affects showcase thumb)')),
                HPanel('', _blur, _3dthumbs),
                _rotate_thumbs,
                _thumb_mist),
            VPanel('Arrangement',
                _thumb_shape,
                _thumb_framesize,
                _thumb_frame_color,
                HPanel('', _thumb_columns, _align),
                ),
        ),
        VPanel("Showcase thumbnail",
            HPanel('Seeking', _showcase_seek),
            VPanel('Effects',
                _wave,
                HPanel('', _showcase_blur, _3dshowcase),
                _rotate,
                HPanel('', Label('Frame style'),_showcase_framestyle)),
            VPanel('Arrangement',
                _showcase_shape,
                _showcase_framesize,
                _showcase_frame_color,
                _showcase_geo),
        ),
    ),
    HPanel('Aspect ratio', Label('Note: the aspect ratio of menu link ' 
        'thumbnails is automatic: (force video ratio on "Playback" tab)')),
)

from libtovid.guis import tovid

behavior = VPanel("Behavior",
    VPanel('',
        VPanel('Execution',_jobs),
        VPanel('Interaction',_keep_files, _no_ask, _no_warn, _no_confirm_backup),
        VPanel('Preview',_grid)),
    SpacedText('Custom todisc options', '', '',
         'Space-separated list of custom options to pass to todisc.'),
)

playback = Tabs("Playback",
    VPanel('Basic settings',
        HPanel('', _aspect,  _widescreen),
        HPanel('Menu Pause', _loop),
        HPanel('Language(s)', _audio_lang, _subtitles),
        HPanel('Navigation',
            _playall,
            _videos_are_chapters,
            _chain_videos,
        ),
        HPanel('DVD buttons',
            _button_style,
            _highlight_color,
            _select_color,
            _outlinewidth,
        ),
    ),
    VPanel('Chapters',
        RelatedList('Chapters', '-files', '1:1', _chapters, side='top', filter=strip_all),
    ),
    VPanel('Grouped Videos',
        RelatedList('Grouped videos', '-files', '1:*', _group, index=True, repeat=True),
    ),
)

encoding = VPanel('Encoding',
    Label("\nVideo re-encoding options - you may leave these at defaults.", 'center'),
    Tabs('tovid options',
        tovid.BASIC_OPTS,
        tovid.VIDEO,
        tovid.AUDIO,
        tovid.BEHAVIOR,
    ),
    SpacedText('Custom tovid options', '', '',
         'Space-separated list of custom options to pass to tovid.'),
)

### --------------------------------------------------------------------

def run():
    app = Application('todisc',
        main, main_menu, submenus, thumbnails, slideshows, playback, behavior, encoding)
    gui = GUI("todiscgui", 800, 660, app)
    gui.run()

if __name__ == '__main__':

    try:
        run()

    except:
        import traceback
        traceback.print_exc(10)
