#! /usr/bin/env python
# -*- coding:utf-8   -*-
# __author__ == "tyomcat"
# "4 cpu"

from multiprocessing import Pool
import os, time

def long_time_task(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    i = 0
    while i<10:
        time.sleep(3)
        print('Task %s (%s) sleep 3 seconds'% (name, os.getpid()))
        i = i + 1
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))
    
    return 

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    p = Pool()
    for i in range(4):
        p.apply_async(long_time_task, args=(i,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')

