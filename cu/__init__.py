import __main__
import asyncio
from .rtmid import *
from .aux import *
from .midutil import *


try:
    from __main__ import __file__ # running from shell?
    _INTERACT = True
except ImportError:
    _INTERACT = False


def proc(events, path=""):
    """This is computil's main processing function."""
    if path:
        midiutil_proc(events, path)
    else:
        asyncio.run(rtmidi_proc(events, _INTERACT))
