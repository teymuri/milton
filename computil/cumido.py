"""
Reading and parsing midi files
"""
import numpy as np
from mido import (MidiFile, bpm2tempo, tick2second)


def _parse_track(track, tpb, tscale):
    nons = [x for x in track if x.type == "note_on"]
    onset = dur = 0
    vc_data = []
    if nons:
        for non_msg, nof_msg in np.split(np.asarray(nons), len(nons)//2):
            onset += tick2second(
                    non_msg.time, tpb, bpm2tempo(60)
                ) * tscale 
            dur = tick2second(
                    nof_msg.time, tpb, bpm2tempo(60)
                ) * tscale
            non_msg_vars = vars(non_msg)
            data = {
                "pch": non_msg_vars["note"],
                "onset": onset,
                "dur": dur,
                "chnl": non_msg_vars["channel"] + 1,
                "vel": non_msg_vars["velocity"]
            } 
            vc_data.append(data)
            onset += dur
    return vc_data

def parse(path, tscale=1):
    fl = MidiFile(path)
    return [_parse_track(t, fl.ticks_per_beat, tscale) for t in fl.tracks]

