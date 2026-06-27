from .connection import Connection

CONN = Connection.get_connection()
CURSOR = CONN.get_cursor()

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

queries = [COUNTDOWN_QUERY, MUSIC_QUERY, TODO_QUERY]

for query in queries:
    CURSOR.execute(query)
    CONN.commit()

CURSOR.close()
