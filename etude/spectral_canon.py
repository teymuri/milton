from math import log2
import computil as cu

first_interval = 4 # in seconds
K = first_interval / log2(9 / 8)
def duration(n):
    return K * log2((8 + n) / (7 + n))

# x = 0
# os=[]
# for n in range(1, 9):
#     os.append(x)
#     x += duration(n)
#
cu.cfg.port_count = 4
cu.open_ports()
# ns=[]
# for o, d in zip(os, cu.get_onset_durs(os)):
#     ns.append(cu.note(knum=33, onset=o, dur=d))
#
# # cu.proc(ns)


# for i in range(1, 23*8+1):
#     print(i, duration(i), i%8==1)

os=[]
ds=[]
for vidx in range(24):
    vonset = K * log2(vidx + 1)
    ox=[vonset]
    dx=[]
    for n in range(1, 185):
        d=duration(n)
        dx.append(d)
        vonset += d
        ox.append(vonset)
    os.append(ox)
    ds.append(dx)

vs=[]
hz=55
for i in range(len(os[:3])):
    v = []    
    hz *= (i + 1)
    for j, o in enumerate(os[:3][i]):
        # breakpoint()
        v.append(cu.note(onset=o, dur=.1, chnl=i+1, knum=cu.hz_to_knum(hz)))
    vs.append(v)

# print(vs)
# print(duration(1), duration(9), K*log2(1))
# print(K*log2(1), K*log2(2), K*log2(3))
# print(K*log2(2)==K)

cu.proc(*vs)
