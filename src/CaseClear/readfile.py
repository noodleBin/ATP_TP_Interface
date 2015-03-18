#!/usr/bin/env python3
#encoding=utf-8
import codecs
"这个模块用于读取widons下的文本文件,windows下的文本文件会存为\
(ANSI, utf-8, unicode, unicode big endian)4种编码格式\
这个模块就用于读取这4种格式的文本"
name = "WinTxtReader"
version = "1.0"
author = "vily"
email = "vily313@126.com"

def readUTF8( f_url ):
    try:
        f = codecs.open( f_url )
    except IOError as err:
        print( "In function readUTF8, ", err )
        return ""
    txt = f.read()
    f.close()
    if txt[:3] == codecs.BOM_UTF8:
        txt = txt[3:].decode( "utf-8" )
        return txt
    return ""

def readANSI( f_url ):
    try:
        f = open( f_url, "r" )
    except IOError as err:
        print( "In function readANSI, ", err )
        return ""
    txt = f.read()
    return txt
def readUNICODE( f_url ):
    try:
        f = codecs.open( f_url )
    except IOError as err:
        print( "In function readUNICODE, ", err )
        return ""
    txt = f.read()
    f.close()
    try:
        txt = txt.decode( "utf-16" )
        return txt
    except UnicodeDecodeError as err:
        print( "In function readUNICODE, ", err )
        return ""
def readUBE( f_url ):    
    return readUNICODE( f_url )

# 自动选择读取这四种编码格式的
def readTxt( f_url ):
    try:
        f = open( f_url, "rb" )
    except IOError as err:
        print( "In function readTxt, ", err )
        return ""
    bytes = f.read()
    f.close()
    if bytes[:3] == codecs.BOM_UTF8:
        return bytes[3:].decode( "utf-8" )
    else:
        # 先当作 ansi 编码解码
        try:
            txt = bytes.decode( "gb2312" )
            #print("当作 ansi 编码解码")
            return txt
        except UnicodeDecodeError as err:
            # 再当作unicode 编码解码
            try:
                txt = bytes.decode( "utf-16" )
                #print("当作 unicode 编码解码")
                return txt
            except UnicodeDecodeError as err:
                print( "In function readTxt, ", err )
                return ""

def readlines( f_url ):
    "该函数只适合与windows平台"
    _text = readTxt( f_url )
    _revtext = []
    
    _startindex = 0
    _index = 0
    while _index < len( _text ):
        if "\n" == _text[_index]:
            _revtext.append( _text[_startindex:_index - 1] )
            _startindex = _index + 1 #该函数只适合与windows平台
        _index = _index + 1
    
    return _revtext

