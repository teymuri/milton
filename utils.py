#!/usr/bin/env python

import time
import rtmidi

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

def play_voice(notes, durs, chs, vels, out=MIDIOUT):
    voice_count = len(notes)
    longest = max([len(v) for v in notes])
    for i in range(longest):
        for j in range(voice_count):
            try:
                note = notes[j][i]
                out.send_message(
                    [NOTE_ON + chs[j] - 1, note, vels[j][i]]
                )
            except IndexError:
                pass
        for j in range(voice_count):
            print(durs[j][i])
            time.sleep(durs[j][i])
        for j in range(voice_count):
            out.send_message(
                [NOTE_OFF + chs[j] - 1, notes[j][i], vels[j][i]]
            )


if __name__ == "__main__":
    with (MIDIOUT.open_port(0) if MIDIOUT.get_ports() else
            MIDIOUT.open_virtual_port("My virtual output")):
        import random
        chs = [[64+i for i in [0, 4, 7, 12]] for _ in range(10)]
        for i in range(1000):
            for ch in chs:
                print(i, ch)
                play_chord(ch, dur=.0001+(i*.001), vel=100, ch=1)

    del MIDIOUT


