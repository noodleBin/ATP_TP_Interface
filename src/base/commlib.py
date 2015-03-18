#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     commlib.py
# Description:  平台共用的函数库      
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      2011-07-22
# Company:      CASCO
# LastChange:   update 2011-07-22
# History:      
#               update 2011-07-22
#               添加loadTrainRout函数
#               update 2011-07-25
#               添加curTime,str2hexlify
#               
#---------------------------------------------------------------------------

from xmlparser import XmlParser
import time
import binascii
import sys
import os
import struct

TRAIN_ROUTE = {
        'route':{
            'path':'.//Route',
            'attr':['Block_List']
            },
        'start':{
            'path':'.//Start',
            'attr':['Block_id', 'Abscissa']
            },
        'dire':{
            'path':'.//Direction',
            'attr':['Value']
            },
        'trainLen':{
            'path':'.//trainLen',
            'attr':['Value']
            },
        'Cog_dir':{
            'path':'.//Cog_dir',
            'attr':['Value']
            }               
        }

Month_Days_Dic = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31} #闰年29天

#记录平台datp的最小时间,这个值在datp的variant有对应关系的
ATP_MAX_TIME = 536870912  

#---------------------------------------------------
#ResponseEnd:1：响应本端，2：响应远端,ccloophour:本端的ccloophour
#---------------------------------------------------
def getResponseCCLoophour( ResponseEnd, ccloophour ):
    "get Response ccloophour"
    if 1 == ResponseEnd:
        return ccloophour
    elif 2 == ResponseEnd:
        return ccloophour - ATP_MAX_TIME if ccloophour > ATP_MAX_TIME else ccloophour + ATP_MAX_TIME
    else:
        print 'getResponseCCLoophour Error Value : ResponseEND！！！' , ResponseEnd, ccloophour
# --------------------------------------------------------------------------
##
# @Brief 解析车辆路径文件
#
# @Param routeFile
#
# @Returns 车辆路径，起点，方向
# --------------------------------------------------------------------------
def loadTrainRout( routeFile ):
    " parser train route file"
    _f = XmlParser()
    _f .loadXmlFile( routeFile )
    #获得route节点的属性
    _route = _f.getAttrListOneElement( TRAIN_ROUTE['route']['path'], \
            TRAIN_ROUTE['route']['attr'] )
    _routeV = [int( _s ) for _s in _route[0].strip().split( ',' )]

    _start = _f.getAttrListOneElement( TRAIN_ROUTE['start']['path'], \
            TRAIN_ROUTE['start']['attr'] )
    _startV = [int( _s ) for _s in _start]

    _dire = _f.getAttrListOneElement( TRAIN_ROUTE['dire']['path'], \
            TRAIN_ROUTE['dire']['attr'] )
    _direV = int( _dire[0] )
    
    _trainLen = int( _f.getAttrListOneElement( TRAIN_ROUTE['trainLen']['path'], \
            TRAIN_ROUTE['trainLen']['attr'] )[0] )
    
    _Cog_dir = int( _f.getAttrListOneElement( TRAIN_ROUTE['Cog_dir']['path'], \
            TRAIN_ROUTE['Cog_dir']['attr'] )[0] )
    
    return _routeV, _startV, _direV, _trainLen, _Cog_dir


# --------------------------------------------------------------------------
##
# @Brief 获得当前时间
#
# @Returns 当前时间，字符串格式
# --------------------------------------------------------------------------
def curTime():
    return time.strftime( '%Y-%m-%d %X', time.localtime( time.time() ) )


# --------------------------------------------------------------------------
##
# @Brief 获得当前时间,精确到毫秒
#
# @Returns 当前时间，字符串格式：2012-02-27 11:37:04.296
# --------------------------------------------------------------------------
def GetCurTime():
    _time = time.time()
    _mm = ( ( _time * 1000 ) % 1000 ) / 1000.0
    return time.strftime( '%Y-%m-%d %X', time.localtime( _time ) ) + str( _mm )[1:]
