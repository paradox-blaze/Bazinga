import sqlite3

DB_NAME = "fingerprints.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fingerprints (
            hash INTEGER,
            time_in_song INTEGER,
            song_name TEXT
        )
        """
    )

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints(hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_song ON fingerprints(song_name)")

    conn.commit()
    conn.close()
