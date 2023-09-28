import jaydebeapi as jdbc
import pandas as pd
import os, sys
import codecs
import sys
import time
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


class JDBCHelper():

    def __init__(self, dict_cs=None, logger=None):
        if dict_cs:
            self.connection_string = dict_cs
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
        ident = "[JDBC-HELPER]"
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

    #########################
    ### CONNECTION_STRING ###
    #########################

    def set_connection_string(self, cs):
        self.connection_string = cs

    def set_cs(self, cs):
        self.connection_string = cs

    def connect(self, dict_cs=None):
        if dict_cs:
            self.connection_string = dict_cs
        try:
            dict_cstr = self.connection_string
            self.conn = jdbc.connect(dict_cstr["class"], dict_cstr["jdbc"],
                                     [dict_cstr["user"], dict_cstr["pass"]], dict_cstr["driver"])
            self.log("Connect to database successfully.")
        except Exception as e:
            self.log("Cannot connect to database", "ERROR")
            self.log(str(e), "ERROR")
            sys.exit(-1)

    def close(self):
        self.conn.close()

    #########################
    ### HELPER FUNCTION ###
    #########################

    def count_records(self, sql_command):
        self.log(f"Count records using: {sql_command}")
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_command)
            row = cursor.fetchone()
            cnt = row[0]
            cnt_str = '{:,}'.format(cnt)
            cursor.close()
            self.log(f"Records count: {str(cnt_str)}")
        except Exception as e:
            cnt = None
            self.log(f"str(e)", "ERROR")
        return cnt

    def execute(self, sql_command):
        sql_txt = sql_command.replace("\r", " ").replace("\n", " ").replace("\t", " ").strip()
        self.log(F"Using: {sql_txt}")
        self.timer_start()
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_command)
            cursor.commit()
            cursor.close()
        except Exception as e:
            self.log(F"{str(e)}", "ERROR")
            cursor.rollback()
            cursor.close()
        txt = self.timer_stop()
        return txt


    def execute_full(self, sql_command, with_result=None):
        sql_txt = sql_command.replace("\r", " ").replace("\n", " ").replace("\t", " ").strip()
        self.log(F"Using: {sql_txt}")
        self.timer_start()
        r = 0
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_command)
            if with_result:
                row = cursor.fetchone()
                self.log("Sample Data")
                r = row[0]
                self.log(F"{str(row)}")
            cursor.close()
        except Exception as e:
            self.log(F"{str(e)}", "ERROR")
            cursor.close()
        txt = self.timer_stop()
        return txt


    def query(self, query_str):
        df = pd.read_sql_query(query_str, self.conn)
        print(df)