# --------------------------------------------------------------------------
##
# @Brief 字符串按照16进制格式显示
#
# @Param str 
#
# @Returns 
# --------------------------------------------------------------------------
def str2hexlify( str ):
    _str = binascii.hexlify( str )
    _rs = ''
    for _s in [_str[_i:_i + 2] for _i in range( len( _str ) ) if _i % 2 == 0]: 
        _rs += '0x%2s|' % ( _s )
    return _rs

#----------------------------------------------------------------------------
##
# @Brief 计算
# 
# @Param data：未解压的字符
#        offset：其实位置
#        len：长度，bit为单位
# @Return   返回值
#----------------------------------------------------------------------------
def getBitValueByLenOff( data, offset, len ):
    "get value by length and length."
    return ( ( struct.unpack( "!B", data )[0] ) >> offset ) & ( ( 1 << len ) - 1 ) #根据需求修改


#-----------------------------------------------------------------------------
#根据当前的数据的偏移，长度等信息获取其对应的值
#偏移有以下几个参数：Byte：表示第几个字节开始，
#                   Bit：表示第几个位开始，
#                   Len：表示一共占多少个Bit，
#                   Data：表示整个数据字符串
#                   Type:数据类型
#-----------------------------------------------------------------------------
def getValueFromStrByInfo( Data, Byte, Bit, Len, Type ):
    "get value from string by information"
    #先根据配置获取当前数据所在的Str
    _ByteLen = None
    if 0 == ( Bit + Len ) % 8:
        _ByteLen = ( Bit + Len ) / 8
    else:
        _ByteLen = ( ( Bit + Len ) / 8 ) + 1
    _tmpDataStr = Data[Byte:Byte + _ByteLen]
    
    _BitStr = getStrToBinStr( _tmpDataStr, Bit, Len )  #'0101011101'
#    print 'getValueFromHexStrByInfo', _BitStr, Data[2 * Byte:2 * ( Byte + _ByteLen )], Byte, Bit, Len, Type
    if 'Binary' == Type:
        return _BitStr
    elif 'Hexa' == Type:
        return transBinStrToHexStr( _BitStr )
    elif Len > 8 and 0 == Len % 8: #整数
        if len( _BitStr ) not in [8, 16, 32, 64]:
            if 24 == len( _BitStr ):
                _tmpBitStr = "00000000" + _BitStr
            else:
                print "getValueFromHexStrByInfo Error!", len( _BitStr )
        else:
            _tmpBitStr = _BitStr
        _packStr = transBinStrToStr( _tmpBitStr )
        
#        print _packStr
        return struct.unpack( Type, _packStr )[0]
    elif Len <= 8:
        return int( _BitStr, 2 )
        
    else:
        print "getValueFromHexStrByInfo Error", Byte, Bit, Len, Type

#-----------------------------------------------------------------------------
#根据当前的数据的偏移，长度等信息获取其对应的值
#偏移有以下几个参数：Byte：表示第几个字节开始，
#                   Bit：表示第几个位开始，
#                   Len：表示一共占多少个Bit，
#                   Data：表示整个数据字符串,两个字符代表一个字节('ab')
#                   Type:数据类型
#-----------------------------------------------------------------------------
def getValueFromHexStrByInfo( Data, Byte, Bit, Len, Type ):
    "get value from hex string by information"
    #先根据配置获取当前数据所在的Str
    _ByteLen = None
    if 0 == ( Bit + Len ) % 8:
        _ByteLen = ( Bit + Len ) / 8
    else:
        _ByteLen = ( ( Bit + Len ) / 8 ) + 1
    _tmpDataStr = Data[2 * Byte:2 * ( Byte + _ByteLen )]
    
    _BitStr = getHexStrToBinStr( _tmpDataStr, Bit, Len )  #'0101011101'
