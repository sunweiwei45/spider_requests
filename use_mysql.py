# coding:UTF-8

import MySQLdb
from mysql_setting import connect, default_table


class UseMySQL():
    """
    该类可以实现对于MySQL数据的增删改查等功能，
    输入该类对象的记录一律以字典的形式
    *
    """
    def __init__(self):
        """
        初始化对象，并用配置文件mysql_setting中的信息来建立连接
        """
        self.conn = MySQLdb.connect(
                      host=connect['host'],
                      port=connect['port'],
                      user=connect['user'],
                      passwd=connect['passwd'],
                      db=connect['db'],
                      charset=connect['charset']
                      )
        self.cursor = self.conn.cursor()
        self.cursor.execute("USE %s" % (str(connect['db'])))
        #修改操作的数据库

    def insert_mysql(self, record=None, table=None):
        """
        将记录插入到制定的的表中，如果没有制定表，就插入到mysql_setting中的default_table中

        :param record:(dict),想要插入表中的记录，字典的key要与数据库中列名一样，顺序无关
        :param table:(string),插入的表名
        :return:
        """
        if table is not None:
            pass
        else:
            table = default_table

        column_list = self.get_table_structure(table)
        columns = ",".join(column_list)
        temp_sql = "INSERT INTO `%s`(%s) VALUES " % (str(table), str(columns))
        #到这一步就将SQL语句拼到类似 ‘INSERT INTO hdf_zixun(doctor_url, page_url) VALUES ’
        temp_list = []
        for column in column_list:
            column = '\'%(' + str(column) + ')s\''
            temp_list.append(column)
        content = ",".join(temp_list)
        content = "(" + content + ")"  #将列表转化为字符串，并以逗号分隔，形成('%(doctor_url)s','%(page_url)s','%(order_type)s')
        sql = temp_sql + content % record  #以字典形式将记录内容插入到SQL语句中
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            print "insert failed"
            self.conn.rollback()  #如果插入失败就回滚

    def select_mysql(self, record=None, table=None):
        """
        从指定表（默认表）中返回符合条件的记录，
        目前只能用于类似‘···where id=* and name=* ···’的样式，类似与‘where id > *...’还有待实现，
        record 还是以字典的形式，
        会以字典列表的形式返回符合条件的所有数据，
        如果字典是一个完整的记录，则返回该条记录
        如：record={'id': 1，'name':sww}则删除所有id=1 and name=sww的所有记录；
        若表中就只有两列（id，name），则返回给条数据，可用于判断该条数据是否在数据库中

        :param record:(dict),查询条件：id=12，name=sww ····
        :param table:(string),指定查询的表，若不指定就是默认表
        :return:(list<dict>)，查询结果
        """

        if table is not None:
            pass
        else:
            table = default_table

        if record is not None:
            temp_list = []
            for key in record:
                content = str(key) + "=" + '\'' + str(record[key]) + '\''
                temp_list.append(content)
            temp_sql = " and ".join(temp_list)
            sql = "SELECT * FROM %s WHERE " % (str(table)) + temp_sql

            try:
                self.cursor.execute(sql)
                result = self.cursor.fetchall()
                result = self.tuple2dictlist(tuple=result, table=table)
                return result
            except:
                print "Find no record!!"

        else:
            sql = "SELECT * FROM %s" % (str(table))
            try:
                self.cursor.execute(sql)
                result = self.cursor.fetchall()
                result = self.tuple2dictlist(tuple=result, table=table)
                return result
            except:
                print "Find no record!!"
            # print "The record can not be empty!"

    def update_mysql(self, update=None, record=None, table=None):
        """
        可以修改指定的表（或是默认的表）里的一些记录，
        目前只能修改类似于‘···id=10’的样式，类似‘id = id + 1’还有待实现
        目前只能用于类似‘···where id=* and name=* ···’的样式，类似与‘where id > *...’还有待实现，

        :param update: (dict),修改的内容
        :param record: (dict),找到想要修改的记录
        :param table: (string),指定修改的表
        :return:
        """
        if table is not None:
            pass
        else:
            table = default_table
        temp_list = []
        for key in update:
            content = str(key) + "=" + '\'' + str(update[key]) + '\''
            temp_list.append(content)
        temp_sql = " and ".join(temp_list)
        sql = "UPDATE %s SET " % (str(table)) + temp_sql

        if update is not None and record is None:
            try:
                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print "Update failed , rollbacked!!"

        elif update is not None and record is not None:
            temp_list = []
            for key in record:
                content = str(key) + "=" + '\'' + str(record[key]) + '\''
                temp_list.append(content)
            temp_sql = " and ".join(temp_list)
            sql = sql + " WHERE " + temp_sql
            try:
                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print "Update failed , rollbacked!!"
        else:
            print "The dictionary named update can not be empty!!"

    def delete_mysql(self, record=None, table=None):
        """
        从指定表（默认表）中删除指定记录，
        目前只能用于类似‘···where id=* and name=* ···’的样式，类似与‘where id > *...’还有待实现，
        record 还是以字典的形式，
        会删除符合条件的所有数据，
        如果字典是一个完整的记录，则删除该条记录，
        如：record={'id': 1，'name':sww}则删除所有id=1 and name=sww的所有记录

        :param record:(dict)，删除的条件
        :param table:(string),删除的表名
        :return:
        """
        if table is not None:
            pass
        else:
            table = default_table

        if record is not None:
            temp_list = []
            for key in record:
                content = str(key) + "=" + '\'' + str(record[key]) + '\''
                temp_list.append(content)
            temp_sql = " and ".join(temp_list)
            sql = "DELETE FROM %s WHERE " % (str(table)) + temp_sql

            try:
                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print "Update failed , rollbacked!!"
        else:
            print "The record can not be empty!"

    def get_table_structure(self, table=None):

        """
        返回输入表的所有的列名称，如果没输入就默认返回mysql_setting中的default_table的列名
        :param table:
        :return:(list<string>),一列表的形式返回列名
        """
        if table is not None:
            pass
        else:
            table = default_table
        sql = "SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name='%s' " % (str(table))
        self.cursor.execute(sql)
        structure = self.cursor.fetchall()
        column_list = []
        for column in structure:
            column_list.append(column[0])
        return column_list


    def tuple2dictlist(self, tuple=None, table=None ):
        """
        将查询结果（元组）转化为字典的列表返回
        :param tuple:(tuple),输入的元组
        :param table:(list<string>),字典的结构
        :return:(list<dict>),返回字典的列表
        """
        if table is not None:
            pass
        else:
            table = default_table

        column_list = self.get_table_structure(table=table)
        if tuple is not None:
            result = []
            for row in tuple:
                temp_dict = {}
                for i in range(len(column_list)):
                    temp_dict[column_list[i]] = row[i]
                result.append(temp_dict)
            return result
        else:
            pass



    def close_mysql(self):
        """
        操作结束，关闭游标和数据库的连接
        :return:
        """
        self.cursor.close()
        self.conn.close()









