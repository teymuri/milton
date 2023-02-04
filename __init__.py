import asyncio
# import computil.mi
# from computil.mid import ( 
#     open_ports, note, chord,
#     rhythm_to_sec, get_onset_durs
# )
from computil.mid import *

def proc(*ugens):
    """This is computil's main processing function."""
    asyncio.run(async_proc(ugens))
