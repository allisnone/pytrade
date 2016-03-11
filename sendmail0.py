# -*- coding:utf-8 -*-
"""
To send mail and notice the state change for EMS sever, MySQL and Web service
Use example: python send_mail.py 'master_server_down'
"""
import smtplib,sys,time
from email.mime.text import MIMEText

def send_keepalived_mail(message,subject,mailto_list):
    """
    Parameters:
    message: string type
    subject: string type
    mailto_list: list type with string email address
    """
    msg = MIMEText(message)       
    msg['Subject'] = subject
    smtp = smtplib.SMTP()
    smtp.connect('142.133.1.1') 
    smtp.sendmail('Administrator@ems.eld.gz.cn.ao.ericsson.se', mailto_list, msg.as_string())  
    smtp.quit()
    return

if __name__ == '__main__':
    message=''
    subject=''
    mailto_list=['jason.g.zhang@ericsson.com']
    msg_type=''
    if len(sys.argv)<=1:
        pass
    else:
        msg_type=sys.argv[1]
    if msg_type=='master_server_down':
        message='Master EMS server(EMS3) is down, switchovered to backup EMS server(EMS0). Please check and recover the Master server.'
        subject='[EMS]Master EMS server switchover'
    elif msg_type=='master_server_normal':
        message='Master EMS server(EMS3) is up, real-server EMS3 works the Master server.'
        subject='[EMS]Master EMS server works normally.'
    elif msg_type=='master_mysql_down':
        message='MySQL service on Master server(EMS3) is down. Please check and recover MySQL service on Master server.'
        subject='[EMS]MySQL service is down on Master EMS server.'
    elif msg_type=='master_http_down':
        message='Web service on Master server(EMS3) is down. Please check and recover Web service on Master server.'
        subject='[EMS]Web service is down on Master EMS server.'
    elif msg_type=='slave_mysql_down':
        message='MySQL service on Slave server(EMS0) is down. Please check and recover MySQL service on Slave server.'
        subject='[EMS]MySQL service is down on Slave EMS server.'
    elif msg_type=='slave_http_down':
        message='Web service on Slave server(EMS0) is down. Please check and recover Web service on Slave server.'
        subject='[EMS]Web service is down on Slave EMS server.'
    else:
        print("Wrong or missing 'msg_type', use example: python send_mail.py 'master_server_down'")
        print("Valid msg_type including: 'master_server_down','master_server_normal', 'master_mysql_down','master_http_down','slave_mysql_down','slave_http_down'")
    
    if message:
        msg_head = 'Dear User, \n \n'
        time_str=time.strftime("%Y-%m-%d %X")
        msg_signature = 'Energy Management System'
        msg_contents=msg_head + time_str + ' ' + message +'\n \n' + msg_signature
        send_keepalived_mail(msg_contents, subject, mailto_list)
    