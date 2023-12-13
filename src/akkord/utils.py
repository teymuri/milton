"""
This module comprises the public interface of akkord.
"""

# from random.random import (random.random.choice, random, random.uniform, random.randint, random.randrange)
import random
from math import (modf, log)
from itertools import (groupby, chain, islice)
from akkord.realtime import _get_note_data

INSTRUMENTS = [
    'Acoustic Grand Piano',
    'Bright Acoustic Piano',
    'Electric Grand Piano',
    'Honky-tonk Piano',
    'Electric Piano 1',
    'Electric Piano 2',
    'Harpsichord',
    'Clavi',
    'Celesta',
    'Glockenspiel',
    'Music Box',
    'Vibraphone',
    'Marimba',
    'Xylophone',
    'Tubular Bells',
    'Dulcimer',
    'Drawbar Organ',
    'Percussive Organ',
    'Rock Organ',
    'Church Organ',
    'Reed Organ',
    'Accordion',
    'Harmonica',
    'Tango Accordion',
    'Acoustic Guitar (nylon)',
    'Acoustic Guitar (steel)',
    'Electric Guitar (jazz)',
    'Electric Guitar (clean)',
    'Electric Guitar (muted)',
    'Overdriven Guitar',
    'Distortion Guitar',
    'Guitar harmonics',
    'Acoustic Bass',
    'Electric Bass (finger)',
    'Electric Bass (pick)',
    'Fretless Bass',
    'Slap Bass 1',
    'Slap Bass 2',
    'Synth Bass 1',
    'Synth Bass 2',
    'Violin',
    'Viola',
    'Cello',
    'Contrabass',
    'Tremolo Strings',
    'Pizzicato Strings',
    'Orchestral Harp',
    'Timpani',
    'String Ensemble 1',
    'String Ensemble 2',
    'SynthStrings 1',
    'SynthStrings 2',
    'Choir Aahs',
    'Voice Oohs',
    'Synth Voice',
    'Orchestra Hit',
    'Trumpet',
    'Trombone',
    'Tuba',
    'Muted Trumpet',
    'French Horn',
    'Brass Section',
    'SynthBrass 1',
    'SynthBrass 2',
    'Soprano Sax',
    'Alto Sax',
    'Tenor Sax',
    'Baritone Sax',
    'Oboe',
    'English Horn',
    'Bassoon',
    'Clarinet',
    'Piccolo',
    'Flute',
    'Recorder',
    'Pan Flute',
    'Blown Bottle',
    'Shakuhachi',
    'Whistle',
    'Ocarina',
    'Lead 1 (square)',
    'Lead 2 (sawtooth)',
    'Lead 3 (calliope)',
    'Lead 4 (chiff)',
    'Lead 5 (charang)',
    'Lead 6 (voice)',
    'Lead 7 (fifths)',
    'Lead 8 (bass + lead)',
    'Pad 1 (new age)',
    'Pad 2 (warm)',
    'Pad 3 (polysynth)',
    'Pad 4 (choir)',
    'Pad 5 (bowed)',
    'Pad 6 (metallic)',
    'Pad 7 (halo)',
    'Pad 8 (sweep)',
    'FX 1 (rain)',
    'FX 2 (soundtrack)',
    'FX 3 (crystal)',
    'FX 4 (atmosphere)',
    'FX 5 (brightness)',
    'FX 6 (goblins)',
    'FX 7 (echoes)',
    'FX 8 (sci-fi)',
    'Sitar',
    'Banjo',
    'Shamisen',
    'Koto',
    'Kalimba',
    'Bag pipe',
    'Fiddle',
    'Shanai',
    'Tinkle Bell',
    'Agogo',
    'Steel Drums',
    'Woodblock',
    'Taiko Drum',
    'Melodic Tom',
    'Synth Drum',
    'Reverse Cymbal',
    'Guitar Fret Noise',
    'Breath Noise',
    'Seashore',
    'Bird Tweet',
    'Telephone Ring',
    'Helicopter',
    'Applause',
    'Gunshot'
]
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
OCTAVES = list(range(11))
NOTES_IN_OCTAVE = len(NOTES)

