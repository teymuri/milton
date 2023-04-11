import __main__
import asyncio
import computil.curtmidi as rt # realtime
import computil.cumidiutil as wr # writer
import computil.cumido as rd # reader
from datetime import datetime
from .utils import *


try:
    from __main__ import __file__ # running a python script.py?
    _SCRIPT = True
except ImportError: # running from shell
    _SCRIPT = False


def proc(events, mid="", opt=False):
    """Processes every thing!
    Set opt to True to listen first and decide to write to the disk or not afterwards."""
    if mid: # write to a midi file
        cumidiutil.save(events, mid)
        print(f"Saved {mid} at {datetime.now()}")
    else: # play now
        if opt:
            asyncio.run(rt.play(events, _SCRIPT))
            mid_path = input("Spec path ( without suffix ) to save\n")
            if mid_path:
                cumidiutil.save(events, mid_path + ".mid")
                print(f"Wrote to {mid_path}.mid at {datetime.now()}")
        else:
            asyncio.run(rt.play(events, _SCRIPT))
