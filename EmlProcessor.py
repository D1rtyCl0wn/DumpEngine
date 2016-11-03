'''
by D1rtyCl0wn

eml operations
thanks to all, whose code was used while developing this
as an example for displaying EMLs as HTML i took the template of DCLeaks, thought it is quite good one for this
'''

# -*- coding: utf-8 -*-


from email.header import decode_header
from email.parser import Parser
import email.utils
import os, StringIO
import email, codecs
from emaildata.attachment import Attachment
import urllib, re

class EmlProcessor():
    headers=None
def listDirectory(path):
    listDir = os.listdir(path)
    return listDir


def listEML(path):
    ls = listDirectory(path)
    if not ls == None:
        emls = []
        for item in ls:
            if item.endswith('.eml'):
                emls.append(os.path.join(path, item))
            # print emls
        return emls
    else:
        return None

def getHeaders(filename):
    with open(filename) as fp:
        headers = Parser().parse(fp)
    return headers


def getTo(headers):
    to = decode_header(headers['to'])
    return to


def getCC(headers):
    cc = decode_header(headers['cc'])
    return cc


def getFrom(headers):
    from_h = decode_header(headers['from'])
    return from_h


def getSubject(headers):
    subj = decode_header(headers['subject'])
    return subj


def getDate(headers):
    sendDate = headers['date']
    return sendDate


def strDateToLong(sendDate):
    try:
        dateTuple = email.utils.parsedate_tz(sendDate)
        return email.utils.mktime_tz(dateTuple)
    except:
        return 0

def get_text_content(eml):
    msg = email.message_from_file(open(eml))
    attachments = get_mail_contents(msg)
    content_string = ""
    for attach in attachments:
        if attach.is_body == 'text/plain':
            text = ''
            # print first 3 lines
            payload, used_charset = decode_text(attach.payload, attach.charset, 'auto')
            for line in payload.split('\n'):
                # be careful console can be unable to display unicode characters
                if line:
                    text = text + line + ' '
            text = text.encode('utf-8')
            text = re.sub('<[^>]*>', ' ', text)
            text = text.translate(None, '”!@#$%^&*()<>?/.,:;\'"|}{[]\\-_=+~`")')
            text=text.replace('\r\n',' ').replace('\n',' ').replace('\r',' ')
            content_string = content_string + text

        if attach.is_body == 'text/html':
            payload, used_charset = decode_text(attach.payload, attach.charset, 'auto')
            html = ""
            for line in payload.split('\n'):
                if line:
                    html = html + line + ' '
            html = html.encode('utf-8')
            content_string = content_string + re.sub('<[^>]*>', ' ', html).translate(None,
                                                                                     '”!@#$%^&*()<>?/.,:;\'"|}{[]\\-_=+~`")')

    return content_string


def get_string(strOrUnicode, encoding='utf-8'):
    strOrUnicode = __if_number_get_string(strOrUnicode)
    if isinstance(strOrUnicode, unicode):
        return strOrUnicode.encode(encoding)
    return strOrUnicode


def __if_number_get_string(number):
    converted_str = number
    if isinstance(number, int) or \
            isinstance(number, float):
        converted_str = str(number)
    return converted_str


def get_unicode(strOrUnicode, encoding='utf-8'):
    strOrUnicode = __if_number_get_string(strOrUnicode)
    if isinstance(strOrUnicode, unicode):
        return strOrUnicode
    return unicode(strOrUnicode, encoding, errors='ignore')