errors = {
    'program': 'Bad input, please refer this spec-\n'
               'http://www.electronics.dit.ie/staff/tscarff/Music_technology/midi/program_change.htm',
    'notes': 'Bad input, please refer this spec-\n'
             'http://www.electronics.dit.ie/staff/tscarff/Music_technology/midi/midi_note_numbers_for_octaves.htm'
}


def instrument_to_program(instrument: str) -> int:
    assert instrument in INSTRUMENTS, errors['program']
    return INSTRUMENTS.index(instrument) + 1


def program_to_instrument(program: int) ->  str:
    assert 1 <= program <= 128, errors['program']
    return INSTRUMENTS[program - 1]


def number_to_note(number: int) -> tuple:
    octave = number // NOTES_IN_OCTAVE
    assert octave in OCTAVES, errors['notes']
    assert 0 <= number <= 127, errors['notes']
    note = NOTES[number % NOTES_IN_OCTAVE]
    return note, octave


def note_to_number(note: str, octave: int) -> int:
    assert note in NOTES, errors['notes']
    assert octave in OCTAVES, errors['notes']
    note = NOTES.index(note)
    note += (NOTES_IN_OCTAVE * octave)
    assert 0 <= note <= 127, errors['notes']
    return note
################### https://gist.github.com/devxpy/063968e0a2ef9b6db0bd6af8079dad2a

_NAMES_KNUMS = dict()

for knum in range(128):
    pset = knum % 12
    okt = knum // 12 - 1
    match pset:
        case 0:
            _NAMES_KNUMS[f"c{okt}"] = knum
        case 1:
            _NAMES_KNUMS[f"c#{okt}"] = knum
            _NAMES_KNUMS[f"db{okt}"] = knum
        case 2:
            _NAMES_KNUMS[f"d{okt}"] = knum
        case 3:
            _NAMES_KNUMS[f"d#{okt}"] = knum
            _NAMES_KNUMS[f"eb{okt}"] = knum
        case 4:
            _NAMES_KNUMS[f"e{okt}"] = knum
        case 5:
            _NAMES_KNUMS[f"f{okt}"] = knum
        case 6:
            _NAMES_KNUMS[f"f#{okt}"] = knum
            _NAMES_KNUMS[f"gb{okt}"] = knum
        case 7:
            _NAMES_KNUMS[f"g{okt}"] = knum
        case 8:
            _NAMES_KNUMS[f"g#{okt}"] = knum
            _NAMES_KNUMS[f"ab{okt}"] = knum
        case 9:
            _NAMES_KNUMS[f"a{okt}"] = knum
        case 10:
            _NAMES_KNUMS[f"a#{okt}"] = knum
            _NAMES_KNUMS[f"bb{okt}"] = knum
        case 11:
            _NAMES_KNUMS[f"b{okt}"] = knum

_KNUMS_NAMES = {kn: nm for nm, kn in _NAMES_KNUMS.items()}

def name_to_knum(name):
    return _NAMES_KNUMS[name]

def knum_to_name(knum):
    return _KNUMS_NAMES[knum]

# https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies
PNO_LO_KNUM, PNO_HI_KNUM = 21, 108
PNO_LO_NAME, PNO_HI_NAME = knum_to_name(PNO_LO_KNUM), knum_to_name(PNO_HI_KNUM)

def make_note(pch=60, onset=0, dur=1, chnl=1, vel=127):
    data = {"type": "note"}
    if isinstance(pch, str):
        knum = name_to_knum(pch)
    else:
        knum = pch
    data.update({"pch": pch,
                 "knum":knum,
                 "onset":onset,
                 "dur":dur,
                 "vel":vel,
                })
    data.update(_get_note_data(knum, chnl, vel))
    return data


