import sqlite3

conn = sqlite3.connect("pets.db")
conn.row_factory = sqlite3.Row    # allows dict-style access
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS pets (
    user_id TEXT PRIMARY KEY,
    pet_name TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    health INTEGER DEFAULT 100,
    hunger INTEGER DEFAULT 0,
    happiness INTEGER DEFAULT 100,
    last_interaction TEXT
);
""")

conn.commit()