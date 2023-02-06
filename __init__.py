import asyncio
from computil.rtmid import *
from computil.aux import *
import __main__

def proc(*items):
    """This is computil's main processing function."""
    try:
        print(f"processing script {__main__.__file__}")
        asyncio.run(rtmidi_proc(items, True))
    except AttributeError:
        print("intact mode")
        asyncio.run(rtmidi_proc(items, False))

