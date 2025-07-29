import os
import sqlite3
from collections import defaultdict

import librosa
import numpy as np
from scipy.fft import fft

from db import get_connection, initialize_db


def hash_triplets(f1, f2, dt):
    return (f1 & 0x3FF) << 20 | (f2 & 0x3FF) << 10 | (dt & 0x3FF)


def preprocess_audio(path, target_sr=8000, win_size=2048, hop_size=512):
    audio, sr = librosa.load(path, sr=target_sr, mono=True)
    window = np.hamming(win_size)
    spectra = []

    for i in range(0, len(audio) - win_size, hop_size):
        chunk = audio[i : i + win_size]
        windowed = chunk * window
        fft_result = fft(windowed)
        magnitude = np.abs(fft_result[: win_size // 2])
        spectra.append(magnitude)
    return np.array(spectra), sr


def get_band_bins(sr, win_size, band_limits):
    freq_per_bin = sr / win_size
    band_bins = []
    for low, high in band_limits:
        low_limit = int(low / freq_per_bin)
        high_limit = int(high / freq_per_bin)
        band_bins.append((low_limit, high_limit))
    return band_bins


def fingerprint(path, song_name):
    spectra, sr = preprocess_audio(path, target_sr=8000)
    band_limits = [
        (0, 700),
        (700, 1400),
        (1400, 2100),
        (2100, 2800),
        (2800, 3400),
        (3400, 4000),
    ]
    band_bins = get_band_bins(sr, win_size=2048, band_limits=band_limits)

    anchors = []

    for t, frame in enumerate(spectra):
        peaks = []

        for band in band_bins:
            low_bin, high_bin = band
            if high_bin > len(frame):
                continue
            band_slice = frame[low_bin:high_bin]
            if len(band_slice) == 0:
                continue

            max_idx = np.argmax(band_slice)
            freq_bin = low_bin + max_idx
            mag = band_slice[max_idx]
            peaks.append((freq_bin, mag))
        if not peaks:
            continue
        avg_mag = np.mean([mag for _, mag in peaks])

        for freq_bin, mag in peaks:
            if mag >= avg_mag:
                anchors.append((t, freq_bin))
    fan_out = 5
    max_delta_time = 10
    fingerprint_map = defaultdict(list)

    for i, (t1, f1) in enumerate(anchors):
        for j in range(1, fan_out + 1):
            if i + j >= len(anchors):
                break
            t2, f2 = anchors[i + j]
            dt = t2 - t1
            if 0 < dt <= max_delta_time:
                hash_value = hash_triplets(f1, f2, dt)
                fingerprint_map[hash_value].append((t1, song_name))
    return fingerprint_map
