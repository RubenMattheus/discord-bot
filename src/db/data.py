from .connection import Connection

class Data:
    def __init__(self):
        self.conn = Connection.get_connection()
        self.cursor = self.conn.get_cursor()

    def _execute_query(self, query, data=None, fetch_one=False):
        cursor = self.conn.get_cursor()
        try:
            if data is None:
                cursor.execute(query)
            else:
                cursor.execute(query, data)
            if query.strip().lower().startswith("select"):
                return cursor.fetchone() if fetch_one else cursor.fetchall()
            self.conn.commit()
        except Exception as e:
            print(f"Database error with query {query}: {e}")
        finally:
            cursor.close()

    """
    Countdown
    """
    def insert_countdown(self, serverid, channelid, day, month, year):
        query = "INSERT OR REPLACE INTO countdown (serverID, channelID, day, month, year) VALUES (?, ?, ?, ?, ?)"
        self._execute_query(query, (serverid, channelid, day, month, year))
    
    def delete_countdown(self, serverid):
        query = "DELETE FROM countdown WHERE serverID = ?;"
        self._execute_query(query, (serverid,))

    def select_countdowns(self):
        query = "SELECT * FROM countdown;"
        return self._execute_query(query)

    """
    Music
    """
    def insert_musicqueue(self, serverid, channel_id, message_id):
        query = "INSERT OR REPLACE INTO music (serverID, channelID, messageID) VALUES (?, ?, ?)"
        self._execute_query(query, (serverid, channel_id, message_id))

    def select_server_ids_music(self):
        query = "SELECT serverID FROM music;"
        return self._execute_query(query)
    
    def select_musicchannel(self, serverid):
        query = "SELECT channelID FROM music WHERE serverID = ?;"
        return self._execute_query(query, (serverid,), True)
    
    def select_queuemessage(self, serverid):
        query = "SELECT messageID FROM music WHERE serverID = ?;"
        return self._execute_query(query, (serverid,), True)

    """
    Todo list
    """
    def insert_todo(self, server_id, todo):
        query = "INSERT OR REPLACE INTO todo (serverID, todo) VALUES (?, ?)"
        self._execute_query(query, (server_id, todo))

    def select_todo(self, server_id):
        query = "SELECT todo FROM todo WHERE serverID = ?;"
        return self._execute_query(query, (server_id,), fetch_one=True)
