'''
by D1rtyCl0wn
this file contains functions for basic DB and FS interactions
it includes functions, that fill DB tables with indexed files
#TODO: handling txt dumps

'''


import os
import random
import string

from get_text import getText as get_text
import psycopg2
import db_connection
import EmlProcessor
import static_strings
import hashlib


class DBInteractions():
    dbconnection = None
    def __init__(self, dbConn):
        self.dbconnection = dbConn

    def create_mdump_table(self, tablename):
        '''
        :param connection: db_connection()
        :param tablename: name of the table
        :return:
        '''
        t_struct = [['id', 'serial', 'PRIMARY KEY'],
                    ['subjectf', 'text', ''],
                    ['fromf', 'text', ''],
                    ['tof', 'text', ''],
                    ['datef', 'bigint', ''],
                    ['text_content', 'text', ''],
                    ['html_path', 'text', ''],
                    ['filepath', 'text', '']
                    ]
        success = self.dbconnection.create_table(tablename, t_struct)
        if success:
            return tablename
        else:
            return None

    def create_docs_table(self,tablename):
        t_struct=[['id', 'serial', 'PRIMARY KEY'],
                    ['filename', 'text', ''],
                    ['filepath', 'text', ''],
                    ['tcontent', 'text', ''],
                    ]
        success = self.dbconnection.create_table(tablename,t_struct)
        if success:
            return tablename
        else:
            return None

    def create_pastes_table(self,tablename):
        t_struct = [['id', 'serial', 'PRIMARY KEY'],
                    ['datef', 'timestamptz', ''],
                    ['tcontent', 'text', ''],
                    ]
        success = self.dbconnection.create_table(tablename, t_struct)
        if success:
            return tablename
        else:
            return None

    def create_entries_table(self,tablename):
        t_struct = [['id', 'serial', 'PRIMARY KEY'],
                    ['author', 'text', ''],
                    ['dump', 'text', ''],
                    ['dumpid', 'text', ''],
                    ['datef', 'timestamptz', ''],
                    ['description', 'text', ''],
                    ['title','text','']
                    ]
        success = self.dbconnection.create_table(tablename,t_struct)
        if success:
            return tablename
        else:
            return None

    def list_subdirs(self,path):
        flist = []
        for path_, subdirs, files in os.walk(path):
            for filename in files:
                f = os.path.join(path_, filename)
                if (filename[0] != '.'):
                    flist.append(f)
        return flist

    def docs2db(self, path, table):
        p = self.list_subdirs(path)
        for o in p:
            print o
        text=''
        o=None
        gt = get_text()
        for f in p:
            fname = f.split(path)[1].replace("-"," ").replace("+"," ").replace("_", " ")
            f=os.path.join(path,f)
            print f
            if (os.path.isdir(f)==False):
                ext=''
                try:
                    ext = f.split('.')[1]
                except Exception:
                    pass
                print f,ext
                if (ext=="docx"):
                    text = gt.get_docx_text(f)
                if (ext=="doc" or ext=='rtf'):
                    text = gt.get_doc_text(f)
                if (ext=="xlsx"):
                    text = gt.get_xlsx_text(f)
                if(ext=="xls"):
                    text = gt.get_xls_text(f)
                if (ext=='pdf'):
                    text = gt.get_pdf_text(f)
                else:
                    text = "empty"
                row_dict = {'filename':fname, 'filepath':f,'tcontent':text}

                self.dbconnection.insert_into_values(table,row_dict)
            else:
                print f, "is a directory"

    def emls2db(self,html_storage,path,table, error_log_path=''):
        '''
        :param connection: working db_connection
        :param html_storage: path to directory, from which HTML'ed letters gonna be served
        :param path: path to the directory with eml's
        :param table: name of the table
        :return:
        '''
        eproc = EmlProcessor
        files=eproc.listEML(path)
        error_log=[]
        if error_log_path=='':
            error_log_path=os.path.join(path,'error.log')
        for emlfile in files:
            print emlfile
            headers = eproc.getHeaders(emlfile)
            s_date = eproc.strDateToLong(eproc.getDate(headers))
            if s_date==None:
                s_date="01/01/1970, 00:00:00 +000"
            else:
                s_date=s_date
            to = eproc.getTo(headers)
            to_string = "".encode('utf-8')
            for t in to:
                if(t[1] == None):
                    try:
                        to_string = eproc.get_string(to_string+" "+t[0].replace("'","").replace('"',""))
                    except:
                        t[0] = unicode(t[0],'utf8')
                        t[0] = t[0].encode('unicode_escape')
                        to_string = to_string+" "+t[0].replace("'","").replace('"',"")
                else:
                    to_string = to_string+" "+t[0].decode(t[1]).encode('utf-8')
                to_string = to_string.replace("\""," ")
                to_string = to_string.replace("'"," ")
                to_string = to_string.replace("<"," ")
                to_string = to_string.replace(">"," ")
                to_string = to_string.replace("/"," ")
                to_string = to_string.replace("\\"," ")

            from_string = "".encode('utf-8')
            from_header = eproc.getFrom(headers)
            for f in from_header:
                if(f[1]==None):
                    try:
                        from_string = from_string + f[0].replace("'","").replace('"',"").decode('utf-8').encode('utf-8')
                    except:
                        f[0] = unicode(f[0],'utf8')
                        f[0] = t[0].encode('unicode_escape')
                        from_string = from_string + f[0].replace("'","").replace('"',"")
                else:
                    from_string = from_string + f[0].decode(f[1]).encode('utf-8')
                from_string = from_string.replace("\""," ")
                from_string = from_string.replace("'"," ")
                from_string = from_string.replace("<"," ")
                from_string = from_string.replace(">"," ")
                from_string = from_string.replace("\\"," ")
                from_string = from_string.replace("/"," ")

            subject = eproc.getSubject(headers)
            subj_string = "".encode('utf-8')
            if(subject[0][1]==None):
                try:
                    subj_string = subject[0][0].encode('utf-8')
                except:
                    subj_string = unicode(subject[0][0],'utf8')
                    subj_string = subj_string.encode('unicode_escape')
            else:
                subj_string = subject[0][0].decode(subject[0][1]).encode('utf-8')

            subj_string = subj_string.replace('"',"_")
            #subj_string = subj_string.replace('\'',"_")
            subj_string = subj_string.replace('<',"_")
            subj_string = subj_string.replace('>',"_")
            subj_string = subj_string.replace('/',"_")
            subj_string = subj_string.replace('\\',"_")
            subj_string = subj_string.replace(':',"_")
            subj_string = subj_string.replace('?',"_")
            subj_string = subj_string.replace('*',"_")
            subj_string = subj_string.replace('|',"_")
            subj_string = subj_string.replace('\t',"_")
            subj_string = subj_string.replace('\r\n',"_")
            subj_string = subj_string.replace('\n',"__")

            msg_text = eproc.get_text_content(emlfile)
            msg_text =unicode(msg_text,'utf8',errors='ignore')
            msg_text = msg_text.encode('unicode_escape')
            msg_text = msg_text.replace('"',"")
            msg_text = msg_text.replace('`',"")
            msg_text = msg_text.replace('\'',"")
            msg_text = msg_text.replace('\r\n'," ")
            msg_text = msg_text.replace('\n'," ")
            msg_text = msg_text.replace('\t'," ")
            msg_text=eproc.get_string(msg_text)

            print headers
            html_path=eproc.eml_to_html(emlfile,html_storage).split(static_strings.BASEROOT)[1]
            print html_path
            fields = {'subjectf':subj_string,
                      'fromf':from_string,
                      'tof':to_string,
                      'datef':s_date,
                      'text_content':msg_text,
                      'html_path':html_path,
                      'filepath':emlfile
                      }
            self.dbconnection.insert_into_values(table,fields)

        erfile = open(error_log_path,'w+')
        for error in error_log:
            erfile.write(error+'\r\n')
        erfile.close()

    def add_contents_entry(self, table, dumpid, dtype, author, date, descr, title):
        '''

        :param dbconnection:
        :param dumpid:
        :param dtype:
        :param author:
        :param date:
        :param descr:
        :param picpath:
        :return:
        '''
        row = {'author':author,
               'dump':dtype,
               'did':dumpid,
               'datef':date,
               'description':descr,
               'title':title}

        self.dbconnection.insert_into_values(table,row)


    def random_string(self, length=10, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(length))


    def truncate_table(self,table):
        self.dbconnection.set_cursor()
        sql= 'TRUNCATE '+table+';'
        cur = self.dbconnection.cursor
        cur.execute(sql)
        self.dbconnection.connection.commit()
        cur.close()
        return True

