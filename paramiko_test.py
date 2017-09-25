#!/usr/bin/python
# encoding=utf-8
# Filename: paramiko_test.py
import datetime
import threading
import paramiko


class Myssh(object):
    def __init__(self):
        self.cmds = []
        self.servers = {}
        pass
    
    def set_cmds(self,cmds):
        self.cmds = cmds
        
    def add_server(self,server_ip,username,password):
        #server = {'ip':'192.168.1.1','username':'root','password':'root'}
        server_info = {'username':username,'password':password}
        self.servers.update({'server_ip':server_info})
        
    def delete_server(self,server_ip):
        self.servers.pop(server_ip)
        
    def add_servers(self,server_list=[]):
        for serv in server_list:
            if len(serv)>=3:
                server_ip,username,password=serv[0],serv[1],serv[2]
                self.add_server(server_ip, username, password)
            else:
                pass
            
        return    
        
    def empty_servers(self):
        self.servers=[]
        
    def sshCmd(self,ip, username, passwd, cmds):
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            client.connect(ip, 22, username, passwd, timeout=5)
            for cmd in cmds:
                stdin, stdout, stderr = client.exec_command(cmd)
                lines = stdout.readlines()
                # print out
                for line in lines:
                    print line,
            print '%s\t 运行完毕\r\n' % (ip)
        except Exception, e:
            print '%s\t 运行失败,失败原因\r\n%s' % (ip, e)
        finally:
            client.close()

    #上传文件
    def uploadFile(self,ip,username,passwd):
        try:
            t=paramiko.Transport((ip,22))
            t.connect(username=username,password=passwd)
            sftp=paramiko.SFTPClient.from_transport(t)
            remotepath='/root/main.py'
            localpath='/home/data/javawork/pythontest/src/main.py'
            sftp.put(localpath,remotepath)
            print '上传文件成功'
        except Exception, e:
            print '%s\t 运行失败,失败原因\r\n%s' % (ip, e)
        finally:
            t.close()

    #下载文件
    def downloadFile(self,ip,username,passwd):
        try:
            t=paramiko.Transport((ip,22))
            t.connect(username=username,password=passwd)
            sftp=paramiko.SFTPClient.from_transport(t)
            remotepath='/root/storm-0.9.0.1.zip'
            localpath='/home/data/javawork/pythontest/storm.zip'
            sftp.get(remotepath,localpath)
            print '下载文件成功'
        except Exception, e:
            print '%s\t 运行失败,失败原因\r\n%s' % (ip, e)
        finally:
            t.close()  
            
    def server_processing(self):
        # 需要执行的命令列表
        cmds = ['uptime', 'ifconfig']
        # 需要进行远程监控的服务器列表
        server_list = ['xxx.xxx.xxx.xxx']
        self.add_servers(server_list)
        username = "root"
        passwd = "xxxxxx"
        threads = []
        print "程序开始运行%s" % datetime.datetime.now()
        # 每一台服务器创建一个线程处理
        if not self.servers:
            return
        
        for server_ip in list(self.servers.keys()):
            server_ip = server['ip']
            username = self.servers[server_ip]['username']
            passwd = self.servers[server_ip]['password']
            th = threading.Thread(target=sshCmd, args=(server, username, passwd, self.cmds))
            th.start()
            threads.append(th)
    
        # 等待线程运行完毕
        for th in threads:
            th.join()
    
        print "程序结束运行%s" % datetime.datetime.now()
    
        #测试文件的上传与下载
        #uploadFile(servers[0],username,passwd)
        #downloadFile(servers[0],username,passwd)
