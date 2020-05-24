from configparser import ConfigParser
import os


class SriftConfig():
    def __init__(self):
        self.config_path = 'config/config.ini'

        if not os.path.isfile(self.config_path):
            print(f'Config does not exist: Creating one in {self.config_path}')
            self.config = ConfigParser()
            self.config.add_section('discord')
            self.config.set('discord', 'token', 'your discord bot token')
            self.config.add_section('mongoengine')
            self.config.set('mongoengine', 'db', 'srift')
            self.config.set('mongoengine', 'host', 'localhost')
            self.config.set('mongoengine', 'port', '27017')

            os.makedirs(self.config_path[:-11])
            with open(self.config_path, 'w') as f:
                self.config.write(f)

    def getParsedConfig(self):
        cfg = ConfigParser()
        cfg.read(self.config_path)
        return cfg
