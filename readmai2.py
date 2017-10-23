import poplib  
from email.parser import Parser  
from email.header import decode_header  
from email.utils import parseaddr  
import datetime
#email = input('Email:')  
#password = input('Password: ')  

email = "zgx20022002@163.com"

# Email password
password = "821853Zgx"

#pop3_server = input('POP3 server: ')  
pop3_server = 'pop.163.com'  
#这是检测编码部分，有点不懂  
def guess_charset(msg):  
    charset = msg.get_charset()  
    if charset is None:  
        content_type = msg.get('Content-type', '').lower()  
        pos = content_type.find('charset=')  
        if pos >= 0:  
            charset = content_type[pos + 8:].strip()  
    return charset  
#这里只取出第一发件人  
def decode_str(s):  
    value, charset = decode_header(s)[0]  
    if charset:  
        value = value.decode(charset)  
    return value  
#递归打印信息  

def get_mail_msg(pop_connection,mail_index,decoder='GBK'):
    resp, lines, octets = pop_connection.retr(mail_index)
    msg = ''
    try:
        msg_content = b'\r\n'.join(lines).decode(decoder)
        msg = Parser().parsestr(msg_content) 
    except:
        pass
    return msg


def get_msg_property(msg,property=['From', 'To', 'Subject','Date']):
    result = {}
    for header in property:  
        value = msg.get(header, '') 
        #print('value=',value) 
        if value:  
            if header == 'Subject' or header=='Date':  
                value = decode_str(value)  
            else:  
                hdr, addr = parseaddr(value)  
                name = decode_str(hdr)  
                value = u'%s <%s>' % (name, addr)
            result[header] = value
        #print('%s%s: %s' % ('  ' * indent, header, value))  
    return result
            
def print_info(msg, indent = 0,charset='GBK'):  
    if indent == 0:
        """
        for header in ['From', 'To', 'Subject','Date']:  
            value = msg.get(header, '') 
            print('value=',value) 
            if value:  
                if header == 'Subject' or header=='Date':  
                    value = decode_str(value)  
                else:  
                    hdr, addr = parseaddr(value)  
                    name = decode_str(hdr)  
                    value = u'%s <%s>' % (name, addr)  
            print('%s%s: %s' % ('  ' * indent, header, value)) 
        """
        result = get_msg_property(msg)
        print('result=',result)
    if (msg.is_multipart()):  
        parts = msg.get_payload()  
        for n, part in enumerate(parts):  
            print('%spart %s' % ('  '*indent, n))  
            print('%s--------------------' % ('   '*indent))  
            print_info(part, indent + 1)  
    else:  
        content_type = msg.get_content_type()  
        if content_type == 'text/plain' or content_type == 'text/html':  
            content = msg.get_payload(decode = True)  
            charset = guess_charset(msg)  
            print('content=',content)
            if charset:  
                #content = content.decode(charset)  
                try:
                    content = content.decode(charset)
                    print('%sText: %s' % ('  '*indent, content + '...'))  
                except:
                    print('contect decide exception')
            
        else:  
            print('%sAttachment: %s' % ('  '*indent, content_type))  
  
#下载原始邮件  
server = poplib.POP3(pop3_server)  
server.set_debuglevel(0)  
print(server.getwelcome().decode('utf-8'))  
server.user(email)  
server.pass_(password)  
#打印邮件数量和占用空间  

print('Message: %s, Size: %s' % server.stat())  
resp, mails, octets = server.list()  
print('mails=',mails)  
  
#解析邮件  
index = len(mails)  
ind =index
while True:#ind>0:
    """
    resp, lines, octets = server.retr(ind)  
    print('head=',resp)
    #msg_content = b'\r\n'.join(lines).decode('utf-8')  
    #try:
    if True:
        msg_content = b'\r\n'.join(lines).decode('GBK')
        msg = Parser().parsestr(msg_content) 
        print('msg=',msg)
        #print_info(msg) 
        result = get_msg_property(msg)
        print('result=',result)
    #except:
    #    pass 
    """
    resp, mails, octets = server.list()  
    index = len(mails)  
    ind =index
    print(datetime.datetime.now())
    msg = get_mail_msg(pop_connection=server,mail_index=ind,decoder='GBK')
    result = get_msg_property(msg)
    print('result=',result)
    ind = ind - 1
    #break
  
      
server.quit()  