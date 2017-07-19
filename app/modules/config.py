import codecs
import yaml

def read_config(filepath):
    # read configuration file
    config = {}
    with codecs.open('config.yml', 'r', encoding='utf8') as f:
        yml_dict = yaml.safe_load(f)
        for k in yml_dict:
            config[k] = yml_dict[k]

    return config