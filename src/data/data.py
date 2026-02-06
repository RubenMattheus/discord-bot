from src.data.connection import Connection

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

    # ---
    # GET
    # ---

    def get_server_ids_music(self):
        query = "SELECT serverID FROM music;"
        return self._execute_query(query)
    
    def get_musicchannel(self, id):
        query = "SELECT musicChannelID FROM music WHERE serverID = ?;"
        return self._execute_query(query, (id,), True)
    
    def get_queuemessage(self, id):
        query = "SELECT queueMessageID FROM music WHERE serverID = ?;"
        return self._execute_query(query, (id,), True)
    
    # ---
    # CREATE
    # ---

    def create_musicqueue(self, server_id, channel_id, message_id):
        query = "INSERT OR REPLACE INTO music (serverID, musicChannelID, queueMessageID) VALUES (?, ?, ?)"
        self._execute_query(query, (server_id, channel_id, message_id))
