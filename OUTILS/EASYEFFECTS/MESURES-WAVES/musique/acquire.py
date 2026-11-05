"""Loopback capture of music files through the Realtek endpoint (shared WASAPI).

Safety: the endpoint is muted and mute is verified before and during playback
(the loopback taps the signal before the endpoint mute). The master volume is
never changed. Original mute/volume are restored in `finally`. Power (Waves
Playback ON/OFF) is toggled through UI Automation and always restored to ON.
"""
import ctypes
ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
import datetime, hashlib, json, os, pathlib, sys, time
import numpy as np
import soundfile as sf
import pyaudiowpatch as pa
import comtypes.client
from pycaw.pycaw import AudioUtilities
from PIL import ImageGrab

ROOT = pathlib.Path(__file__).resolve().parent
UI = comtypes.client.GetModule('UIAutomationCore.dll')
IDS = dict(bass='cmdMaxxBass', details='cmdDetails', width='cmdWidth', power='cmdPower', midnight='cmdMidnight')
EQ = ['EQ31', 'EQ63', 'EQ125', 'EQ250', 'EQ500', 'EQ1K', 'EQ2K', 'EQ4K', 'EQ8K', 'EQ16K']
EXPECTED_PROFILE = dict(bass='50 %', details='35 %', width='35 %', midnight='Off', **{k: '0.0 dB' for k in EQ})


def dump(path, obj):
    pathlib.Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding='utf-8')


class Waves:
    def __init__(self):
        self.a = comtypes.client.CreateObject(UI.CUIAutomation, interface=UI.IUIAutomation)
        self.w = self.a.GetRootElement().FindFirst(2, self.a.CreatePropertyCondition(30005, 'MaxxAudioPro'))
        if not self.w:
            raise RuntimeError('Waves window missing (open MaxxAudio Pro, Playback tab)')

    def _find(self, key):
        try:
            return self.w.FindFirst(4, self.a.CreatePropertyCondition(30011, IDS.get(key, key)))
        except Exception:
            return None

    def _click(self, element):
        r = element.CurrentBoundingRectangle
        ctypes.windll.user32.SetForegroundWindow(self.w.CurrentNativeWindowHandle)
        time.sleep(.5)
        ctypes.windll.user32.SetCursorPos((r.left + r.right) // 2, (r.top + r.bottom) // 2)
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0); ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)

    def el(self, key):
        # The UWP frame can be recreated between acquisitions: re-find the
        # window and, if needed, re-display the Playback tab (no setting changed).
        for attempt in range(6):
            e = self._find(key)
            if e:
                return e
            w = self.a.GetRootElement().FindFirst(2, self.a.CreatePropertyCondition(30005, 'MaxxAudioPro'))
            if w:
                self.w = w
                tab = self._find('cmdMenuAudio')
                if tab and not self._find(key):
                    self._click(tab)
            time.sleep(2.5)
        raise RuntimeError(f'Control {key} not found after retries')

    def state(self):
        return {k: self.el(k).CurrentItemStatus for k in list(IDS) + EQ}

    def snapshot(self, label):
        st = self.state(); r = self.w.CurrentBoundingRectangle
        (ROOT / 'states').mkdir(exist_ok=True)
        ImageGrab.grab(bbox=(r.left, r.top, r.right, r.bottom)).save(ROOT / 'states' / (label + '.png'))
        dump(ROOT / 'states' / (label + '.json'), dict(time=datetime.datetime.now().astimezone().isoformat(), controls=st))
        return st

    def power(self, on):
        want = 'On' if on else 'Off'
        if self.el('power').CurrentItemStatus == want:
            return
        r = self.el('power').CurrentBoundingRectangle
        ctypes.windll.user32.SetForegroundWindow(self.w.CurrentNativeWindowHandle)
        time.sleep(.6)
        ctypes.windll.user32.SetCursorPos((r.left + r.right) // 2, (r.top + r.bottom) // 2)
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0); ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
        time.sleep(1.0)
        if self.el('power').CurrentItemStatus != want:
            raise RuntimeError('Power state mismatch after click')
        time.sleep(1.0)  # let the APO settle


def endpoint():
    d = AudioUtilities.GetSpeakers()
    if d is None or 'Realtek' not in d.FriendlyName:
        raise RuntimeError('Default endpoint is not Realtek')
    return d


def other_active_sessions():
    out = []
    for s in AudioUtilities.GetAllSessions():
        if s.State == 1 and not s.SimpleAudioVolume.GetMute() and s.ProcessId != os.getpid():
            out.append(dict(pid=s.ProcessId, process=s.Process.name() if s.Process else 'System'))
    return out


