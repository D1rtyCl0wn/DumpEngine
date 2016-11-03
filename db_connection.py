'''
by D1rtyCl0wn

this file contains basic DB operations
though it is widely used in the project, it has some bugs, so sometimes it works improperly. Needs to be fixed and improved.
'''


import os

from psycopg2._psycopg import AsIs

from get_text import getText as get_text
import psycopg2

class dbConnection():
    connection=None
    cursor=None
    def set_connection(self, dbname, user, password):
        '''

        :param dbname: DB name
        :param user: username
        :param password: password
        :return: inner variable 'connection' is set to the connection, that we establish; now it can be worked with
        '''
        conn = psycopg2.connect(database=dbname, user=user, password=password)
        self.connection = conn
        print ("Established connection", self.connection)

    def release_connection(self):
        if (self.cursor!=None):
            self.cursor.close()
        if(self.connection!=None):
            self.connection.close()
        else:
            print ("No connection is established")

    def set_cursor(self):
        self.cursor = self.connection.cursor()
        print ("got connection cursor", self.cursor)

    def create_table(self, table_name, table_structure):
        '''
        :param table_name: the name of table to be created
        :param table_structure:
         is a list of 3-value arrays: name, datatype and additional parameters like PRIMARY or something alike
        :return: success or non-success
        '''
        self.set_cursor()
        attribs_list=[]

        for attrib in table_structure:
            print attrib

            if not attrib[2]=='':
                attribs_list.append(attrib[0] + (' ') + (attrib[1])+(' ')+(attrib[2]))
            else:
                attribs_list.append(attrib[0] + (' ') + (attrib[1]))

        sql_attribs=''
        for attrib in attribs_list:
            sql_attribs = sql_attribs+(attrib)+(', ')

        sql_attribs=sql_attribs[:-2] #closing statement
        print sql_attribs
        cur=self.cursor
        try:
            sql = "CREATE TABLE IF NOT EXISTS %s (%s)"%(table_name,sql_attribs)
            print sql
            cur.execute(sql)
            self.connection.commit()
            cur.close()
            return True
        except Exception as e:
            print ('Error!', e.message)
            return False


    def select_from_where(self, selection, from_table, where_clause=None, order_by=''):
        '''
        #TODO: make it safe and smooth
        :param selection:what is to be selected
        :param from_table: from which table is it to be selected
        :param where_clause: the selection filter
        :return: result of selection as list
        '''
        self.set_cursor()
        cur = self.cursor
        if where_clause!=None:
            sql = "SELECT %s FROM %s WHERE %s" % (selection, from_table, where_clause)
            if order_by != '':
                sql = "SELECT %s FROM %s WHERE %s ORDER BY %s" % (selection, from_table, where_clause, order_by)
            cur.execute(sql)
        else:
            sql="SELECT %s FROM %s" % (selection, from_table)
            if order_by != '':
                sql = "SELECT %s FROM %s ORDER BY %s" % (selection, from_table, order_by)
            cur.execute(sql)
        select_result = cur.fetchall()
        cur.close()
        return select_result

    def insert_into_values(self,tablename,attr_values):
        '''
        :param tablename:
        :param attr_values:
        :return:
        '''
        self.set_cursor()
        cur=self.cursor
        fields = ''
        values = ''
        print attr_values
        for attr in attr_values.keys():
            fields = fields + (attr) + ', '
            values = values + ("'"+str(attr_values[attr]))+"'" + ', '
        fields = fields[:-2].replace("'","")
        values = values[:-2]
        # fields = ', '.join(attr_values.keys())
        # values = ', '.join(['%%(%s)s' % x for x in attr_values])
        # print values

        sql = ("""INSERT INTO %s (%s) VALUES (%s)"""% (tablename, fields, values))
        print sql, type(sql)
        print cur.mogrify(sql)
        cur.execute(sql)
        self.connection.commit()
        cur.close()


    def list_subdirs(self,path):
        flist = []
        for path_, subdirs, files in os.walk(path):
            for filename in files:
                f = os.path.join(path_, filename)
                if (filename[0] != '.'):
                    flist.append(f)
        return flist

    def update_set_where(self, table, updattr, new_value,whattr, whvalue):
        sql = "UPDATE %s SET %s = '%s' WHERE %s = %s" % (table, updattr, new_value, whattr, whvalue)
        self.set_cursor()
        cur = self.cursor
        try:
            print cur.mogrify(sql)
            cur.execute(sql)
            self.connection.commit()
            return True
        except Exception as e:
            print 'couldn\'t update because of \r\n',e
            return False