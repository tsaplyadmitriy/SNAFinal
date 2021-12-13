import os

import yaml


class YamlReader:
    def __init__(self, filename):
        self.filename = 'account/management/commands/resources/' + filename

    def get(self, line):
        with open(self.filename, 'r') as f:
            yaml_data = yaml.load(f, Loader=yaml.FullLoader)

        return yaml_data[line]
