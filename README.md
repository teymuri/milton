# Composition Utilities

The aim of this package is to provide a higher level, musically more expressive and abstract set of subroutines to be
integrated in compositional workflows.
This package is a work-in-progress.

# Quick Start

```python
# import the module
>>> import computil as cu

# initialize the module
>>> cu.open_ports()

# create a single note
>>> c4 = cu.note(knum=60)

# and put it in a list and send it to the processor to play it
>>> cu.proc([c4])

# the full signature of the note function has the parameters:
# knum: the midi key number
# onset: the time to play the note in seconds (default is 0)
# dur: the duration of the note
# chnl: the midi channel to play the note on
# vel: the dynamic of the note

# now create a A minor chord with a duration of 2 seconds, 
# and play it 1 second after the processor starts
>>> a_min = cu.chord(knums=(69, 72, 76), onset=1, dur=2)

# and send it to the processor to play it
>>> cu.proc([a_min])

# now let us give the processor a list of notes/chords to play:
# the chromatic scale starting from the middle c upwards.
>>> voice = [cu.note(knum=60 + i, onset=i, dur=0.1) for i in range(12)]
>>> cu.proc([voice])

# playing polyphony is as easy as passing multiple lists of note/chords
# to the processor:
>>> voice1 = [cu.note(knum=60 + i, onset=i, dur=0.5) for i in range(12)]
>>> voice2 = [cu.note(knum=48 + i, onset=i + 0.5, dur=0.5) for i in range(12)]
>>> voice3 = [cu.chord(knums=[60+i, 60+i+4, 60+i+7], onset=i + 0.2, dur=0.5) for i in range(12)]

>>> cu.proc([voice1, voice2, voice3])

```