def eml_to_html(eml, out_path):
    # print "Converting ", eml, "\n"
    msg = email.message_from_file(open(eml))
    attachments = get_mail_contents(msg)
    headers = getHeaders(eml)
    subject = getSubject(headers)
    subj_string = "".encode('utf-8')
    if (subject[0][1] == None):
        subj_string = unicode(subject[0][0], 'utf-8', errors='ignore')
    else:
        subj_string = subject[0][0].decode(subject[0][1]).encode('utf-8')

    orig_subj_str = get_string(subj_string)
    # print orig_subj_str
    subj_string = subj_string.replace('"', "_")
    # subj_string = subj_string.replace('\'',"_")
    subj_string = subj_string.replace('<', "_")
    subj_string = subj_string.replace('>', "_")
    subj_string = subj_string.replace('/', "_")
    subj_string = subj_string.replace('\\', "_")
    subj_string = subj_string.replace(':', "_")
    subj_string = subj_string.replace('?', "_")
    subj_string = subj_string.replace('*', "_")
    subj_string = subj_string.replace('|', "_")
    subj_string = subj_string.replace('\t', "_")
    subj_string = subj_string.replace('\r\n', "_")
    subj_string = subj_string.replace('\n', "__")

    from_string = "".encode('utf-8')
    from_header = getFrom(headers)
    # print from_header
    for f in from_header:
        if (f[1] == None):
            from_string = from_string + f[0].replace("'", "").replace('"', "").decode('utf-8').encode('utf-8')
        else:
            from_string = from_string + f[0].decode(f[1]).encode('utf-8')
    orig_from_s = get_string(from_string)
    from_string = from_string.replace("\"", " ")
    from_string = from_string.replace("'", " ")
    from_string = from_string.replace("<", " ")
    from_string = from_string.replace(">", " ")
    from_string = from_string.replace("\\", " ")
    from_string = from_string.replace("/", " ")

    to = getTo(headers)
    to_string = "".encode('utf-8')
    for t in to:
        if (t[1] == None):
            # print t[0]
            to_string = to_string + " " + t[0].replace("'", "").replace('"', "").decode('utf-8').encode('utf-8')
        else:
            # print t[0].decode(t[1])
            to_string = to_string + " " + t[0].decode(t[1]).encode('utf-8')
    orig_to_s = get_string(to_string)
    to_string = to_string.replace("\"", " ")
    to_string = to_string.replace("'", " ")
    to_string = to_string.replace("<", " ")
    to_string = to_string.replace(">", " ")
    to_string = to_string.replace("/", " ")
    to_string = to_string.replace("\\", " ")

    s_date = getDate(headers)
    if s_date==None:
        s_date="Unknown"

    out_fname = os.path.join(out_path, os.path.basename(eml).split('.eml', 1)[0] + '.html')
    html_headers = '<html><head><META content="text/html; charset=utf-8" http-equiv=Content-Type><meta charset="UTF-8"> <STYLE>.MailHeader3 {TEXT-ALIGN: right; WRITING-MODE: lr-tb; MARGIN: 0px; COLOR: black; FONT-SIZE: 12px; VERTICAL-ALIGN: top; FONT-WEIGHT: bold}.MailHeader4 {MARGIN: 0px; COLOR: black; FONT-SIZE: 12px; VERTICAL-ALIGN: middle; FONT-WEIGHT: normal}</STYLE></head><body>'
    html_headers = html_headers + '<div id=HtmlMerger><TABLE style="BORDER-BOTTOM: #a0a0a0 1px solid; PADDING-BOTTOM: 0px; BACKGROUND-COLOR: #ffffff; MARGIN: 0px; PADDING-LEFT: 0px; PADDING-RIGHT: 0px; PADDING-TOP: 0px" border=0 cellSpacing=0 cellPadding=2 width="100%"><TBODY>'
    html_email_headers = '<TR><TD><SPAN class=MailHeader3>From:&nbsp;&nbsp;</SPAN></TD><TD><SPAN class=MailHeader4>' + orig_from_s.replace(
        "<", "&lt;").replace(">", "&gt;").replace("\n", "\n<br>") + '</SPAN></TD></TR>'
    html_email_headers = html_email_headers + '<TR><TD><SPAN class=MailHeader3>Sent&nbsp;time:&nbsp;&nbsp;</SPAN></TD><TD><SPAN class=MailHeader4>' + s_date + '</SPAN></TD></TR>'
    html_email_headers = html_email_headers + '<TR><TD><SPAN class=MailHeader3>To:&nbsp;&nbsp;</SPAN></TD><TD><SPAN class=MailHeader4>' + orig_to_s.replace(
        "<", "&lt;").replace(">", "&gt;").replace("\n", "\n<br>") + '</SPAN></TD></TR>'
    html_email_headers = html_email_headers + '<TR><TD><SPAN class=MailHeader3>Subject:&nbsp;&nbsp;</SPAN></TD><TD><SPAN class=MailHeader4>' + orig_subj_str.replace(
        "<", "&lt;").replace(">", "&gt;").replace("\n", "\n<br>") + '</SPAN></TD></TR>'
    html_headers = html_headers + html_email_headers + '<TR><TD style="PADDING-BOTTOM: 0px; PADDING-LEFT: 0px; PADDING-RIGHT: 0px; FONT-SIZE: 5px; PADDING-TOP: 0px" colSpan=2>&nbsp; </TD></TR></TBODY></TABLE></DIV><BR>'

    html_headers = get_string(html_headers)
    with  codecs.open(out_fname, 'w') as export_file:
        export_file.write(html_headers)

    attach_list = []

    for attach in attachments:
        fdir = os.path.join(out_path, os.path.basename(out_fname).split('.html', 1)[0] + '_files')
        dict_att_cid = {}

        if attach.is_body == 'text/plain':
            text = ''
            # print first 3 lines
            payload, used_charset = decode_text(attach.payload, attach.charset, 'auto')
            # payload = payload.decode(attach.charset).encode('utf-8')

            for line in payload.split('\n'):
                # be careful console can be unable to display unicode characters
                if line:
                    # print '\t\t', line
                    text = text + line + '\n<br>'
            # print text
            text.encode('utf-8')
            with  codecs.open(out_fname, 'a', encoding='utf-8') as export_file:
                export_file.write(text)

        if attach.is_body == 'text/html':
            html_pre = '<div id="inner-html"><pre>'
            # print first 3 lines
            payload, used_charset = decode_text(attach.payload, attach.charset, 'auto')

            for line in payload.split('\n'):
                # be careful console can be unable to display unicode characters
                if line:
                    # print '\t\t', line
                    html_pre = html_pre + line + '\n<br>'
            html_pre = html_pre + '</pre></div>'
            with  codecs.open(out_fname, 'a', encoding='utf-8') as export_file:
                export_file.write(html_pre)

        if attach.is_body == None:
            # print attach.type
            filename = 'file'.encode('utf-8')
            # attach_list.append(filename)
            try:
                # print attach.type
                filename = attach.filename.encode('utf-8')

                # fdir = os.path.join(out_path,os.path.basename(out_fname).split('.html',1)[0]+'_files')
                # print fdir
                if not os.path.exists(fdir):
                    os.makedirs(fdir)
                fnam = os.path.join(fdir, filename)
                # print fnam

                content = attach.payload
                fd = open(fnam, 'wb')
                fd.write(content)
                fd.close()

            except Exception as detail:
                print detail
                pass
            finally:
                attach_list.append(filename)
            if 'image' in attach.type:
                cid = attach.content_id
                dict_att_cid[cid] = os.path.join(fdir, filename)
                # print "Processing image...\n", cid,"::", filename
    if len(attach_list) > 0:
        with codecs.open(out_fname, 'a', encoding='utf-8') as export_file:
            export_file.write(
                '<hr><h4>Attachments:</h4><hr><TABLE style="BORDER-BOTTOM: #a0a0a0 1px solid; PADDING-BOTTOM: 0px; BACKGROUND-COLOR: #ffffff; MARGIN: 0px; PADDING-LEFT: 0px; PADDING-RIGHT: 0px; PADDING-TOP: 0px" border=0 cellSpacing=0 cellPadding=2 width="100%"><TBODY>')
            for att in attach_list:
                # print att
                # print os.path.join(fdir,att)
                try:
                    export_file.write('<TR><TD><SPAN class=MailHeader4><a href="' + os.path.join(
                        os.path.basename(out_fname).split('.html', 1)[0] + '_files',
                        att.decode('utf-8')) + '">' + att.decode('utf-8') + '</a></SPAN></TD></TR>')
                except Exception as e:
                    print "exception: ", e
            export_file.write('</TBODY></TABLE>')

    with  codecs.open(out_fname, 'a', encoding='utf-8') as export_file:
        export_file.write('</body></html>')

    temp = open(out_path + os.path.sep + 'temp', 'a')
    fedit = open(out_fname, 'r')
    for line in fedit.readlines():
        if '"cid:' in line:
            cid = line.split('"cid:')[1].split('"')[0]
            # print "the cid is ",cid
            try:
                line = line.replace('"cid:' + cid.replace("'", '') + '"', "file:///" + urllib.quote(dict_att_cid[cid]))
            except Exception as detail:
                print "exc ", detail
                pass
                # print line
        temp.write(line)
    temp.close()
    fedit.close()
    fedit = open(out_fname, 'w')
    temp = open(out_path + os.path.sep + 'temp', 'r')

    with open(out_path + os.path.sep + 'temp') as temp:
        with open(out_fname, "w") as fedit:
            for line in temp:
                fedit.write(line)
    os.remove(out_path + os.path.sep + 'temp')

    # print "\nEnd processing ", eml, "\n"
    return out_fname


