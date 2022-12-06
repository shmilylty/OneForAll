"""
SQLite database initialization and operation
"""

from common import records

from common.records import Connection
from config.log import logger
from config import settings


class Database(object):
    def __init__(self, db_path=None):
        self.conn = self.get_conn(db_path)

    @staticmethod
    def get_conn(db_path):
        """
        Get database connection

        :param   db_path: Database path
        :return: db_conn: SQLite database connection
        """
        logger.log('TRACE', f'Establishing database connection')
        if isinstance(db_path, Connection):
            return db_path
        protocol = 'sqlite:///'
        if not db_path:  # 数据库路径为空连接默认数据库
            db_path = f'{protocol}{settings.result_save_dir}/result.sqlite3'
        else:
            db_path = f'{protocol}{db_path}'
        db = records.Database(db_path)  # 不存在数据库时会新建一个数据库
        logger.log('TRACE', f'Use the database: {db_path}')
        return db.get_connection()

    def query(self, sql):
        try:
            results = self.conn.query(sql)
        except Exception as e:
            logger.log('ERROR', e.args)
            return None
        return results

    def create_table(self, table_name):
        """
        Create table

        :param str table_name: table name
        """
        table_name = table_name.replace('.', '_')
        if self.exist_table(table_name):
            logger.log('TRACE', f'{table_name} table already exists')
            return
        logger.log('TRACE', f'Creating {table_name} table')
        self.query(f'create table "{table_name}" ('
                   f'id integer primary key,'
                   f'alive int,'
                   f'request int,'
                   f'resolve int,'
                   f'url text,'
                   f'subdomain text,'
                   f'port int,'
                   f'level int,'
                   f'cname text,'
                   f'ip text,'
                   f'public int,'
                   f'cdn int,'
                   f'status int,'
                   f'reason text,'
                   f'title text,'
                   f'banner text,'
                   f'header text,'
                   f'history text,'
                   f'response text,'
                   f'ip_times text,'
                   f'cname_times text,'
                   f'ttl text,'
                   f'cidr text,'
                   f'asn text,'
                   f'org text,'
                   f'addr text,'
                   f'isp text,'
                   f'resolver text,'
                   f'module text,'
                   f'source text,'
                   f'elapse float,'
                   f'find int)')

    def insert_table(self, table_name, result):
        table_name = table_name.replace('.', '_')
        self.conn.query(
            f'insert into "{table_name}" '
            f'(id, alive, resolve, request, url, subdomain, port, level,'
            f'cname, ip, public, cdn, status, reason, title, banner, header,'
            f'history, response, ip_times, cname_times, ttl, cidr, asn, org,'
            f'addr, isp, resolver, module, source, elapse, find) '
            f'values (:id, :alive, :resolve, :request, :url,'
            f':subdomain, :port, :level, :cname, :ip, :public, :cdn,'
            f':status, :reason, :title, :banner, :header, :history, :response,'
            f':ip_times, :cname_times, :ttl, :cidr, :asn, :org, :addr, :isp,'
            f':resolver, :module, :source, :elapse, :find)', **result)

    def save_db(self, table_name, results, module_name=None):
        """
        Save the results of each module in the database

        :param str table_name: table name
        :param list results: results list
        :param str module_name: module
        """
        logger.log('TRACE', f'Saving the subdomain results of {table_name} '
                            f'found by module {module_name} into database')
        table_name = table_name.replace('.', '_')
        if results:
            try:
                self.conn.bulk_query(
                    f'insert into "{table_name}" '
                    f'(id, alive, resolve, request, url, subdomain, port, level, '
                    f'cname, ip, public, cdn, status, reason, title, banner, header, '
                    f'history, response, ip_times, cname_times, ttl, cidr, asn, org, '
                    f'addr, isp, resolver, module, source, elapse, find) '
                    f'values (:id, :alive, :resolve, :request, :url, '
                    f':subdomain, :port, :level, :cname, :ip, :public, :cdn,'
                    f':status, :reason, :title, :banner, :header, :history, :response, '
                    f':ip_times, :cname_times, :ttl, :cidr, :asn, :org, :addr, :isp, '
                    f':resolver, :module, :source, :elapse, :find)', results)
            except Exception as e:
                logger.log('ERROR', e)

    def exist_table(self, table_name):
        """
        Determine table exists

        :param   str table_name: table name
        :return  bool: Whether table exists
        """
        table_name = table_name.replace('.', '_')
        logger.log('TRACE', f'Determining whether the {table_name} table exists')
        results = self.query(f'select count() from sqlite_master where type = "table" and'
                             f' name = "{table_name}"')
        if results.scalar() == 0:
            return False
        else:
            return True

    def copy_table(self, table_name, bak_table_name):
        """
        Copy table to create backup

        :param str table_name: table name
        :param str bak_table_name: new table name
        """
        table_name = table_name.replace('.', '_')
        bak_table_name = bak_table_name.replace('.', '_')
        logger.log('TRACE', f'Copying {table_name} table to {bak_table_name} new table')
        self.query(f'drop table if exists "{bak_table_name}"')
        self.query(f'create table "{bak_table_name}" '
                   f'as select * from "{table_name}"')

    def clear_table(self, table_name):
        """
        Clear the table

        :param str table_name: table name
        """
        table_name = table_name.replace('.', '_')
        logger.log('TRACE', f'Clearing data in table {table_name}')
        self.query(f'delete from "{table_name}"')

    def drop_table(self, table_name):
        """
        Delete table

        :param str table_name: table name
        """
        table_name = table_name.replace('.', '_')
        logger.log('TRACE', f'Deleting {table_name} table')
        self.query(f'drop table if exists "{table_name}"')

    def rename_table(self, table_name, new_table_name):
        """
        Rename table name

        :param str table_name: old table name
        :param str new_table_name: new table name
        """
        table_name = table_name.replace('.', '_')
        new_table_name = new_table_name.replace('.', '_')
        logger.log('TRACE', f'Renaming {table_name} table to {new_table_name} table')
        self.query(f'alter table "{table_name}" '
                   f'rename to "{new_table_name}"')

    def deduplicate_subdomain(self, table_name):
        """
        Deduplicate subdomains in the table

        :param str table_name: table name
        """
        table_name = table_name.replace('.', '_')
        logger.log('TRACE', f'Deduplicating subdomains in {table_name} table')
        self.query(f'delete from "{table_name}" where '
                   f'id not in (select min(id) '
                   f'from "{table_name}" group by subdomain)')

    def remove_invalid(self, table_name):
        """
        Remove nulls or invalid subdomains in the table

        :param str table_name: table name
        """
        table_name = table_name.replace('.', '_')
        logger.log('TRACE', f'Removing invalid subdomains in {table_name} table')
        self.query(f'delete from "{table_name}" where '
                   f'subdomain is null or resolve == 0')

    def get_data(self, table_name):
        """
        Get all the data in the table

        :param str table_name: table name
        """
        table_name = table_name.replace('.', '_')
        logger.log('TRACE', f'Get all the data from {table_name} table')
        return self.query(f'select * from "{table_name}"')

    def export_data(self, table_name, alive, limit):
        """
        Get part of the data in the table

        :param str table_name: table name
        :param any alive: alive flag
        :param str limit: limit value
        """
        table_name = table_name.replace('.', '_')
        sql = f'select id, alive, request, resolve, url, subdomain, level,' \
              f'cname, ip, public, cdn, port, status, reason, title, banner,' \
              f'cidr, asn, org, addr, isp, source from "{table_name}" '
        if alive and limit:
            if limit in ['resolve', 'request']:
                where = f' where {limit} = 1'
                sql += where
        elif alive:
            where = f' where alive = 1'
            sql += where
        sql += ' order by subdomain'
        logger.log('TRACE', f'Get the data from {table_name} table')
        return self.query(sql)

    def count_alive(self, table_name):
        table_name = table_name.replace('.', '_')
        sql = f'select count() from "{table_name}" where alive = 1'
        return self.query(sql)

    def get_resp_by_url(self, table_name, url):
        table_name = table_name.replace('.', '_')
        sql = f'select response from "{table_name}" where url = "{url}"'
        logger.log('TRACE', f'Get response data from {url}')
        return self.query(sql).scalar()

    def get_data_by_fields(self, table_name, fields):
        table_name = table_name.replace('.', '_')
        field_str = ', '.join(fields)
        sql = f'select {field_str} from "{table_name}"'
        logger.log('TRACE', f'Get specified field data {fields} from {table_name} table')
        return self.query(sql)

    def update_data_by_url(self, table_name, info, url):
        table_name = table_name.replace('.', '_')
        field_str = ', '.join(map(lambda kv: f'{kv[0]} = "{kv[1]}"', info.items()))
        sql = f'update "{table_name}" set {field_str} where url = "{url}"'
        return self.query(sql)

    def close(self):
        """
        Close the database connection
        """
        self.conn.close()
