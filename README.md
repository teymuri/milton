# Algorithmic Composition Utilities

The aim of this package is to provide a higher level, musically more expressive and abstract set of routines.
It is meant to make expressing algorithmic music more intuitive and easy, by taking care of low-level MIDI implementation
so that the composer can focus on his composition rather than following midi messages.
This package is a *work-in-progress* and *in active development*. Your feedback is very welcome! :-)

# Quick Start

```python
# import the module
>>> import akkord as cu

# First initialize the module,
>>> cu.realtime.init()

# create a single note,
>>> c4 = cu.make_note("c4")

# and put it in a list and send it to the processor to play it.
>>> cu.proc([c4])

# Let us now define a second note with the key number 72, and specify it's starting time (onset) to be 1 second after the processor starts.
>>> c5 = cu.make_note(pch=72, onset=1)
>>> cu.proc([c4, c5])

# You should have heared both notes, played after each other.

# The full signature of the note function has the parameters:
# pch: the name of the note (a string) or the midi key number
# onset: is the ongoing time expressed in seconds, with respect to the process start time 0 (default is 0, which means now)
# dur: the duration of the note
# chnl: the midi channel to play the note on
# vel: the dynamic of the note

# Now we want to create an A minor chord with a duration of 2 seconds, 
# and play it 1/2 second after the processor starts,
>>> a_min = cu.make_chord(pchs=(69, 72, 76), onset=.5, dur=2)

# and send it to the processor to play it.
>>> cu.proc([a_min])

# Let us now give the processor a list of notes/chords to play:
# the chromatic scale starting from the middle c upwards.
>>> voice1 = [cu.make_note(pch=60+i, onset=i, dur=0.5) for i in range(12)]
>>> cu.proc([voice1])

# Playing polyphony is as easy as passing multiple lists of note/chords
# to the processor:
>>> voice2 = [cu.make_note(pch=48+i, onset=i+0.5, dur=0.5) for i in range(12)]
>>> voice3 = [cu.make_chord(pchs=[60+i, 60+i+4, 60+i+7], onset=i+0.2, dur=0.5) for i in range(12)]
>>> cu.proc([voice1, voice2, voice3])

# If you want to write a midi file to the disk instead of playing it back
# pass a path string as the second argument to the processor
>>> cu.proc([voice1, voice2, voice3], "/tmp/akkord.mid")
```
