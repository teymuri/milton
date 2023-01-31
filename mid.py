import time
import asyncio
import rtmidi
import rtmidi.midiutil
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

def get_client_ids():
    return _client_registry.keys()

def kill_client(cid): # cid = client id
    if cid in _client_port_registry: # perhaps no ports ever opened!
        _client_port_registry[cid].close_port()
        del _client_port_registry[cid]
        time.sleep(0.1)
    _client_registry[cid].delete()
    del _client_registry[cid]

# This is the client used on each processing, and
# is set one per each proc call.
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
    

def _is_chnl_in_use(chnl): # chnl is midi-perspective
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



_chnl_usage_trace = {
    # channel: [reference/usage, status]
    # status = is in use by a microtone (if usage > 0)
    # status False and reference>0 means in-use by equal tempered notes
    chnl: [0, None] for chnl in range(16)
}
def _is_chnl_free_for_micton(chnl):
    """Returns true if chnl is accessible for a microtone, ie
    no other references to this channel exist."""
    return _chnl_usage_trace[chnl][0] == 0 

def _is_chnl_free_for_eqtemp(chnl):
    """Returns true if channel is accessible for an equal-tempered note,
    ie either no references to the channel exist, or those references
    are all to eqaul-tempered notes too."""
    return _chnl_usage_trace[chnl][0] == 0 or\
           _chnl_usage_trace[chnl][1] is False

def _get_next_free_chnl_for_micton():
    """Returns the next for microtones accessible channel, ie
    a channel with 0 references."""
    for chnl, stat in _chnl_usage_trace.items():
        if stat[0] == 0: # 0 references
            return chnl

def _get_next_free_chnl_for_eqtemp():
    """Returns the next for equal-tempered notes free channel, ie
    a channel with zero references or with references to other
    equal-tempered notes."""
    for chnl, stat in _chnl_usage_trace.items():
        if stat[0] == 0 or stat[1] is False:
            return chnl

def _verify_setup_chnl_for_micton_ip(midi_chnl):
    global _chnl_usage_trace
    if not _is_chnl_free_for_micton(midi_chnl):
        midi_chnl = _get_next_free_chnl_for_micton()
    # increment channel's usage
    _chnl_usage_trace[midi_chnl][0] = 1
    # set status to in-use by a microtone
    _chnl_usage_trace[midi_chnl][1] = True
    return midi_chnl

def _verify_setup_chnl_for_eqtemp_ip(midi_chnl):
    global _chnl_usage_trace
    if not _is_chnl_free_for_eqtemp(midi_chnl):
        midi_chnl = _get_next_free_chnl_for_eqtemp()
    # increment channel's references
    _chnl_usage_trace[midi_chnl][0] += 1
    # set status to in-use by non-microtones if not happened yet
    if _chnl_usage_trace[midi_chnl][1] is not False:
        _chnl_usage_trace[midi_chnl][1] = False
    return midi_chnl

def _get_msgs(knum, midi_chnl, vel) -> tuple:
    non_msg = nof_msg = bend_msg = bend_reset_msg = None
    fpart, ipart = modf(knum)
    ipart = int(ipart)
    if fpart: # is microtonal
        midi_chnl = _verify_setup_chnl_for_micton_ip(midi_chnl)
        bend_msg, bend_reset_msg = _get_bend_msgs(knum, ipart, midi_chnl)
    else:
        midi_chnl = _verify_setup_chnl_for_eqtemp_ip(midi_chnl)
    non_msg, nof_msg = _get_non_nof_msgs(ipart, midi_chnl, vel)
    return non_msg, nof_msg, bend_msg, bend_reset_msg, midi_chnl


def play_note(knum, dur=1, chnl=1, vel=127):
    global _chnl_usage_trace
    non, nof, bend, bend_reset, chnl_ = _get_msgs(knum, chnl-1, vel)
    try:
        if bend:
            _CLIENT.send_message(bend)
        _CLIENT.send_message(non)
        time.sleep(dur)
    finally:
        _CLIENT.send_message(nof)
        if bend_reset:
            _chnl_usage_trace[chnl_][0] -= 1
            assert _chnl_usage_trace[chnl_][0] == 0
            _chnl_usage_trace[chnl_][1] = None
            _CLIENT.send_message(bend_reset)
        else:
            _chnl_usage_trace[chnl_][0] -= 1
            if _chnl_usage_trace[chnl_][0] == 0:
                _chnl_usage_trace[chnl_][1] = None

