import sqlite3

DB_NAME = "tenders.db"


def init_portal_table():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS portals(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT UNIQUE

    )

    """)

    conn.commit()
    conn.close()


def save_portal(domain):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:

        cursor.execute(

            "INSERT INTO portals(domain) VALUES(?)",
            (domain,)
        )

        conn.commit()

    except:
        pass

    conn.close()


def get_portals():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT domain FROM portals")

    portals = [x[0] for x in cursor.fetchall()]

    conn.close()

    return portals