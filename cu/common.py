"""
bunch of useful functions
"""

from random import random
from cu.rt import _get_note_data


def note(knum=60, onset=0, dur=1, chnl=1, vel=127):
    data = _get_note_data(knum, chnl, vel)
    return ("n",) + data + (onset, dur, {"knum":knum,"onset":onset,"dur":dur,"chnl":chnl,"vel":vel})

def chord(knums=(60, 64, 67), onset=0, dur=1, chnl=1, vel=127):
    return ["c"] + [note(kn, onset, dur, chnl, vel) for kn in knums]
def pret(x):
    """Prints and returns the thing, good for debuging."""
    print(x)
    return x

def bpm_to_sec(bpm):
    """Returns the duration of one beat in tempo bpm."""
    return 60 / bpm

def rhy_to_sec(rhy, tempo):
    """"""
    return rhy * 4.0 * bpm_to_sec(tempo)

def knum_to_hz(knum):
    return 440 * 2 ** ((knum - 69) / 12.)

def hz_to_knum(hz):
    if hz == 0:
        raise computil.err.CUZeroHzErr()
    return 12 * (log2(hz) - log2(440)) + 69

def get_intervals(ns):
    return [b - a for a, b in zip(ns[:-1], ns[1:])]

def durs_to_onsets(durs):
    os = []
    o = 0
    for d in durs:
        o += d
        os.append(o)
    return os

def scale_to_sum(nums, _sum):
    """Scales a set of numbers such that they sum up 
    to _sum after scaling

    https://math.stackexchange.com/questions/1009138/how-do-you-scale-a-set-of-number-such-that-they-sum-to-0-5-after-scaling"""
    return [n * _sum / sum(nums) for n in nums]

def minmax_norm(x, minx, maxx, low_bound=0, up_bound=1):
    """Min-max normalization (usually called feature scaling) performs 
    a linear transformation on the original data. This technique gets all 
    the scaled data in the range (0, 1) and arbitrarily rescale a range 
    between an arbitrary set of values (lower and upper bounds).
    Google feature scaling."""
    rescale_rng = up_bound - low_bound
    return low_bound + ((x - minx) * rescale_rng) / (maxx - minx) 

def ascprob(idx, seqlen):
    r = random()< minmax_norm(idx, 0, seqlen-1)
    return r

# def ascprob(idx, seqlen):
#     return 0 <= random() < (idx + 1) / seqlen

def get_onset(note):
    return note[-1]["onset"]

def get_chnl(note):
    return note[-1]["chnl"]

def get_vel(note):
    return note[-1]["vel"]

def get_knum(note):
    return note[-1]["knum"]

def get_dur(note):
    return note[-1]["dur"]
