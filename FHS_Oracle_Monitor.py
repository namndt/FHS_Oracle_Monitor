# Import from my module
from FHS_WSbase import ServiceBase
from FHS_Logger import ConfigLogger
from FHS_Config import INI_Config
from FHS_L2System import Queries
# Import importance module
import cx_Oracle
from pysnmp.hlapi import *
import psutil
from psutil._common import bytes2human
# Import another util
import socket
from datetime import datetime
from time import sleep
from time import time
import servicemanager
import requests
import logging
from enum import Enum
import sys
import os
import concurrent.futures
import getopt
from collections import namedtuple


class const():
    """List constant value that inside INI file"""
    LINE_NOTIFY_API_URL = 'http://10.199.15.109:8080/api/line/notify.php'
    LINE_TOKEN = 'EifTcZb7XI5P1aefVS9DscyIlQGQCsS8tNe475OwfGX'
    INTERVAL_SECONDS = 0

    SESSIONS_LIMIT_USAGE_PERCENT = 0.00
    PROCESSES_LIMIT_USAGE_PERCENT = 0.00
    SGA_LIMIT_USAGE_PERCENT = 0.00
    PGA_LIMIT_USAGE_PERCENT = 0.00
    MAX_DISK_USE_PERCENT = 0.00

    HOSTNAME = ''
    IP_ADDRESS = ''
    SNMP_COMMUNITY_NAME = ''
    SYSTEM = ''
    MAINTAINER = ''
    ORACLE_SID = ''
    ORACLE_USER = ''
    ORACLE_PASSWORD = ''

    DEBUG = True
    HAS_L3_IP = True


class survey(Enum):
    SESS = 1
    PROC = 2
    SGA = 3
    PGA = 4
    INSTANCE = 5


