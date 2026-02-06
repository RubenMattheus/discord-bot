from src.data.data import Data

class Repository:
    def __init__(self):
        self.data = Data()

    # ---
    # GET
    # ---

    def get_server_ids_music(self):
        result = self.data.get_server_ids_music()
        return result if result is not None else None

    def get_musicchannel(self, id: int):
        result = self.data.get_musicchannel(id)
        return result['musicChannelID'] if result is not None else None
    
    def get_queuemessage(self, id: int):
        result = self.data.get_queuemessage(id)
        return result['queueMessageID'] if result is not None else None

    # ---
    # ADD
    # ---  

    def add_musicqueue(self, id: int, channel_id: int, message_id: int):
        self.data.create_musicqueue(id, channel_id, message_id)
