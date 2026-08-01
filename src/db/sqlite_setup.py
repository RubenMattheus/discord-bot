from .connection import Connection

COUNTDOWN_QUERY = """
CREATE TABLE IF NOT EXISTS countdown (
    serverID INTEGER PRIMARY KEY,
    channelID INTEGER,
    day INTEGER,
    month INTEGER,
    year INTEGER
)"""

MUSIC_QUERY = """
CREATE TABLE IF NOT EXISTS music (
    serverID INTEGER PRIMARY KEY,
    channelID INTEGER,
    messageID INTEGER
)"""

TODO_QUERY = """
CREATE TABLE IF NOT EXISTS todo (
    serverID INTEGER PRIMARY KEY,
    todo TEXT
)"""

def create_tables():
    """ Create the database tables if they don't already exist """
    conn = Connection.get_connection()
    cursor = conn.get_cursor()
    for query in (COUNTDOWN_QUERY, MUSIC_QUERY, TODO_QUERY):
        cursor.execute(query)
        conn.commit()
    cursor.close()
