#!/usr/bin/python
# -*- coding:utf-8 -*-
#  ======================================================================
#  FileName:    upload.py
#  Description:    用于上传配置文件至下位机
#  Author:    Chary Cha
#  Version:    0.0.1
#  Created:    2012-1-10
#  Company:    CASCO
#  ======================================================================
from ftplib import FTP
import os

class MyFTP():
    __ftp = None
    ___file_handler = None
    __ip = None

    def __init__( self, ip ):
        self.__ip = ip
        self.__ftp = FTP( self.__ip )
        self.__ftp.login()
        print self.__ftp.getwelcome()
                
    def UpLoad( self, pathname, destpath ):
        _bufsize = 1024
        #把目标机目录设为"/tffs0/"
        self.__ftp.cwd( destpath )
        for root, dirs, files in os.walk( pathname ):
            for _filename in files:    
                _fullname = os.path.join( root, _filename )
                try:
                    self.__file_handler = open( _fullname, 'rb' )
                except IOError, e:
                    print "UpLoad error:", e
                    self.__file_handler = None
                    return None
                #'STOR '后面必须有空格
                _strBuffer = 'STOR ' + _filename
                self.__ftp.storbinary( _strBuffer, self.__file_handler, _bufsize )
                if None != self.__file_handler:
                    self.__file_handler.close()
        return True 
    
    #传单个文件
    def UpLoadFile( self, pathname, filename, destpath ):
        _bufsize = 1024
        #把目标机目录设为"/tffs0/"
        self.__ftp.cwd( destpath )
        _fullname = os.path.join( pathname, filename )
        try:
            self.__file_handler = open( _fullname, 'rb' )
        except IOError, e:
            print "UpLoad error:", e
            self.__file_handler = None
            return None
        _strBuffer = 'STOR ' + filename
        try:
            self.__ftp.storbinary( _strBuffer, self.__file_handler, _bufsize )
        except:
            print "UpLoadFile Error!", filename
            self.__ftp.storbinary( _strBuffer, self.__file_handler, _bufsize )
        if None != self.__file_handler:
            self.__file_handler.close()
        return True 

    #--------------------------------------------------------------
    #@上传绝对路径的配置文件至路径
    #--------------------------------------------------------------
    def uploadSingleFile( self, filename, destpath, destname ):
        _bufsize = 1024
        #把目标机目录设为"/tffs0/"
        self.__ftp.cwd( destpath )
        try:
            self.__file_handler = open( filename, 'rb' )
        except IOError, e:
            print "UpLoad error:", e
            self.__file_handler = None
            return None
        _strBuffer = 'STOR ' + destname
        try:
            self.__ftp.storbinary( _strBuffer, self.__file_handler, _bufsize )
        except:
            print "uploadSingleFile Error!", filename
            self.__ftp.storbinary( _strBuffer, self.__file_handler, _bufsize )
        if None != self.__file_handler:
            self.__file_handler.close()
        return True 
                    
                    
    def DownLoad( self, pathname, destpath ):
        _bufsize = 1024
            #把目标机目录设为"/tffs0/"
        _filelist = self.Query( pathname )
        print _filelist
        for _filename in _filelist:
            print _filename
            _localname = os.path.join( destpath, _filename )
            print _localname
            if _filename == "atpmap.txt":
                continue
            try:
                self.__file_handler = open( _localname, 'wb' )
                _file_handler_callback = self.__file_handler.write
            except IOError, e:
                print "DownLoad error:", e
                _file_handler_callback = None
                self.__file_handler = None
                return None
            #'RETR '后面必须有空格
            _strBuffer = 'RETR ' + _filename

            self.__ftp.retrbinary( _strBuffer, _file_handler_callback, _bufsize )        
            if None != self.__file_handler:
                self.__file_handler.close()
            
    def Query( self, destroot ):
        print self.__ftp.dir()
        return self.__ftp.nlst( destroot )    
                
    def Delete( self, destroot, filename ):
        #把目标机目录设为"/tffs0/"
        self.__ftp.cwd( destroot )
        try:
            self.__ftp.delete( filename )
        except:
            return None
        
    def DeleteAll( self, destroot ):
        _filelist = self.Query( destroot )
        for files in _filelist:
            self.Delete( destroot, files )
                             
    def Close( self ):
        self.__ftp.quit()
            
if __name__ == '__main__':
    ftp = MyFTP( '192.100.120.16' )
    rt = ftp.UpLoad( 'C:\\chary', '/tffs0/' )
    #rt = ftp.Delete('/tffs0/','')
    rt = ftp.Query( '/tffs0/' )
    #rt = ftp.DownLoad('/tffs0/','C:/chary')
    print "rt", rt
    ftp.Close()
    
