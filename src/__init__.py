import __main__
import asyncio
from rtmid import *
from aux import *


def proc(events):
    """This is computil's main processing function."""
    try:
        print(f"processing script {__main__.__file__}")
        asyncio.run(rtmidi_proc(events, True))
    except AttributeError:
        asyncio.run(rtmidi_proc(events, False))