invalid_chars_in_filename = '<>:"/\\|?*\%\'' + reduce(lambda x, y: x + chr(y), range(32), '')
invalid_windows_name = 'CON PRN AUX NUL COM1 COM2 COM3 COM4 COM5 COM6 COM7 COM8 COM9 LPT1 LPT2 LPT3 LPT4 LPT5 LPT6 LPT7 LPT8 LPT9'.split()

# email address REGEX matching the RFC 2822 spec from perlfaq9
#    my $atom       = qr{[a-zA-Z0-9_!#\$\%&'*+/=?\^`{}~|\-]+};
#    my $dot_atom   = qr{$atom(?:\.$atom)*};
#    my $quoted     = qr{"(?:\\[^\r\n]|[^\\"])*"};
#    my $local      = qr{(?:$dot_atom|$quoted)};
#    my $domain_lit = qr{\[(?:\\\S|[\x21-\x5a\x5e-\x7e])*\]};
#    my $domain     = qr{(?:$dot_atom|$domain_lit)};
#    my $addr_spec  = qr{$local\@$domain};
#
# Python's translation

atom_rfc2822 = r"[a-zA-Z0-9_!#\$\%&'*+/=?\^`{}~|\-]+"
atom_posfix_restricted = r"[a-zA-Z0-9_#\$&'*+/=?\^`{}~|\-]+"  # without '!' and '%'
atom = atom_rfc2822
dot_atom = atom + r"(?:\." + atom + ")*"
quoted = r'"(?:\\[^\r\n]|[^\\"])*"'
local = "(?:" + dot_atom + "|" + quoted + ")"
domain_lit = r"\[(?:\\\S|[\x21-\x5a\x5e-\x7e])*\]"
domain = "(?:" + dot_atom + "|" + domain_lit + ")"
addr_spec = local + "\@" + domain

