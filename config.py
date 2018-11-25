# A.Piskun
# 07/11/2018
#
#


class Config:
    def __init__(self):
        self.config = None

    def configure(self, config):
        self.config = config

    def get_config(self):
        return self.config

    def set(self, key, value):
        self.config[key] = value


def init_from_json(path):
    import json
    with open(path, encoding="utf-8") as f:
        config_class.configure(json.load(f))


def get(key):
    return config_class.get_config().get(key)


def set(key, value):
    return config_class.set(key, value)


config_class = Config()
