
from cu import *

def test():
    import random

    v_cnt = 4
    n_cnt = 1000
    asyncio.run(
        play_poly(
            [[random.randint(48, 82) for _ in range(n_cnt)] for _ in range(v_cnt)],
            [[.001] * n_cnt for _ in range(v_cnt)],
            [random.randint(1, 16) for _ in range(v_cnt)], 
            [[50] * n_cnt for _ in range(v_cnt)],
            True
        )
    )

def piccolo():
    viertel = 6/5
    notes = list(range(36, 75, 2)) + list(range(72, 35, -2))
    up = list(range(36, 75, 2))
    down = reversed(up)
    d = viertel / 2 / len(up)
    for p in cycle(up):
        print(p)
        play_note(p, d, vel=50)
# Note names
G3 = 55
C4 = 60
D4 = 62
E4 = 64
F4 = 65
G4 = 67

MAJ4 = [0, 3, 7, 12]
open_ports()
def trem():
    ts =[]
    chs = [[62+i for i in MAJ4] for _ in range(10)]
    x=0
    for i in range(1000):
        d = .0001 + i * .001
        dd = 0.5 - i * .1
        ts.append(chord(chs[0], onset=d,dur=.0001, vel=100, chnl=1))
        # for x in range(10):
        #
            # print(dd)
            # play_note(40, dur=d, vel=100)
        # for ch in chs:
            # play_chord(ch, dur=d, vel=100, ch=1)
    return ts

proc(
    [trem()],
    "/tmp/test.mid"
)