email_address_re = re.compile('^' + addr_spec + '$')


class Attachment:
    def __init__(self, part, filename=None, type=None, payload=None, charset=None, content_id=None, description=None,
                 disposition=None, sanitized_filename=None, is_body=None):
        self.part = part  # original python part
        self.filename = filename  # filename in unicode (if any)
        self.type = type  # the mime-type
        self.payload = payload  # the MIME decoded content
        self.charset = charset  # the charset (if any)
        self.description = description  # if any
        self.disposition = disposition  # 'inline', 'attachment' or None
        self.sanitized_filename = sanitized_filename  # cleanup your filename here (TODO)
        self.is_body = is_body  # usually in (None, 'text/plain' or 'text/html')
        self.content_id = content_id  # if any
        if self.content_id:
            # strip '<>' to ease searche and replace in "root" content (TODO)
            if self.content_id.startswith('<') and self.content_id.endswith('>'):
                self.content_id = self.content_id[1:-1]


def getmailheader(header_text, default="ascii"):
    """Decode header_text if needed"""
    try:
        headers = email.Header.decode_header(header_text)
    except email.Errors.HeaderParseError:
        # This already append in email.base64mime.decode()
        # instead return a sanitized ascii string
        # this faile '=?UTF-8?B?15HXmdeh15jXqNeVINeY15DXpteUINeTJ9eV16jXlSDXkdeg15XXldeUINem15PXpywg15TXptei16bXldei15nXnSDXqdecINek15zXmdeZ?==?UTF-8?B?157XldeR15nXnCwg157Xldek16Ig157Xl9eV15wg15HXodeV15bXnyDXk9ec15DXnCDXldeh15gg157Xl9eR16rXldeqINep15wg15HXmdeQ?==?UTF-8?B?15zXmNeZ?='
        return header_text.encode('ascii', 'replace').decode('ascii')
    else:
        for i, (text, charset) in enumerate(headers):
            try:
                headers[i] = unicode(text, charset or default, errors='replace')
            except LookupError:
                # if the charset is unknown, force default
                headers[i] = unicode(text, default, errors='replace')
        return u"".join(headers)


def getmailaddresses(msg, name):
    """retrieve addresses from header, 'name' supposed to be from, to,  ..."""
    addrs = email.utils.getaddresses(msg.get_all(name, []))
    for i, (name, addr) in enumerate(addrs):
        if not name and addr:
            # only one string! Is it the address or is it the name ?
            # use the same for both and see later
            name = addr

        try:
            # address must be ascii only
            addr = addr.encode('ascii')
        except UnicodeError:
            addr = ''
        else:
            # address must match address regex
            if not email_address_re.match(addr):
                addr = ''
        addrs[i] = (getmailheader(name), addr)
    return addrs