#    print 'getValueFromHexStrByInfo', _BitStr, Data[2 * Byte:2 * ( Byte + _ByteLen )], Byte, Bit, Len, Type
    if 'Binary' == Type:
        return _BitStr
    elif 'Hexa' == Type:
        return transBinStrToHexStr( _BitStr )
    elif Len > 8 and 0 == Len % 8: #整数
        if len( _BitStr ) not in [8, 16, 32, 64]:
            if 24 == len( _BitStr ):
                _tmpBitStr = "00000000" + _BitStr
            else:
                print "getValueFromHexStrByInfo Error!", len( _BitStr )
        else:
            _tmpBitStr = _BitStr
        _packStr = transBinStrToStr( _tmpBitStr )
        
#        print _packStr
        return struct.unpack( Type, _packStr )[0]
    elif Len <= 8:
        return int( _BitStr, 2 )
        
    else:
        print "getValueFromHexStrByInfo Error", Byte, Bit, Len, Type

#-----------------------------------------
#将二进制数据转换为HexString
#"10010111"->'97'
#-----------------------------------------    
def transBinStrToHexStr( _BitStr ):
    "transform bin string to Hex string"
    _str = ""
    _Len = len( _BitStr ) / 4
    for _i in range( _Len ):
        _str += BinStr2HexStr( _BitStr[_i * 4:( _i + 1 ) * 4] )
    return _str
    
#-----------------------------------------
#将二进制数据转换为String
#"10010111"->'a'
#-----------------------------------------    
def transBinStrToStr( _BitStr ):
    "transform bin string to string"
    _str = ""
    _Len = len( _BitStr ) / 8
    for _i in range( _Len ):
        _tmpint = int( _BitStr[_i * 8:( _i + 1 ) * 8], 2 )
        _str += chr( _tmpint )
    return _str

#-----------------------------------------
#Str:"00ab"转换为二进制string
#Bit:数据开始的偏移
#Len：数据长度
#-----------------------------------------
def getStrToBinStr( Str, Bit, Len ):
    "get string to bin string"
    _HexStr = binascii.hexlify( Str )
    
    return getHexStrToBinStr( _HexStr, Bit, Len )

#-----------------------------------------------------------------------------
#HexStr:"00ab"转换为'0000000010101011'
#Bit:数据开始的偏移
#Len：数据长度
#-----------------------------------------------------------------------------
def getHexStrToBinStr( HexStr, Bit, Len ):
    "get Hex string to Bin string"
    _str = ""
    
    for _char in HexStr:
        _str += HexStr2BinStr( _char )
    
    return _str[Bit:Bit + Len]    

#---------------------------------------------------
#将为二进制转换一个Hex字符串显示形式
#如"1010"转换为'a'
#---------------------------------------------------
def BinStr2HexStr( Bin ):
    "Bin 2 Hex"
    _rev = None
    if '0000' == Bin:
        _rev = '0'
    elif '0001' == Bin:
        _rev = '1'
    elif '0010' == Bin:
        _rev = '2'
    elif '0011' == Bin:
        _rev = '3'
    elif '0100' == Bin:
        _rev = '4'
    elif '0101' == Bin:
        _rev = '5'
    elif '0110' == Bin:
        _rev = '6'
    elif '0111' == Bin:
        _rev = '7'
    elif '1000' == Bin:
        _rev = '8'
    elif '1001' == Bin:
        _rev = '9'
    elif '1010' == Bin:
        _rev = 'a'
    elif '1011' == Bin:
        _rev = 'b'
    elif '1100' == Bin:
        _rev = 'c'
    elif '1101' == Bin:
        _rev = 'd'
    elif '1110' == Bin:
        _rev = 'e'
    elif '1111' == Bin:
        _rev = 'f'   
        
    return _rev

