"""
This file contains abstracts around 
https://github.com/MarkCWirt/MIDIUtil.git
"""
import midiutil





def save(events, path):
    # find out number of tracks
    tracks = {"frei": 0, "voices": 0}
    for e in events:
        try:
            if e["type"] == "note" or e["type"] == "chord":
                # frei rumliegende Noten/Akkorde gehen inselben Track
                if tracks["frei"] == 0:
                    tracks["frei"] = 1
        except TypeError:
            tracks["voices"] += 1
    tracks_count = sum(tracks.values())
    file_obj = midiutil.MIDIFile(tracks_count, deinterleave=False)
    for i in range(tracks_count):
        file_obj.addTempo(i, 0, 60)
    vidx=0
    for e in events:
        try:
            if e["type"] == "note":
                file_obj.addNote(0, e["chnl"], e["non"][1],
                                 e["onset"], e["dur"], e["non"][2])
            elif e["type"] == "chord":
                for x in e["notes"]:
                    file_obj.addNote(0, x["chnl"], x["non"][1],
                                     x["onset"], x["dur"], x["non"][2])
        except TypeError:
            for x in e:
                if x["type"] == "note":
                    file_obj.addNote(vidx, x["chnl"], x["non"][1],
                                     x["onset"], x["dur"], x["non"][2],
                                    )
                elif x["type"] == "chord":
                    for y in x["notes"]:
                        file_obj.addNote(vidx,y["chnl"], y["non"][1],
                                     y["onset"], y["dur"], y["non"][2]
                                        )
                else:
                    raise ValueError("Error aus cumidiutil.py")
            vidx+=1
    with open(path, "wb") as midfile:
        file_obj.writeFile(midfile)
