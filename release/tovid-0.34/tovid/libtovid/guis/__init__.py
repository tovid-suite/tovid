# __init__.py (guis)

"""This module contains metagui-based GUIs for several of the tovid scripts.

Each of these is intended to be imported and run from some command-line
frontend script (such as ``todiscgui``), but the .py files in this directory
are themselves executable.

Having all GUI components encapsulated in a module makes it easier for
GUIs to borrow parts from each other (such as ``todisc.py`` borrowing
Controls from ``todisc.py``).

Each ``.py`` file in this directory (except this one) should define a
``run()`` method, which starts up the corresponding GUI::

    def run():
        app = Application('tovid', MAIN, VIDEO, AUDIO, BEHAVIOR)
        gui = GUI("tovid metagui", 640, 720, app)
        gui.run()

To make the ``.py`` itself executable, just add::

    if __name__ == '__main__':
        run()


"""

__all__ = [
    'todisc',
    'tovid',
    'makemenu',
    'makexml',
    'idvid',
    #'wxgtk', # for old tovid GUI, currently in libtovid.gui?
]
