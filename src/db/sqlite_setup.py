from .connection import Connection

conn = Connection.get_connection()
cursor = conn.get_cursor()

countdown_query = """
CREATE TABLE IF NOT EXISTS countdown (
    serverID INTEGER PRIMARY KEY,
    channelID INTEGER,
    day INTEGER,
    month INTEGER,
    year INTEGER
)"""

music_query = """
CREATE TABLE IF NOT EXISTS music (
    serverID INTEGER PRIMARY KEY,
    channelID INTEGER,
    messageID INTEGER
)"""

todo_query = """
CREATE TABLE IF NOT EXISTS todo (
    serverID INTEGER PRIMARY KEY,
    todo TEXT
)"""

queries = [countdown_query, music_query, todo_query]

for query in queries:
    cursor.execute(query)
    conn.commit

cursor.close()
