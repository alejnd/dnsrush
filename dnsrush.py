#!/usr/bin/env python
#  coding: utf-8

# dnsrush: Parallel DNS resolver
import sys
import os.path 
import threading
import socket


dnsipaddr_buffer =[]
n_threads = 30
threads   = []
instructions ="""dnsrush: Parallel DNS resolver.
usage: <dns file rercords> <output file> """
lock  = threading.Lock()

def get_dnsquery():
    lock.acquire()
    if len(query_buffer) < 1: result = False
    else: result = query_buffer.pop().split()[0]
    lock.release()
    return result

def push_dnsquery(query, ipaddr):
    """ append() is thread safe, so no lock is needed"""
    dnsipaddr_buffer.append(query+' , '+ipaddr)
    return

#--- DNS Query helper ------
class Resolver(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__ (self)
        
    def run(self):
        query = get_dnsquery()
        while query:
            try:
                ipaddr = socket.gethostbyname(query)
                push_dnsquery(query, ipaddr)
                print  query, ipaddr,' Threrad:', self.getName()
            except: pass
            query = get_dnsquery()
            

        
if __name__ == '__main__':

#--- Arg parser ------    
    cmd_args = sys.argv[1:]
    if len(cmd_args) !=2: 
        print instructions
        sys.exit() 
    if os.path.isfile(cmd_args[0]): 
        dnsfile    = cmd_args[0]
        outputfile = cmd_args[1]
    else: 
        print 'Invalid input file'
        sys.exit()

    fdns =open(dnsfile,'r')
    query_buffer = fdns.readlines()
    fdns.close()

#--- Thread init ------    
    for i in range(n_threads):
        dns_helper = Resolver()
        threads.append(dns_helper)
        threads[i].setName(i)
        threads[i].start()
    for i in threads: i.join()

#--- Save results -------
    f = open(outputfile,'w')
    for line in dnsipaddr_buffer: f.write(line+'\n')
    f.close()
