import yaml

class Config:
    def __init__(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            self.cfg = yaml.safe_load(f)

    def get(self, section, key, default=None):
        return self.cfg.get(section, {}).get(key, default)
