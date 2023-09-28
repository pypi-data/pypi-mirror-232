import os
import glob
import urllib.parse
import pyodbc
import sys
import time
import boto3
from boto3.session import Session
from datetime import datetime


class AWSStorage():
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, logger=None):
        self.s3 = None
        self.conn = None
        self.connection_string = None
        self.time = None

        if logger:
            self.logger = logger
        else:
            self.logger = None

        if aws_access_key_id and aws_secret_access_key:
            self.connect(aws_access_key_id, aws_secret_access_key)

    def log(self, input_str, level=None):
        ident = "[AWS] "
        if not self.logger:
            dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("[" + dt_str + "] " + ident + input_str)
        else:
            self.logger.log(input_str, level)

    def timer_start(self):
        self.time = time.time()

    def timer_stop(self):
        t = time.time()
        i = t - self.time
        txt = "{:.3f}".format(i)
        self.log(F"Finished in {txt}s")
        return txt

    def connect(self, aws_access_key_id, aws_secret_access_key):
        self.log("Connecting to S3")
        try:
            self.s3 = boto3.client("s3",
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key,
                                   use_ssl=True)
            self.log("S3 : Session authenticated.")
        except Exception as e:
            self.log("S3 : Cannot authenticate session.")

    def upload(self, bucket_name, filename, destination=None):
        try:
            target_name = ""
            if not destination:
                target_name = os.path.basename(filename)
            elif destination.endswith("/"):
                target_name = destination + os.path.basename(filename)
            else:
                target_name = destination

            self.log(F"Upload {filename} to bucket '{bucket_name}'")
            self.log(F"Destination = s3://{bucket_name}/{target_name}")
            self.s3.upload_file(filename, bucket_name, target_name)
            self.log(F"Success")

        except Exception as e:
            self.log(f"Error: {str(e)}")

    def upload_recursive(self, bucket_name, source_path, destination_path):
        try:
            if not destination_path.endswith("/"):
                destination_path += "/"

            for source_file in glob.glob(os.path.join(source_path, '**/*'), recursive=True):
                if os.path.isfile(source_file):
                    relative_path = os.path.relpath(source_file, source_path)
                    destination_file = os.path.join(destination_path, relative_path)
                    self.upload(bucket_name, source_file, destination_file)

        except Exception as e:
            self.log(f"Error: {str(e)}")

    def set_redshift_connection(self, cs):
        self.connection_string = cs

    def redshift_connect(self, cs=None):
        if cs:
            self.connection_string = cs
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.log("Connect to database successfully.")
        except:
            self.log("Cannot connect to database")
            sys.exit(-1)

    def redshift_execute(self, sql_command):
        self.timer_start()
        self.log(F"Using {sql_command}")
        cursor = self.conn.cursor()
        cursor.execute(sql_command)
        cursor.commit()
        cursor.close()
        self.timer_stop()

    def redshift_copy(self, table_name, s3_name, plain_text=None):
        if plain_text:
            gzip_string = ""
        else:
            gzip_string = "GZIP"
        self.timer_start()
        sql_command = F"""
        COPY {table_name}
        FROM '{s3_name}'
        credentials 'aws_access_key_id={self.aws_access_key_id};aws_secret_access_key={self.aws_secret_access_key}'
        DELIMITER '\t' CSV {gzip_string} IGNOREHEADER 1;
        """
        self.log(F"Using {sql_command}")
        cursor = self.conn.cursor()
        cursor.execute(sql_command)
        cursor.commit()
        cursor.close()
        self.timer_stop()

    def redshift_disconnect(self):
        self.conn.close()


if __name__ == "__main__":
    pass
