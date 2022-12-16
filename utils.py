#!/usr/bin/env python

import time
import rtmidi
import asyncio

from rtmidi.midiconstants import NOTE_OFF, NOTE_ON


MIDIOUT = rtmidi.MidiOut()

def play_note(note=60, dur=1, ch=1,vel=127,  out=MIDIOUT):
    # 3 bytes of non,nof msgs
    note_on = [NOTE_ON + ch - 1, note, vel]
    note_off = [NOTE_OFF + ch - 1, note, vel]
    try:
        out.send_message(note_on)
        time.sleep(dur)
    finally:
        out.send_message(note_off)

def play_chord(notes=[60], dur=1, ch=1,vel=127, out=MIDIOUT):
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
            print(f"CH {ch} pitch {p} dur {durs[i]} vel {vels[i]}")
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

async def play_poly(voice_pitches, voice_durs, chs, voice_vels, show=False, out=MIDIOUT):
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


if __name__ == "__main__":
    with (MIDIOUT.open_port(0) if MIDIOUT.get_ports() else
            MIDIOUT.open_virtual_port("My virtual output")):

        # import random
        # chs = [[64+i for i in [0, 4, 7, 12]] for _ in range(10)]
        # for i in range(1000):
        #     for ch in chs:
        #         print(i, ch)
        #         play_chord(ch, dur=.0001+(i*.001), vel=100, ch=1)



        asyncio.run(
            play_poly(
                [[50, -1, 60, -1, 70, -1, 40],
                [50, -1, 60, -1, 70, -1, 40]],
                [[1, 1, .5, 1, .25, .75, 1], 
                [.5, 1, .5, 1, .25, .75, 1]],
                [1, 2], 
                [[100, 100, 100, 100, 100, 100, 100],
                [100, 100, 100, 100, 100, 100, 100]],
                True
            )
        )

    del MIDIOUT


