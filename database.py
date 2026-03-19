import sqlite3
import hashlib
from urllib.parse import urlparse

DB_NAME = "tenders.db"


def init_db():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS tenders(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE,
        title TEXT,
        link TEXT,
        description TEXT,
        source TEXT,
        domain TEXT,
        similarity REAL

    )

    """)

    conn.commit()
    conn.close()


def generate_hash(tender):

    key = f"{tender.get('title')} {tender.get('link')}"

    return hashlib.md5(key.encode()).hexdigest()


def save_tender(tender):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    h = generate_hash(tender)

    domain = urlparse(tender.get("link", "")).netloc

    try:

        cursor.execute("""

        INSERT INTO tenders
        (hash,title,link,description,source,domain,similarity)

        VALUES (?,?,?,?,?,?,?)

        """, (

            h,
            tender.get("title"),
            tender.get("link"),
            tender.get("description"),
            tender.get("source"),
            domain,
            tender.get("similarity")

        ))

        conn.commit()

    except:
        pass

    conn.close()