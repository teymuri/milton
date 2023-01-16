#!/usr/bin/env python

import time
import rtmidi
import asyncio

from rtmidi.midiconstants import NOTE_OFF, NOTE_ON


MIDI_OUT = rtmidi.MidiOut()

def play_note(note=60, dur=1, ch=1,vel=127):
    # 3 bytes of non,nof msgs
    note_on = [NOTE_ON + ch - 1, note, vel]
    note_off = [NOTE_OFF + ch - 1, note, vel]
    with (MIDI_OUT.open_port(0) if MIDI_OUT.get_ports() else
            MIDI_OUT.open_virtual_port("My virtual output")):
        try:
            MIDI_OUT.send_message(note_on)
            time.sleep(dur)
        finally:
            MIDI_OUT.send_message(note_off)

def play_chord(notes=[60], dur=1, ch=1,vel=127, out=MIDI_OUT):
    count = len(notes)
    on_msgs = [[NOTE_ON + ch - 1, n, vel] for n in notes]
    off_msgs = [[NOTE_OFF + ch - 1, n, vel] for n in notes]
    try:
        for i in range(count):
            out.send_message(on_msgs[i])
        time.sleep(dur)
    finally:
        for i in range(count):
            out.send_message(off_msgs[i])


async def _play_voice(pitches, durs, ch, vels, out, show):
    for i, p in enumerate(pitches):
        if show:
            print(f"Ch {ch} Pitch {p} Dur {durs[i]} Vel {vels[i]}")
        if p < 0: # rest
            non = [NOTE_ON + ch -1, 0, 0]
            nof = [NOTE_OFF + ch - 1, 0, 0]
        else:
            non = [NOTE_ON + ch - 1, p, vels[i]]
            nof = [NOTE_OFF + ch - 1, p, vels[i]]
        try:
            out.send_message(non)
            await asyncio.sleep(durs[i])
        finally:
            out.send_message(nof)

# TODO: packing chords in voices should become possible.
async def play_poly(voice_pitches, voice_durs, chs, voice_vels, show=False, out=MIDI_OUT):
    play_voices = [] # playable voices
    for i in range(len(voice_pitches)):
        play_voices.append(
            asyncio.create_task(_play_voice(
                voice_pitches[i],
                voice_durs[i],
                chs[i],
                voice_vels[i],
                out,
                show)
            )
        )
    await asyncio.wait(play_voices)


def test():
    global MIDI_OUT
    with (MIDI_OUT.open_port(0) if MIDI_OUT.get_ports() else
            MIDI_OUT.open_virtual_port("My virtual output")):

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
    del MIDI_OUT

def piccolo():
    viertel = 6/5
    notes = list(range(36, 75, 2)) + list(range(72, 35, -2))
    up = list(range(36, 75, 2))
    down = reversed(up)
    d = viertel / 2 / len(up)
    for p in cycle(up):
        print(p)
        play_note(p, d, vel=50)
    
def run(func):
    """Run the func and cleanup the shit."""
    global MIDI_OUT
    with (MIDI_OUT.open_port(0) if MIDI_OUT.get_ports() else
            MIDI_OUT.open_virtual_port("My virtual output")):
        func()
    del MIDI_OUT


# Note names
G3 = 55
C4 = 60
D4 = 62
E4 = 64
F4 = 65
G4 = 67

MAJ4 = [0, 3, 7, 12]
def trem():
    chs = [[62+i for i in MAJ4] for _ in range(10)]
    for i in range(1000):
        d = .0001 + i * .001
        dd = 0.5 - i * .1
        for x in range(10):

            print(dd)
            play_note(E4, dur=dd, vel=100)
        # for ch in chs:
        #     play_chord(ch, dur=d, vel=100, ch=1)


if __name__ == "__main__":
    from itertools import cycle
    # test()
    # clean(piccolo)
    clean(trem)
