# coding:utf-8
from tools_hjh.ThreadPool import ThreadPool


class DBConn:
    """ 维护一个关系型数据库连接池，目前支持oracle，pgsql，mysql，sqlite；支持简单的sql执行 """
    
    ORACLE = 'oracle'
    PGSQL = 'pgsql'
    MYSQL = 'mysql'
    SQLITE = 'sqlite'

    def __init__(self, dbtype, host=None, port=None, db=None, username=None, password=None, poolsize=2, encoding='UTF-8', lib_dir=None):
        """ 初始化连接池
                如果是sqlite，db这个参数是要显示给入的
                如果是oracle，db给入的是sid或是servername都是可以的 """
                
        self.dbtype = dbtype
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.password = password
        self.poolsize = poolsize
        self.encoding = encoding
        self.lib_dir = lib_dir
        
        self.runtp = ThreadPool(1, save_result=True)
        self.dbpool = None
        
        self.config = {
            'host':self.host,
            'port':self.port,
            'database':self.db,
            'user':self.username,
            'password':self.password,
            'maxconnections':self.poolsize,  # 最大连接数
            'blocking':True,  # 连接数达到最大时，新连接是否可阻塞
            'reset':False
        }
        
        if self.dbtype == 'pgsql' or self.dbtype == 'mysql':
            from dbutils.pooled_db import PooledDB
        if self.dbtype == "pgsql":
            import psycopg2
            self.dbpool = PooledDB(psycopg2, **self.config)
        elif self.dbtype == "mysql":
            import pymysql
            self.dbpool = PooledDB(pymysql, **self.config)
        elif self.dbtype == "sqlite": 
            import sqlite3
            from dbutils.persistent_db import PersistentDB
            self.dbpool = PersistentDB(sqlite3, database=db)
        elif self.dbtype == "oracle":
            import cx_Oracle
            if lib_dir is not None:
                cx_Oracle.init_oracle_client(lib_dir=lib_dir)
            try:
                dsn = cx_Oracle.makedsn(host, port, service_name=db)
                self.dbpool = cx_Oracle.SessionPool(user=username,
                                                    password=password,
                                                    dsn=dsn,
                                                    max=poolsize,
                                                    increment=1,
                                                    encoding=encoding)
            except:
                dsn = cx_Oracle.makedsn(host, port, sid=db)
                self.dbpool = cx_Oracle.SessionPool(user=username,
                                                    password=password,
                                                    dsn=dsn,
                                                    max=poolsize,
                                                    increment=1,
                                                    encoding=encoding)
    
    def __run(self, sqls, param=None, auto_commit=None):

        # 替换占位符
        if self.dbtype == 'pgsql' or self.dbtype == 'mysql':
            sqls = sqls.replace('?', '%s')
        elif self.dbtype == 'oracle':
            sqls = sqls.replace('?', ':1')            
        else:
            pass
        
        sql_list = []
        
        # sql只有一行
        if not '\n' in sqls:
            sql_list.append(sqls.rstrip(';'))
            
        # sql有多行
        else:
            # 去掉每行的首尾空格、换行，再去掉最后一个;,去掉--开头的行
            str2 = ''
            for line in sqls.split('\n'):
                line = line.strip()
                if not line.startswith('--') and len(line) > 0:
                    str2 = str2 + line + '\n'
            for sql in str2.split(';\n'):
                if sql is not None and sql != '' and len(sql) > 0:
                    sql_list.append(sql)
        
        # 获取连接
        if self.dbtype == "oracle":
            conn = self.dbpool.acquire()
        else:
            conn = self.dbpool.connection()
            
        cur = conn.cursor()
        
        for sql in sql_list:
            # 执行非SELECT语句
            if not sql.lower().strip().startswith("select"):
                sql = sql.strip()
                if type(param) == list:
                    cur.executemany(sql, param)
                elif type(param) == tuple:
                    cur.execute(sql, param)
                elif param is None:
                    cur.execute(sql)
                if auto_commit: 
                    if sql.lower().strip().startswith("update") or sql.lower().strip().startswith("delete") or sql.lower().strip().startswith("insert"):
                        conn.commit()
                rownum = cur.rowcount
                cur.close()
                conn.close()
                rs = rownum
           
            # 执行SELECT语句
            if sql.lower().strip().startswith("select"):
                sql = sql.strip()
                if param is None:
                    cur.execute(sql)
                elif type(param) == tuple:
                    cur.execute(sql, param)
                rs = QueryResults(cur, conn)
            
        return rs

    def run(self, sql, param=None, wait=False, auto_commit=True):
        """ 执行点什么
        sql中的占位符可以统一使用“?”
        wait为True则会等待当前正在执行的sql，有bug，暂不处理，自用规避"""
        if wait == True:
            tpnum = self.runtp.run(self.__run, (sql, param, auto_commit))
            self.runtp.wait()
            rs = self.runtp.result_map.pop(tpnum)
            return rs
        else:
            return self.__run(sql, param, auto_commit)
    
    def close(self):
        try:
            self.dbpool.close()
        except:
            pass
        finally:
            self.dbpool = None
    
    def __del__(self):
        self.close()
    
        
class QueryResults:

    def __init__(self, cur, conn):
        self.cur = cur
        self.conn = conn
        self.row = ''

    def get_cols(self, end_close=False):
        col = []
        for c in self.cur.description:
            col.append(c[0])
        if end_close:
            self.close()
        return tuple(col)

    def get_rows(self, end_close=False):
        rows = self.cur.fetchall()
        rows_new = []
        for row in rows:
            row_new = []
            for cell in row:
                cell_new = str(cell)
                row_new.append(cell_new)
            rows_new.append(row_new)
        if end_close:
            self.close()
        return rows_new
    
    def next(self):
        self.row = self.cur.fetchone()
        if self.row == None:
            return False
        else:
            return True

    def get_row(self):
        return self.row
    
    def get_table(self, begin_num=1, end_num=None):
        table = []
        table.append(self.get_cols())
        idx = 0
        while self.next():
            idx = idx + 1
            if idx >= begin_num:
                table.append(self.get_row())
            if end_num != None and idx >= end_num:
                break
        return table
    
    def close(self):
        try:
            self.cur.close()
        except:
            pass
        try:
            self.conn.close()
        except:
            pass
        
    def __del__(self):
        self.close()
