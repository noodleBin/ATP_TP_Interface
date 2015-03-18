#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     decompress.py
# Description:  调用decompress.dll的外包文件    
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2013-02-25
# Company:      CASCO
# LastChange:   
# History:      
#----------------------------------------------------------------------------
from ctypes import *
from base import commlib
import Queue


#------------------------------------------------
#本DLL调用MSVCR100.DLL，Kernal32.DLL
#------------------------------------------------
class DecompressDLL( object ):
    """
    decompress DLL
    """
    
    def __init__( self, path ):
        "init"
        self.__DLL = CDLL( path ) #不能中文路径
        self.__setArgTypes()
    
        
    def __setArgTypes( self ):
        "set arg types"
        self.__DLL.fastlz_decompress.argtypes = [POINTER( c_char ), c_int, POINTER( c_char ), c_int]
        
    
    def getDecompressStr( self, compressStr, comperssLen, decompressLen ):
        "get decompress string"
        _rev = "0" * decompressLen
        self.__DLL.fastlz_decompress( compressStr,
                                      comperssLen,
                                      _rev,
                                      decompressLen )
        return _rev
    
if __name__ == '__main__' :
    pass
