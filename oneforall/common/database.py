#!/usr/bin/env python3
# coding=utf-8

"""
SQLite数据库初始化和操作
"""

import records
import config
from records import Connection
from config import logger


class Database(object):
    def __init__(self, db_path=None):
        self.conn = self.get_conn(db_path)

    @staticmethod
    def get_conn(db_path):
        """
        获取数据库对象

        :param db_path: 数据库连接或路径
        :return: SQLite数据库
        """
        logger.log('DEBUG', f'正在获取数据库连接')
        if isinstance(db_path, Connection):
            return db_path
        protocol = 'sqlite:///'
        if not db_path:  # 数据库路径为空连接默认数据库
            db_path = f'{protocol}{config.result_save_path}/result.sqlite3'
        else:
            db_path = protocol + db_path
        db = records.Database(db_path)  # 不存在数据库时会新建一个数据库
        logger.log('DEBUG', f'使用数据库: {db_path}')
        return db.get_connection()

    def create_table(self, table_name):
        """
        创建表结构

        :param str table_name: 要创建的表名
        """
        table_name = table_name.replace('.', '_')
        logger.log('DEBUG', f'正在创建{table_name}表')
        try:
            self.conn.query(f'create table if not exists "{table_name}" ('
                            f'id integer primary key,'
                            f'url text,'
                            f'subdomain text,'
                            f'port int,'
                            f'ips text,'
                            f'status int,'
                            f'reason text,'
                            f'valid int,'
                            f'new int,'
                            f'title text,'
                            f'banner text,'
                            f'header text,'
                            f'response text,'
                            f'module text,'
                            f'source text,'
                            f'elapsed float,'
                            f'count int)')
        except Exception as e:
            logger.log('ERROR', e)

    def save_db(self, table_name, results, module_name=None):
        """
        将各模块结果存入数据库

        :param str table_name: 表名
        :param list results: 结果列表
        :param str module_name: 模块名
        """
        logger.log('DEBUG', f'正在将{module_name}模块发现{table_name}的子域'
                   '结果存入数据库')
        table_name = table_name.replace('.', '_')
        if results:
            try:
                self.conn.bulk_query(
                    f'insert into "{table_name}" ('
                    f'id, url, subdomain, port, ips, status, reason, valid,'
                    f'new, title, banner, header, response, module, source, '
                    f'elapsed, count)'
                    f'values (:id, :url, :subdomain, :port, :ips, :status,'
                    f':reason, :valid, :new, :title, :banner, :header,'
                    f':response, :module, :source,:elapsed, :count)',
                    results)
            except Exception as e:
                logger.log('ERROR', e)

    def exist_table(self, table_name):
        """
        判断是否存在某表

        :param str table_name: 表名
        """
        table_name = table_name.replace('.', '_')
        logger.log('DEBUG', f'正在查询是否存在{table_name}表')
        try:
            result = self.conn.query(f'select count() from sqlite_master '
                                     f'where type = "table" and '
                                     f'name = "{table_name}"')
        except Exception as e:
            logger.log('ERROR', e)
        else:
            if len(result) != 0:
                return True
            else:
                return False

    def copy_table(self, table_name, bak_table_name):
        """
        复制表创建备份

        :param str table_name: 表名
        :param str bak_table_name: 新表名
        """
        table_name = table_name.replace('.', '_')
        bak_table_name = bak_table_name.replace('.', '_')
        logger.log('DEBUG', f'正在将{table_name}表复制到{bak_table_name}新表')
        try:
            self.conn.query(f'drop table if exists "{bak_table_name}"')
            self.conn.query(f'create table "{bak_table_name}" '
                            f'as select * from "{table_name}"')
        except Exception as e:
            logger.log('ERROR', e)

    def clear_table(self, table_name):
        """
        清空表中数据

        :param str table_name: 表名
        """
        table_name = table_name.replace('.', '_')
        logger.log('DEBUG', f'正在清空{table_name}表中的数据')
        try:
            self.conn.query(f'delete from "{table_name}"')
        except Exception as e:
            logger.log('ERROR', e)

    def drop_table(self, table_name):
        """
        删除表

        :param str table_name: 表名
        """
        table_name = table_name.replace('.', '_')
        logger.log('DEBUG', f'正在删除{table_name}表')
        try:
            self.conn.query(f'drop table if exists "{table_name}"')
        except Exception as e:
            logger.log('ERROR', e)

    def rename_table(self, table_name, new_table_name):
        """
        重命名表名

        :param str table_name: 表名
        :param str new_table_name: 新表名
        """
        table_name = table_name.replace('.', '_')
        new_table_name = new_table_name.replace('.', '_')
        logger.log('DEBUG', f'正在将{table_name}表重命名为{table_name}表')
        try:
            self.conn.query(f'alter table "{table_name}" '
                            f'rename to "{new_table_name}"')
        except Exception as e:
            logger.log('ERROR', e)

    def deduplicate_subdomain(self, table_name):
        """
        去重表中的子域

        :param str table_name: 表名
        """
        table_name = table_name.replace('.', '_')
        logger.log('DEBUG', f'正在去重{table_name}表中的子域')
        try:
            self.conn.query(
                f'delete from "{table_name}" where id not in (select min(id) '
                f'from "{table_name}" group by subdomain)')
        except Exception as e:
            logger.log('ERROR', e)

    def remove_invalid(self, table_name):
        """
        去除表中的空值或无效子域

        :param str table_name: 表名
        """
        table_name = table_name.replace('.', '_')
        logger.log('DEBUG', f'正在去除{table_name}表中的无效子域')
        try:
            self.conn.query(
                f'delete from "{table_name}" where '
                f'subdomain is null or valid == 0')
        except Exception as e:
            logger.log('ERROR', e)

    def get_data(self, table_name):
        """
        获取表中的所有数据

        :param str table_name: 表名
        """
        table_name = table_name.replace('.', '_')
        logger.log('DEBUG', f'获取{table_name}表中的所有数据')
        try:
            rows = self.conn.query(f'select * from "{table_name}"')
        except Exception as e:
            logger.log('ERROR', e)
        else:
            return rows

    def export_data(self, table_name, valid):
        """
        获取表中的部分数据

        :param str table_name: 表名
        :param any valid: 有效性
        """
        table_name = table_name.replace('.', '_')
        query = f'select id, url, subdomain, port, ips, status, reason,' \
                f'valid, new, title, banner from "{table_name}"'
        if valid == 0 or valid == 1:
            where = f' where valid = {valid}'
            query += where
        logger.log('DEBUG', f'获取{table_name}表中的所有数据')
        try:
            rows = self.conn.query(query)
        except Exception as e:
            logger.log('ERROR', e)
        else:
            return rows

    def close(self):
        self.conn.close()
