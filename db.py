# -*- coding: utf-8 -*-
# @Summary : Working with Engines and Connections
# @File    : db.py
# @Software: PyCharm
import sqlalchemy
from sqlalchemy import Table

from conf.constants import default_engine, it_engine, edw_engine, it_online_engine, old_oracle_engine, \
    rule_engine, credit_engine, market_engine
from utils.get_db_config import zk, env
from utils.loger import sentry_log, code_log


class DBInterfaceError(Exception):
    pass


class DBConn(object):

    def __init__(self, db_name='data_mining', auto_commit=True):
        self._db_name = db_name
        self._engine = self._get_engine()
        if not auto_commit:
            self._connection = self.get_connection()
            self._transaction = self._connection.begin()

    # def __del__(self):
    #     if self._connection:
    #         self._connection.close()

    def get_connection(self):
        co_result = None
        try:
            co_result = self._engine.connect()
            code_log.info('%s engine pool status is %s' % (self._db_name, self._engine.pool.status()))
        except Exception, ex:
            if zk.get("/credit_report/%s/sentry_flag" % env.lower())[0].decode('utf8') == 'true':
                sentry_log.captureException(tags={"db": "connection"})
        return co_result

    def get_connect(self):
        return self._connection

    def roll_back(self):
        self._transaction.rollback()

    def commit(self):
        self._transaction.commit()

    def _get_engine(self):
        if self._db_name == 'data_mining':
            engine = default_engine
        elif self._db_name == 'it':
            engine = it_engine
        elif self._db_name == 'edw':
            engine = edw_engine
        elif self._db_name == 'it_online':
            engine = it_online_engine
        elif self._db_name == 'oracle':
            engine = old_oracle_engine
        elif self._db_name == 'rule':
            engine = rule_engine
        elif self._db_name == 'credit':
            engine = credit_engine
        elif self._db_name == 'market':
            engine = market_engine
        else:
            engine = default_engine
        return engine

    def transaction(self):

        return self._transaction

    def execute(self, cmd, get_all=True):
        """
        Execute a sql and return result, fetch one if not get_all.
        :param cmd: str, raw sql string.
        :param get_all: boolean. True if want to fetch all else fetch one.
        :return: Fetch all if get_all else fetch one.
        """
        self._connection = self.get_connection()
        try:
            code_log.info('query cmd is %s' % cmd)
            result = self._connection.execute(cmd)
            try:
                result = result.fetchall() if get_all else result.fetchone()
            except Exception, e:
                if zk.get("/credit_report/%s/sentry_flag" % env.lower())[0].decode('utf8') == 'true':
                    sentry_log.captureException(tags={"db": "execute"})
                code_log.error('db_error: %s, cmd is %s' % (str(e), cmd))

            return result
        except Exception, ex:
            if zk.get("/credit_report/%s/sentry_flag" % env.lower())[0].decode('utf8') == 'true':
                sentry_log.captureException(tags={"db": "connection"})
            raise DBInterfaceError(ex)
        finally:
            code_log.info('delete connection for db %s' % self._db_name)
            self._connection.close()

    def insert(self, table_name, data_dict):
        """
        Insert data_dict to table_name.
        :param table_name: str, table to insert into.
        :param data_dict: dict, {key: value} for insert.
        :return: primary keys of inserted elements if insert successfully.
        """
        self._connection = self.get_connection()
        try:
            table = Table(table_name, sqlalchemy.MetaData(), autoload=True, autoload_with=self._engine)
            stmt = table.insert().values(**data_dict)
            result = self._connection.execute(stmt)
            return result.inserted_primary_key[0] if result.inserted_primary_key else 0
        except Exception, ex:
            self._connection.close()
            print 'table_name: ', table_name
            import traceback
            traceback.print_exc()
            raise DBInterfaceError(ex)
        finally:
            code_log.info('delete connection for db %s' % self._db_name)
            self._connection.close()

    def update(self, table_name, condition_dict, update_dict):
        """
        Update table_name by update_dict where condition_dict.
        :param table_name: str, table to update.
        :param condition_dict: dict, update condition.
        :param update_dict: dict, {key: value} for update.
        :return: Updated rows count.
        """
        self._connection = self.get_connection()
        try:
            table = Table(table_name, sqlalchemy.MetaData(), autoload=True, autoload_with=self._engine)
            stmt = table.update().values(**update_dict)
            for key, value in condition_dict.items():
                if key in table.c:
                    where_column = table.c[key]
                    stmt = stmt.where(where_column == value)
            result = self._connection.execute(stmt)
            return result.rowcount
        except Exception, ex:
            self._connection.close()
            raise DBInterfaceError(ex)
        finally:
            code_log.info('delete connection for db %s' % self._db_name)
            self._connection.close()

    def delete(self, table_name, condition_dict):
        """
        Delete from table_name where condition_dict.
        :param table_name: str, table to delete from.
        :param condition_dict: dict, delete condition.
        :return: Deleted rows count.
        """
        self._connection = self.get_connection()
        try:
            table = Table(table_name, sqlalchemy.MetaData(), autoload=True, autoload_with=self._engine)
            stmt = table.delete()
            for key, value in condition_dict.items():
                if key in table.c:
                    where_column = table.c[key]
                    stmt = stmt.where(where_column == value)
            result = self._connection.execute(stmt)
            return result.rowcount
        except Exception, ex:
            self._connection.close()
            raise DBInterfaceError(ex)
        finally:
            code_log.info('delete connection for db %s' % self._db_name)
            self._connection.close()


if __name__ == "__main__":
    # try:
    #     a = DBConn('edw')
    # finally:
    #     a.__del__()
    # try:
    #     a1 = DBConn('edw')
    # finally:
    #     a1.__del__()
    # try:
    #     a2 = DBConn('edw')
    # finally:
    #     a2.__del__()

    # with DBConn('edw') as a:
    #     pass
    # with DBConn('edw') as a1:
    #     pass
    # with DBConn('edw') as a2:
    #     pass
    # with DBConn('edw') as a3:
    #     pass
    # with DBConn('edw') as a4:
    #     pass
    # with DBConn('edw') as a5:
    #     pass
    # with DBConn('edw') as a6:
    #     pass
    # with DBConn('edw') as a7:
    #     pass
    # with DBConn('edw') as a8:
    #     pass
    a = DBConn('edw')
    a2 = DBConn('edw')
    a3 = DBConn('edw')
    a4 = DBConn('edw')
    a5 = DBConn('edw')
    a6 = DBConn('edw')
    a7 = DBConn('edw')
    a4.execute('select 1')
