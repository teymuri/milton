#!/usr/bin/env python

import time
import rtmidi
import asyncio

from rtmidi.midiconstants import (NOTE_OFF, NOTE_ON,
                                ALL_SOUND_OFF, CONTROL_CHANGE,
                                RESET_ALL_CONTROLLERS)

MY_SYNTH_PORTS = ("zynaddsubfx", )
MOUT = rtmidi.MidiOut(rtmidi.API_UNIX_JACK, name="Computil Client")

def play_note(pitch=60, dur=1, ch=1, vel=127):
    # 3 bytes of non,nof msgs
    non = [NOTE_ON + ch - 1, pitch, vel]
    nof = [NOTE_OFF + ch - 1, pitch, vel]
    try:
        MOUT.send_message(non)
        time.sleep(dur)
    finally:
        MOUT.send_message(nof)

def play_chord(notes=[60], dur=1, ch=1,vel=127, out=MOUT):
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
async def play_poly(voice_pitches, voice_durs, chs, voice_vels, show=False, out=MOUT):
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

def piccolo():
    viertel = 6/5
    notes = list(range(36, 75, 2)) + list(range(72, 35, -2))
    up = list(range(36, 75, 2))
    down = reversed(up)
    d = viertel / 2 / len(up)
    for p in cycle(up):
        print(p)
        play_note(p, d, vel=50)

def find_port_idx(port_name):    
    for i, my_port in enumerate(MY_SYNTH_PORTS):
        if my_port in port_name:
            return i
    raise NameError(f"Port '{port_name}' doesn't exist")


def run(func):
    """Run the func and cleanup the shit."""
    global MOUT
    ports = MOUT.get_ports()
    for p in ports:
        try:
            print(p, find_port_idx(p))
        except NameError:
            print(p)
    with (MOUT.open_port(1) if MOUT.get_ports() else
            MOUT.open_virtual_port("My virtual output")):
        try:
            func()
        finally:
            for channel in range(16):
                MOUT.send_message([CONTROL_CHANGE, ALL_SOUND_OFF, 0])
                MOUT.send_message([CONTROL_CHANGE, RESET_ALL_CONTROLLERS, 0])
                time.sleep(0.05)
            del MOUT


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

            # print(dd)
            play_note(40, dur=d, vel=100)
        # for ch in chs:
        #     play_chord(ch, dur=d, vel=100, ch=1)

def is_known_port(port_name):
    for my_port in MY_SYNTH_PORTS:
        if my_port in port_name:
            return True
    return False

if __name__ == "__main__":
    from itertools import cycle
    # test()
    import rtmidi.midiutil
    # print(rtmidi.get_compiled_api())
    # print(rtmidi.API_UNIX_JACK)
    # print(MOUT.get_current_api())
    # print(MOUT.get_ports())
    # print(MOUT.get_port_count())
    # z=MOUT.get_port_name(1)
    # MOUT.open_port(1, name=z)
    run(trem)
