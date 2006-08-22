import tempfile
import xml.dom
import os
from cli import Script, Arg

dom = xml.dom.getDOMImplementation()

def mktempname(*args, **kwargs):
    fd, fname = tempfile.mkstemp(*args, **kwargs)
    os.close(fd)
    return fname

def mktempstream(*args, **kwargs):
    return open(mktempname(*args, **kwargs), "+w")

VALID_TAGS = {
    'filename': None,
    'characterset': 'UTF-8',
    'fontsize': '18.0',
    'font': 'Vera.ttf',
    'horizontal-alignment': 'center',
    'vertical-alignment': 'bottom',
    'left-margin': '60',
    'right-margin': '60',
    'subtitles-fps': '25',
    'movie-fps': None,
    'movie-width': None,
    'movie-height': None,
}

def create_xml(opts):
    """Returns a string with the XML necessary for spumux"""
    doc = dom.createDocument(None, "subpictures", None)
    root = doc.firstChild
    
    stream = doc.createElement("stream")
    root.appendChild(stream)
    
    textsub = doc.createElement("textsub")
    
    for key in VALID_TAGS:
        try:
            textsub.setAttribute(key, opts[key])
        except KeyError:
            default = VALID_TAGS[key]
            if default is None:
                raise
            # set the default value
            textsub.setAttribute(key, default)
            
    return doc.toprettyxml()

def spumux(xmlopts, stream=0):
    """
    Runs a script from the command line
    """
    filename = xmlopts['filename']
    data = create_xml(xmlopts)
    
    
    fd = mktempstream(suffix=".xml")
    try:
        fd.write(data)
        fd.close()
    except:
        # remove temp file and raise error
        os.unkink(fd)
        raise
    
    # make sure the temporary mpeg is created on the same directory
    base_dir = os.path.dirname(filename)
    tmp_mpg = mktempname(suffix=".mpg", dir=base_dir)
    
    script = Script()
    
    # spumux -s0 < in > out
    cmd = Arg('spumux').add("-s").add(stream)
    cmd.read_from(filename)
    cmd.write_to(tmp_mpg)
    script.append(cmd)
    
    # remove old file
    script.append(Arg('rm').add('-f', filename))
    
    # rename temporary file to new file
    script.append(Arg('mv').add(tmp_mpg, filename))
    
    script.run()

def generate(options):
    """generate the subtitles from the following options"""
    infile = options['in']
    xmlopts = {
        'movie-fps': options['fps'],
        'movie-width': infile.video.width,
        'movie-height': infile.video.height,
        'filename': options['out'],
    }
    spumux(xmlopts)
