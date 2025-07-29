import os
import tempfile
import time

import sounddevice as sd
from scipy.io.wavfile import write

from add_song import add_song
from db import initialize_db
from match import match


def record_snippet(duration=10, sample_rate=8000):
    print(f"\n Recording for {duration} seconds...")

    recording = sd.rec(
        int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16"
    )
    sd.wait()

    temp_path = tempfile.mktemp(prefix="query_", suffix=".wav", dir=".")
    write(temp_path, sample_rate, recording)

    print(f"Recording saved to {temp_path}")
    return temp_path


def query_from_file():
    path = input("Enter the path of the audio query file: ").strip()

    if not os.path.isfile(path):
        print("Error: File does not exist.")
        return

    match(path)


def query_from_recording():
    temp_path = record_snippet()
    time.sleep(0.5)
    match(temp_path)
    os.remove(temp_path)


def main():
    initialize_db()

    while True:
        print("\nWelcome to Bazinga!")
        print("Choose an option:")
        print("  [a] Add a new song to the fingerprint database")
        print("  [q] Query a song snippet from a file")
        print("  [r] Record live audio and query it")
        print("  [x] Exit")

        choice = input("\nEnter your choice (a/q/r/x): ").strip().lower()

        if choice == "a":
            add_song()
        elif choice == "q":
            query_from_file()
        elif choice == "r":
            query_from_recording()
        elif choice == "x":
            print("Exiting...")
            break
        else:
            print("Invalid input! Please enter 'a', 'q', 'r', or 'x'.")


if __name__ == "__main__":
    main()
