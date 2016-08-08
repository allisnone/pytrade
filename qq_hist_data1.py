#-*- coding: UTF-8 -*- 
'''
Created on 2016-8-1
@author: Jason
'''
import urllib.request
import csv
#http://hq.sinajs.cn/list=sh000001
#http://qt.gtimg.cn/q=sh000001
#http://qt.gtimg.cn/q=sh000001
#http://qt.gtimg.cn/q=sh000016#http://qt.gtimg.cn/q=sz399001
#http://qt.gtimg.cn/q=sz399005
#http://qt.gtimg.cn/q=sz399006
#http://www.07net01.com/2015/10/953702.html
#ichart.yahoo.com/table.csv?s=000001.SS&a=06&b=8&c=2016&d=07&e=8&f=2016&g=d
#ichart.yahoo.com/table.csv?s=000001.SS&a=06&b=8&c=2016&d=07&e=8&f=2016&g=d
#http://qt.gtimg.cn/q=sh000001

#http://blog.chinaunix.net/uid-22414998-id-3487668.html

url = 'http://qt.gtimg.cn/q=sh000001'
url = 'http://ichart.yahoo.com/table.csv?s=000001.SS&a=06&b=8&c=2016&d=07&e=8&f=2016&g=d'
req = urllib.request.Request(url)
response = urllib.request.urlopen(req)
#the_page = response.read() 
the_page = response.read().decode('utf-8')#.encode('utf-8') 

print(the_page)
data_str = the_page.split('\n')
data_list = []
data =[]
fields = data_str[0].split(',')
dict_len = len(fields)
for i in range(0,dict_len):
    fields[i] = fields[i].strip('\00').encode()
print('fields=',fields)
for one_str in data_str[1:-1]:
    one_data = one_str.split(',')
    print(one_data)
    
    one_dict = dict()
    for i in range(dict_len):
        one_data[i] = one_data[i].strip('\00').encode()
        one_data[i] = bytes(one_data[i],encoding="utf-8")
        one_dict[fields[i]] = one_data[i]
    data_list.append(one_data)
    data.append(one_dict)
print(data)
#csvfile = file('sh0001.csv','wb')
with open('sh0001.csv', 'wb') as csvfile:
    csv_writer = csv.writer(csvfile)
    dict_writer = csv.DictWriter(csvfile,fields)
#csv.writer(the_page,'utf-8')
#csv_writer.writerow(data[0])
#csv_writer.writerows(data)
#data.insert(0, fieldnames)
#fields = [1,2,3,4,5,6]
#csv_writer.writerow(fields)
#csv_writer.writerow(the_page)
csv_writer.writerows(data_list)
