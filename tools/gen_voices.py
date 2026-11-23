"""Generate the app's voices with Microsoft Edge neural voices (edge-tts).

Usage (run by .github/workflows/voices.yml):
  python tools/gen_voices.py samples
      -> voice-samples/<lang>-<voice>.mp3, a few test sentences per candidate voice
  python tools/gen_voices.py full --fr fr-FR-EloiseNeural --en en-US-AnaNeural [--rate -8%]
      -> audio/fr.mp3, audio/fr.json, audio/en.mp3, audio/en.json (all phrases, packed)
"""
import argparse, asyncio, json, os, re, subprocess, sys, tempfile
import numpy as np
import soundfile as sf
import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHRASES = json.load(open(os.path.join(ROOT, 'tools', 'phrases.json'), encoding='utf-8'))

CANDIDATES = {
    'fr': ['fr-FR-EloiseNeural', 'fr-FR-DeniseNeural', 'fr-FR-VivienneMultilingualNeural',
           'fr-FR-RemyMultilingualNeural', 'fr-FR-HenriNeural'],
    'en': ['en-US-AnaNeural', 'en-US-JennyNeural', 'en-US-AvaMultilingualNeural', 'en-US-AriaNeural'],
}
SAMPLE_KEYS = ['L_B', 's1', 'stepDone', 's4', 'F_S', 'NL_3']
SR = 24000
# questions the child must answer: slower so a 5-year-old can follow
SLOW_PREFIXES = ('O_', 'ON_', 'F_', 'ML_', 'GQ_')
SLOW_RATE = '-25%'
GAP = 0.35


async def synth(text, voice, rate, path, tries=4):
    for i in range(tries):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(path)
            if os.path.getsize(path) > 0:
                return
        except Exception as e:  # network hiccup: wait and retry
            print('retry', i + 1, voice, repr(text)[:40], e, file=sys.stderr)
        await asyncio.sleep(2 * (i + 1))
    raise RuntimeError(f'failed: {voice} {text!r}')


def to_wave(mp3_path):
    wav = mp3_path + '.wav'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', mp3_path, '-ac', '1', '-ar', str(SR), wav], check=True)
    a, _ = sf.read(wav, dtype='float32')
    nz = np.where(np.abs(a) > 0.01)[0]
    if len(nz):
        a = a[max(0, nz[0] - int(SR * .03)): nz[-1] + int(SR * .06)]
    return a


def normalize(a, target_rms=0.12):
    speech = a[np.abs(a) > 0.01]
    rms = float(np.sqrt((speech ** 2).mean())) if len(speech) else 0
    if rms > 0:
        a = a * (target_rms / rms)
    return np.clip(a, -0.98, 0.98)


def encode(wave, out_mp3):
    tmp = out_mp3 + '.wav'
    sf.write(tmp, wave, SR)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp, '-ac', '1', '-b:a', '64k', out_mp3], check=True)
    os.remove(tmp)


async def samples(rate):
    out = os.path.join(ROOT, 'voice-samples')
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for lang, voices in CANDIDATES.items():
            for voice in voices:
                parts = []
                try:
                    for i, key in enumerate(SAMPLE_KEYS):
                        p = os.path.join(tmp, f'{voice}_{i}.mp3')
                        await synth(PHRASES[lang][key], voice, rate, p)
                        parts += [to_wave(p), np.zeros(int(SR * .7), dtype=np.float32)]
                except RuntimeError as e:
                    print('skipped voice', voice, e)
                    continue
                name = voice.split('-')[2].replace('Neural', '').replace('Multilingual', '')
                encode(normalize(np.concatenate(parts)), os.path.join(out, f'{lang}-{name}.mp3'))
                print('sample', lang, voice)


async def full(fr_voice, en_voice, rate):
    out = os.path.join(ROOT, 'audio')
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for lang, voice in (('fr', fr_voice), ('en', en_voice)):
            parts, mp, pos = [], {}, 0
            lead = np.zeros(int(SR * .3), dtype=np.float32)
            parts.append(lead); pos += len(lead)
            for n, (key, text) in enumerate(PHRASES[lang].items()):
                p = os.path.join(tmp, f'{lang}_{n}.mp3')
                await synth(text, voice, SLOW_RATE if key.startswith(SLOW_PREFIXES) else rate, p)
                a = to_wave(p)
                mp[key] = [round(pos / SR, 4), round(len(a) / SR, 4)]
                gap = np.zeros(int(SR * GAP), dtype=np.float32)
                parts += [a, gap]; pos += len(a) + len(gap)
            encode(normalize(np.concatenate(parts)), os.path.join(out, f'{lang}.mp3'))
            json.dump(mp, open(os.path.join(out, f'{lang}.json'), 'w'))
            print(lang, voice, len(mp), 'clips', round(pos / SR, 1), 's')
    # new audio means a new offline cache version
    sw = os.path.join(ROOT, 'sw.js')
    src = open(sw, encoding='utf-8').read()
    src = re.sub(r"const VERSION = '[^']*';", f"const VERSION = 'abc-{os.environ.get('GITHUB_RUN_ID', 'local')}';", src)
    open(sw, 'w', encoding='utf-8').write(src)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['samples', 'full'])
    ap.add_argument('--fr', default='fr-FR-EloiseNeural')
    ap.add_argument('--en', default='en-US-AnaNeural')
    ap.add_argument('--rate', default='-8%')
    a = ap.parse_args()
    asyncio.run(samples(a.rate) if a.mode == 'samples' else full(a.fr, a.en, a.rate))
