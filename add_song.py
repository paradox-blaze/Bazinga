from db import get_connection
from fingerprinting import fingerprint


def add_song():
    path = input(
        "Enter the path of the song you want to add to the fingerprint database: "
    ).strip()
    songname = input(
        "Enter the name of the song you want to add to the database: "
    ).strip()

    conn = get_connection()
    cursor = conn.cursor()
    fingerprint_map = fingerprint(path, songname)
    for HASH, VALUE in fingerprint_map.items():
        for time, song in VALUE:
            cursor.execute(
                "INSERT INTO fingerprints (hash, time_in_song, song_name) VALUES (?, ?, ?)",
                (HASH, time, song),
            )

    print("Fingerprinting done for ", songname)

    conn.commit()
    conn.close()
