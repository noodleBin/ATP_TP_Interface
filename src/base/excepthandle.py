#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     excepthandle.py
# Description:  用于处理异常情况下的相关信息记录     
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2012-03-30
# Company:      CASCO
# LastChange:   update 2012-03-30
# History:      
#---------------------------------------------------------------------------
import Queue
from loglog import LogLog
import threading
import gc
import time
import commlib
import os
import filehandle
from caseprocess import CaseParser
#用于记录系统线程异常消息的队列，队列中的数据格式为：(type,时间，类的名称，错误内容)
#type:包括几种类型：1：设备类，该类错误将导致脚本运行重启，并进行下一个用例的执行，(这种情况将结束所有设备)
#             2：ftp的异常，该类异常将会导致上传文件问题，这可能需要重新启动下位机，重新进行ftp连接
#             3：telnet的异常此种异常导致重新连接telnet
#             4：other运行时的设备异常
ExceptHandleQ = Queue.Queue()
Log = LogLog()
filepath = commlib.getCurFileDir() + "/Log/" + time.strftime( '%Y-%m-%d-%H_%M_%S', time.localtime( time.time() ) ) + "-Exception.log"
Log.orderLogger( filepath, "Exception" )


def LogException():
    "log exception"
    _rev = None
#    while True:
    try:
        _msg = ExceptHandleQ.get_nowait()
        Log.logError( repr( _msg[1] ) + " " + repr( _msg[2] ) + " " + repr( _msg[3] ) )
#        print _msg
        _rev = _msg[0]
    except:
        _rev = -1
    return _rev


def ClearEmptyLogFile():
    "clear empty log file"
#    print "ClearEmptyLogFile"
    _dir, file = os.path.split( filepath )
    root, dirs, files = CaseParser.getFolderlist( _dir ) 
    for _f in files:
        if file != _f:
            _tmppath = os.path.join( root, _f )
            #删除空的文件
            if 0 == os.path.getsize( _tmppath ):
                filehandle.deleteFile( _tmppath )            
    
    
def LogClose():
    "close log"
#    print "LogClose"
    Log.fileclose()
    #检测文件是否为空，为空则删除
    if 0 == os.path.getsize( filepath ):
        print "LogClose: No Error! Delete file", filepath
        filehandle.deleteFile( filepath )
    
#结束所有的运行线程#处理主线程和其他显示线程外，以便进行下一个用例的相关操作
#AuiNode:界面的节点
def EndCurCaseThread( AuiNode ):
    "End Current Case Thread"
    try:
        AuiNode.Runstatus = False 
#         AuiNode.tpSim.telnet.ConnectTelnet()
#         AuiNode.tpSim.telnet.CloseTelnet()
        AuiNode.tpSim.omap.OMAPEnd()
        time.sleep( 2 ) #保证已经无消息给上位机   
        AuiNode.tpSim.deviceRunstart = False    
        #发送结束发送消息给平台的发送队列
        AuiNode.tpSim.inQ.put( "END Case" )
        AuiNode.tpSim.deviceEnd()       
        print 'GC collect:', gc.collect()
        time.sleep( 5 ) 
        AuiNode.test_config_panel.SetCaseStatus( 4 )
    except:
        print  "EndCurCaseThread error!"             

if __name__ == '__main__':
    pass
