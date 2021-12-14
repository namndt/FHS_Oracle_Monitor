from sys import executable
from sys import exit
import os.path
from FHS_L2System import L2OraSystem
from configparser import ConfigParser
from configparser import RawConfigParser


class INI_Config():
    def __init__(self, fileName):
        self.__config = RawConfigParser()
        if fileName is not None:
            self.__fileName = fileName
            self.__filePath = os.path.join(os.path.dirname(executable), self.__fileName)

    def is_exist(self):
        return os.path.isfile(self.__filePath)

    def read(self, section, key):
        self.__config.read(self.__filePath, encoding='UTF-8')

        value = self.__config.get(section=section, option=key)
        return value

    def make_new_file(self, target):
        __config = RawConfigParser()
        __config['LINE_NOTIFY'] = {
            'line_token': 'EifTcZb7XI5P1aefVS9DscyIlQGQCsS8tNe475OwfGX',
            'interval_seconds': 60
        }
        __config['SETTING'] = {
            'n_sessions_used_percent_limit': 90,
            'n_processes_used_percent_limit': 90,
            'p_disk_usage_percent_max': 85,
            'm_SGA_usage_u_limit': 90,
            'm_PGA_usage_u_limit': 90,
            'snmp_communityName': 'public',
            'target_hostname': f'{target}'
        }
        for host in L2OraSystem.keys():
            if host == target.upper():
                __config.add_section(host)
                for opt in L2OraSystem[host]:
                    __config.set(host, opt, L2OraSystem[host][opt])
        with open(self.__filePath, mode='w', encoding='UTF-8') as configFile:
            __config.write(configFile)


if __name__ == "__main__":
    print('run config')
    config = INI_Config(fileName='FHS_L2System.ini')
