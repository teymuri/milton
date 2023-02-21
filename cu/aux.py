"""
bunch of useful functions
"""

from random import random


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
    if random() < minmax_norm(idx, 0, seqlen-1):
        return True
    else:
        return False
