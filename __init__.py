import asyncio
from computil.rtmid import *
from computil.aux import *

def proc(*items):
    """This is computil's main processing function."""
    asyncio.run(rtmid_proc(items))
