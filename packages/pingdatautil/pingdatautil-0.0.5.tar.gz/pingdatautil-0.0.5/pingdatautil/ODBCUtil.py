import pyodbc
import sys
import time
from datetime import datetime
import re


class ODBCUtil():

    def __init__(self, cs=None, logger=None):
        if cs:
            self.connection_string = cs
            self.connect()
        else:
            self.connection_string = None

        self.dialect = "MSSQL"
        self.separator = "\t"
        self.conn = None
        self.time = None
        self.time_start = None
        self.time_end = None

        if logger:
            self.logger = logger
        else:
            self.logger = None

    ###############
    ### LOGGING ###
    ##############

    def log(self, input_str, level=None):
        ident = "[ODBC-HELPER]"
        if not self.logger:
            dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("[" + dt_str + "] " + ident + " " + input_str)
        else:
            self.logger.log(ident + " " + input_str, level)

    def timer_start(self):
        self.log(F"Timer Start")
        self.time = time.time()

    def timer_stop(self):
        t = time.time()
        i = t - self.time
        txt = "{:.3f}".format(i)
        self.log(F"Finished in {txt}s")
        return txt
