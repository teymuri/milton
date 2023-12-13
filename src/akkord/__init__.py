import __main__
import asyncio
import akkord.realtime
import akkord.writer
import akkord.reader
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
        writer.save(events, mid)
        print(f"Saved {mid} at {datetime.now()}")
    else: # play now
        if opt:
            asyncio.run(realtime.play(events, _SCRIPT))
            mid_path = input("Spec path ( without suffix ) to save\n")
            if mid_path:
                writer.save(events, mid_path + ".mid")
                print(f"Wrote to {mid_path}.mid at {datetime.now()}")
        else:
            asyncio.run(realtime.play(events, _SCRIPT))
