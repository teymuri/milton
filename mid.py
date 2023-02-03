import time
import asyncio
import rtmidi
import rtmidi.midiutil
import computil.cfg
import computil.err
from math import (modf, log2)
from datetime import datetime, timedelta
from contextlib import ExitStack
from rtmidi.midiconstants import (
    NOTE_OFF, NOTE_ON, PITCH_BEND,
    ALL_SOUND_OFF, CONTROL_CHANGE,
    RESET_ALL_CONTROLLERS
)



_client_registry = dict()
# This is the client used on each processing, and
# is set one per each proc call.
_CLIENT = None
NO_BEND_VAL = 2 ** 13
NO_BEND_RESET_LSB = NO_BEND_VAL & 0x7f # isthis msb or lsb for send_message?!??
NO_BEND_RESET_MSB = (NO_BEND_VAL >> 7) & 0x7f
SEMITONE_BEND_RANGE = 4096
# todo: support more channels through more tracks/ports?
_chnls_pool = set(range(16))

def _get_clientid_and_chnl(chnl):
    chnl -= 1
    client_id = chnl // 16
    client_chnl = chnl % 16
    return client_id, client_chnl

def bpm_to_sec(bpm):
    """Returns the duration of one beat in tempo bpm."""
    return 60 / bpm

def rhythm_to_sec(rhy, tempo):
    """"""
    return rhy * 4.0 * bpm_to_sec(tempo)

def knum_to_hz(knum):
    return 440 * 2 ** ((knum - 69) / 12.)

def hz_to_knum(hz):
    if hz == 0:
        raise computil.err.CUZeroHzErr()
    return 12 * (log2(hz) - log2(440)) + 69

def _get_bend_msgs(knum, knum_ipart, ch):
    bend_val = NO_BEND_VAL + NO_BEND_VAL * (12 / computil.cfg.bend_range) * log2(knum_to_hz(knum) / knum_to_hz(knum_ipart))
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





