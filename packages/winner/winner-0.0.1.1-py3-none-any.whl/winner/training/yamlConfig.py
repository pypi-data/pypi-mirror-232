

import yaml
from yaml.loader import SafeLoader

def GetConfig(config_file_path):
    """Get config"""
    config = Config()
    config.read_config(config_file_path)
    return config

class Config:
    def __init__(self, title, train, eval, owner=None, author=None):
        self.title = title
        self.train = train
        self.eval = eval
        self.owner = owner
        self.author = author

    def read_config(self, config_file_path):
        """Read config file"""
        with open(config_file_path, "r") as file:
            config = yaml.load(file, Loader=SafeLoader)
        self._set_config(config)
        return config

    def _set_config(self, config):
        """Set config"""
        self.title = config["title"]
        self.train = config["train"]
        self.eval = config["eval"]
        self.owner = config["owner"]
        self.author = config["author"]

    def write_config(self, config_file_path):
        """Write config file"""
        config = self._get_config()
        with open(config_file_path, "w") as file:
            yaml.dump(config, file)

    def _get_config(self):
        pass

    def __repr__(self):
        return f"Config(title={self.title}, train={self.train}, eval={self.eval}, owner={self.owner}, author={self.author})"
    
