# -*- coding:utf-8 -*-
import smtplib
from email.mime import text
from email.mime.text import MIMEText

def send_mail(sub,content,mail_to_list=None):
    """
    :param mailto_list: list type, receiver email address,like ['104450966@qq.com','3151173548@qq.com']
    :param sub: str type, subject of email title
    :param content: str type, content of email title
    :return: bool type 
    """
    mailto_list=['104450966@qq.com']
    if mail_to_list!=None:
        mailto_list=mail_to_list
    mail_host='smtp.163.com'
    mail_user='zgx20022002@163.com'
    mail_pass='821853Zgx'  
    mail_postfix="qq.com"
    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content)  
    msg['Subject'] = sub  
    msg['From'] = mail_user 
    msg['To'] = ";".join(mailto_list)
    """
    s=smtplib.SMTP_SSL(mail_host,465)
    s.login(mail_user,mail_pass)  
    s.sendmail(mail_user, mailto_list, msg.as_string())  
    s.close()
    """  
    try:  
        #s = smtplib.SMTP()
        s=smtplib.SMTP_SSL(mail_host,465)
        s.login(mail_user,mail_pass)  
        s.sendmail(mail_user, mailto_list, msg.as_string())  
        s.close()  
        return True  
    except:# SMTPDataError as e:
        print("send mail failure to ",mailto_list)
        #print(e)
        return False
#"""

def form_mail_info(market_type,score,symbol=None, position_unit=None,give_content=None):
    sub=''
    content=''
    position_handle=0.33
    if position_unit!=None:
        position_handle=position_unit
    if market_type=='system':
        sub='A股系统风险监测'
        if give_content!=None:
            content=give_content
        else:
            if score<-2.5:
                content='系统风险，系统量化打分=%s (-5~5分)，一键清仓退出。' % score
            elif score<=0:
                content='系统弱势，系统量化打分=%s (-5~5分),最高 %s%%仓位。' % (score,position_handle*100)
            elif score<=2.5:
                content='暂无系统风险，系统量化打分=%s (-5~5分),持仓待涨。' % score
            else:
                content='系统多头强势，系统量化打分=%s (-5~5分),加仓%s%%。' %  (score,position_handle*100)
                
    elif market_type=='stock' and symbol:
        sub='个股监测，股票：%s' % symbol
        if give_content!=None:
            content=give_content
        else:
            if score<-2.5:
                content='股票: %s 量化打分=%s, 大幅回辙, 止损退出' % (symbol,score)
            elif score<=0:
                content='股票: %s 量化打分=%s,短期弱势, 减仓%s%%' % (symbol,score,position_handle*100)
            elif score<=2.5:
                content='股票: %s 量化打分=%s,短期看涨, 持仓待涨' % (symbol,score)
            else:
                content='股票: %s 量化打分=%s,短期看涨, 加仓%s%%' % (symbol,score,position_handle*100)
    else:
        pass
    return  sub,content
"""
if __name__ == '__main__':  
    #send_info=[['104450966@qq.com','sub1','content1'],['3151173548@qq.com','sub2','content2'] ]
    market_type='system'
    market_type='stock'
    score=-2.6
    symbol='000987'
    give_content='仅仅是测试'
    sendto_list=['104450966@qq.com','3151173548@qq.com']
    sub,content=form_mail_info(market_type, score)#,give_content=give_content)
    print(content)
    send_mail(sub,content,sendto_list)
"""
    
