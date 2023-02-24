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


def proc(events, mid=""):
    """Processes every thing!"""
    if mid: # write to a midi file
        mu.proc(events, mid)
    else: # play now
        asyncio.run(rt.proc(events, _SCRIPT))
