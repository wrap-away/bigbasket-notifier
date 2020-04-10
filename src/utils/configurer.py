import os
import configparser


class Configurer:
    def __init__(self, filename: str = "config.ini") -> None:
        self.abs_filename = self.get_abs_filename(filename)
        self.config = configparser.ConfigParser()
        self.config.read(self.abs_filename)
        self.sections = self.config.sections()

    @staticmethod
    def get_abs_filename(filename: str) -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            os.pardir, os.pardir, filename))

    def get_configuration(self, key: str, section: str):
        try:
            return self.config[section][key]
        except KeyError:
            print("key named: {} wasn't provided." % key)
            return False

    def write_configuration(self, key: str, value: str, section: str) -> bool:
        self.config.set(section, key, value)
        with open(self.abs_filename, 'w') as configfile:
            self.config.write(configfile)
            configfile.close()
        return True


config = Configurer()
