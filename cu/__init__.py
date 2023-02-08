import __main__
import asyncio
from .rtmid import *
from .aux import *
from .midutil import *


try:
    from __main__ import __file__ # running a python script.py?
    _SCRIPT = True
except ImportError: # running from shell
    _SCRIPT = False


def proc(events, mid=""):
    """This is computil's main processing function."""
    if mid: # write to a midi file
        midiutil_proc(events, mid)
    else: # play
        asyncio.run(rtmidi_proc(events, _SCRIPT))
