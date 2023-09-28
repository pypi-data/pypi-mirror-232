import os
import sys
import json
import importlib
from MAMPSQLImport import configs
import mysql.connector  # Needed to establish MySQL connection

# Define path for a flag file that indicates whether configuration is done
config_flag_path = os.path.join(os.path.expanduser('~'), '.mamp_sql_import_config_done')

def get_config_path():
    # This function finds the absolute path of the configs.py file
    return os.path.abspath(configs.__file__)

def initial_setup():
    print("Setting up MAMP SQL Import...")
    
    # Prompt user for configurations
    mysqldump_path = input("Enter path to mysqldump: ")
    mysql_path = input("Enter path to mysql: ")
    mysql_user = input("Enter MySQL user: ")
    mysql_pass = input("Enter MySQL password: ")
    mysql_host = input("Enter MySQL host (default: localhost): ") or 'localhost'
    
    # Modify configs.py with user's input
    config_content = f"""
mysqldump_path = '{mysqldump_path}'
mysql_path = '{mysql_path}'
mysql_user = '{mysql_user}'
mysql_pass = '{mysql_pass}'
mysql_host = '{mysql_host}'
"""
    with open(get_config_path(), 'w') as config_file:
        config_file.write(config_content)
    
    # Create a flag file indicating configuration is done
    with open(config_flag_path, 'w') as flag_file:
        flag_file.write('done')

# Check if the configuration flag file exists
if not os.path.exists(config_flag_path):
    initial_setup()
else:
    reset = input("Do you want to reset configurations? (yes/no): ").strip().lower()
    if reset == 'yes':
        initial_setup()

# Re-import configs to ensure we get the latest values
importlib.reload(configs)
from MAMPSQLImport.configs import *

# Establish the MySQL connection after the configuration setup
mydb = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_pass
)

mycursor = mydb.cursor()

from MAMPSQLImport.functions import *

database_name = input("Database name: ")

if not database_name:
    print("Please enter a valid database name")
    exit()

db_creation_response = mycursor.execute("CREATE DATABASE IF NOT EXISTS "+database_name)

dbs_to_import = []

for root, dirs, files in os.walk(dbs_dir):
    for file in files:
        dbs_to_import.append(os.path.join(root, file))

for file_path in dbs_to_import:
    if os.path.exists(file_path):
        file_name = os.path.basename(file_path)
        if database_name + ".sql" == file_name:
            import_db(file_path, database_name)
