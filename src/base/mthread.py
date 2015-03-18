#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     mthread.py
# Description:  线程调度      
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      2011-07-24
# Company:      CASCO
# LastChange:   
# History:      create 2011-07-24
#               添加线程优先级设置功能
#----------------------------------------------------------------------------
import threading
import ctypes
import Queue

w32 = ctypes.windll.kernel32
THREAD_SET_INFORMATION = 0x20

#设置相关的优先级，变量，注意这个只能在windows上使用Linux系统无效
THREAD_PRIORITY_ABOVE_NORMAL = 1
THREAD_PRIORITY_BELOW_NORMAL = -1
THREAD_PRIORITY_HIGHEST = 2
THREAD_PRIORITY_IDLE = -15
THREAD_PRIORITY_LOWEST = -2
THREAD_PRIORITY_NORMAL = 0
THREAD_PRIORITY_TIME_CRITICAL = 15

Priority_dic = {"ABOVE_NORMAL":THREAD_PRIORITY_ABOVE_NORMAL,
                "BELOW_NORMAL":THREAD_PRIORITY_BELOW_NORMAL,
                "HIGHEST":THREAD_PRIORITY_HIGHEST,
                "IDLE":THREAD_PRIORITY_IDLE,
                "LOWEST":THREAD_PRIORITY_LOWEST,
                "NORMAL":THREAD_PRIORITY_NORMAL,
                "TIME_CRITICAL":THREAD_PRIORITY_TIME_CRITICAL}

class MThread( threading.Thread ):
    """
    thread class
    """
    __name = None
    __func = None
    __args = None
    
    def __init__( self, func, args, name ):
        "init thread"
        threading.Thread.__init__( self, name = name )
        self.__name = name
        self.__func = func
        self.__args = args
    
    def run( self ):
        "thread run"
        apply( self.__func, self.__args )
    
    def getThreadName( self ):
        "get thread name"
        return self.__name

    def setPriority( self, priority ):
#        print 'setPriority', self.ident  #该函数作为属性访问 
#        self.tid = self.ident
#        print self.tid
        if not self.isAlive(): 
            print 'Unable to set priority of stopped thread' , self.__name
        handle = w32.OpenThread( THREAD_SET_INFORMATION, False, self.ident ) 
        result = w32.SetThreadPriority( handle, priority ) 
        w32.CloseHandle( handle ) 
        if not result: 
            print 'Failed to set priority of thread', w32.GetLastError(), self.__name

    def setPriority_ABOVE_NORMAL( self ):
        self.setPriority( THREAD_PRIORITY_ABOVE_NORMAL )
        
    def setPriority_BELOW_NORMAL( self ):
        self.setPriority( THREAD_PRIORITY_BELOW_NORMAL )        
        
    def setPriority_HIGHEST( self ):
        self.setPriority( THREAD_PRIORITY_HIGHEST ) 
        
    def setPriority_IDLE( self ):
        self.setPriority( THREAD_PRIORITY_IDLE ) 
        
    def setPriority_LOWEST( self ):
        self.setPriority( THREAD_PRIORITY_LOWEST )         
        
    def setPriority_NORMAL( self ):
        self.setPriority( THREAD_PRIORITY_NORMAL )    
        
    def setPriority_TIME_CRITICAL( self ):
        self.setPriority( THREAD_PRIORITY_TIME_CRITICAL )    

    #----------------------------------------
    #用于设置优先级，Priority有7种可能具体参见字典
    #----------------------------------------
    def StartThread( self, Priority = "NORMAL" ):
        "start thread"
        if False == self.isDaemon(): #设置所有线程为Daemon模式
            self.setDaemon( True )
        #开启线程
        self.start()
        self.setPriority( Priority_dic[Priority] )
         
#import time
#def test():
#    print 'test', w32.GetCurrentThreadId()
#    while True:
#        time.sleep( 1 )
#        print 'aa'
if __name__ == '__main__':
    pass
#    print w32.GetCurrentThreadId() 
#    a = MThread( test, '', 'da' )
#    a.start()
#    a.setPriority( 1 )
#    for _t in threading.enumerate():
#        print dir( _t )
#        print _t.ident
#        print 'thread name:', _t.getName()
