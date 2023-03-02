"""
bunch of useful functions
"""

from random import random
from computil.rt import _get_note_data

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

for knum in range(21, 128):
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

def note(pitch=60, onset=0, dur=1, chnl=1, vel=127):
    data = {"type": "note"}
    if isinstance(pitch, str):
        knum = name_to_knum(pitch)
    else:
        knum = pitch
    data.update({"pitch": pitch,
                 "knum":knum,
                 "onset":onset,
                 "dur":dur,
                 "vel":vel})
    data.update(_get_note_data(knum, chnl, vel))
    return data


def chord(pitches=(60, 64, 67), onset=0, dur=1, chnl=1, vel=127):
    data = {"type": "chord"}
    data.update({"pitches":pitches, "onset":onset, "dur":dur,"vel":vel})
    data.update({"notes":[note(p, onset, dur, chnl, vel) for p in pitches]})
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
    onsets = list(onsets)
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

def prob(x): return random() < x

# def ascprob(idx, seqlen):
#     return 0 <= random() < (idx + 1) / seqlen

def get_onset(nt):
    """Returns note's onset time."""
    return nt["onset"]

def get_chnl(nt): return nt["chnl"]

def get_vel(nt): return nt["vel"]

def get_knum(nt): return nt["knum"]

def get_pitch(nt): return nt["pitch"]

def get_dur(nt): return nt["dur"]

def exp_growth(init, rate, periods):
    """Returns an exponential curve."""
    return [init * pow(rate, t) for t in range(periods)]

def get_pc(knum):
    """Returns the pitch class of the key number."""
    return knum % 12

def fit(knum, min, max):
    """Returns the knum transposed to be fitted into the
    boundary of min-max."""
    if min <= knum <= max:
        return knum
    else:
        pc = get_pc(knum)
        m = min
        while m < max:
            if get_pc(m) == pc:
                return m
            m += 1
        raise ValueError(f"Can't fit {knum} into {min}, {max}")
