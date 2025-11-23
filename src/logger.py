# -*- coding: utf-8 -*-
""" Simple logger """

from datetime import datetime
import traceback as tb
from inspect import stack
from os import stat
from os.path import isfile, isdir, abspath
from os.path import join as pathjoin, split as pathsplit
from pathlib import Path
from zipfile import ZipFile, ZIP_LZMA
from enum import Enum


IDENT = ' ' * 2
LOG_SEPARATOR = '=' * 100


class LogLevel(Enum):
    """ Log level enum """
    INFO = 1
    DEBUG = 2
    WARN = 3
    WARNING = 3
    ERROR = 4


class Logger:
    """ Logger write logs to file and console with log()
        It also can print traceback with log_trace()
    """

    def __init__(self, logfile='last.log', logroot='logs', silent=False,
                 announce=False):
        self.logfile: str = logfile
        self.silent: bool = silent
        if not logroot:
            logroot = abspath('.')
        self.logpath: str = abspath(pathjoin(logroot, logfile))
        if not isdir(pathsplit(self.logpath)[0]):
            Path(pathsplit(self.logpath)[0]).mkdir(parents=True, exist_ok=True)

        if announce:
            self.log("Logging is active", no_log=True)
        if self.check_logfile():
            with open(self.logpath, 'r', encoding='utf-8') as file:
                line_count = sum(1 for _ in file)
            if line_count <= 4:
                self._create_logfile()
                return
            file_ctime: float = stat(self.logpath).st_ctime
            raw_dt = datetime.fromtimestamp(file_ctime)
            timeformat: str = f'%Y-%m-%d-%H-%M-%S-{raw_dt.microsecond}'
            new_filename: str = raw_dt.strftime(timeformat)
            new_filename += f'.{self.logfile}' if self.logfile != 'last.log'\
                            else '.log'
            new_filepath = Path(pathsplit(self.logpath)[0])
            new_filepath /= (new_filename + '.zip')
            with ZipFile(new_filepath, mode='x',
                         compression=ZIP_LZMA, compresslevel=9) as filezip:
                filezip.write(self.logpath, new_filename)
        self._create_logfile()

    def _create_logfile(self):
        with open(self.logpath, 'w+', encoding='utf-8') as file:
            if file.writable():
                header = f'# Encoding: {file.encoding}\n'
                header += f'# Created: {datetime.now()}\n'
                header += LOG_SEPARATOR + '\n\n'
                file.write(header)
            else:
                raise OSError(f'Error @Logger: {self.logfile}' +
                              'is not writable!')

    def check_logfile(self) -> bool:
        """ Check if logfile exists and creates it if not"""
        return self.logpath and isfile(self.logpath)

    def log(self, msg: str, level=LogLevel.INFO, owner=None, no_log=False):
        """ Log a message """
        if not msg:
            return
        if not isinstance(level, LogLevel):
            level = LogLevel.INFO

        if owner is None:
            owner = ''
            caller = ''
        else:
            owner = '@' + owner
            caller = stack()[1].function
        if caller == 'log_trace':
            caller = stack()[2].function

        skip_names = {'<module>', 'main', 'runcode', 'log', 'log_trace'}
        if caller and not caller.startswith('_') and caller not in skip_names:
            caller = '#' + caller
        else:
            caller = ''

        whole_msg = f"{datetime.now()} [{level.name}] "\
                    f"{owner}{caller}\t: {msg}\n"
        if not self.silent:
            print(whole_msg, end='', flush=True)
        if not self.check_logfile():
            raise FileNotFoundError("Error @Logger: " +
                                    f"no logfile '{self.logfile}' found!")
        if no_log:
            return
        with open(self.logpath, 'a', encoding='utf8') as file:
            if not file.writable():
                raise OSError("Error @Logger:" +
                              f"'{self.logfile}' is not writable!")
            file.write(whole_msg)

    def log_trace(self, msg: str, err=Exception,
                  level=LogLevel.ERROR, owner=None):
        """ Log with trace """
        rawtrace = tb.extract_stack()
        tracelist: list = tb.format_list(rawtrace)
        errtype: str = type(err).__name__
        errname: str = str(err.__name__) if errtype == 'type' else str(errtype)
        header: str = f'\n{IDENT}Traceback (most recent call last):\n{IDENT*2}'
        message = header + (IDENT*2).join(str(i) for i in tracelist
                                          if "log_trace" not in i)
        message += IDENT + errname
        message += ': ' + msg if len(message) > 1 else ''
        message += '\n'
        self.log(message, level, owner)

    def set_silent(self, silent: bool = None):
        """ Switch console print """
        if not isinstance(silent, bool):
            self.silent = not self.silent
        else:
            self.silent = silent

    def get_silent(self):
        """ Getter fo silent"""
        return self.silent


logger = Logger()
log = logger.log
log_trace = logger.log_trace
