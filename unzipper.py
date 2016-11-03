'''
by D1rtyCl0wn
class for unzip and handle unzipped
'''

import zipfile, gzip
import os

class Unzipper():

    def is_zip(self,filename):
        check = zipfile.is_zipfile(filename)
        if check:
            return True
        else:
            return False

    def zip_is_ok(self,zip_file):
        if self.is_zip(zip_file):
            zfileobj = zipfile.ZipFile(zip_file)
            ret = zfileobj.testzip()

            if ret is not None:
                print "First bad file in zip: %s" % ret
                return False
            else:
                print "Zip file is good."
                return True
        else:
            return False

    def unzip_archive(self, archive,place=os.getcwd()):
        if self.zip_is_ok(archive):
            if place==os.getcwd():
                try:
                    zip_obj = zipfile.ZipFile(archive,'r')
                    zip_obj.extractall(os.getcwd())
                    return True
                except Exception as e:
                    print e
                    return False
            else:
                try:
                    if not os.path.exists(place):
                        os.makedirs(place)
                    zip_obj = zipfile.ZipFile(archive,'r')
                    zip_obj.extractall(place)
                    return True
                except:
                    return False
