#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     telnet.py
# Description:  用于建立telnet连接，同时开启记录数据和发送数据指令的功能     ，ftp上传工具也集成在其中
# Author:       XIONG KUNPENG
# Version:      0.0.1
# Created:      2012-02-19
# Company:      CASCO
# LastChange:   
# History:      create 2012-02-19
#----------------------------------------------------------------------------
import telnetlib
from xmlparser import XmlParser
import socket
from mthread import MThread
import time
import os
from base import commlib
from myftp import MyFTP

class TelnetParser( object ):
    '''
    telnet control
    '''
    __telnetHandle = None  #存储各个telnet的信息{host：[hostName,ip,port,password,savePath,handle],...}
    __ftpHandle = None  #存储各个ftp的信息{host：[hostName,ip,port,password,handle],...}
    __enter = '\n'
    __filehandel = None    #存储文件句柄{host:[filehandle,saveFlag],...}
    __ctrl_x = "\030"      #用于重启设备
    __Dou_Quot = '"'       #双引号
    __comma = ','
    __cp_command = "cp "       #copy command
    __rm_command = "remove "   #remove command
    importFileParser = {'path':'.//telnet',
                        'attr':['Name', 'hostName', 'ip', 'port', 'password', 'savePath']
                       }
    
     
    def __init__( self ):
        "do nothing."
        self.__telnetHandle = {}
        self.__filehandel = {}


    def importConfig( self, xmlpath ):
        " import config file"
        self.__telnetHandle = {}
        self.__ftpHandle = {}
        _f = XmlParser()
        _f.loadXmlFile( xmlpath )
        _telnet = _f.getAttrListManyElement( self.importFileParser['path'],
                                            self.importFileParser['attr'] )
        for _t in _telnet:
            _host = _t[0]
            _hostName = _t[1]
            _ip = _t[2]
            _port = _t[3]
            _password = _t[4]
            _savePath = _t[5]
            _handle = None
            self.__telnetHandle[_host] = [_hostName, _ip, _port, _password, _savePath, _handle]
            self.__ftpHandle[_host] = [_hostName, _ip, _port, _password, _handle]
#        print self.__telnetHandle
        _f.closeXmlFile()
    
    def joinPath( self, logfolder ):
        "join path to save path"
        for _host in self.__telnetHandle:
            self.__telnetHandle[_host][-2] = commlib.joinPath( logfolder , self.__telnetHandle[_host][-2] ) 
    
    def ConnectFTP( self, Log = None ):
        "connect FTP."
        for _ftp_key in self.__ftpHandle:
            _item = self.__telnetHandle[_ftp_key]
            _connectFlag = False
            #一直连接直至连接成功才停止
            _handle = None
            
            while False == _connectFlag:
                try:
                    _handle = MyFTP( _item[1] )
                    _connectFlag = True
                    print 'ftp:', _item[1]
                except socket.error, e:
                    if Log == None:
                        print "fail to ftp to ip:", _item[1], e
                    else:
                        Log( "fail to ftp to ip:" + _item[1] + repr( e ) )
                    _connectFlag = False
            if Log == None:
                print "succeed to ftp to ip:", _item[1]
            else:
                Log( "succeed to ftp to ip:" + _item[1] ) 
                                   
            self.__ftpHandle[_ftp_key][-1] = _handle    
            
            
    def CloseFTP( self ):
        "close FTP."
        for _ftp_key in self.__ftpHandle:
            self.__ftpHandle[_ftp_key][-1].Close()
            self.__ftpHandle[_ftp_key][-1] = None
    
    def SendFileToHardWareByFTP( self, hostname, sourcepath, destpath, destname ): 
        "send file to hardware by FTP."         
        #将路径装换为绝对路径
        _sourcefile = os.path.abspath( sourcepath )
        if self.__ftpHandle.has_key( hostname ):
            if None != self.__ftpHandle[hostname][-1]:
                self.__ftpHandle[hostname][-1].uploadSingleFile( _sourcefile, destpath, destname )
                print "SendFileToHardWareByFTP: ", sourcepath, destpath, destname
            else:
                print "SendFileToHardWareByFTP: not open ftp yet, ip:", self.__ftpHandle[hostname][1]
        else:
            print "DeleteFileFromHardWareByFTP: not have host:", hostname

    def DeleteFileFromHardWareByFTP( self, hostname, destpath, destname ): 
        "send file to hardware by FTP."         

        if self.__ftpHandle.has_key( hostname ):
            if None != self.__ftpHandle[hostname][-1]:
                self.__ftpHandle[hostname][-1].Delete( destpath, destname )
            else:
                print "DeleteFileFromHardWareByFTP: not open ftp yet, ip:", self.__ftpHandle[hostname][1]
        else:
            print "DeleteFileFromHardWareByFTP: not have host:", hostname
                
    def ConnectTelnet( self, Log = None ): 
        "connect telnet."
        for _telnet_key in self.__telnetHandle:
            _item = self.__telnetHandle[_telnet_key]
            
            #已经建立连接则不再重新建立
            if None != self.__telnetHandle[_telnet_key][-1]: 
                continue
            
            _connectFlag = False
            #一直连接直至连接成功才停止
            _handle = None
            
            while False == _connectFlag:
                try:
                    _handle = telnetlib.Telnet( _item[1] ) 
                    #判断是否需要密码,密码如果没有输入的话可能导致控制命令无法发送至下位机
                    _handle.read_until( "Password: ", 1 )  
                    _handle.write( _item[3] + self.__enter ) 
                    _connectFlag = True
                    self.__filehandel[_telnet_key] = [None, True]
                except socket.error, e:
                    if Log == None:
                        print "fail to telnet to ip:", _item[1], e
                    else:
                        Log( "fail to telnet to ip:" + _item[1] )
                    _connectFlag = False
            if Log == None:
                print "succeed to telnet to ip:", _item[1]
            else:
                Log( "succeed to telnet to ip:" + _item[1] ) 
                                   
            self.__telnetHandle[_telnet_key][-1] = _handle     

    def StartSaveTelnetContent( self ):
        "start save telnet content."
        for _key in self.__telnetHandle:
            #打开文件
            self.__filehandel[_key][0] = open( self.__telnetHandle[_key][4], 'w' )
            #开启存储线程
            _thread = MThread( self.SaveContent, ( _key, ), _key )
