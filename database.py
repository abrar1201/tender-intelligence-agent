import sqlite3

DB_NAME = "tenders.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
       CREATE TABLE IF NOT EXISTS tenders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            link TEXT UNIQUE,
            similarity REAL,
            source TEXT,
            cluster INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_tender(tender):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute("""
            INSERT OR IGNORE INTO tenders
            (title, description, link, similarity, source, cluster)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tender["title"],
            tender["description"],
            tender["link"],
            tender["similarity"],
            tender.get("source"),
            tender.get("cluster")
        ))

        conn.commit()
    except Exception as e:
        print("DB error:", e)

    conn.close()