def get_filename(part):
    """Many mail user agents send attachments with the filename in
    the 'name' parameter of the 'content-type' header instead
    of in the 'filename' parameter of the 'content-disposition' header.
    """
    filename = part.get_param('filename', None, 'content-disposition')
    if not filename:
        filename = part.get_param('name', None)  # default is 'content-type'

    if filename:
        # RFC 2231 must be used to encode parameters inside MIME header
        filename = email.Utils.collapse_rfc2231_value(filename).strip()

    if filename and isinstance(filename, str):
        # But a lot of MUA erroneously use RFC 2047 instead of RFC 2231
        # in fact anybody miss use RFC2047 here !!!
        filename = getmailheader(filename)

    return filename


def _search_message_bodies(bodies, part):
    """recursive search of the multiple version of the 'message' inside
    the the message structure of the email, used by search_message_bodies()"""

    type = part.get_content_type()
    if type.startswith('multipart/'):
        # explore only True 'multipart/*'
        # because 'messages/rfc822' are also python 'multipart'
        if type == 'multipart/related':
            # the first part or the one pointed by start
            start = part.get_param('start', None)
            related_type = part.get_param('type', None)
            for i, subpart in enumerate(part.get_payload()):
                if (not start and i == 0) or (start and start == subpart.get('Content-Id')):
                    _search_message_bodies(bodies, subpart)
                    return
        elif type == 'multipart/alternative':
            # all parts are candidates and latest is best
            for subpart in part.get_payload():
                _search_message_bodies(bodies, subpart)
        elif type in ('multipart/report', 'multipart/signed'):
            # only the first part is candidate
            try:
                subpart = part.get_payload()[0]
            except IndexError:
                return
            else:
                _search_message_bodies(bodies, subpart)
                return

        elif type == 'multipart/signed':
            # cannot handle this
            return

        else:
            # unknown types must be handled as 'multipart/mixed'
            # This is the peace of code could probably be improved, I use a heuristic :
            # - if not already found, use first valid non 'attachment' parts found
            for subpart in part.get_payload():
                tmp_bodies = dict()
                _search_message_bodies(tmp_bodies, subpart)
                for k, v in tmp_bodies.iteritems():
                    if not subpart.get_param('attachment', None, 'content-disposition') == '':
                        # if not an attachment, initiate value if not already found
                        bodies.setdefault(k, v)
            return
    else:
        bodies[part.get_content_type().lower()] = part
        return

    return


def search_message_bodies(mail):
    """search message content into a mail"""
    bodies = dict()
    _search_message_bodies(bodies, mail)
    return bodies


def get_mail_contents(msg):
    """split an email in a list of attachments"""

    attachments = []

    # retrieve messages of the email
    bodies = search_message_bodies(msg)
    # reverse bodies dict
    parts = dict((v, k) for k, v in bodies.iteritems())

    # organize the stack to handle deep first search
    stack = [msg, ]
    while stack:
        part = stack.pop(0)
        type = part.get_content_type()
        if type.startswith('message/'):
            # ('message/delivery-status', 'message/rfc822', 'message/disposition-notification'):
            # I don't want to explore the tree deeper her and just save source using msg.as_string()
            # but I don't use msg.as_string() because I want to use mangle_from_=False
            from email.Generator import Generator
            fp = StringIO.StringIO()
            g = Generator(fp, mangle_from_=False)
            g.flatten(part, unixfrom=False)
            payload = fp.getvalue()
            filename = 'mail.eml'
            attachments.append(
                Attachment(part, filename=filename, type=type, payload=payload, charset=part.get_param('charset'),
                           description=part.get('Content-Description')))
        elif part.is_multipart():
            # insert new parts at the beginning of the stack (deep first search)
            stack[:0] = part.get_payload()
        else:
            payload = part.get_payload(decode=True)
            charset = part.get_param('charset')
            filename = get_filename(part)

            disposition = None
            if part.get_param('inline', None, 'content-disposition') == '':
                disposition = 'inline'
            elif part.get_param('attachment', None, 'content-disposition') == '':
                disposition = 'attachment'

            attachments.append(Attachment(part, filename=filename, type=type, payload=payload, charset=charset,
                                          content_id=part.get('Content-Id'),
                                          description=part.get('Content-Description'), disposition=disposition,
                                          is_body=parts.get(part)))

    return attachments


def decode_text(payload, charset, default_charset):
    if charset:
        try:
            return payload.decode(charset), charset
        except UnicodeError:
            pass

    if default_charset and default_charset != 'auto':
        try:
            return payload.decode(default_charset), default_charset
        except UnicodeError:
            pass

    for chset in ['ascii', 'utf-8', 'utf-16', 'windows-1252', 'cp850', 'koi8-r']:
        try:
            return payload.decode(chset), chset
        except UnicodeError:
            pass

    return payload, None