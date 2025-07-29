import os
from collections import defaultdict

from db import get_connection
from fingerprinting import fingerprint


def match(query_path, sample_rate=8000, hop_size=512, top_n=1):
    print("Fingerprinting query audio...")
    query_fingerprints = fingerprint(query_path, song_name="query")

    query_hashes = []
    for h, times in query_fingerprints.items():
        for t_query, _ in times:
            query_hashes.append((h, t_query))

    print(f"Generated {len(query_hashes)} hashes from query audio.")

    conn = get_connection()
    cursor = conn.cursor()

    offset_histogram = defaultdict(lambda: defaultdict(int))

    print("Matching hashes with DB...")
    for h, t_query in query_hashes:
        cursor.execute(
            "SELECT time_in_song, song_name FROM fingerprints WHERE hash = ?", (h,)
        )
        for t_db, song_name in cursor.fetchall():
            offset = t_query - t_db
            offset_histogram[song_name][offset] += 1

    conn.close()

    print("Finding best match...")

    best_match = None
    best_score = 0
    best_offset = 0

    for song_name, offsets in offset_histogram.items():
        for offset, count in offsets.items():
            if count > best_score:
                best_score = count
                best_match = song_name
                best_offset = offset

    if best_match:
        time_in_sec = round(best_offset * hop_size / sample_rate, 2)
        mins = int(time_in_sec // 60)
        secs = int(time_in_sec % 60)
        print(f"Match: '{best_match}' — confidence: {best_score} matching hashes")
        return best_match, time_in_sec, best_score
    else:
        print("No match found.")
        return None, None, 0
