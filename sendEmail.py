# -*- coding:utf-8 -*-
import smtplib
from email.mime import text
from email.mime.text import MIMEText

def send_position_mail(position_df,symbol=None):
    if position_df.empty:
        return
    sys_score=position_df.tail(1).iloc[0].sys_score
    position=position_df.tail(1).iloc[0].position
    operation=position_df.tail(1).iloc[0].operation
    latest_day=position_df.tail(1).index.values.tolist()[0]
    #sendto_list=['104450966@qq.com']#,'40406275@qq.com']#,'jason.g.zhang@ericsson.com']#,'david.w.song@ericsson.com']#,'3151173548@qq.com']
    sendto_list=[['104450966@qq.com']]#,['40406275@qq.com']]#,'jason.g.zhang@ericsson.com']#,'david.w.song@ericsson.com']#,'3151173548@qq.com']
    sub,content=get_score_content(score=sys_score,position_unit=position,symbol=symbol)#,give_content=give_content)
    sub = sub + ' ' + latest_day
    sub,additional_content=get_position_content(sub,position, operation)
    content = content + additional_content
    content = content + '\n' + '近10天系统风险和仓位量化： \n' + '%s'% position_df.tail(10)
    #print(content)
    for sendto in sendto_list:
        send_mail(sub,content,sendto)

def send_mail(sub,content,mail_to_list=None,limit_try=50):
    """
    :param mailto_list: list type, receiver email address,like ['104450966@qq.com','3151173548@qq.com']
    :param sub: str type, subject of email title
    :param content: str type, content of email title
    :return: bool type 
    """
    mailto_list=['104450966@qq.com']
    #mailto_list=['104450966@qq.com','1016564866@qq.com']
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
        limit_try= limit_try -1
        if limit_try>0:
            print('Try to send mail again')
            send_mail(sub,content,mail_to_list,limit_try)
        else:
            return False
        #print(e)
        
#"""
#send_mail(sub='test', content='test')
def get_score_content(score,symbol=None, position_unit=None,give_content=None):
    sub=''
    content=''
    position_handle=0.33
    if position_unit!=None:
        position_handle=position_unit
    if symbol==None: #system risk
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
                
    else:
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
    return  sub,content

def get_position_content(sub,position, operation):
    additional_content = '\n'
    if position>0.6:
        pass
    elif position>0.3:
        sub = '[alarm]' + sub
        suggest_pos = position*100
        sugestion = '建议轻仓操作,持仓不超过  %s%%的仓位' % suggest_pos
        additional_content = additional_content + sugestion
    else:
        sub = '[alert]' + sub
        suggest_pos = position*100
        sugestion = '建议空仓,持仓最多不超过  %s%%的仓位' % suggest_pos
        additional_content = additional_content + sugestion
    if operation<-0.3 or operation>0.3:
        if '[alarm]' in sub:
            sub = '[alert]' + sub[6:]
        elif '[alert]' in sub:
            pass
        else:
            pass
        operation = operation*100
        oper='减仓'
        if operation>0:
            oper='加仓'
        sugestion = '\n!!!!!\n系统反向激烈波动，建议'+ oper + '%s%% 至 %s%%的仓位 。' % (operation,position*100)
        additional_content = additional_content + sugestion
    else:
        pass
    return sub,additional_content
    
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
    
