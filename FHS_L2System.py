from sys import executable
from sys import exit
import os.path
from configparser import RawConfigParser


L2OraSystem = {
    'HT-CY-SVR01': {
        'system': '熱軋廠-鋼捲庫',
        'os': 'nt',
        'ip_address': '10.199.136.51',
        'maintainer': ['阮玉太', '黎友進'],
        'oracle_sid': 'HATINH',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM'
    },
    'HT-SY-SVR01': {
        'system': '熱軋廠-板胚庫',
        'os': 'nt',
        'ip_address': '10.199.136.1',
        'maintainer': ['楊明玉', '阮玉太'],
        'oracle_sid': 'HATINH',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM'
    },
    'L2SCC01': {
        'system': '熱軋廠-熱軋主線',
        'os': 'nt',
        'ip_address': '10.199.136.21',
        'maintainer': ['鄧文財', '黃清捷'],
        'oracle_sid': 'L2SCC',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM'
    },
    'FCEL2SERVER1': {
        'system': '熱軋廠-加熱爐',
        'os': 'nt',
        'ip_address': '172.22.148.1',
        'maintainer': ['楊文勇', '黎玉仲'],
        'oracle_sid': 'ORCL',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM'
    },
    'L2IFS': {
        'system': '熱軋廠-SPC',
        'os': 'nt',
        'ip_address': '195.1.0.10',
        'maintainer': ['阮友創', '鄧文財'],
        'oracle_sid': 'ORCL',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'APFC01': {
        'system': '熱軋廠-APFC',
        'os': 'nt',
        'ip_address': '192.168.156.3',
        'maintainer': ['黃清捷', '黃氏花'],
        'oracle_sid': 'ORCL',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'RSMSMAIN': {
        'system': '熱軋廠-磨輥間',
        'os': 'nt',
        'ip_address': '10.199.136.42',
        'maintainer': ['陶春位', '阮氏垂江'],
        'oracle_sid': 'ROLLSHOP',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'WINDOWS-51QNQJN': {
        'system': '熱軋廠-精整一號線',
        'os': 'nt',
        'ip_address': '10.199.136.61',
        'maintainer': ['范文功', '阮德原'],
        'oracle_sid': 'HSPMLL2GDB',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'WINDOWS-PDM9KKB': {
        'system': '熱軋廠-精整二號線',
        'os': 'nt',
        'ip_address': '10.199.136.64',
        'maintainer': ['范文功', '阮德原'],
        'oracle_sid': 'HSPMLL2GDB',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'BMER2-SCC1': {
        'system': '線棒廠-開胚線',
        'os': 'nt',
        'ip_address': '10.199.96.82',
        'maintainer': ['陳雄強', '陳德雄'],
        'oracle_sid': 'ORCL',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'BMER2-QCS1': {
        'system': '線棒廠-開胚線',
        'os': 'nt',
        'ip_address': '172.22.3.11',
        'maintainer': ['陳雄強', '陳德雄'],
        'oracle_sid': 'ORCL',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'COML2-SERV01': {
        'system': '線棒廠-複合線',
        'os': 'nt',
        'ip_address': '10.199.112.11',
        'maintainer': ['阮進仕', '何慶南'],
        'oracle_sid': 'FHTCOML2',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'WRML2-SERV01': {
        'system': '線棒廠-高速線',
        'os': 'nt',
        'ip_address': '10.199.112.31',
        'maintainer': ['阮進仕', '何慶南'],
        'oracle_sid': 'FHSWRML2',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'ClmServer': {
        'system': '線棒廠-精整線',
        'os': 'nt',
        'ip_address': '10.199.96.87',
        'maintainer': ['潘氏金芝', '鄧文財'],
        'oracle_sid': 'XE',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'BDMFURL2SRV': {
        'system': '線棒廠-開胚加熱爐',
        'os': 'nt',
        'ip_address': '10.199.96.84',
        'maintainer': ['陳曰林', '鄧文財'],
        'oracle_sid': 'ORCL',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'FurL2Server': {
        'system': '線棒廠-高速加熱爐',
        'os': 'nt',
        'ip_address': '10.199.112.38',
        'maintainer': ['陳曰林', '鄧文財'],
        'oracle_sid': 'HATINH',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'FURL2Server': {
        'system': '線棒廠-複合加熱爐',
        'os': 'nt',
        'ip_address': '10.199.112.18',
        'maintainer': ['陳曰林', '鄧文財'],
        'oracle_sid': 'HATINH',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'HT-LPM-SVR01': {
        'system': '線棒廠-大小鋼胚WMS',
        'os': 'nt',
        'ip_address': '10.199.96.61',
        'maintainer': ['阮誠倫', '黎德英'],
        'oracle_sid': 'HATINH',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'K2B85-DB1': {
        'system': '線棒成品自動倉庫',
        'os': 'nt',
        'ip_address': '192.168.111.11',
        'maintainer': ['阮誠倫', '黎德英'],
        'oracle_sid': 'MCS',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'DB-1': {
        'system': '資材自動倉庫',
        'os': 'posix',
        'ip_address': '10.199.136.51',
        'maintainer': ['阮誠倫', '黎德英'],
        'oracle_sid': 'WMSDB',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    },
    'HTFHSITD1024141': {
        'system': '熱軋主線',
        'os': 'nt',
        'ip_address': '10.198.171.95',
        'maintainer': ['阮庭進南'],
        'oracle_sid': 'ORCL',
        'oracle_user': 'SYSTEM',
        'oracle_password': 'SYSTEM',
    }
}

# SESSIONS AND PROCESSES
# https://docs.oracle.com/cd/B16240_01/doc/doc.102/e16282/oracle_database_help/oracle_database_database_resource_usage_session_usage.html
SESSIONS = """
SELECT
    ACTIVE_SESS.VALUE AS "ACTIVE_SESSIONS",
    INACTIVE_SESS.VALUE AS "INACTIVE_SESSIONS",
    MAX_SESS.VALUE AS "MAX_SESSIONS"
FROM
    (SELECT COUNT(*) VALUE FROM V$SESSION WHERE UPPER(STATUS) = 'ACTIVE') ACTIVE_SESS,
    (SELECT COUNT(*) VALUE FROM V$SESSION WHERE UPPER(STATUS) = 'INACTIVE') INACTIVE_SESS,
    (SELECT VALUE FROM V$PARAMETER WHERE UPPER(NAME) = 'SESSIONS') MAX_SESS
"""

PROCESSES = """
SELECT
    NORMAL_PROC.VALUE AS "NORMAL_PROCESS",
    BACKGROUND_PROC.VALUE AS "BACKGROUND_PROCESS",
    MAX_PROC.VALUE AS "MAX_PROCESSES"
FROM
    (SELECT COUNT(*) VALUE FROM V$PROCESS WHERE BACKGROUND IS NULL) NORMAL_PROC,
    (SELECT COUNT(*) VALUE FROM V$PROCESS WHERE BACKGROUND IS NOT NULL) BACKGROUND_PROC,
    (SELECT VALUE FROM V$PARAMETER WHERE UPPER(NAME) = 'PROCESSES') MAX_PROC
"""

# SGA
SGA_STAT = """
SELECT
    USED.VALUE AS SGA_USAGE_IN_MB,
    FREE.VALUE AS SGA_FREE_IN_MB,
    TOTAL.VALUE AS SGA_MAX_SIZE
FROM
    (SELECT ROUND(SUM(BYTES)/1024/1024, 3) VALUE FROM V$SGASTAT WHERE UPPER(NAME) != 'FREE MEMORY') USED,
    (SELECT ROUND(SUM(BYTES)/1024/1024, 3) VALUE FROM V$SGASTAT WHERE UPPER(NAME)  = 'FREE MEMORY') FREE,
    (SELECT ROUND(VALUE/1024/1024, 3) AS VALUE FROM V$PARAMETER WHERE UPPER(NAME) = 'SGA_MAX_SIZE') TOTAL
"""

# PGA statistics:
# http://www.dba-oracle.com/t_v_pgastat.htm
# https://docs.oracle.com/cd/E18283_01/server.112/e17110/dynviews_2096.htm
# https://docs.oracle.com/database/121/REFRN/GUID-4666F72E-1E2F-4FFF-89C7-E8144657F78A.htm#GUID-4666F72E-1E2F-4FFF-89C7-E8144657F78A__G2030180
PGA_STAT = """
SELECT
    NAME,
    CASE UNIT
        WHEN 'bytes' THEN ROUND(VALUE/1024/1024, 3)
        ELSE VALUE
    END VALUE,
    CASE WHEN UNIT IS NULL THEN 'Times'
        ELSE REPLACE(UNIT, 'bytes', 'MB')
    END UNIT
FROM
    V$PGASTAT
WHERE NAME IN (
    'aggregate PGA target parameter','aggregate PGA auto target',
    'total PGA inuse','total PGA allocated','total freeable PGA memory',
    'over allocation count','cache hit percentage'
    )
"""
PGA_statistics = """
SELECT
    ROUND(SUM(SE1.VALUE/1024/1024), 3) "PGA_CURRENT_SIZE",
    ROUND(SUM(SE2.VALUE/1024/1024), 3) "PGA_MAXIMUM_SIZE"
FROM
    V$SESSTAT SE1, V$SESSTAT SE2, V$SESSION SSN, V$BGPROCESS BGP,
    V$PROCESS PRC, V$STATNAME STAT1, V$STATNAME STAT2
WHERE
    SE1.STATISTIC# = STAT1.STATISTIC# AND STAT1.NAME = 'session pga memory'
AND SE2.STATISTIC#  = STAT2.STATISTIC# AND STAT2.NAME = 'session pga memory max'
AND SE1.SID = SSN.SID
AND SE2.SID = SSN.SID
AND SSN.PADDR = BGP.PADDR (+)
AND SSN.PADDR = PRC.ADDR (+)
"""

# UGA statistics
UGA_statistics = """
SELECT
    ROUND(SUM(SE1.VALUE/1024/1024), 3) "UGA_CURRENT_SIZE",
    ROUND(SUM(SE2.VALUE/1024/1024), 3) "UGA_MAXIMUM_SIZE"
FROM
    V$SESSTAT SE1, V$SESSTAT SE2, V$SESSION SSN, V$BGPROCESS BGP,
    V$PROCESS PRC, V$STATNAME STAT1, V$STATNAME STAT2
WHERE
    SE1.STATISTIC# = STAT1.STATISTIC# AND STAT1.NAME = 'session uga memory'
AND SE2.STATISTIC#  = STAT2.STATISTIC# AND STAT2.NAME = 'session uga memory max'
AND SE1.SID = SSN.SID
AND SE2.SID = SSN.SID
AND SSN.PADDR = BGP.PADDR (+)
AND SSN.PADDR = PRC.ADDR (+)
"""

# ORACLE DATABASE SERVER
ORA_INSTANCE = """
SELECT
    INSTANCE_NAME, HOST_NAME, STATUS,
    INSTANCE_ROLE, DATABASE_STATUS,
    ACTIVE_STATE, BLOCKED
FROM
    V$INSTANCE
"""

Queries = {
    'SESSIONS': SESSIONS,
    'PROCESSES': PROCESSES,
    'SGA': SGA_STAT,
    'PGA': PGA_STAT,
    'INSTANCE': ORA_INSTANCE
}

if __name__ == "__main__":
    rawConfig = RawConfigParser()
    for key in L2OraSystem.keys():
        rawConfig.add_section(key)
        for key1 in L2OraSystem[key]:
            rawConfig.set(key, key1, L2OraSystem[key][key1])
    with open(r'D:\SVN_WorkingDir\FHS_Oracle_Monitor\test.ini', mode='w', encoding='UTF-8') as configFile:
        rawConfig.write(configFile)