def make_chord(pchs=(60, 64, 67), onset=0, dur=1, chnl=1, vel=127):
    data = {"type": "chord"}
    data.update({
        "pchs":pchs,
        "onset":onset,
        "dur":dur,
        "vel":vel,
        "notes": [make_note(p, onset, dur, chnl, vel) for p in pchs],
        })
    return data

def pret(*xs):
    """Prints and returns the thing, good for debuging."""
    for x in xs:
        print(x)
    return xs[-1]

def bpm_to_sec(bpm):
    """Returns the duration of one beat in tempo bpm."""
    return 60 / bpm

def rhy_to_sec(rhy, tempo):
    """"""
    return rhy * 4.0 * bpm_to_sec(tempo)

def sec_to_bpm(sec):
    """A unit (prob. quarter note) of sec duration is equal to 
    which metronome number?"""
    return 60 / sec

def knum_to_hz(knum):
    return 440 * 2 ** ((knum - 69) / 12.)

def hz_to_knum(hz):
    if hz == 0:
        raise akkord.err.CUZeroHzErr()
    return 12 * (log2(hz) - log2(440)) + 69

def get_intervals(ns):
    return [b - a for a, b in zip(ns[:-1], ns[1:])]


def dur_to_onset(durs, initos=0):
    """Returns a list of (accumulated onset, corresponding duration).
    The initial onset is the desired starting onset."""
    durs = list(durs) # convert to pop
    onsets = []
    while durs:
        d = durs.pop(0)
        onsets.append((d, initos))
        initos += d
    return onsets

def onset_to_dur(onsets):
    return [b - a for b, a in zip(onsets[1:], onsets[:-1])]

def normsum(ns, _sum=1):
    """Scales a set of numbers such that they sum up 
    to _sum after scaling

    https://math.stackexchange.com/questions/1009138/how-do-you-scale-a-set-of-number-such-that-they-sum-to-0-5-after-scaling"""
    return [n * _sum / sum(ns) for n in ns]

def minmax_norm(x, minx, maxx, low_bound=0, up_bound=1):
    """Min-max normalization (usually called feature scaling) performs 
    a linear transformation on the original data. This technique gets all 
    the scaled data in the range (0, 1) and arbitrarily rescale a range 
    between an arbitrary set of values (lower and upper bounds).
    Google feature scaling."""
    rescale_rng = up_bound - low_bound
    return low_bound + ((x - minx) * rescale_rng) / (maxx - minx) 

def ascprob(idx, seqlen):
    return random.random() < minmax_norm(idx, 0, seqlen-1)

def occured(prob): return random.random() < prob

# def ascprob(idx, seqlen):
#     return 0 <= random.random() < (idx + 1) / seqlen

def get_onset(x): return x["onset"]

def get_chnl(x): return x["chnl"]

def get_vel(x): return x["vel"]

def get_knum(nt): return nt["knum"]

def get_pitch(nt): return nt["pitch"]
def get_pitches(chd): return chd["pitches"]
def get_dur(nt): return nt["dur"]
def is_note(x): return x["type"] == "note"
def is_chord(x): return x["type"] == "chord"

def nth_geom_term(n, init, rate):
    """Returns the nth term of a geometric sequence."""
    return init * pow(rate, n - 1)

def geom_seq(init, rate, count):
    return [nth_geom_term(n, init, rate) for n in range(1, count + 1)]


def aspc(knum):
    """Returns the pitch class of the key number."""
    return knum % 12

def clip(this, lo=0, hi=1):
    """Returns this if lo <= this <= hi, otherwise return
    the nearest boundary: lo if this < lo, hi if this > hi."""
    if lo <= this <= hi:
        return this
    elif this < lo:
        return lo
    else: # this > hi
        return hi

def fit(knum, min, max, mode=0):
    """Returns the knum transposed to be fitted into the
    boundary of min-max."""
    if min <= knum <= max:
        return knum
    else:
        pc = aspc(knum)
        pcs = [(aspc(kn), kn) for kn in range(min, max+1)]
        if mode == 0: # somewhere from middle (random.random)
            return random.choice([pckn for pckn in pcs if pckn[0] == pc])[1]




