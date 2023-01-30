import time
import rtmidi
import rtmidi.midiutil
import asyncio
import cu.cfg
import cu.err
from math import (modf, log2)
from rtmidi.midiconstants import (
    NOTE_OFF, NOTE_ON, PITCH_BEND,
    ALL_SOUND_OFF, CONTROL_CHANGE,
    RESET_ALL_CONTROLLERS
)




_client_registry = dict()
_client_port_registry = dict()

def init_client(client_id=0):
    client = rtmidi.MidiOut(name=f"cu output {client_id}",
                            rtapi=rtmidi.API_LINUX_ALSA)
    # register the created output client
    _client_registry[client_id] = client

def kill_client(client_id=0):
    _client_port_registry[client_id].close_port()
    del _client_port_registry[client_id]
    time.sleep(0.1)
    _client_registry[client_id].delete()
    del _client_registry[client_id]

_CLIENT = None
NO_BEND_VAL = 2 ** 13
NO_BEND_RESET_LSB = NO_BEND_VAL & 0x7f # isthis msb or lsb for send_message?!??
NO_BEND_RESET_MSB = (NO_BEND_VAL >> 7) & 0x7f
SEMITONE_BEND_RANGE = 4096
# todo: support more channels through more tracks/ports?
_chnls_pool = set(range(16))


def _is_the_port(port_name):    
    port_name = port_name.lower()
    # pid = port identifier: part of port's name
    return all([pid.lower() in port_name for pid in cu.cfg.in_port_id])



def _get_client_port(client_id):
    """Opens and returns the client with id."""
    client = _client_registry[client_id]
    if client.is_port_open():
        return _client_port_registry[client_id]
    else: # no ports opened yet
        port_idx = None
        ports = client.get_ports()
        # connect to the desired port
        if ports:
            for i, p in enumerate(ports):
                if _is_the_port(p): 
                    port_idx = i
                    break
        if port_idx is None:
            port = client.open_virtual_port(f"cu vport for client {client_id}")
        else:
            port = client.open_port(port_idx, f"cu port for client {client_id}")
        _client_port_registry[client_id] = port
        return port

def knum_to_hz(knum):
    return 440 * 2 ** ((knum - 69) / 12.)

def hz_to_knum(hz):
    if hz == 0:
        raise cu.err.CUZeroHzErr()
    return 12 * (log2(hz) - log2(440)) + 69

def _get_bend_msgs(knum, knum_ipart, ch):
    bend_val = NO_BEND_VAL + NO_BEND_VAL * (12 / cu.cfg.bend_range) * log2(knum_to_hz(knum) / knum_to_hz(knum_ipart))
    # note that crazy fractional parts could result in loss of information(because of rounding)
    bend_val = round(bend_val)
    bend_msg = (PITCH_BEND + ch, bend_val & 0x7f, (bend_val >> 7) & 0x7f)
    bend_reset_msg = (PITCH_BEND + ch, NO_BEND_RESET_LSB, NO_BEND_RESET_MSB)
    return bend_msg, bend_reset_msg

def _get_non_nof_msgs(knum_ipart, ch, vel):
    # don't need the fract part here, the fractional part goes into the bend message
    # 3 bytes of NON/NOF messages:
    # [status byte, data byte 1, data byte 2]
    # status byte, first hex digit: 8 for note off, 9 for note on
    # data byte 1: pitch, data byte 2: velocity
    non_msg = (NOTE_ON + ch, knum_ipart, vel)
    # http://www.music-software-development.com/midi-tutorial.html
    # the vel is the release velocity, by default set it to 0
    nof_msg = (NOTE_OFF + ch, knum_ipart, 0)
    return non_msg, nof_msg
    

def _is_chnl_in_use(chnl):
    if chnl not in _chnls_pool:
        return True
    else:
        return False


def play_note(knum=60, dur=1, chnl=1, vel=127):
    global _chnls_pool
    fpart, ipart = modf(knum)
    ipart = int(ipart)
    chnl -= 1 # convert from user-perspective to midi-perspective
    if fpart: # do not just fuck with the chnl!
        if _is_chnl_in_use(chnl): # then pick up another chnl
            chnl = _chnls_pool.pop()
        bend_msg, bend_reset_msg = _get_bend_msgs(knum, ipart, chnl)
    else: # mark chnl as in use
        _chnls_pool.remove(chnl)
    non_msg, nof_msg = _get_non_nof_msgs(ipart, chnl, vel)
    try:
        if fpart: # needs microtonal channel adjustment
            _CLIENT.send_message(bend_msg)
        _CLIENT.send_message(non_msg)
        time.sleep(dur)
    finally:
        _CLIENT.send_message(nof_msg)
        if fpart: # reset channel microtuning
            _CLIENT.send_message(bend_reset_msg)
        # put the chnl back in the pool
        _chnls_pool.add(chnl)

