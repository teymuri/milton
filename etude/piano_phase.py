import computil as cu


# helper functions and Piano 1
phasing_trope = (64, 66, 71, 73, 74, 66, 64, 73, 71, 66, 74, 73)
phasing_pulse = 1/24
phasing_tempo = 72

def piano1_voice(trope, amp, chan):
    tlen = len(trope)
    cycs = tlen
    rate = cu.rhythm_to_sec(phasing_pulse, phasing_tempo)

