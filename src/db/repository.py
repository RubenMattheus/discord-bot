from .data import Data

class Repository:
    def __init__(self):
        self.data = Data()

    """
    Countdown
    """
    def add_countdown(self, server_id: int, channel_id: int, day: int, month: int, year: int):
        self.data.insert_countdown(server_id, channel_id, day, month, year)

    def remove_countdown(self, server_id: int):
        self.data.delete_countdown(server_id)

    def get_countdowns(self):
        result = self.data.select_countdowns()
        return result if result is not None else None

    """
    Music
    """
    def add_musicqueue(self, id: int, channel_id: int, message_id: int):
        self.data.insert_musicqueue(id, channel_id, message_id)

    def get_server_ids_music(self):
        result = self.data.select_server_ids_music()
        return result if result is not None else None

    def get_musicchannel(self, id: int):
        result = self.data.select_musicchannel(id)
        return result['channelID'] if result is not None else None
    
    def get_queuemessage(self, id: int):
        result = self.data.select_queuemessage(id)
        return result['messageID'] if result is not None else None

    """
    Todo list
    """
    def add_todo(self, server_id: int, todo: str):
        self.data.insert_todo(server_id, todo)

    def get_todo(self, server_id: int):
        result = self.data.select_todo(server_id)
        return result if result is not None else None