def capture(label, source_name, state_name, wv):
    path = ROOT / 'captures' / (label + '.wav')
    if path.exists():
        print('SKIP (exists)', label); return
    (ROOT / 'captures').mkdir(exist_ok=True)
    src = ROOT / 'reference' / source_name
    x, rate = sf.read(src, dtype='float32', always_2d=True)
    if rate != 48000 or x.shape[1] != 2:
        raise RuntimeError('Unexpected source format')
    ui_before = wv.state()
    if state_name == 'on':
        bad = {k: (ui_before[k], v) for k, v in EXPECTED_PROFILE.items() if ui_before[k] != v}
        if bad or ui_before['power'] != 'On':
            raise RuntimeError(f'Profile not as expected for ON: {bad} power={ui_before["power"]}')
    elif ui_before['power'] != 'Off':
        raise RuntimeError('Power not Off for OFF state')
    d = endpoint(); v = d.EndpointVolume
    original = dict(scalar=v.GetMasterVolumeLevelScalar(), mute=v.GetMute())
    act = other_active_sessions()
    if act:
        raise RuntimeError(f'Other active audio sessions: {act}')
    chunks, events = [], []
    start = datetime.datetime.now().astimezone().isoformat()

    def cb(data, n, info, status):
        chunks.append(data)
        if status:
            events.append(dict(status=status, frames=n))
        return (None, pa.paContinue)

    try:
        v.SetMute(1, None)
        if not v.GetMute():
            raise RuntimeError('Mute not confirmed: refusing to play')
        with pa.PyAudio() as p:
            host = p.get_host_api_info_by_type(pa.paWASAPI)
            out = p.get_device_info_by_index(host['defaultOutputDevice'])
            loop = p.get_wasapi_loopback_analogue_by_dict(out)
            if 'Realtek' not in out['name'] or not loop['isLoopbackDevice']:
                raise RuntimeError('Invalid render/loopback device')
            if int(out['defaultSampleRate']) != rate or loop['maxInputChannels'] != 2:
                raise RuntimeError('Native format mismatch')
            with p.open(format=pa.paFloat32, channels=2, rate=rate, input=True, input_device_index=loop['index'],
                        frames_per_buffer=512, stream_callback=cb):
                with p.open(format=pa.paFloat32, channels=2, rate=rate, output=True,
                            output_device_index=out['index'], frames_per_buffer=512) as play:
                    for i, off in enumerate(range(0, len(x), 512)):
                        if i % 94 == 0 and not v.GetMute():
                            v.SetMute(1, None)
                            raise RuntimeError('Mute lost during playback: aborted')
                        play.write(x[off:off + 512].tobytes(), exception_on_underflow=True)
                time.sleep(.3)
        if not chunks:
            raise RuntimeError('No loopback packets')
        y = np.frombuffer(b''.join(chunks), dtype=np.float32).reshape(-1, 2).copy()
        ui_after = wv.state()
        if ui_after != ui_before:
            raise RuntimeError('UI state changed during capture')
        sf.write(path, y, rate, subtype='FLOAT')
        meta = dict(label=label, time=start, source=source_name, source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                    capture_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), waves_state=state_name,
                    ui_state_before=ui_before, ui_state_after=ui_after, endpoint=d.FriendlyName, endpoint_id=d.id,
                    rate=rate, frames=len(y), original=original, mute_during=True,
                    peak_dbfs=float(20 * np.log10(max(1e-30, float(np.max(np.abs(y)))))),
                    rms_dbfs=float(20 * np.log10(max(1e-30, float(np.sqrt(np.mean(y.astype(np.float64) ** 2)))))),
                    clipped_samples=int(np.sum(np.abs(y) >= 1)), callback_events=events,
                    method='PyAudioWPatch WASAPI shared loopback, float32, no RAW/exclusive, endpoint muted, volume untouched')
        dump(path.with_suffix('.json'), meta)
        print(f'DONE {label}: peak {meta["peak_dbfs"]:.1f} rms {meta["rms_dbfs"]:.1f} events {len(events)}', flush=True)
    finally:
        v.SetMasterVolumeLevelScalar(original['scalar'], None)
        v.SetMute(original['mute'], None)


def run(only=None):
    ref = json.loads((ROOT / 'reference' / 'reference.json').read_text(encoding='utf-8'))
    if only:
        ref = [r for r in ref if r['label'] in only]
    wv = Waves()
    initial = wv.state()
    dump(ROOT / 'initial-ui-state.json', initial)
    wv.snapshot('initial')
    try:
        for state_name in ['on', 'off']:
            wv.power(state_name == 'on')
            wv.snapshot('state-' + state_name)
            for r in ref:
                capture(f'{r["label"]}_L{abs(r["target_lufs"])}_{state_name}', r['file'], state_name, wv)
    finally:
        wv.power(True)
        final = wv.snapshot('final')
        dump(ROOT / 'restoration.json', dict(time=datetime.datetime.now().astimezone().isoformat(),
                                             initial=initial, final=final, identical=initial == final))
        print('RESTORED, identical to initial:', initial == final, flush=True)


if __name__ == '__main__':
    run(sys.argv[1:] or None)