#            _thread.isDaemon()
#            _thread.setDaemon( True )
#            _thread.start()
            _thread.StartThread()

    def SaveContent( self, host ):
        "save content from telnet."
#        print host
        while True == self.__filehandel[host][1]:
            _content = self.__telnetHandle[host][-1].read_until( self.__enter, 1 )[:-1]
#           print _content
            #写入数据
            self.__filehandel[host][0].write( _content )
        #结束时将文件关闭掉
        self.__filehandel[host][0].close()
        self.__filehandel[host][0] = None
        print "telnet close.", host
        
    
    def CloseTelnet( self ):
        "close telnet."
        for _key in self.__telnetHandle:
            self.__filehandel[_key][1] = False
        time.sleep( 1 )
        for _key in self.__telnetHandle:
            if "ATP" in _key: #只重启VLE
                print "BOOT device:", _key
                time.sleep( 0.1 )#每个板子的重启时间间隔，避免同时发送有的不会响应
                self.__telnetHandle[_key][-1].write( self.__ctrl_x )
        for _key in self.__telnetHandle:    
            self.__telnetHandle[_key][-1].close()
            self.__telnetHandle[_key][-1] = None
            
    
    #---------------------------------------------------------------
    #@注：hostname必须为host目录下的文件否则无法传送
    #---------------------------------------------------------------
    def SendFileToHardWare( self, hostname, sourcepath, destpath ):
        "send file to hard ware."
        #将路径装换为绝对路径
        _sourcefile = os.path.abspath( sourcepath )
        
#        print self.__cp_command , self.__Dou_Quot, _sourcefile, self.__Dou_Quot , self.__comma , \
#                     self.__Dou_Quot , destpath , self.__Dou_Quot        
        
        _command = self.__cp_command + self.__Dou_Quot + _sourcefile + self.__Dou_Quot + self.__comma + \
                     self.__Dou_Quot + destpath + self.__Dou_Quot
        

        
        if self.__telnetHandle.has_key( hostname ):
            if None != self.__telnetHandle[hostname][-1]:
                self.__telnetHandle[hostname][-1].write( _command )
            else:
                print "SendFileToHardWare: not open telnet yet, ip:", self.__telnetHandle[hostname][1]
        else:
            print "SendFileToHardWare: not have host:", hostname
                
            
                    
    def RemoveFileFromHardWare( self, hostname, path ):
        "remove file from hard ware."
        _command = self.__rm_command + self.__Dou_Quot + path + self.__Dou_Quot
        
        if self.__telnetHandle.has_key( hostname ):
            if None != self.__telnetHandle[hostname][-1]:
                self.__telnetHandle[hostname][-1].write( _command )
            else:
                print "RemoveFileFromHardWare: not open telnet yet, ip:", self.__telnetHandle[hostname][1]
        else:
            print "RemoveFileFromHardWare: not have host:", hostname
                        
        
            
if __name__ == '__main__':
    _t = TelnetParser()
    _t.importConfig( r"../setting/telnet_config.xml" )
        
        
