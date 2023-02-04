import computil as cu


# helper functions and Piano 1
phasing_trope = (64, 66, 71, 73, 74, 66, 64, 73, 71, 66, 74, 73)
phasing_pulse = 1/24
phasing_tempo = 72

def piano1(trope, amp, chan):
    tlen = len(trope)
    cycs = tlen
    rate = cu.rhythm_to_sec(phasing_pulse, phasing_tempo)
    notes = []
    repeat = tlen * cycs
    i = 0
    while repeat:
        x = i % tlen
        k = trope[x]
        notes.append(cu.note(onset=rate*i, knum=k, 
                            dur=rate * 1.5, vel=amp,
                            chnl=chan))
        i += 1
        repeat -= 1
    return notes

cu.open_ports()
cu.proc(piano1(phasing_trope, 100, 1))
