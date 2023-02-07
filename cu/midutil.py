import midiutil as mu



def _find_tracks_count(events):
    chnls = set()
    for e in events:
        if e[0] == "n":
            non,nof,bend,bend_r,c,cl,os,d=event[1:] # eine note
            chnls.add(c)
        elif e[0] == "c":
            for x in e[1:]: # ist ein akkord oder voice?
                non,nof,bend,bend_r,c,cl,os,d=x[1:]
                chnls.add(c)
        else:
            for x in e:
                if x[0] == 'n':
                    non,nof,bend,bend_r,c,cl,os,d=x[1:] # eine note
                    chnls.add(c)
    return chnls


def midiutil_proc(events, path):
    # find out number of tracks
    tracks = {"frei": 0, "voices": 0}
    for e in events:
        try:
            if e[0] in "nc":
                # frei rumliegende Noten/Akkorde gehen inselben Track
                if tracks["frei"] == 0:
                    tracks["frei"] = 1
        except TypeError:
            tracks["voices"] += 1
    tracks_count = sum(tracks.values())
    file_obj = mu.MIDIFile(tracks_count)
    for i in range(tracks_count):
        file_obj.addTempo(i, 0, 60)
    vidx=0
    for e in events:
        if e[0] == "n":
            non,nof,bend,bend_r,c,cl,os,d=event[1:] # eine note
            file_obj.addNote(0, c, non[1], os, d, non[2])
        elif e[0] == "c": # chord
            for x in e[1:]: # ist ein akkord oder voice?
                non,nof,bend,bend_r,c,cl,os,d=x[1:]
                file_obj.addNote(0, c, non[1], os, d, non[2])
        else: # voice
            for x in e:
                if x[0] == "n":
                    non,nof,bend,bend_r,c,cl,os,d=x[1:] # eine note
                    file_obj.addNote(vidx, c, non[1], os, d, non[2])
                    # try:
                    #     file_obj.addNote(0, c, non[1], os, d, non[2])
                    # except IndexError:
                    #     breakpoint()
                elif x[0] == "c":
                    for y in x[1:]:
                        non,nof,bend,bend_r,c,cl,os,d=y[1:] # note?
                        file_obj.addNote(vidx, c, non[1], os, d, non[2])
                else:
                    raise ValueError("Wieeeeee?")
            vidx+=1
    with open(path, "wb") as midfile:
        file_obj.writeFile(midfile)
