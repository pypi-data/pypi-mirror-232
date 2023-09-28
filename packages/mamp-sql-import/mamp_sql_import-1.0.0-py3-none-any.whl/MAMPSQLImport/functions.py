from configs import *

def get_export_cmd(file_name, database):
    return '{} -u {} -p{} {} > {}'.format(mysql_path, mysql_user, mysql_pass, database, get_backup_path(file_name))


def get_import_cmd(file_path, database):
    return '{} -u {} -p{} {} < {}'.format(mysql_path, mysql_user, mysql_pass, database, file_path)


def get_backup_path(file_name):
    return os.path.join(backup_dir, file_name)


def get_db_path(file_name):
    return os.path.join(dbs_dir, file_name)


def import_db(file_path, database):
    pass
    os.system(get_import_cmd(file_path, database))