#---------------------------------------------------
#将一个Hex字符串转换为二进制显示型式
#如"a"转换为'1010'
#---------------------------------------------------
def HexStr2BinStr( Hex ):
    "Hex 2 Bin"
    _rev = None
    if '0' == Hex:
        _rev = '0000'
    elif '1' == Hex:
        _rev = '0001'
    elif '2' == Hex:
        _rev = '0010'
    elif '3' == Hex:
        _rev = '0011'
    elif '4' == Hex:
        _rev = '0100'
    elif '5' == Hex:
        _rev = '0101'
    elif '6' == Hex:
        _rev = '0110'
    elif '7' == Hex:
        _rev = '0111'
    elif '8' == Hex:
        _rev = '1000'
    elif '9' == Hex:
        _rev = '1001'
    elif 'a' == Hex:
        _rev = '1010'
    elif 'b' == Hex:
        _rev = '1011'
    elif 'c' == Hex:
        _rev = '1100'
    elif 'd' == Hex:
        _rev = '1101'
    elif 'e' == Hex:
        _rev = '1110'
    elif 'f' == Hex:
        _rev = '1111'   
        
    return _rev
        
#-------------------------------------------
#将一个unsigned short转化成16个bit:即0,1
#@_H:16位的一个整数
#@返回一个16个元素的列表，低位存在前面
#-------------------------------------------
def transform_Hto16Bit( _H ):
    "tranform unsigned short into 16 bit"
    _revl = [] #返回值
        
    for _i in range( 0, 16 ):
        _revl.append( _H % 2 )
        _H = _H / 2
    _revl.reverse() 
    return _revl    

#-------------------------------------------
#将一个unsigned short转化成16个bit:即0,1
#@_Q:64位的一个整数
#@返回一个64个元素的列表，低位存在前面
#-------------------------------------------
def transform_Qto64Bit( _Q ):
    "tranform long long into 64 bit"
    _revl = [] #返回值
        
    for _i in range( 0, 64 ):
        _revl.append( _Q % 2 )
        _Q = _Q / 2
    _revl.reverse() 
    return _revl 

#-------------------------------------------
#将bit列表:即[0,1,1,...]转换为INT
#@bitlist:bit列表（左边为高位，右边为低位）
#@返回一个整数
#-------------------------------------------
def transform_BitlistToInt( bitlist ):
    "tranform bit list into int"
    _revl = 0    
    for _bit in bitlist:
        _revl = _revl * 2 + _bit
                
    return _revl
    
#-------------------------------------------
#将3个Byte转化成1个checksum:
#@_B1,_B2,_B3:3个Byte，_B1为最高位，_B3为低位
#@返回一个checksum
#-------------------------------------------
def transfor_3BytetoI( _B1, _B2, _B3 ):
    "get checksum from 3 bytes"
    return _B1 * 256 * 256 + _B2 * 256 + _B3
    
#-------------------------------------------
#将一个checksum转化为3个byte:
#@_checksum
#@返回_B1,_B2,_B3:3个Byte，_B1为最高位，_B3为低位
#-------------------------------------------
def transform_Ito3Byte( _checksum ):
    "get  3 bytes from checksum"
    _B3 = _checksum % 256
    _B2 = ( ( _checksum - _B3 ) / 256 ) % 256
    _B1 = ( ( _checksum - _B3 - _B2 * 256 ) / 256 / 256 ) % 256
    return _B1, _B2, _B3   
#---------------------------------------------
#获取脚本文件的当前路径
#---------------------------------------------
def getCurFileDir():
    path = sys.path[0]
    if os.path.isdir( path ):
        return path
    elif os.path.isfile( path ):
        return os.path.dirname( path )
    
#---------------------------------------------
#@拼接路径
#---------------------------------------------
def joinPath( a, b ):
    "join path"
    if ":" in b: #b为绝对路径，不join
        return b
    
    if "\\" not in b[1:] and "/" not in b[1:]:
        if "\\" in b or "/" in b:
            return os.path.join( a, b[1:] )
        else:
            return os.path.join( a, b )
    elif b[0] in ["\\", "/"]:
        if a[-1] in ["\\", "/"]:
            return a + b[1:]
        else:
            return a + b
    else:
        return a + "\\" + b

