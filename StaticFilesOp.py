'''
by D1rtyCl0wn
contains some FS operations
'''

import os, sys, string, random
from unzipper import Unzipper
import static_strings

class FileS():
    rootdir=static_strings.BASEROOT

    def __init__(self,rootdir=static_strings.BASEROOT):
        if os.path.exists(rootdir):
            self.rootdir = rootdir

    def random_string(self,length=10,chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(length))

    def create_mdump(self, mdir=static_strings.MAILROOT):
        mbasepath = os.path.join(self.rootdir,mdir)
        mdlist = os.listdir(mbasepath)
        try:
            rname = 'mail_'+self.random_string()
            while rname in mdlist:
                rname='mail_'+self.random_string()
            dpath = os.path.join(mbasepath, rname)
            os.makedirs(dpath)
            os.makedirs(os.path.join(dpath,'emls'))
            os.makedirs(os.path.join(dpath, 'html'))
            return [rname,dpath]
        except Exception as e:
            print(e)
            return None

    def create_docdump(self, ddir=static_strings.DOCROOT):
        dbasepath = os.path.join(self.rootdir,ddir)
        ddlist = os.listdir(dbasepath)
        try:
            rname = 'docs_'+self.random_string()
            while rname in ddlist:
                rname = 'docs_'+self.random_string()
            dpath = os.path.join(dbasepath,rname)
            os.makedirs(dpath)
            return [rname,dpath]
        except Exception as e:
            print(e)
            return None

    def create_txtdump(self, tdir=static_strings.TXTROOT):
        dbasepath = os.path.join(self.rootdir,tdir)
        tdlist = os.listdir(dbasepath)
        try:
            rname = 'txt_'+self.random_string()
            while rname in tdlist:
                rname = 'txt_'+self.random_string()
            dpath = os.path.join(dbasepath,rname)
            os.makedirs(dpath)
            return [rname,dpath]
        except Exception as e:
            print(e)
            return None

    def sanitize_dir(self,dir,dtype):
        if dtype=='mail':
            '''delete all non-eml files from dir'''
            listdir = os.listdir(dir)
            i=0
            print listdir
            for f in listdir:
                print f.lower()
                if f.lower().endswith('.eml'):
                    i=i+1
            print "Files needed:", i
            if i==0:
                return False
            else:
                return True
        elif dtype=='docs':
            '''delete all non-office files from dir'''
            listdir = os.listdir(dir)
            i = 0
            for f in listdir:
                if f.lower().endswith('.doc' or '.docx' or '.pdf' or '.xls' or '.xlsx' or '.ppt' or '.rtf' or '.pptx'):
                    i = i + 1
            print "Files needed:", i
            if i == 0:
                return False
            else:
                return True
        elif dtype=='txt':
            '''think about it'''

            return True
        else:
            return False