_chnl_usage_trace = {
    # channel: [reference/usage, status]
    # status = is in use by a microtone (if usage > 0)
    # status False and reference>0 means in-use by equal tempered notes
    chnl: [0, None] for chnl in range(computil.cfg.port_count * 16)
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


def play_note(knum=60, dur=1, chnl=1, vel=127):
    global _chnl_usage_trace
    client_id, chnl = _get_clientid_and_chnl(chnl)
    client = _client_registry[client_id]
    non, nof, bend, bend_reset, chnl_ = _get_msgs(knum, chnl, vel)
    try:
        if bend:
            client.send_message(bend)
        client.send_message(non)
        time.sleep(dur)
    finally:
        client.send_message(nof)
        if bend_reset:
            _chnl_usage_trace[chnl_][0] -= 1
            assert _chnl_usage_trace[chnl_][0] == 0
            _chnl_usage_trace[chnl_][1] = None
            client.send_message(bend_reset)
        else:
            _chnl_usage_trace[chnl_][0] -= 1
            if _chnl_usage_trace[chnl_][0] == 0:
                _chnl_usage_trace[chnl_][1] = None

async def _async_play_note(knum, dur, chnl, vel):
    global _chnl_usage_trace
    client_id, chnl = _get_clientid_and_chnl(chnl)
    client = _client_registry[client_id]
    non, nof, bend, bend_reset, chnl_ = _get_msgs(knum, chnl, vel)
    try:
        if bend:
            client.send_message(bend)
        client.send_message(non)
        await asyncio.sleep(dur)
    finally:
        client.send_message(nof)
        if bend_reset:
            _chnl_usage_trace[chnl_][0] -= 1
            assert _chnl_usage_trace[chnl_][0] == 0
            _chnl_usage_trace[chnl_][1] = None
            client.send_message(bend_reset)
        else:
            _chnl_usage_trace[chnl_][0] -= 1
            if _chnl_usage_trace[chnl_][0] == 0:
                _chnl_usage_trace[chnl_][1] = None

async def _send_non_bend(t, non, bend, client):
    await asyncio.sleep(t)
    print(t,non)
    if bend:
        client.send_message(bend)
    client.send_message(non)

async def _send_nof_bend_reset(t,dur,nof, bend_reset, chnl_, client):
    global _chnl_usage_trace
    await asyncio.sleep(t+dur)
    # print(t,dur,nof)
    client.send_message(nof)
    if bend_reset:
        _chnl_usage_trace[chnl_][0] -= 1
        assert _chnl_usage_trace[chnl_][0] == 0
        _chnl_usage_trace[chnl_][1] = None
        client.send_message(bend_reset)
    else:
        _chnl_usage_trace[chnl_][0] -= 1
        if _chnl_usage_trace[chnl_][0] == 0:
            _chnl_usage_trace[chnl_][1] = None


def _sched_play_note(knum, chnl, vel):
    client_id, chnl = _get_clientid_and_chnl(chnl)
    client = _client_registry[client_id]
    non, nof, bend, bend_reset, chnl_ = _get_msgs(knum, chnl, vel)
    return non, nof, bend, bend_reset, chnl_, client
    # try:
    #     if bend:
    #         client.send_message(bend)
    #     client.send_message(non)
    #     await asyncio.sleep(dur)
    # finally:
    #     client.send_message(nof)
    #     if bend_reset:
    #         _chnl_usage_trace[chnl_][0] -= 1
    #         assert _chnl_usage_trace[chnl_][0] == 0
    #         _chnl_usage_trace[chnl_][1] = None
    #         client.send_message(bend_reset)
    #     else:
    #         _chnl_usage_trace[chnl_][0] -= 1
    #         if _chnl_usage_trace[chnl_][0] == 0:
    #             _chnl_usage_trace[chnl_][1] = None

async def _async_play_chord(knums, dur, chnl, vel):
    global _chnl_usage_trace
    client_id, chnl = _get_clientid_and_chnl(chnl)
    client = _client_registry[client_id]
    msgs = [_get_msgs(knum, chnl, vel) for knum in knums]
    try:
        for non, _, bend, _, _ in msgs:
            if bend: # either bend message or None
                client.send_message(bend)
            client.send_message(non)
        await asyncio.sleep(dur)
    finally:
        for _, nof, _, bend_reset, chnl_ in msgs:
            client.send_message(nof)
            if bend_reset:
                _chnl_usage_trace[chnl_][0] -= 1
                assert _chnl_usage_trace[chnl_][0] == 0
                _chnl_usage_trace[chnl_][1] = None
                client.send_message(bend_reset)
            else:
                _chnl_usage_trace[chnl_][0] -= 1
                if _chnl_usage_trace[chnl_][0] == 0:
                    _chnl_usage_trace[chnl_][1] = None

def play_chord(knums=(60, 64, 67), dur=1, chnl=1, vel=127):
    global _chnl_usage_trace
    client_id, chnl = _get_clientid_and_chnl(chnl)
    client = _client_registry[client_id]
    msgs = [_get_msgs(knum, chnl, vel) for knum in knums]
    try:
        for non, _, bend, _, _ in msgs:
            if bend: # either bend message or None
                client.send_message(bend)
            client.send_message(non)
        time.sleep(dur)
    finally:
        for _, nof, _, bend_reset, chnl_ in msgs:
            client.send_message(nof)
            if bend_reset:
                _chnl_usage_trace[chnl_][0] -= 1
                assert _chnl_usage_trace[chnl_][0] == 0
                _chnl_usage_trace[chnl_][1] = None
                client.send_message(bend_reset)
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


async def _sched_play_voice(knums, ts, durs, chnl, vels):
    for i, knum in enumerate(knums):
        # await _sched_play_note(knum, ts[i], durs[i], chnl, vels[i])
        non, nof, bend, bend_reset, chnl_, client = _sched_play_note(knum, chnl, vels[i])
        os=_get_diff_times(ts)
        x= _send_non_bend(ts[i], non, bend, client)
        y= _send_nof_bend_reset(ts[i],durs[i],nof, bend_reset, chnl_, client)
        return x, y

def voice(knums, ts, durs, chnl, vels):
    x=[]
    os=_get_diff_times(ts)
    for i, knum in enumerate(knums):
        # await _sched_play_note(knum, ts[i], durs[i], chnl, vels[i])
        non, nof, bend, bend_reset, chnl_, client = _sched_play_note(knum, chnl, vels[i])
        x.append( ( non, nof, bend, bend_reset, chnl_, client, ts[i],durs[i] ))  
        # x= _send_non_bend(os[i], non, bend, client)
        # y= _send_nof_bend_reset(os[i],durs[i],nof, bend_reset, chnl_, client)
    return x

_proc_stime = None


def _get_diff_times(onsets):
    try:
        onsets = [0] + onsets
    except TypeError:
        onsets = (0,) + onsets
    return [b - a for a, b in zip(onsets[:-1], onsets[1:])]

async def play_poly(voices):
    for knums, onsets, durs, chnls, vels in voices:
        await  _sched_play_voice(knums, _get_diff_times(onsets), durs, chnls, vels)
    # await asyncio.gather(
    #     *(_play_voice(v[0], v[1], v[2], v[3]) for v in voices)
    # )



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

# save a list of available ports
_tmp_client = rtmidi.MidiOut(rtapi=rtmidi.API_LINUX_ALSA)
_AVAILABLE_PORTS = [p.lower() for p in _tmp_client.get_ports()]
# hopefuly ports are listed in right order by get_ports!!!
SYNTH_PORT_IDXS = [i for i, p in enumerate(_AVAILABLE_PORTS) if computil.cfg.synth_id.lower() in p]
_tmp_client.delete()

def open_ports(): 
    """Opens output ports on each client. This should happen
    before sending anything to the processor."""
    for i in range(computil.cfg.port_count):
        # create a new output client and register it
        client = rtmidi.MidiOut(name=f"computil output {i}", rtapi=rtmidi.API_LINUX_ALSA)
        client.open_port(SYNTH_PORT_IDXS[i], f"client {i} port")
        _client_registry[i] = client

# def close_ports():
#     for idx, client in _client_registry.items():
#         client.close_port()
#         del client



def proc(fun, args=None, client_id=0, poly=False):
    """Run the fun, processing the rtmidi calls and cleanup if called from within a script.
    If running from inside a script also dealloc the MIDI_OUT_CLIENT object.
    proc should be given one single
    fun which is your whole composition, don't call it multiple times
    via iteration etc."""
    clients = _client_registry.values()
    global _proc_stime
    _proc_stime = datetime.now()
    with ExitStack() as exit_stack:
        for client_ctx in clients:
            exit_stack.enter_context(client_ctx)
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
            print("\npanicking...")
            for client in clients:
                for chnl in range(16):
                    client.send_message([CONTROL_CHANGE | chnl, ALL_SOUND_OFF, 0])
                    client.send_message([CONTROL_CHANGE | chnl, RESET_ALL_CONTROLLERS, 0])
                    time.sleep(0.05)
                time.sleep(0.05)
        except (computil.err.CUZeroHzErr):
            print("can't convert 0 hz to midi knum")

def _panic(clients):
    print("\npanicking...")
    for client in clients:
        print(client, "panic")
        for chnl in range(16):
            client.send_message([CONTROL_CHANGE | chnl, ALL_SOUND_OFF, 0])
            client.send_message([CONTROL_CHANGE | chnl, RESET_ALL_CONTROLLERS, 0])
            time.sleep(0.05)
        time.sleep(0.05)

async def _async_proc(coros, args=None, client_id=0, poly=False):
    """Run the fun, processing the rtmidi calls and cleanup if called from within a script.
    If running from inside a script also dealloc the MIDI_OUT_CLIENT object.
    proc should be given one single
    fun which is your whole composition, don't call it multiple times
    via iteration etc."""
    clients = _client_registry.values()
    global _proc_stime
    _proc_stime = datetime.now()
    with ExitStack() as exit_stack:
        for client_ctx in clients:
            exit_stack.enter_context(client_ctx)
        try:
            ts=[]
            for coro in coros:
                for n in coro:
                    non,nof,bend,bend_r,c,cl,os,d=n
                    ts.append(asyncio.create_task(
                        _send_non_bend(os,non,bend,cl)
                    ))
                    ts.append(asyncio.create_task(
                        _send_nof_bend_reset(os,d,nof,bend_r,c,cl)
                    ))
            await asyncio.gather(*ts)
        except (EOFError, KeyboardInterrupt, asyncio.CancelledError):
            _panic(clients)
        except (computil.err.CUZeroHzErr):
            print("can't convert 0 hz to midi knum")

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