def Hex2Bin( Hexstr, Len = None ):
    "16进制转2进制"
    _tmp = int( Hexstr, 16 )
    _rev = ""
    while _tmp > 0:
        _m = _tmp % 2
        _tmp /= 2
        _rev = str( _m ) + _rev
    
    #补充0值
    if None != Len and Len > len( _rev ):
        _rev = '0' * ( Len - len( _rev ) ) + _rev
    return _rev

def getBitsValueFromByte( Byte, startBit, Len ):
    "get Bits Value From Byte"
    return ( Byte >> ( 8 - startBit - Len ) ) & ( 2 ** Len - 1 )

#--------------------------------------------------
#将码位值填充到Byte中去
#--------------------------------------------------
def AddBitsValueToByte( Byte, startBit, Len, Value ):
    "get Bits Value From Byte"
    _rev = Byte & ( 255 - ( ( 2 ** Len - 1 ) << ( 8 - startBit - Len ) ) ) #清除需要修改的码位
#    print ( ( 2 ** Len - 1 ) << startBit )
    _rev = _rev | ( Value << ( 8 - startBit - Len ) ) #赋值码位
    return _rev         

#---------------------------------------------------------------------
#判断当前年份是否是闰年,ABCD：CD能被4整除是闰年且非零，或者ABCD能被400整除
#---------------------------------------------------------------------
def  isLeapYear( year ):
    "check if leap year"
    _low2Value = year % 100
    if 0 == _low2Value:
        if 0 == year % 400:
            return True
    elif 0 == year % 4:
        return True
    return False

#---------------------------------------------------------------------
# 获取从1970.1.1.0.0到当前时间的秒数
#---------------------------------------------------------------------
def  getWholeSecondsFrom1970( year, month, day, hour, minute, second ):
    "get Whole Seconds From 1970"
    if year < 1970:
        print "getWholeSecondsFrom1970 error!"
        return 0
    _seconds = 0 #初始化
    for _y in range( 1970, year ):#当前年不纳入计算
        if True == isLeapYear( _y ):#闰年
            _seconds += 366 * 24 * 3600
        else:
            _seconds += 365 * 24 * 3600
   
    #计算当前年的天数
    for _m in range( 1, month ):
#        print _m
        if  True == isLeapYear( year ) and 2 == _m:
#            print "-----------"
            _seconds += 29 * 24 * 3600 #闰月
        else:
            _seconds += Month_Days_Dic[_m] * 24 * 3600
    
    
    #计算剩余的时间
    _seconds += ( day - 1 ) * 24 * 3600 + hour * 3600 + minute * 60 + second
    
    #考虑东8区情况
    _seconds -= 8 * 3600
    
    if _seconds < 0:
        _seconds = -1
    return _seconds 

#--------------------------------------------------------------------
#获取从1900.1.1.0.0到当前时间的秒数
#--------------------------------------------------------------------
def getWholeSecondFrom1900( year, month, day, hour, minute, second ):
    "get Whole Second From 1900"
    _seconds = getWholeSecondsFrom1970( year, month, day, hour, minute, second )
    
    return _seconds + int( "83AA7E80", 16 ) #添加默认值1970-1900的时间


#--------------------------------------------------------------------
#获取从1900.1.1.0.0到当前时间的秒数
#--------------------------------------------------------------------
def getCurTimeWholeSecondFrom1900():
    "get Whole Second From 1900"
    return int( time.time() ) + int( "83AA7E80", 16 ) #添加默认值1970-1900的时间
      
if __name__ == '__main__':
#    print 'loadTrainRout ', loadTrainRout( '../scenario/train_route.xml' )
    print time.time()
    print 'curtime ', curTime(), GetCurTime()
    print 'mes2str ', str2hexlify( '12345' )
    print "getBitsValueFromByte", getBitsValueFromByte( 63, 1, 4 )
    print "AddBitsValueToByte", AddBitsValueToByte( 255, 3, 4, 0 )
    print "getWholeSecondsFrom1970", getWholeSecondsFrom1970( 2012, 5, 3, 8, 0, 0 )
