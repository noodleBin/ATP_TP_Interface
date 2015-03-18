#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     mapcheck.py
# Description:  用于检验地图库是否符合标准,主要查看地图库中的地图是否完全
# Author:       XiongKunpeng
# Version:      0.0.1
# Created:      date
# Company:      CASCO
# LastChange:   Created 2012-03-13
# History:      
#----------------------------------------------------------------------------
from base import commlib
from base.caseprocess import CaseParser
from lxml import etree
import codecs
import os
import readfile

class MapCheck( object ):
    """
    map check
    """
    
    __filelist = ['/atpCpu1Binary.txt', \
                 '/atpCpu2Binary.txt', \
                 '/atpText.txt', \
                 '/ccnvBinary.txt', \
                 '/ccnvText.txt']

    def __init__( self ):
        "map check init"
        
    #----------------------------------------------
    #@path:为绝对路径
    #----------------------------------------------
    @classmethod
    def CheckMap( self, path ):
        "import map"
        #遍历该路径下的的所有文件夹
        root, dirs, files = CaseParser.getFolderlist( path ) 
        for _dir in dirs:
            _tmppath = os.path.join( root, _dir )
            if False == self.checkMapFolderValid( _tmppath ):
                print "Wrong map!", _tmppath
            else:
                pass
#                print "right map:", _tmppath

    @classmethod
    def CreateDesXml( cls , path, xmlpath ):
        "create Desciption Xml."
        _lines = readfile.readlines( path )

        _XML_file = open( xmlpath, 'w' )
        #创建XML根节点
        _Maps = etree.Element( "Maps" )
        _Maps.set( "Version", "Bcode_CC_OFFLINE_VN_Build20111227" )
        for _line in _lines:
#            print _line
            _Des, _Name = cls.getDesAndName( _line )
            _map = etree.SubElement( _Maps, "Map" )
            _map.set( "Name", _Name ) #类型
#            print _Des
            _map.set( "Description", _Des ) #类型
        
        _String = etree.tostring( _Maps, pretty_print = True, encoding = "utf-8" )           
        _XML_file.write( r'''<?xml version="1.0" encoding="utf-8"?>''' ) #保存数据
        _XML_file.write( '\n' ) #保存数据
        _XML_file.write( _String )
        _XML_file.close()     
    
    @classmethod
    def getDesAndName( cls, _string ):
        "get desciption and name"
        #获取描述所在的位置
#        print _string
        _index = 12 + _string[13:].index( '_' )
        _Des = _string[_index + 2:]
        _Name = _string[0:_index + 1]
        #不需要 
#        _Des = cls.replaceAnd( _Des ) 
        
        return _Des, _Name
        
    @classmethod
    def replaceAnd( cls, string ): 
        "replace & with -"
        _index = 0
        _string = u""
#        print string
        for _s in string:
#            print _s
            if "&" == _s:
                _string = u"和"
            else:
                _string = _string + _s
        
        return string
        
    #---------------------------------------------------
    #@检测用例所需的文件是否具备
    #@包括文件一个文件夹UP_Log
    #---------------------------------------------------
    @classmethod
    def checkMapFolderValid( self, path ):
        "检验case路径下的case时候有效，无效则返回false"
        for _f in self.__filelist:
            if False == os.path.exists( path + _f ):
                print "Not exist Map file:", _f[1:], "path:", path
                return False
            
        return True

if __name__ == '__main__':        
    "mapcheck"
#    print readfile.readlines( "E:/ATP_Validate_2012_02_17/MapLib/description.txt" )
    MapCheck.CheckMap( "E:/ATP_Validate_2012_04_04/Bcode_CC_OFFLINE_VN_Build20111227" )
    MapCheck.CreateDesXml( "E:/ATP_Validate_2012_04_04/Bcode_CC_OFFLINE_VN_Build20111227/description.txt", \
                           "E:/ATP_Validate_2012_04_04/Bcode_CC_OFFLINE_VN_Build20111227/description.xml" )