def _group_by_onset(vcs):
    return [list(g) for _,g in groupby(sorted(vcs, key=get_onset), key=get_onset)]

def _pitch_mixture(items):
    ps = []
    for item in items:
        if is_note(item):
            ps.append(get_pitch(item))
        elif is_chord(item):
            ps.extend(get_pitches(item))
        else:
            raise TypeError
    # Does it make any difference in which order 
    # the notes are listed?!!
    return sorted(set(ps))

def _str_grp_items(grp):
    sort_grp = sorted(grp, key=get_dur)
    dur_cps = [get_dur(x) for x in sort_grp]
    _str = [sort_grp.pop(0)]
    i = 1
    while sort_grp:
        item = sort_grp.pop(0).copy()
        last_item = _str[-1]
        item["onset"] = get_onset(last_item) + get_dur(last_item)
        item["dur"] = dur_cps[i] - dur_cps[i-1] # dur of item is bigger than dur of last item
        _str.append(item)
        i += 1
    return _str



def mix(vcs, oscoll="mix"):
    """Returns a single voice which is a mixture of all voices.
    Collision arg decides what to do if multiple notes/chords
    overlap, i.e. have the same onset (default is mix: mixing 
    them to build a single chord. Other args can be...)"""
    mixed = []
    concat_vcs = [itm for vc in vcs for itm in vc]
    for g in _group_by_onset(concat_vcs):
        if len(g) > 1:
            if oscoll == "mix":
                longest = max(g, key=get_dur) # group's longest event
                mixed.append(chord(
                    pitches=_pitch_mixture(g),
                    onset=get_onset(longest),
                    dur=get_dur(longest),
                    chnl=get_chnl(longest)+1 if is_note(longest) else get_chnl(longest["notes"][0])+1, # what about
                    # microtonal???!!!
                    vel=get_vel(longest)
                    )
                )
        else:
            mixed.append(g[0])
    return mixed

def break_num(n, hi=1):
    """Breaks the number into a list of smaller ints/floats ingredients.
    hi is the highest possible number allowed to appear in the list."""
    ns = []
    if isinstance(n, float) or isinstance(hi, float):
        f = random.uniform
    else:
        f = random.randint
    if hi < 0:
        # random.uniform will return negative floats when hi is negative
        raise ValueError(f"highest allowed ingredient can't be negative, got {hi}")
    while n > 0:
        r = f(0, hi)
        if r:
            ns.append(n if r > n else r)
            n -= r
    return ns

def break_num2(num, count):
    """breaks the num into count random ingredients"""
    ingreds = [num / count for _ in range(count)]
    while count:
        i1 = random.randrange(len(ingreds))
        i2 = (i1 + 1) % len(ingreds)
        n = random.uniform(0, ingreds[i1])
        ingreds[i1] -= n
        ingreds[i2] += n
        count -= 1
    return ingreds

def group_by_patt(it, patt):
    """Groups items of the iterable based on patterns in patt list."""
    grp = []
    for end_idx in patt:
        if end_idx > len(it):
            raise IndexError(f"can't make sublist of length {end_idx} from a list of length {len(it)}")
        grp.append(it[0:end_idx])
        it = it[end_idx:]
    return grp

def roundf_to(fnum, to=2):
    """Rounds the float to the nearest exponent of to, e.g.
    2.314 returns 2.25"""
    f, i = modf(fnum)
    return i + pow(to, round(log(f, to)))

# todo: use n%len(it) to rotate even if n>len(n)
def nth_rotation(it, nth):
    """Returns an iterable which is the nth rotation of it, e.g.
    rotate([1,2,3,4], 2) => [3,4,1,2]"""
    return chain(islice(it, nth, None), islice(it, 0, nth))

def get_rotations(it, count):
    return [nth_rotation(it, nth) for nth in range(count)]
