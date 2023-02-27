
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

# Note names
G3 = 55
C4 = 60
D4 = 62
E4 = 64
F4 = 65
G4 = 67

MAJ4 = [0, 3, 7, 12]
from cu import cfg
cfg.synth_id = "ZynAddSubFX"
print(cfg.synth_id)
rt.init()
def trem():
    ts =[]
    chs = [[30+i+j for i in MAJ4] for j in range(10)]
    x=0
    for i in range(1000):
        d = i * (x % 10)* .01
        # dd = 0.5 - i * .1
        # ts.append(note(60, onset=d,dur=.01, vel=100, chnl=3))
        x+= 1
        for ch in chs:
            ts.append(chord([48,52, 55, 60], onset=d, dur=.1, vel=10, chnl=1))
    return ts

proc(
    [trem()],
    # [[chord([62+i for i in MAJ4], onset=i*.001, dur=.001) for i in range(10)]],
    # "/tmp/test.mid"
)


