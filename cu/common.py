"""
bunch of useful functions
"""

from random import random
from cu.rt import _get_note_data


def note(knum=60, onset=0, dur=1, chnl=1, vel=127):
    data = {"type": "note"}
    data.update({"knum":knum,"onset":onset,"dur":dur,"vel":vel})
    data.update(_get_note_data(knum, chnl, vel))
    return data


def chord(knums=(60, 64, 67), onset=0, dur=1, chnl=1, vel=127):
    data = {"type": "chord"}
    data.update({"knums":knums, "onset":onset, "dur":dur,"vel":vel})
    data.update({"notes":[note(kn, onset, dur, chnl, vel) for kn in knums]})
    return data

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


def dur_to_onset(durs, offset=0):
    """Returns a list of (accumulated onset, corresponding duration).
    Offset is the desired starting onset."""
    durs = list(durs) # convert to pop
    onsets = []
    while durs:
        d = durs.pop(0)
        onsets.append((d, offset))
        offset += d
    return onsets

def onset_to_dur(onsets):
    return [b - a for b, a in zip(onsets[1:], onsets[:-1])]

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

def get_onset(nt):
    """Returns note's onset time."""
    return nt[-1]["onset"]

def get_chnl(nt):
    return nt[-1]["chnl"]

def get_vel(nt):
    return nt[-1]["vel"]

def get_knum(nt):
    return nt[-1]["knum"]

def get_dur(nt):
    return nt[-1]["dur"]

def exp_growth(init, rate, periods):
    """Returns an exponential curve."""
    return [init * pow(rate, t) for t in range(periods)]
