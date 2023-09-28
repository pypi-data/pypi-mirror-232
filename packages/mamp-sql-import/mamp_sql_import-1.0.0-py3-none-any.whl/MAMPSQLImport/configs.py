import os
import json
import pkg_resources

mysqldump_path = '/Applications/MAMP/library/bin/mysqldump'
mysql_path = '/Applications/MAMP/library/bin/mysql'
mysql_user = 'root'
mysql_pass = 'yourrootpassword'
mysql_host = 'localhost'

backup_dir = pkg_resources.resource_filename('MAMPSQLImport', 'backups/')
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

dbs_dir = pkg_resources.resource_filename('MAMPSQLImport', 'dbs/')
if not os.path.exists(dbs_dir):
    os.makedirs(dbs_dir)
