#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     zlibcommpressdll.py
# Description:  调用dgzDll.dll的外包文件    
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2013-07-26
# Company:      CASCO
# LastChange:   
# History:      
#----------------------------------------------------------------------------
from ctypes import *
from base import commlib
import Queue
from base import filehandle

#------------------------------------------------
#本DLL调用MSVCR100.DLL，Kernal32.DLL,不支持中文路径
#压缩文件路劲也不支持中文
#------------------------------------------------
class ZLIBcompressDLL( object ):
    """
    ZLIBcompress DLL
    """
    
    def __init__( self, path ):
        "init"
        self.__DLL = CDLL( path ) #不能中文路径
        self.__setArgTypes()
    
        
    def __setArgTypes( self ):
        "set arg types"
        self.__DLL.defile.argtypes = [POINTER( c_char ), POINTER( c_char ), c_int]
        self.__DLL.infile.argtypes = [POINTER( c_char ), POINTER( c_char )]
        self.__DLL.inflatestring.argtypes = [POINTER( c_char ), c_int, POINTER( c_char ), POINTER( c_int )]
        self.__DLL.deflatestring.argtypes = [POINTER( c_char ), c_int, POINTER( c_char ), POINTER( c_int ), c_int]
    
    def deflate( self, srcFilePath, dstFilePath , level = 6 ):
        "deflate file"
        if self.__DLL.defile( srcFilePath, dstFilePath, level ) < 0:
            print "deflate file fail", srcFilePath, dstFilePath, level
            return False
        return True
    
    def inflate( self, srcFilePath, dstFilePath ):
        "inflate file"
        if self.__DLL.infile( srcFilePath, dstFilePath ) < 0:
            print "inflate file fail", srcFilePath, dstFilePath
            return False
        return True
    
    def inflateStr( self, srcstring ):
        
        _dstStr = "0" * ( len( srcstring ) * 50 ) #假设压缩倍率最高为50倍
        _dstLen = c_int32()
#        print len( srcstring )
        _rev = self.__DLL.inflatestring( srcstring,
                                        len( srcstring ),
                                        _dstStr,
                                        pointer( _dstLen ) )
#        print _dstLen.value
        return _dstStr[0:_dstLen.value]

    def deflateStr( self, srcstring, level = 6 ):
        
        _dstStr = "0" * len( srcstring )
        _dstLen = c_int32()
#        print len( srcstring )
        _rev = self.__DLL.deflatestring( srcstring,
                                        len( srcstring ),
                                        _dstStr,
                                        pointer( _dstLen ),
                                        level )
#        print _dstLen.value
        return _dstStr[0:_dstLen.value]
    
#    def inflatString( self, srcstring ):
#        "inflat string"
#        _file = open( "D:/tmp.bin", "wb" )
#        _file.write( srcstring )
#        _file.close()
#        
#        self.inflate( "D:/tmp.bin", "D:/tmp1.bin" )
#        _file = open( "D:/tmp1.bin", "rb" )
#        _dstStr = _file.read()
#        _file.close()  
#        filehandle.deleteFile( "D:/tmp.bin" )
#        filehandle.deleteFile( "D:/tmp1.bin" )
#        return  _dstStr
#    
#    def deflatString( self, srcstring, level = 6 ):
#        "deflat string"
#        _file = open( "D:/tmp.bin", "wb" )
#        _file.write( srcstring )
#        _file.close()
#        
#        self.deflate( "D:/tmp.bin", "D:/tmp1.bin", level = level )
#        _file = open( "D:/tmp1.bin", "rb" )
#        _dstStr = _file.read()
#        _file.close()  
#        filehandle.deleteFile( "D:/tmp.bin" )
#        filehandle.deleteFile( "D:/tmp1.bin" )
#        return  _dstStr  
    
if __name__ == '__main__' :
    test = ZLIBcompressDLL( "../dll/dgzDll.dll" )
    _file = open( "C:/Users/60844/Desktop/dgztest/a3241.itc", "rb" )
#    _dst = test.inflatString( _file.read() )
    _dst = test.inflateStr( _file.read() )
    _file.close()
    _file = open( "C:/Users/60844/Desktop/dgztest/a32412.itc", "wb" )
    _dst1 = test.deflateStr( _dst )
    _file.write( _dst1 )
    _file.close()    

    _file = open( "C:/Users/60844/Desktop/dgztest/a32413.itc", "wb" )
    _file.write( _dst )
    _file.close() 
    
#    print test.inflatString( _dst )
    
#    test.inflate( "C:/Users/60844/Desktop/dgztest/a.itc",
#                  "C:/Users/60844/Desktop/dgztest/b.itc" )
#    test.deflate( "C:/Users/60844/Desktop/dgztest/b.itc",
#                  "C:/Users/60844/Desktop/dgztest/a1.itc", 9 )
    

    
