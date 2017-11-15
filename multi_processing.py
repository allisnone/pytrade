#! /usr/bin/env python
# -*- coding:utf-8   -*-
# __author__ == "tyomcat"
# "4 cpu"

#https://www.cnblogs.com/huanxiyun/articles/5826902.html
#http://www.cnblogs.com/Tour/p/4564710.html
import multiprocessing
from multiprocessing import Pool
import os, time

def long_time_task(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    i = 0
    while i<3:
        time.sleep(3)
        print('Task %s (%s) sleep 3 seconds'% (name, os.getpid()))
        i = i + 1
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))
    return os.getpid()

def callback_show(v):
    print('sub_pid=',v)
    
def map_task(data):
    start = time.time()
    i = 0
    data_value = data
    data_name =data
    if isinstance(data, int):
        pass
    elif isinstance(data, tuple):
        data_name = data[0]
        data_value =data[1]
        while i<3:
            time.sleep(1)
            data_value = data_value * data_value
            print('Task %s (%s) sleep 3 seconds: %s,%s'% (data_name, os.getpid(),i,data_value))
            i = i + 1
    else:
        while i<3:
            time.sleep(1)
            print('Task %s (%s) sleep 3 seconds: %s'% (data_name, os.getpid(),i))
            i = i + 1
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (data_name, (end - start)))
"""
if __name__=='__main__':
    
    print('Parent process %s.' % os.getpid())
    sub_pid=[0,0,0,0]
    p = Pool(multiprocessing.cpu_count())
    for i in range(4):
        sub_pid[i] = p.apply_async(long_time_task, args=(i,),callback=callback_show)
        
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('sub_pid0=',sub_pid[0].get())
    print('All subprocesses done.')
"""
if __name__=='__main__':
    start = time.time()
    names = ['a','b','c','d','e','f','g','h']
    data = [1,2,3,4,5,6,7,8]
    p2 = Pool(5)
    #p2.map(map_task,names)
    p2.map(map_task,zip(names,data))
    print('Waiting for all subprocesses done...')
    p2.close()
    p2.join()
    end = time.time()
    print('Task %s runs %0.2f seconds.' % ('all', (end - start)))
    print('All subprocesses done.')
    


