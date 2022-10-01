from configparser import RawConfigParser

instance_config = RawConfigParser()
instance_config.optionxform = str
instance_config.read('instance.ini')
instance = instance_config['DEFAULT']


def instance_data():
    return {key: value for key, value in instance.items()}
