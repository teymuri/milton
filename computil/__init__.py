import __main__
import asyncio
import computil.rt
import computil.mu
from .common import *


try:
    from __main__ import __file__ # running a python script.py?
    _SCRIPT = True
except ImportError: # running from shell
    _SCRIPT = False


def proc(events, mid="", opt=False):
    """Processes every thing!
    Set opt to True to listen first and decide to write to the disk or not afterwards."""
    if mid: # write to a midi file
        mu.save(events, mid)
    else: # play now
        if opt:
            asyncio.run(rt.play(events, _SCRIPT))
            mid_path = input("That's how u compose! Take it (specify path) or leave it...\n")
            if mid_path:
                mu.save(events, mid_path)
                print(f"Wrote to {mid_path}")
        else:
            asyncio.run(rt.play(events, _SCRIPT))
