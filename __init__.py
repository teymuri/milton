import asyncio
import computil.mid
from computil.mid import ( 
    open_ports, voice, note, chord
)

def proc(*ugens):
    """This is computil's main processing function."""
    asyncio.run(mid._async_proc(ugens))
