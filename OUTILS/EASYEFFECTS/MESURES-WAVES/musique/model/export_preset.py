"""Write the EasyEffects 8.3.0 output presets from model.json."""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
M = json.loads((HERE / 'model.json').read_text())
LIMIT_DB, LOOKAHEAD_MS = -0.3, 5.0


def eq_bands(gains):
    out = {}
    for i, (f, g, q) in enumerate(zip(M['eq_freqs'], gains, M['eq_q'])):
        out[f'band{i}'] = dict(frequency=float(f), gain=round(float(g), 2), q=float(q), type='Bell', mode='APO (DR)',
                               slope='x1', width=4.0, mute=False, solo=False)
    return out


def stereo_tools(mode):
    return {'balance-in': 0.0, 'balance-out': 0.0, 'bypass': False, 'delay': 0.0, 'dry': -100.0,
            'input-gain': 0.0, 'middle-level': 0.0, 'middle-panorama': 0.0, 'mode': mode, 'mutel': False,
            'muter': False, 'output-gain': 0.0, 'phasel': False, 'phaser': False, 'sc-level': 1.0,
            'side-balance': 0.0, 'side-level': 0.0, 'softclip': False, 'stereo-base': 0.0,
            'stereo-phase': 0.0, 'wet': 0.0}


def multiband():
    mb = {'bypass': False, 'input-gain': 0.0, 'output-gain': 0.0, 'dry': -80.01, 'wet': 0.0,
          'compressor-mode': 'Modern', 'envelope-boost': 'None', 'stereo-split': False}
    for n in range(8):
        b = {'compressor-enable': n < 5, 'mute': False, 'solo': False, 'attack-time': M['attack_ms'],
             'release-time': M['release_ms'], 'release-threshold': -80.01, 'knee': -M['knee_db'], 'makeup': 0.0,
             'compression-mode': 'Downward', 'sidechain-type': 'Internal', 'sidechain-mode': 'RMS',
             'sidechain-source': 'Middle', 'stereo-split-source': 'Left/Right', 'sidechain-lookahead': 0.0,
             'sidechain-reactivity': 10.0, 'sidechain-preamp': 0.0}
        if n < 5:
            b['attack-threshold'] = round(M['thresholds_db'][n], 1)
            b['ratio'] = round(M['ratios'][n], 2)
        else:
            b['attack-threshold'] = 0.0; b['ratio'] = 1.0
        if n > 0:
            b['enable-band'] = n < 5
            b['split-frequency'] = float((M['splits'] + [8000, 12000, 16000])[n - 1])
        mb[f'band{n}'] = b
    return mb


def limiter(out_gain):
    return {'mode': 'Herm Thin', 'oversampling': 'None', 'dithering': 'None', 'sidechain-type': 'Internal',
            'bypass': False, 'input-gain': 0.0, 'output-gain': out_gain, 'lookahead': LOOKAHEAD_MS, 'attack': 5.0,
            'release': 5.0, 'threshold': LIMIT_DB, 'sidechain-preamp': 0.0, 'stereo-link': 100.0, 'alr': False,
            'gain-boost': False}


def preset(out_gain):
    return {'output': {
        'blocklist': [],
        'plugins_order': ['stereo_tools#0', 'equalizer#0', 'stereo_tools#1', 'multiband_compressor#0', 'limiter#0'],
        'stereo_tools#0': stereo_tools('LR > MS (Stereo to Mid-Side)'),
        'equalizer#0': {'balance': 0.0, 'bypass': False, 'decramp': 'Off', 'input-gain': 0.0, 'output-gain': 0.0,
                        'mode': 'IIR', 'num-bands': len(M['eq_freqs']), 'pitch-left': 0.0, 'pitch-right': 0.0,
                        'split-channels': True, 'left': eq_bands(M['mid_gains']), 'right': eq_bands(M['side_gains'])},
        'stereo_tools#1': stereo_tools('MS > LR (Mid-Side to Stereo)'),
        'multiband_compressor#0': multiband(),
        'limiter#0': limiter(out_gain)}}


for name, g in [('Dell Latitude 7440 - modèle Waves ON (mesures musique)', 0.0),
                ('Dell Latitude 7440 - modèle Waves ON (mesures musique, -6 dB)', -6.0)]:
    (ROOT / f'{name}.json').write_text(json.dumps(preset(g), indent=2, ensure_ascii=False), encoding='utf-8')
    print('written', name)
print('EQ gain range Mid', min(M['mid_gains']), max(M['mid_gains']), '| Side', min(M['side_gains']), max(M['side_gains']))
