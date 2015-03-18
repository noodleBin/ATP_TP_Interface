#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     citbdll.py
# Description:  调用citbdll的外包文件     
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2013-02-25
# Company:      CASCO
# LastChange:   
# History:      
#----------------------------------------------------------------------------
from ctypes import *
import time

class CRC( object ):
    """
    CRC DLL
    """
    
    __DLL = None
    
    
    def __init__( self ):
        "init"
    
    @classmethod
    def loadCRCDLL( self ):
        try:
            self.__DLL = CDLL( r'./dll/CRCCheck.dll' )
            self.__setArgTypes()
        except WindowsError,e:
            print repr(e)

    @classmethod    
    def __setArgTypes( self ):
        self.__DLL.CRC_Calculate_10811_MSB_CRC16.argtypes = [POINTER( c_char ), c_uint]
        self.__DLL.CRC_Calculate_10811_LSB_CRC16.argtypes = [POINTER( c_char ), c_uint]
    
    @classmethod    
    def CRC_Calculate_10811_MSB_CRC16( self, msg, len ):
        return self.__DLL.CRC_Calculate_10811_MSB_CRC16( msg, len )
    
    @classmethod
    def CRC_Calculate_10811_LSB_CRC16( self, msg, len ):
        return self.__DLL.CRC_Calculate_10811_LSB_CRC16( msg, len )
    
if __name__ == '__main__' :
    import struct
    tmp = struct.pack( "!22B",
                        255, 255,
                        240,
                        1, 1, 1, 1, 1, 1, 128,
                        0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 6 )
    import base.commlib
    print base.commlib.str2hexlify( tmp )
    CRC.loadCRCDLL()
    print CRC.CRC_Calculate_10811_LSB_CRC16( tmp, 22 )
