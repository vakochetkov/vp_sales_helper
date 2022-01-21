import json
from pathlib import Path

from python_json_config import ConfigBuilder
from constants import PATH_TO_CONFIG


class BotConfig():
    def __init__(self):
        if not Path(PATH_TO_CONFIG).exists():
            self._create()                
        self._load()

    def _create(self):
        with open(Path(PATH_TO_CONFIG), 'w', encoding='utf-8') as file:
            json.dump({ 'chat_id' : None, 'user_map' : None }, file)

    def _load(self):
        builder = ConfigBuilder()
        self.config = builder.parse_config(PATH_TO_CONFIG)

    def save(self):
        with open(Path(PATH_TO_CONFIG), 'w', encoding='utf-8') as file:
            file.write(self.config.to_json())
        
    def reload(self):
        self.save()
        self._load()

    def reset(self):
        self._create()
        self._load()

    @property
    def chat_id(self):
        """ Chat ID """
        return self.config.chat_id

    @chat_id.setter
    def chat_id(self, value):
        self.config.update('chat_id', value)
        self.reload()

    @property
    def user_map(self):
        """ Delivery -> User map """
        if self.config.user_map:
            return self.config.user_map.to_dict()
        else:
            return None

    @user_map.setter
    def user_map(self, value):
        self.config.update('user_map', value)
        self.reload()


config = BotConfig()


if __name__ == "__main__": # TEST
    print("Test config loader")
    #assert config.chat_id == None, "failed"
    #assert config.user_map == None, "failed"
    
    config.chat_id = -123456789
    assert config.chat_id == -123456789, "failed" 

    config.user_map = {
        "test" : ["@name"],
        "тест" : ["@name", "@user", "@тест1"],
        "1234" : ["@1111", "@Us_eR_123"],
    }
    print(config.user_map)
    assert config.user_map["test"][0] == "@name", "failed"
    assert config.user_map["тест"][2] == "@тест1", "failed"
    assert config.user_map["1234"][0] == "@1111", "failed"

    config.reset()
    assert config.chat_id == None, "failed"
    assert config.user_map == None, "failed"