# ------------------------
# INIT DATABASE
# ------------------------
def init_db():
    import sqlite3

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # ------------------------
    # USERS TABLE
    # ------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    bio TEXT,
    github TEXT,
    linkedin TEXT
)
""")
    
    # ------------------------
    # PORTFOLIO TABLE (FIXED)
    # ------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        description TEXT,
        skills TEXT,
        github TEXT,
        demo TEXT,
        category TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")
    conn.commit()
    conn.close()