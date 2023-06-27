import json

class Settings:
    '''Load the settings from the json file'''

    def __init__(self, json_path):
        self.json_path = json_path
        self.data = json.load(open(json_path, "r"))

    def basic(self, key):
        return self.data["basic"][key]
    
    def notification_draw(self, key):
        return self.data["notification_draw"][key]
    
    def colors(self, key):
        return self.data["colors"][key]