async def _async_play_note(knum, dur, chnl, vel):
    global _chnl_usage_trace
    non, nof, bend, bend_reset, chnl_ = _get_msgs(knum, chnl-1, vel)
    try:
        if bend:
            _CLIENT.send_message(bend)
        _CLIENT.send_message(non)
        await asyncio.sleep(dur)
    finally:
        _CLIENT.send_message(nof)
        if bend_reset:
            _chnl_usage_trace[chnl_][0] -= 1
            assert _chnl_usage_trace[chnl_][0] == 0
            _chnl_usage_trace[chnl_][1] = None
            _CLIENT.send_message(bend_reset)
        else:
            _chnl_usage_trace[chnl_][0] -= 1
            if _chnl_usage_trace[chnl_][0] == 0:
                _chnl_usage_trace[chnl_][1] = None


async def _async_play_chord(knums, dur, chnl, vel):
    global _chnl_usage_trace
    msgs = [_get_msgs(knum, chnl-1, vel) for knum in knums]
    try:
        for non, _, bend, _, _ in msgs:
            if bend: # either bend message or None
                _CLIENT.send_message(bend)
            _CLIENT.send_message(non)
        await asyncio.sleep(dur)
    finally:
        for _, nof, _, bend_reset, chnl_ in msgs:
            _CLIENT.send_message(nof)
            if bend_reset:
                _chnl_usage_trace[chnl_][0] -= 1
                assert _chnl_usage_trace[chnl_][0] == 0
                _chnl_usage_trace[chnl_][1] = None
                _CLIENT.send_message(bend_reset)
            else:
                _chnl_usage_trace[chnl_][0] -= 1
                if _chnl_usage_trace[chnl_][0] == 0:
                    _chnl_usage_trace[chnl_][1] = None

def play_chord(knums, dur=1, chnl=1, vel=127):
    global _chnl_usage_trace
    msgs = [_get_msgs(knum, chnl-1, vel) for knum in knums]
    try:
        for non, _, bend, _, _ in msgs:
            if bend: # either bend message or None
                _CLIENT.send_message(bend)
            _CLIENT.send_message(non)
        time.sleep(dur)
    finally:
        for _, nof, _, bend_reset, chnl_ in msgs:
            _CLIENT.send_message(nof)
            if bend_reset:
                _chnl_usage_trace[chnl_][0] -= 1
                assert _chnl_usage_trace[chnl_][0] == 0
                _chnl_usage_trace[chnl_][1] = None
                _CLIENT.send_message(bend_reset)
            else:
                _chnl_usage_trace[chnl_][0] -= 1
                if _chnl_usage_trace[chnl_][0] == 0:
                    _chnl_usage_trace[chnl_][1] = None


async def _play_voice(knums, durs, chnl, vels):
    for i, knum in enumerate(knums):
        if isinstance(knum, (list, tuple)): # a chord
            await _async_play_chord(knum, durs[i], chnl, vels[i])
        else: # a single note
            await _async_play_note(knum, durs[i], chnl, vels[i])

async def play_poly(voices):
    await asyncio.gather(
        *(_play_voice(v[0], v[1], v[2], v[3]) for v in voices)
    )



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

        

def proc(fun, args=None, client_id=0, poly=False):
    """Run the fun, processing the rtmidi calls and cleanup if called from within a script.
    If running from inside a script also dealloc the MIDI_OUT_CLIENT object.
    proc should be given one single
    fun which is your whole composition, don't call it multiple times
    via iteration etc."""
    global _CLIENT
    _CLIENT = _client_registry[client_id]
    with _get_client_port(client_id): # open the port for the chosen client
        try:
            if poly: # run async
                if isinstance(args, dict): # isinstance(None, dict) => False
                    asyncio.run(fun(**args))
                elif isinstance(args, (tuple, list)):
                    asyncio.run(fun(*args))
                elif args is not None:
                    asyncio.run(fun(args))
                else:
                    asyncio.run(fun())
            else:
                if isinstance(args, dict):
                    fun(**args)
                elif isinstance(args, (tuple, list)):
                    fun(*args)
                elif args is not None:
                    fun(args)
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