# def play_note(knum=60, dur=1, chnl=1, vel=127):
#     global _chnls_pool
#     fpart, ipart = modf(knum)
#     ipart = int(ipart)
#     chnl -= 1 # convert from user-perspective to midi-perspective
#     if fpart: # do not just fuck with the chnl!
#         if _is_chnl_in_use(chnl): # then pick up another chnl
#             chnl = _chnls_pool.pop()
#         bend_msg, bend_reset_msg = _get_bend_msgs(knum, ipart, chnl)
#     else: # mark chnl as in use
#         _chnls_pool.remove(chnl)
#     non_msg, nof_msg = _get_non_nof_msgs(ipart, chnl, vel)
#     try:
#         if fpart: # needs microtonal channel adjustment
#             MIDI_OUT_CLIENT.send_message(bend_msg)
#         MIDI_OUT_CLIENT.send_message(non_msg)
#         time.sleep(dur)
#     finally:
#         MIDI_OUT_CLIENT.send_message(nof_msg)
#         if fpart: # reset channel microtuning
#             MIDI_OUT_CLIENT.send_message(bend_reset_msg)
#         # put the chnl back in the pool
#         _chnls_pool.add(chnl)
#

# def play_chord(knums=[60], dur=1, ch=1, vel=127):
#     count = len(knums)
#     on_msgs = [[NOTE_ON + ch - 1, n, vel] for n in knums]
#     off_msgs = [[NOTE_OFF + ch - 1, n, vel] for n in knums]
#     try:
#         for i in range(count):
#             MIDI_OUT_CLIENT.send_message(on_msgs[i])
#         time.sleep(dur)
#     finally:
#         for i in range(count):
#             MIDI_OUT_CLIENT.send_message(off_msgs[i])
#
#
# async def _play_voice(pitches, durs, ch, vels, out, show):
#     for i, p in enumerate(pitches):
#         if show:
#             print(f"Ch {ch} Pitch {p} Dur {durs[i]} Vel {vels[i]}")
#         if p < 0: # rest
#             non = [NOTE_ON + ch -1, 0, 0]
#             nof = [NOTE_OFF + ch - 1, 0, 0]
#         else:
#             non = [NOTE_ON + ch - 1, p, vels[i]]
#             nof = [NOTE_OFF + ch - 1, p, vels[i]]
#         try:
#             out.send_message(non)
#             await asyncio.sleep(durs[i])
#         finally:
#             out.send_message(nof)
#
# # TODO: packing chords in voices should become possible.
# async def play_poly(voice_pitches, voice_durs, chs, voice_vels, show=False, out=MIDI_OUT_CLIENT):
#     play_voices = [] # playable voices
#     for i in range(len(voice_pitches)):
#         play_voices.append(
#             asyncio.create_task(_play_voice(
#                 voice_pitches[i],
#                 voice_durs[i],
#                 chs[i],
#                 voice_vels[i],
#                 out,
#                 show)
#             )
#         )
#     await asyncio.wait(play_voices)
#

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

        


# This is the main function to use should probably not be here!.
def proc(fun, args=None, client_id=0):
    """Run the fun, processing the rtmidi calls and cleanup if called from within a script.
    If running from inside a script also dealloc the MIDI_OUT_CLIENT object.
    proc should be given one single
    fun which is your whole composition, don't call it multiple times
    via iteration etc."""
    global _CLIENT
    _CLIENT = _client_registry[client_id]
    with _get_client_port(client_id): # open the port for the chosen client
        try:
            if isinstance(args, dict):
                fun(**args)
            elif isinstance(args, (list, tuple)):
                fun(*args)
            else:
                fun()
        except (EOFError, KeyboardInterrupt):
            # if interrupted while running funtion, panic!
            print("\npanic!")
            for ch in range(16):
                _CLIENT.send_message([CONTROL_CHANGE | ch, ALL_SOUND_OFF, 0])
                _CLIENT.send_message([CONTROL_CHANGE | ch, RESET_ALL_CONTROLLERS, 0])
                time.sleep(0.05)
        except (cu.err.CUZeroHzErr):
            print("can't convert 0 hz to midi knum")
        # finally:
        #     if cu.cfg.as_script: # don't if in the python shell, as the midiout might still be needed
        #         print("finished processing")
        #         # de-allocating pointer to c++ instance
        #         # MIDI_OUT_CLIENT.delete()


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
        # for x in range(10):
        #
            # print(dd)
            # play_note(40, dur=d, vel=100)
        for ch in chs:
            play_chord(ch, dur=d, vel=100, ch=1)


