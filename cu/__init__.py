import __main__
import asyncio
import cu.rt
import cu.mu
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
        mu.proc(events, mid)
    else: # play now
        if opt:
            asyncio.run(rt.proc(events, _SCRIPT))
            mid_path = input("That's how u compose! Take it (specify path) or leave it...")
            if mid_path:
                mu.proc(events, mid_path)
                print(f"Wrote to {mid_path}")
        else:
            asyncio.run(rt.proc(events, _SCRIPT))
