import asyncio
import mid
from mid import ( 
    open_ports, voice
)

def proc(ugens):
    """This is computil's main processing function."""
    asyncio.run(mid._async_proc(ugens))
