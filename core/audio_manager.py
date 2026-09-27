"""
Audio Manager — Procedural sound effects and background music via pygame.mixer
Generates banger sound effects mathematically — no audio files required!
"""
import pygame
import numpy as np
import math
import random

class AudioManager:
    def __init__(self):
        # Ensure mixer is not already running, then re-init as stereo
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        pygame.mixer.init(44100, -16, 2, 512)
        pygame.mixer.set_num_channels(32)
        self._sfx_cache  = {}
        self._music_buf  = None
        self.sfx_vol     = 0.8
        self.music_vol   = 0.6
        self._num_channels = pygame.mixer.get_init()[2]  # actual channels (1 or 2)
        self._build_sfx()
        self._build_music()
        self._playing_music = False

    # ─── Waveform helpers ─────────────────────────────────────────────────────
    @staticmethod
    def _sine(freq, duration, sr=44100, amp=0.5):
        t = np.linspace(0, duration, int(sr * duration), False)
        wave = amp * np.sin(2 * np.pi * freq * t)
        return wave

    @staticmethod
    def _square(freq, duration, sr=44100, amp=0.3):
        t = np.linspace(0, duration, int(sr * duration), False)
        wave = amp * np.sign(np.sin(2 * np.pi * freq * t))
        return wave

    @staticmethod
    def _noise(duration, sr=44100, amp=0.5):
        n = int(sr * duration)
        return amp * (np.random.random(n) * 2 - 1)

    @staticmethod
    def _envelope(wave, attack=0.01, decay=0.1, sustain=0.7, release=0.15):
        sr = 44100
        n = len(wave)
        env = np.ones(n)
        a = int(sr * attack)
        d = int(sr * decay)
        r = int(sr * release)
        s_end = max(n - r, a + d)
        # Attack
        env[:a] = np.linspace(0, 1, a)
        # Decay
        env[a:a+d] = np.linspace(1, sustain, d)
        # Sustain (stays at sustain level)
        # Release
        if s_end < n:
            env[s_end:] = np.linspace(sustain, 0, n - s_end)
        return wave * env

    def _to_sound(self, wave):
        """Convert a mono float32 numpy wave to a pygame.Sound using WAV bytes.
        This approach is immune to mixer channel count issues."""
        import io, wave as wave_mod
        wave = np.clip(wave, -1.0, 1.0)
        wave_int = (wave * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave_mod.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(wave_int.tobytes())
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    # ─── SFX Synthesis ────────────────────────────────────────────────────────
    def _build_sfx(self):
        sr = 44100
        sfx = {}

        # Punch hit — short thud + crack
        base  = self._sine(80, 0.08, amp=0.6)
        crack = self._noise(0.08, amp=0.4)[:len(base)]
        punch = self._envelope(base + crack, attack=0.002, decay=0.05, sustain=0.0, release=0.03)
        sfx["punch"] = self._to_sound(punch)

        # Heavy hit — deeper thud
        base  = self._sine(55, 0.12, amp=0.7)
        crack = self._noise(0.12, amp=0.5)[:len(base)]
        heavy = self._envelope(base + crack, attack=0.003, decay=0.08, sustain=0.1, release=0.04)
        sfx["heavy_hit"] = self._to_sound(heavy)

        # Block / parry — metallic clank
        t = np.linspace(0, 0.15, int(sr * 0.15))
        clank = 0.5 * np.sin(2*np.pi*800*t) * np.exp(-20*t)
        clank += 0.3 * np.sin(2*np.pi*1200*t) * np.exp(-30*t)
        clank += 0.2 * self._noise(0.15, amp=0.3)[:len(clank)]
        sfx["block"] = self._to_sound(clank)

        # Magic cast — rising sine sweep
        t = np.linspace(0, 0.3, int(sr * 0.3))
        freq_sweep = np.linspace(200, 800, len(t))
        magic = 0.5 * np.sin(2 * np.pi * np.cumsum(freq_sweep) / sr)
        magic = self._envelope(magic, attack=0.05, decay=0.1, sustain=0.5, release=0.15)
        sfx["magic"] = self._to_sound(magic)

        # Magic hit — resonant boom + shimmer
        t = np.linspace(0, 0.4, int(sr * 0.4))
        boom  = 0.5 * np.sin(2*np.pi*120*t) * np.exp(-8*t)
        shimmer = 0.3 * np.sin(2*np.pi*2000*t) * np.exp(-15*t)
        noise_layer = 0.2 * self._noise(0.4, amp=0.3)[:len(t)]
        magic_hit = boom + shimmer + noise_layer
        sfx["magic_hit"] = self._to_sound(magic_hit)

        # Jump — quick ascending tone
        t = np.linspace(0, 0.12, int(sr * 0.12))
        freqs = np.linspace(300, 600, len(t))
        jump = 0.3 * np.sin(2 * np.pi * np.cumsum(freqs) / sr)
        jump = self._envelope(jump, attack=0.01, decay=0.05, sustain=0.0, release=0.06)
        sfx["jump"] = self._to_sound(jump)

        # KO / knockdown — deep thud + reverb
        t = np.linspace(0, 0.6, int(sr * 0.6))
        ko = 0.6 * np.sin(2*np.pi*60*t) * np.exp(-5*t)
        ko += 0.4 * self._noise(0.6, amp=0.3)[:len(t)] * np.exp(-6*t)
        sfx["ko"] = self._to_sound(ko)

        # Victory — short arpeggio fanfare
        notes = [523, 659, 784, 1047]   # C5 E5 G5 C6
        total_dur = 0.6
        t_full = np.zeros(int(sr * total_dur))
        step = total_dur / len(notes)
        for i, freq in enumerate(notes):
            start = int(i * step * sr)
            end   = start + int(step * sr)
            t = np.linspace(0, step, end - start)
            note = 0.4 * np.sin(2 * np.pi * freq * t)
            note = self._envelope(note, attack=0.01, decay=0.1, sustain=0.6, release=0.2)
            t_full[start:end] += note
        sfx["victory"] = self._to_sound(t_full)

        # Round start — dramatic impact
        t = np.linspace(0, 0.5, int(sr * 0.5))
        impact = 0.5 * np.sin(2*np.pi*100*t) * np.exp(-6*t)
        impact += 0.3 * np.sin(2*np.pi*200*t) * np.exp(-8*t)
        impact += 0.2 * self._noise(0.5, amp=0.4)[:len(t)] * np.exp(-10*t)
        sfx["round_start"] = self._to_sound(impact)

        # Coin earned — high ding
        t = np.linspace(0, 0.25, int(sr * 0.25))
        ding = 0.35 * np.sin(2*np.pi*1500*t) * np.exp(-12*t)
        ding += 0.2 * np.sin(2*np.pi*2000*t) * np.exp(-15*t)
        sfx["coin"] = self._to_sound(ding)

        # Combo hit — rising pitch per hit
        for i in range(1, 9):
            freq = 300 + i * 80
            t = np.linspace(0, 0.08, int(sr * 0.08))
            combo = 0.35 * np.sin(2*np.pi*freq*t) * np.exp(-20*t)
            sfx[f"combo_{i}"] = self._to_sound(combo)

        # Critical hit — dramatic flash sound
        t = np.linspace(0, 0.35, int(sr * 0.35))
        crit = 0.6 * np.sin(2*np.pi*180*t) * np.exp(-5*t)
        crit += 0.4 * np.sin(2*np.pi*900*t) * np.exp(-10*t)
        crit += 0.3 * self._noise(0.35, amp=0.5)[:len(t)] * np.exp(-8*t)
        sfx["critical"] = self._to_sound(crit)

        # Rage mode activate — roar-like
        t = np.linspace(0, 0.8, int(sr * 0.8))
        rage = 0.5 * np.sin(2*np.pi*80*t)
        rage += 0.3 * np.sin(2*np.pi*160*t)
        rage *= (1 - np.exp(-3*t)) * np.exp(-1.5*t)
        rage += 0.2 * self._noise(0.8, amp=0.4)[:len(t)] * np.exp(-2*t)
        sfx["rage"] = self._to_sound(rage)

        # Menu select
        t = np.linspace(0, 0.1, int(sr * 0.1))
        select = 0.3 * np.sin(2*np.pi*600*t) * np.exp(-20*t)
        sfx["select"] = self._to_sound(select)

        # Menu confirm
        t = np.linspace(0, 0.15, int(sr * 0.15))
        confirm = 0.35 * np.sin(2*np.pi*800*t) * np.exp(-15*t)
        confirm += 0.2 * np.sin(2*np.pi*1200*t) * np.exp(-20*t)
        sfx["confirm"] = self._to_sound(confirm)

        # Purchase
        t = np.linspace(0, 0.3, int(sr * 0.3))
        purchase = 0.3 * np.sin(2*np.pi*1000*t) * np.exp(-8*t)
        purchase += 0.25 * np.sin(2*np.pi*1500*t) * np.exp(-10*t)
        purchase += 0.2 * np.sin(2*np.pi*2000*t) * np.exp(-12*t)
        sfx["purchase"] = self._to_sound(purchase)

        # Level up — ascending arpeggio
        notes = [392, 494, 587, 740, 988]  # G4 B4 D5 F#5 B5
        t_full = np.zeros(int(sr * 1.0))
        step = 0.15
        for i, freq in enumerate(notes):
            start = int(i * 0.12 * sr)
            end   = start + int(step * sr)
            if end > len(t_full): end = len(t_full)
            t = np.linspace(0, step, end - start)
            note = 0.35 * np.sin(2 * np.pi * freq * t)
            note = self._envelope(note, attack=0.01, decay=0.05, sustain=0.7, release=0.09)
            t_full[start:end] += note
        sfx["level_up"] = self._to_sound(t_full)

        self._sfx_cache = sfx

    # ─── Background Music Synthesis ───────────────────────────────────────────
    def _build_music(self):
        """Generate a loopable dark electronic battle track."""
        sr = 44100
        bpm = 140
        beat = 60 / bpm
        bars = 8
        total = beat * 4 * bars
        n = int(sr * total)
        track = np.zeros(n)

        def add_note(buf, freq, start_sec, dur_sec, amp=0.2, wave_fn=None):
            s = int(start_sec * sr)
            e = min(s + int(dur_sec * sr), len(buf))
            if s >= len(buf): return
            t = np.linspace(0, dur_sec, e - s, False)
            if wave_fn == "square":
                w = amp * np.sign(np.sin(2 * np.pi * freq * t))
            elif wave_fn == "noise":
                w = amp * (np.random.random(len(t)) * 2 - 1)
            else:
                w = amp * np.sin(2 * np.pi * freq * t)
            env = np.exp(-3 * t / dur_sec)
            buf[s:e] += w * env

        # Bass line pattern (dark/menacing)
        bass_notes = [55, 55, 65, 55, 49, 55, 58, 55]   # A1 etc
        for bar in range(bars):
            for beat_i, freq in enumerate(bass_notes[:4]):
                t_start = (bar * 4 + beat_i) * beat
                add_note(track, freq, t_start, beat * 0.9, amp=0.35)
                add_note(track, freq * 2, t_start, beat * 0.5, amp=0.12)  # octave layer

        # Kick drum (thud every beat)
        for beat_i in range(int(bars * 4)):
            t_start = beat_i * beat
            t = np.linspace(0, 0.15, int(sr * 0.15))
            kick = 0.5 * np.sin(2*np.pi*80*t) * np.exp(-20*t)
            kick += 0.3 * self._noise(0.15, amp=0.4)[:len(t)] * np.exp(-30*t)
            s = int(t_start * sr)
            e = min(s + len(kick), n)
            track[s:e] += kick[:e-s]

        # Snare (beats 2 & 4)
        for bar in range(bars):
            for snare_beat in [1, 3]:
                t_start = (bar * 4 + snare_beat) * beat
                snare_t = np.linspace(0, 0.1, int(sr * 0.1))
                snare = 0.3 * self._noise(0.1, amp=0.6)[:len(snare_t)] * np.exp(-25*snare_t)
                snare += 0.2 * np.sin(2*np.pi*200*snare_t) * np.exp(-30*snare_t)
                s = int(t_start * sr)
                e = min(s + len(snare), n)
                track[s:e] += snare[:e-s]

        # Hi-hat pattern (8th notes)
        for beat_i in range(int(bars * 8)):
            t_start = beat_i * beat / 2
            hh_t = np.linspace(0, 0.05, int(sr * 0.05))
            hh = 0.15 * self._noise(0.05, amp=1.0)[:len(hh_t)] * np.exp(-50*hh_t)
            s = int(t_start * sr)
            e = min(s + len(hh), n)
            track[s:e] += hh[:e-s]

        # Melodic lead (dark scale)
        melody = [110, 130, 98, 110, 147, 130, 165, 130]  # Am pentatonic area
        for bar in range(bars):
            note_i = bar % len(melody)
            freq = melody[note_i]
            t_start = bar * 4 * beat + beat
            add_note(track, freq, t_start, beat * 2, amp=0.18, wave_fn="square")
            add_note(track, freq * 1.5, t_start + beat, beat * 1.5, amp=0.10)

        # Normalize
        peak = np.max(np.abs(track))
        if peak > 0:
            track = track / peak * 0.75

        track_int = (track * 32767).astype(np.int16)
        import io, wave as wave_mod
        buf = io.BytesIO()
        with wave_mod.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(track_int.tobytes())
        buf.seek(0)
        self._music_buf = pygame.mixer.Sound(buf)

    # ─── Public API ───────────────────────────────────────────────────────────
    def play_sfx(self, name, volume=None):
        snd = self._sfx_cache.get(name)
        if snd:
            vol = volume if volume is not None else self.sfx_vol
            snd.set_volume(vol)
            snd.play()

    def play_music(self, loop=True):
        if self._music_buf and not self._playing_music:
            self._music_buf.set_volume(self.music_vol)
            loops = -1 if loop else 0
            self._music_buf.play(loops=loops)
            self._playing_music = True

    def stop_music(self):
        if self._music_buf:
            self._music_buf.stop()
        self._playing_music = False

    def set_sfx_volume(self, vol):
        self.sfx_vol = max(0.0, min(1.0, vol))

    def set_music_volume(self, vol):
        self.music_vol = max(0.0, min(1.0, vol))
        if self._music_buf:
            self._music_buf.set_volume(self.music_vol)
