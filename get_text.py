# encoding=utf8
'''
by D1rtyCl0wn
actually, this is a compilation of different libs, found all over the web for parsing office docs
at the moment it supports xls(x), doc(x), rtf, pdf
'''

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import xlrd

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

from subprocess import Popen, PIPE

class getText():
    WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    PARA = WORD_NAMESPACE + 'p'
    TEXT = WORD_NAMESPACE + 't'

    XL_NAMESPACE = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    XL_PARA = XL_NAMESPACE + 'si'
    XL_TEXT = XL_NAMESPACE + 't'

    def get_docx_text(self,path):
        """
        Take the path of a docx file as argument, return the text in unicode.
        """
        document = zipfile.ZipFile(path)
        print document.namelist()
        xml_content = document.read('word/document.xml')
        document.close()
        tree = XML(xml_content)

        paragraphs = []
        for paragraph in tree.getiterator(self.PARA):
            texts = [node.text
                     for node in paragraph.getiterator(self.TEXT)
                     if node.text]
            if texts:
                paragraphs.append(''.join(texts))

        return '\t'.join(paragraphs)

    def get_xlsx_text(self,path):
        """
            Take the path of a docx file as argument, return the text in unicode.
            """
        document = zipfile.ZipFile(path)
        print document.namelist()
        xml_content = document.read('xl/sharedStrings.xml')
        document.close()
        tree = XML(xml_content)
        paragraphs = []
        for paragraph in tree.getiterator(self.XL_PARA):
            texts = [node.text
                     for node in paragraph.getiterator(self.XL_TEXT)
                     if node.text]
            if texts:
                paragraphs.append(''.join(texts))

        return '\t'.join(paragraphs)

    def get_pdf_text(self,path):
        try:
            rsrcmgr = PDFResourceManager()
            retstr = StringIO()
            codec = 'utf-8'
            laparams = LAParams()
            device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
            fp = file(path, 'rb')
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            password = ""
            maxpages = 0
            caching = True
            pagenos = set()
            for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                          check_extractable=True):
                interpreter.process_page(page)
            fp.close()
            device.close()
            str = retstr.getvalue()
            retstr.close()
            #print str.encode('utf-8')
            return str.encode('utf-8')
        except:
            return "PROTECTED"

    def get_doc_text(self,path):
        if path[-4:] == ".doc":
            cmd = ['antiword', path]
            p = Popen(cmd, stdout=PIPE)
            stdout, stderr = p.communicate()
        return stdout.decode('utf-8', 'ignore')

    def get_xls_text(self,path):
        content = ''
        workbook = xlrd.open_workbook(path)
        sh_num = workbook.nsheets
        # print workbook.sheet_names()
        i = 0
        # print sh_num
        sheet = workbook.sheet_by_index(0)
        # print sheet.nrows, sheet.ncols
        j = 0
        while i < int(sh_num):
            sheet = workbook.sheet_by_index(i)
            while (i < sheet.nrows):
                # print i
                j = 0
                while (j < sheet.ncols):
                    content = content + ('\t') + sheet.cell(i, j).value.encode('utf-8')
                    # print j, sheet.cell(i,j).value.encode('utf-8')
                    j += 1
                i += 1
        return content
