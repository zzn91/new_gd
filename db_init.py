import os
import MySQLdb
from config.config import DevelopmentConfig

__author__ = "Zhaozn"



def init_database():
    '''
    初始化创建数据库
    :param app:
    :param status: True 数据库如果存在删除、并创建
    :param app_db:
    :return:
    '''
    try:
        DB_HOST = DevelopmentConfig.DB_HOST
        DB_USER = DevelopmentConfig.DB_USER
        DB_PWD = DevelopmentConfig.DB_PWD
        DB_NAME = DevelopmentConfig.DB_NAME

        db = MySQLdb.connect(DB_HOST, DB_USER, DB_PWD, charset='utf8')
        cursor = db.cursor()
        cursor.execute('show databases')
        db_names = cursor.fetchall()
        db_name_list = [name[0] for name in db_names]
        if DB_NAME in db_name_list:
            cursor.execute('drop database if exists ' + DB_NAME)
            cursor.execute('CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci' % DB_NAME)
            cursor.execute('mysqldump -u %s -p %s %s > %s ' % (DB_USER,
                                                               DB_PWD,
                                                               DB_NAME,
                                                               'init.sql'))
        else:
            cursor.execute('CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci' % DB_NAME)
            cursor.execute('mysqldump -u %s -p %s %s > %s ' % (DB_USER,
                                                               DB_PWD,
                                                               DB_NAME,
                                                               'init.sql'))
    except MySQLdb.Error as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))


if __name__ == "__main__":
    init_database()