class WLevel(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class 
(Enum):
    def __str__(self):
        return str(self.value)
    SESS_QUOTA = 'Maximum number of sessions (%) exceeded'
    PROC_QUOTA = 'Maximum number of process (%) exceeded'
    SGA_QUOTA = 'Maximum SGA allocated (%) exceeded'
    PGA_QUOTA = 'Maximum PGA allocated (%) exceeded'
    INSTANCE = 'DataBase Server is Down.'
    DISK_QUOTA = 'Maximum Disk usage (%) exceeded'
    RESTORE = '異常處理完畢'


class LINE_Reporter():
    def send_notify(self, message: str):
        data = {'token': const.LINE_TOKEN, 'message': message}
        try:
            response = requests.post(url=const.LINE_NOTIFY_API_URL, data=data)

            if response.status_code == 200:
                logger.debug('Line Notify has been sent: {}'.format(message.replace('\n', ' ')))
        except Exception as ex:
            logger.exception(f'Send LINE failed: {ex}')

    def abnormal_compose(self, datetime: datetime, level: WLevel, event: Event, msg=''):
        addr = const.IP_ADDRESS if const.HAS_L3_IP else const.IP_ADDRESS + f'\nRelay machine: {socket.gethostname()}'
        message = f"""
●原因: [{event} {msg}]
●系統: {const.SYSTEM}
●設備名稱: {const.HOSTNAME}
●設備位址: {addr}
●維運技師: {const.MAINTAINER}
●嚴重等級: {level.name}
●發生時間: {datetime}
"""
        return message

    def restore_compose(self, restoreTime, event='', msg=''):
        addr = const.IP_ADDRESS if const.HAS_L3_IP else const.IP_ADDRESS + f'\nRelay machine: {socket.gethostname()}'
        message = f"""
●原因: [{event}{msg}]
●系統: {const.SYSTEM}
●設備名稱: {const.HOSTNAME}
●設備位址: {addr}
●維運技師: {const.MAINTAINER}
●復原時間: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
●異常時長: {restoreTime}
"""
        return message


class OracleDatabase():
    '''Running SQL statements in separate threads in Python use threading module'''
    def __init__(self) -> None:
        self.__line__ = LINE_Reporter()
        self.__start__ = 0
        self.__stop__ = 0
        self.isServerDown = None
        self.isProcExceed = None
        self.isSessExceed = None
        self.isPGAExceed = None
        self.isSGAExceed = None

    def __setattr__(self, name: str, value) -> None:
        try:
            if name in ['__line__', '__start__', '__stop__']:
                return super().__setattr__(name, value)
            elif value is None:  # initial flag
                return super().__setattr__(name, False)
            elif self.__getattribute__(name) is True and value is False:
                super().__setattr__('__stop__', datetime.now())
                super().__setattr__(name, value)
                msg = self.__line__.restore_compose(self.abnormal_time_calc(), Event.RESTORE)
                self.__line__.send_notify(msg)
            elif self.__getattribute__(name) is not True and value is True:
                super().__setattr__('__start__', datetime.now())
                super().__setattr__(name, value)
        except Exception as e:
            logger.exception(e)

    def __getattribute__(self, name: str):
        return super().__getattribute__(name)

    def abnormal_time_calc(self):
        return self.__stop__ - self.__start__

    def connect(self):
        '''initial standalone connection with cx_Oracle.connect()'''
        user = const.ORACLE_USER
        password = const.ORACLE_PASSWORD
        dsn = cx_Oracle.makedsn(host=const.HOSTNAME, port=1521, service_name=const.ORACLE_SID)
        # Initialize the Oracle client library first. Beacause some system using Oracle Client older version( 11.1 or older)
        if const.DEBUG is False:  # Oracle Client 11.2 is available in developer PC
            try:
                lib_dir = os.path.dirname(sys.executable) + '\\instantclient_11_2'
                cx_Oracle.init_oracle_client(lib_dir=lib_dir)
            except Exception:
                logger.error('Cannot locate a 64-bit Oracle Client library')

        conn = None  # Initial connection. Return None if connect failed
        try:
            conn = cx_Oracle.connect(user=user, password=password, dsn=dsn, mode=cx_Oracle.SYSDBA, encoding='UTF-8', threaded=True)
            logger.debug(f'Connection string: {user}/{password}@{const.HOSTNAME}:1521/{const.ORACLE_SID}')
            self.isServerDown = False
        except cx_Oracle.Error as e:
            error, = e.args
            if error.code == 1017:
                self.__line__.send_notify(f'連不到 [{const.IP_ADDRESS}]。原因為[{user}/{password}]: {error.message}')
                logger.error(f'Code: {error.code}, Message: {error.message}')
            else:  # database is down
                self.isServerDown = True
                logger.error(error.message)
                msg = self.__line__.abnormal_compose(datetime.now().strftime('%Y/%m/%d %H:%M:%S'), WLevel.CRITICAL, Event.INSTANCE)
                self.__line__.send_notify(msg)
        finally:
            return conn

    def execute(self, cursor, query, survey):
        '''https://www.oracle.com/technical-resources/articles/embedded/vasiliev-python-concurrency.html'''
        try:
            cursor.execute(query)
            # to fetch each row of a query as a dictionary
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = namedtuple("ResultQuery", columns)
            data = cursor.fetchall()
            cursor.close()
            self.oradb_EWS(data, survey)
        except Exception as e:
            logger.exception(e)

    def oradb_EWS(self, data, survey: survey):
        '''Early Warning System for unusual happening of Oracle database'''
        now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        if survey == survey.SESS:
            active_sess = float(data[0].ACTIVE_SESSIONS)
            inactive_sess = float(data[0].INACTIVE_SESSIONS)
            max_sess = float(data[0].MAX_SESSIONS)
            percent_usage = round(100 * (active_sess + inactive_sess) / max_sess, ndigits=2)
            if percent_usage >= const.SESSIONS_LIMIT_USAGE_PERCENT:
                self.isSessExceed = True
                msg_to_send = self.__line__.abnormal_compose(now, WLevel.WARNING, Event.SESS_QUOTA, f'- {percent_usage}%')
                self.__line__.send_notify(message=msg_to_send)
            else:
                self.isSessExceed = False
            logger.info(f'Active session: {active_sess}, Inactive session: {inactive_sess}, Max session: {max_sess}, Percent: {percent_usage}%')

        elif survey == survey.PROC:
            normal_proc = float(data[0].NORMAL_PROCESS)
            background_proc = float(data[0].BACKGROUND_PROCESS)
            max_proc = float(data[0].MAX_PROCESSES)
            percent_usage = round(100 * (normal_proc + background_proc) / max_proc, ndigits=2)
            if percent_usage >= const.PROCESSES_LIMIT_USAGE_PERCENT:
                self.isProcExceed = True
                msg_to_send = self.__line__.abnormal_compose(now, WLevel.WARNING, Event.PROC_QUOTA, f'- {percent_usage}%')
                self.__line__.send_notify(message=msg_to_send)
            else:
                self.isProcExceed = False
            logger.info(f'Normal progress: {normal_proc}, Background progress: {background_proc}, Max progress: {max_proc}, Percent: {percent_usage}%')

        elif survey == survey.PGA:
            pgadict = {row.NAME.lower(): row.VALUE for row in data}
            pga_usage = float(pgadict['total pga inuse'])
            pga_max = float(pgadict['aggregate pga target parameter'])
            percent_usage = round(100 * (pga_usage / pga_max), ndigits=2)
            if percent_usage >= const.PGA_LIMIT_USAGE_PERCENT:
                self.isPGAExceed = True
                msg_to_send = self.__line__.abnormal_compose(now, WLevel.CRITICAL, Event.PGA_QUOTA, f'- {percent_usage}%')
                self.__line__.send_notify(message=msg_to_send)
            else:
                self.isPGAExceed = False
            logger.info(f'PGA usage: {pga_usage}, Max PGA: {pga_max}, Percent: {percent_usage}%')

        elif survey == survey.SGA:
            sga_usage = float(data[0].SGA_USAGE_IN_MB)
            sga_max = float(data[0].SGA_MAX_SIZE)
            percent_usage = round(100 * (sga_usage / sga_max), ndigits=2)
            if percent_usage >= const.SGA_LIMIT_USAGE_PERCENT:
                self.isSGAExceed = True
                msg_to_send = self.__line__.abnormal_compose(now, WLevel.CRITICAL, Event.SGA_QUOTA, f'- {percent_usage}%')
                self.__line__.send_notify(message=msg_to_send)
            else:
                self.isSGAExceed = False
            logger.info(f'SGA usage: {sga_usage}, Max SGA: {sga_max}, Percent: {percent_usage}%')

        elif survey == survey.INSTANCE:
            inst_status = data[0].STATUS.upper()
            db_status = data[0].DATABASE_STATUS.upper()
            if inst_status != 'OPEN' or db_status != 'ACTIVE':
                self.isServerDown = True
                msg_to_send = self.__line__.abnormal_compose(now, WLevel.CRITICAL, Event.INSTANCE, f'\nInstance status: {inst_status}\nDB status: {db_status}')
                self.__line__.send_notify(message=msg_to_send)
            else:
                self.isServerDown = False
            logger.info(f'Instance name: {data[0].INSTANCE_NAME}, Status: {inst_status}, Database status: {db_status}, Active state: {data[0].ACTIVE_STATE}, Blocked: {data[0].BLOCKED}')


class OSUtil():
    def __init__(self):
        self.__line__ = LINE_Reporter()

    def hard_drive_monitor(self):
        try:
            if const.HAS_L3_IP:
                for part in psutil.disk_partitions(all=False):
                    if os.name == 'nt':  # Windows OS
                        if 'cdrom' in part.opts or part.fstype == '':  # skip cd-rom drives with no disk in it
                            continue
                        usage = psutil.disk_usage(part.mountpoint)
                        self.hdrive_EWS(part.mountpoint, usage=usage, snmp=False)
            else:  # Use pySNMP to send GET command.
                self.hrStorage_snmp()
        except Exception as e:
            logger.exception(e)

    def hrStorage_snmp(self):
        '''Using pysnmp send walk command, OID more info at https://cric.grenoble.cnrs.fr/Administrateurs/Outils/MIBS/?oid=1.3.6.1.2.1.25'''
        storageList = self.snmpwalk('1.3.6.1.2.1.25.2.3.1')  # Equivalent to HOST-RESOURCES-MIB::hrStorageEntry
        # Get hrStorageFixedDisk which its hrStorageType is HOST-RESOURCES-MIB::hrStorageTypes.4 (1.3.6.1.2.1.25.2.1.4)
        try:
            fixedDisks = [x.split('=')[0][-1:] for x in storageList if '1.3.6.1.2.1.25.2.1.4' in x]
            for fdisk in fixedDisks:
                name = [x.split('=')[1] for x in storageList if f'SNMPv2-SMI::mib-2.25.2.3.1.3.{fdisk}' in x][0]   # HOST-RESOURCES-MIB::hrStorageDescr
                unit = [x.split('=')[1] for x in storageList if f'SNMPv2-SMI::mib-2.25.2.3.1.4.{fdisk}' in x][0]   # HOST-RESOURCES-MIB::hrStorageAllocationUnits in bytes
                total_in_unit = [x.split('=')[1] for x in storageList if f'SNMPv2-SMI::mib-2.25.2.3.1.5.{fdisk}' in x][0]  # HOST-RESOURCES-MIB::hrStorageSize
                used_in_unit = [x.split('=')[1] for x in storageList if f'SNMPv2-SMI::mib-2.25.2.3.1.6.{fdisk}' in x][0]   # HOST-RESOURCES-MIB::hrStorageUsed

                used_GB = float(bytes2human(float(used_in_unit) * float(unit))[:-1])
                total_GB = float(bytes2human(float(total_in_unit) * float(unit))[:-1])
                self.hdrive_EWS(deviceName=name, used=used_GB, total=total_GB, snmp=True)
        except Exception as e:
            logger.exception(e)

    def snmpwalk(self, OID) -> list:
        logger.info(f'SNMP send request to {const.HOSTNAME}:161, oid: {OID}')
        list_return = []
        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(const.SNMP_COMMUNITY_NAME),
            UdpTransportTarget((const.HOSTNAME, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(OID)),
            lexicographicMode=False, lookupMib=True
        ):

            if not errorIndication and not errorStatus:
                for varBind in varBinds:
                    result = '='.join([x.prettyPrint() for x in varBind])
                    list_return.append(result)
            else:
                logger.error(errorIndication)
                logger.error('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex) - 1] if errorIndex else '?'))

        return list_return

    def hdrive_EWS(self, deviceName, usage: psutil._common.sdiskusage = None, total=None, used=None, snmp=False):
        '''Early Warning System for Disk quota exceeded'''
        isQuotaExceeded = False
        if snmp:
            percent = round(100 * (used / total), 2)
            if percent >= const.MAX_DISK_USE_PERCENT:
                isQuotaExceeded = True
            logger.info(f'Hard Drive Monitor: name({deviceName}), used({used}G), total({total}G), percent({percent}%)')  # Gigabyte unit default
        else:
            if usage.percent >= const.MAX_DISK_USE_PERCENT:
                isQuotaExceeded = True
            logger.info(f'Hard Drive Monitor: name({deviceName}), used({bytes2human(usage.used)}G), total({bytes2human(usage.total)}G), percent({usage.percent}%)')

        if isQuotaExceeded:
            now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            message = self.__line__.abnormal_compose(
                datetime=now, level=WLevel.WARNING, event=Event.DISK_QUOTA,
                msg=f'- {round(100 * (used / total), 2) if usage is None else usage.percent}%\nDisk name: {deviceName}'
            )
            self.__line__.send_notify(message)


class FHS_Service(ServiceBase):
    # Define service information
    _svc_name_ = 'FHS_Oracle_Monitor'
    _svc_display_name_ = 'FHS_Oracle_Monitor'
    _svc_description_ = '針對熱軋和線棒廠L2系統的Oracle資料庫進行監控'

    is_service_alive = False
    __line__ = LINE_Reporter()

    def start(self):
        apply_config()
        logger.debug(
            '\n---------FHS Oracle services---------\n'
            f'Service Name: {self._svc_name_}\n'
            f'Display Name: {self._svc_display_name_}\n'
            f'Description : {self._svc_description_}\n'
            '-------------------------------------'
        )
        logger.info('L2 Oracle Monitor had been started')
        self.__line__.send_notify('L2 Oracle Monitor had been started!')
        self.is_service_alive = True

    def stop(self):
        logger.critical('L2 Oracle Monitor had been stopped')
        self.__line__.send_notify('L2 Oracle Monitor had been stopped!')
        self.is_service_alive = False

    def main(self):
        start = time()
        osutil = OSUtil()
        orac = OracleDatabase()
        dbconn = None
        while self.is_service_alive:
            try:
                dbconn = orac.connect()
                if dbconn is not None:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        for i, query in enumerate(Queries.items()):
                            cursor = dbconn.cursor()
                            executor.submit(orac.execute, cursor, query[1], survey(i + 1))
                    # Disk space monitor
                osutil.hard_drive_monitor()
                sleep(const.INTERVAL_SECONDS - ((time() - start) % const.INTERVAL_SECONDS))
            except Exception as e:
                logger.exception(e)
            finally:
                if dbconn is not None:
                    dbconn.close()


def apply_config():
    # _config_ = INI_Config(fileName='FHS_Oracle_Monitor.ini')
    try:
        const.HOSTNAME = _config_.read('SETTING', 'target_hostname')
        const.LINE_TOKEN = _config_.read('LINE_NOTIFY', 'line_token')
        const.INTERVAL_SECONDS = float(_config_.read('LINE_NOTIFY', 'interval_seconds'))

        const.IP_ADDRESS = _config_.read(const.HOSTNAME, 'ip_address')
        const.SYSTEM = _config_.read(const.HOSTNAME, 'system')
        const.MAINTAINER = _config_.read(const.HOSTNAME, 'maintainer')
        const.HAS_L3_IP = True if '10.199' in const.IP_ADDRESS or '10.198' in const.IP_ADDRESS else False

        const.ORACLE_SID = _config_.read(const.HOSTNAME, 'oracle_sid')
        const.ORACLE_USER = _config_.read(const.HOSTNAME, 'oracle_user')
        const.ORACLE_PASSWORD = _config_.read(const.HOSTNAME, 'oracle_password')

        const.SESSIONS_LIMIT_USAGE_PERCENT = float(_config_.read('SETTING', 'n_sessions_used_percent_limit'))
        const.PROCESSES_LIMIT_USAGE_PERCENT = float(_config_.read('SETTING', 'n_processes_used_percent_limit'))
        const.SGA_LIMIT_USAGE_PERCENT = float(_config_.read('SETTING', 'm_SGA_usage_u_limit'))
        const.PGA_LIMIT_USAGE_PERCENT = float(_config_.read('SETTING', 'm_PGA_usage_u_limit'))
        const.MAX_DISK_USE_PERCENT = float(_config_.read('SETTING', 'p_disk_usage_percent_max'))
        const.SNMP_COMMUNITY_NAME = _config_.read('SETTING', 'snmp_communityName')
    except Exception as ex:
        logger.exception(f'INI config failed: {ex}')


if __name__ == '__main__':
    ConfigLogger()
    logger = logging.getLogger(__name__)

    _config_ = INI_Config(fileName='FHS_Oracle_Monitor.ini')
    opts, args = getopt.getopt(sys.argv[1:], shortopts="", longopts=["target=", "password=", "username=", "startup=", "perfmonini=", "perfmondll=", "interactive", "wait="])
    for opt, val in opts:
        if opt == '--target':
            if _config_.is_exist() is False:
                _config_.make_new_file(target=val)

    if len(sys.argv) == 1:  # by pass error 1503
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FHS_Service)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        FHS_Service.parse_command_line(FHS_Service)
