from connection import Connection

conn = Connection.get_connection()
cursor = conn.get_cursor()

table_music_query = """
CREATE TABLE IF NOT EXISTS music (
    serverID INTEGER PRIMARY KEY,
    musicChannelID INTEGER,
    queueMessageID INTEGER)
"""

queries = [table_music_query]

for query in queries:
    cursor.execute(query)
    conn.commit

cursor.close()
