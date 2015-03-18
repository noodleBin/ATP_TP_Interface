#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2014-12-11

@author: 61504
'''
from xmlparser import XmlParser

class LineInfoBase( object ):
    
    #数据字典 key,value
    _data = None
    _data = None
    
    #变量和消息文件的元素名称和属性列表
    importFileParser = {
            'lineInfo': {'path':'.//LineInfo',
                'attr':['Line_Id', 'Direction', 'SSA_List', 'Block_List']
                }
        }
    pass

    def __init__( self, name):
        " device class init "
        self._data = {}
    
    def deviceInit( self, *args, **kwargs ):
        self.importVarint( kwargs['varFile'] )
        pass

    # --------------------------------------------------------------------------
    ##
    # @Brief 导入设备使用的关键变量
    # 添加到_data字典 格式 key(Name):value
    # 添加到_data字典 格式 key(Name):[Type,IO,Value]
    #
    # @Param varintFile
    #
    # @Returns
    # --------------------------------------------------------------------------
    def importVarint( self, varintFile ):
        " import device varint"
        _f = XmlParser()
        _f.loadXmlFile( varintFile )
        _var = _f.getAttrListManyElement( self.importFileParser['lineInfo']['path'],
                self.importFileParser['lineInfo']['attr'] )
        for _v in _var:
            #添加到_data
            self._data[int(_v[0])] = _v[1:]
#         print self._data
        _f.closeXmlFile()

    def getDataValue( self, key ):
        " get value by key"
        try:
            return self._data[key]
        except KeyError, e:
            print 'KeyError', e
            return None

    def getDataKeys( self ):
        " get all keys in data"
        return self._data.keys()

    def delDataKeyValue( self, key ):
        " del key in data"
        try:
            del self._data[key]
            return True
        except KeyError, e:
            print 'KeyError', e 
            return None
    
    def clearDataDic( self ):
        " clear all data"
        self._data.clear()

    def getDataDic( self ):
        " get device dataList"
        return self._data

if __name__ == '__main__':
    lineInfo = LineInfoBase('lineInfo')
    lineInfo.deviceInit( varFile = r'./scenario/Line_Info.xml')
    pass