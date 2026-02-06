import sqlite3

class Connection:
    _instance = None

    def __init__(self, db_path='database.db'):
        if Connection._instance is not None:
            raise Exception("Use get_connection() to get the connection")
        self.db_path = db_path
        self.mydb = sqlite3.connect(self.db_path)
        self.mydb.row_factory = sqlite3.Row

    @classmethod
    def get_connection(cls, db_path='database.db'):
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance
    
    def get_db(self):
        return self.mydb
    
    def get_cursor(self):
        return self.mydb.cursor()
    
    def commit(self):
        self.mydb.commit()
    
    def close_connection(self):
        if self.mydb:
            self.mydb.close()
            Connection._instance = None
