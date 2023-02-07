import asyncio
from computil.rtmid import *
from computil.aux import *
import __main__

def proc(events):
    """This is computil's main processing function."""
    try:
        print(f"processing script {__main__.__file__}")
        asyncio.run(rtmidi_proc(events, True))
    except AttributeError:
        asyncio.run(rtmidi_proc(events, False))

