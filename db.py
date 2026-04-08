import sqlite3

DB_PATH = "pets.db"


def _init():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                user_id TEXT PRIMARY KEY,
                pet_name TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                health INTEGER DEFAULT 100,
                hunger INTEGER DEFAULT 0,
                happiness INTEGER DEFAULT 100,
                last_interaction TEXT
            )
        """)
        conn.commit()


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_pet(user_id: str):
    with _connect() as conn:
        return conn.execute(
            "SELECT * FROM pets WHERE user_id = ?", (user_id,)
        ).fetchone()


def create_pet(user_id: str, pet_name: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO pets (user_id, pet_name) VALUES (?, ?)",
            (user_id, pet_name),
        )
        conn.commit()


def update_pet(user_id: str, **fields) -> None:
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [user_id]
    with _connect() as conn:
        conn.execute(
            f"UPDATE pets SET {set_clause} WHERE user_id = ?", values
        )
        conn.commit()


_init()
