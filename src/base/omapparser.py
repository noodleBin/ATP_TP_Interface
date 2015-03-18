#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     omapparser.py
# Description:  omap接口，用于存储数据，以便用于omap读取
# Author:       KUNPENG XIONG
# Version:      0.0.1
# Created:      2011-03-05
# Company:      CASCO
# LastChange:   2011-03-05
# History:      Created --- 2012-03-05
#----------------------------------------------------------------------------
from xmlparser import XmlParser
import struct
from lxml import etree
import os
import Queue
from base import commlib
from mthread import MThread
from base import commlib
import binascii
import socket
import select
import time
import threading
import zipfile
import filehandle
from base import simdata
import random
from base.xmldeal import XMLDeal
import copy
from base.decompressdll import DecompressDLL
from zlibcompressdll import ZLIBcompressDLL

class OMAPParser():
    """
    OMAP Parser
    """
    OMAPShow_mutex = threading.Lock()  #用于读写omap显示时锁存用
    OMAPSave_mutex = {}
    OMAPSave_Path = None #OMAP数据的存储路径文件夹+OMAPData.zip
    
    OMAP_Head_Format = "!IBB" #[loophour,wholeNum,Ser]
    
    OMAPQue = {}     #根据OMAP配置开放队列个数
    OMAPFormat = {} #OMAP消息对应的解析格式，{FRAMELABEL:{Label:[Type,Byte,Bit,Length],...},...],...} #Label必须唯一否则会被覆盖
    OMAPShow = {}   #用于显示的OMAP数据,注意显示的数据的名字不能相同，也即在配置OMAP数据的时候应该保证NameLabel的唯一性
    OMAPLogShow = {} #用于显示OMAPLog时的查找数据使用，{FRAMELABEL：{Page:{(rows,col):[Label,Type,Byte,Bit,Length]}}}
    OMAPSearchShow = {} #用于查找变量是使用的标签 {FRAMELABEL:{Label:[page,row,col],...},...],...} #Label必须唯一否则会被覆盖
#    OMAPLogData = {} #用于存储OMAPLOG数据{FRAMELABEL:datalist,}
    XMLParser = {'path':'.//Omap',
                 'attr':['Name', 'ID', 'Type', 'FrameLength', 'savePath', 'IP', 'PORT'],
                 'Label':'.//Value'
                }
    FormatParser = {'path':'.//FORMAT',
                    'attr':['FRAMELABEL'],
                    'attrLabel':[u'.//LABEL', u'.//TYPE', u'.//BYTE', u'.//BIT', u'.//LENGTH',
                                 u".//PAGE", u".//LINE", u".//COL"]
                    }
    
    EnuXMLParser = {'path':'.//ENUMERATE',
                    'attr':['type'],
                    'subLabel':'.//DATA',
                    'subLabelattr':['code', 'label']
                   }

    
    OMAP_UNPACK_TYPE = {( 'Sig.l.big', 8 ):"!b",
                        ( 'Sig.l.big', 16 ):"!h",
                        ( 'Sig.l.big', 24 ):"!i",
                        ( 'Sig.l.big', 32 ):"!i",
                        ( 'Unsig.l.big', 8 ):"!B",
                        ( 'Unsig.l.big', 16 ):"!H",
                        ( 'Unsig.l.big', 24 ):"!I",
                        ( 'Unsig.l.big', 32 ):"!I",
                        ( 'Binary.big', 8 ):"!B",
                        ( 'Hexa l.big', 32 ):"!I",
                        ( 'Hexa l.big', 16 ):"!H",
                        ( 'Hexa l.big', 8 ):"!B",
                        ( 'Binary', 8 ):"!B",
                        8:"!B",
                        16:"!H",
                        24:"!I",
                        32:"!I" }
    
    Enu_dic = {'Enu-Bool':{0:'False', 1:'True'},
               'Enu-LOCALIZATION_STATE':{0:'NOT_LOCALIZED', \
                                         1:'MOVING_INIT', \
                                         2:'LOCALIZED'},
               'Enu-LocFaultType':{0:'LOCFAULT_NONE', \
                                   1:'LOCFAULT_INVALID_KINEMATIC', \
                                   2:'LOCFAULT_LOC_PERMANENT_FAILURE', \
                                   3:'LOCFAULT_BEACON_VALIDITY_DIST_EXCESS', \
                                   4:'LOCFAULT_INVERSE_LOCATION', \
                                   5:'LOCFAULT_LOCATION_MAX_UNCERTAINTY', \
                                   6:'LOCFAULT_OUT_OF_TRACK_MAP', \
                                   7:'LOCFAULT_POINT_CROSSED', \
                                   8:'LOCFAULT_TRAIN_NOT_INTEGRITY', \
                                   9:'LOCFAULT_END1_COUPLED', \
                                   10:'LOCFAULT_END2_COUPLED'},
               'Enu-CAB_ID':{0:'END_UNKOWN',
                             1:'END_1',
                             2:'END_2'},
               'Enu-EB_CAUSE':{0:'NOT_REQUEST',
                               1:'WORK_OVERTIME',
                               2:'ON_NONEXCLUSIVE_ROUTE',
                               3:'OVER_ENERGY',
                               4:'RM_OVER_SPEED',
                               5:'ROLLBACK_OVER_SPEED',
                               6:'REVERSE_OVER_SPEED',
                               7:'PASSENGER_EMERGENCY_EVACUATION_REQUIRED',
                               8:'DEPARTURE_WITH_NO_TDCL',
                               9:'UNEXPECTED_PSD_OPENING',
                               10:'UNDETECTABLE_DANGER_RISK',
                               11:'OPERATIONAL_REQUEST',
                               12:'NOT_ALL_TRAIN_END_HOLD_DOORS_CLOSED',
                               13:'PB_NOT_APPLIED_DUE_TO_TRAIN_DOORS',
                               14:'PB_NOT_APPLIED_DUE_TO_PSD',
                               15:'APPROACHABLE_SIGNAL_OVERRUN',
                               16:'SAFE_TIMER_FAILED',
                               17:'INCOMPATIBLE_DISTANT_ATP',
                               18:'UPGRADE_PREPARE',
                               19:'MT_SEARCHING_CNT_OVER_LIMIT'}
            } #{Type:{1:Value,...},...}

    __IPAddrID = None
#    __IP = None
#    __PORT = None
    
    __omapHandle = None

    maxMessageSize = 2048
    __Listening = None

    __TPSNode = None #平台节点，主要用于计算位置时使用 
    
    __decompressDll = None #解压缩所需的DLL节点
    
    __needDeCompressFlag = False #是否需要解压标识
    
    __OMAPToleratenceNum = 10 #OMAP消息能够容忍的延时，也即在收到第N包数据的时候，如果第一包还没有收到则丢弃该包数据
    def __init__( self ):
        "init do nothing"
        self.__Listening = True
    
    def SetTpsNode( self, Node ):
        "set tps node"
        self.__TPSNode = Node
    
    @classmethod
    def initDecompressDll( self, path ):
        "initial decompress dll"
        self.__decompressDll = DecompressDLL( path )

    @classmethod
    def initZLIBDll( self, path ):
        "initial ZLIB dll"
        self.__ZLIBDll = ZLIBcompressDLL( path )
    
    #--------------------------------------
    #获取当前的位置，blockid&abs
    #--------------------------------------
    def GetCurPosition( self ):
        "get block id and abssica"
        try:
            _abs1 = self.__TPSNode.loadDeviceDic['rs'].getDataValue( 'coordinates_1' )
            _blockId, _Abs = simdata.TrainRoute.getBlockandAbs( _abs1,
                                                                Type = "Running" )
        except:
            print "GetCurPosition error."
            _blockId, _Abs = 0, 0
            
        return [str( _blockId ), str( _Abs )]
    
    @classmethod
    def importEnuDic( self, path ):
        "import Enu_dic"
        OMAPParser.Enu_dic = {}

        _f = XmlParser()
        _f.loadXmlFile( path )
        
        _Enus = _f.getAllElementByName( self.EnuXMLParser['path'] )
#        tempTypelist = []
        for _Enu in _Enus:
            _typekey = "Enu-" + _f.getAttrListOneNode( _Enu, self.EnuXMLParser['attr'] )[0]
            OMAPParser.Enu_dic[_typekey] = {}
            #添加枚举
            _Datas = _f.getNodeListInNode( _Enu, self.EnuXMLParser['subLabel'] )
            for _data in _Datas:
                _attrs = _f.getAttrListOneNode( _data, self.EnuXMLParser['subLabelattr'] )
                _code = int( _attrs[0] )
                _label = _attrs[1]
                OMAPParser.Enu_dic[_typekey][_code] = _label
                
    def importConfig( self, xmlpath ):
        "import omap config."
        self.__omapHandle = {}
        OMAPParser.OMAPQue = {}
        OMAPParser.OMAPShow = {}
        _f = XmlParser()
        _f.loadXmlFile( xmlpath )
#        _omap = _f.getAttrListManyElement(self.XMLParser['path'],
#                                            self.XMLParser['attr'])
        _omaps = _f.getAllElementByName( self.XMLParser['path'] )
        _info = _f.getRootAttrList( ['IP_Address_ID'] )
        self.__IPAddrID = _info[0]
#        _info = _f.getRootAttrList( ['IP', 'PORT'] )
#        self.__IP = _info[0]
#        self.__PORT = int(_info[1])
        
        for _o_node in _omaps:
            _o = _f.getAttrListOneNode( _o_node, self.XMLParser['attr'] )
            _Name = _o[0]
            _ID = int( _o[1] )
            _Type = _o[2]
            _FrameLength = _o[3]
            _savePath = _o[4]
            _handle = None
            self.__omapHandle[_ID] = [_Name, _ID, _Type, _FrameLength, _savePath, _handle]
            OMAPParser.OMAPQue[_ID] = Queue.Queue()
            _valueNodes = _f.getNodeListInNode( _o_node, self.XMLParser['Label'] )
            OMAPParser.OMAPShow[_Name] = {}
            for _vNode in _valueNodes:
#                if False == OMAPParser.OMAPShow.has_key( _Name ):
#                    OMAPParser.OMAPShow[_Name] = {}
                OMAPParser.OMAPShow[_Name][_f.getNodeText( _vNode )] = ''
                
#        print self.__omapHandle
        _f.closeXmlFile()   

    def getNameByID( self, ID ):
        "get OMAP Frame Name by ID."
        for _ID in self.__omapHandle:
            if ID == _ID:
                return self.__omapHandle[_ID][0]
            

    @classmethod
    def importFormat( self, path ):
        "import Format"
        #{FRAMELABEL：{Page:{(rows,col):[Label,Type,Byte,Bit,Length]}
        OMAPParser.OMAPLogShow = {}        
        OMAPParser.OMAPFormat = {}
        OMAPParser.OMAPSearchShow = {}
        _f = XmlParser()
        _f.loadXmlFile( path )
        
        _Format = _f.getAllElementByName( self.FormatParser['path'] )
#        tempTypelist = []
        for _ff in _Format:
            _FRAMELABEL = _f.getAttrListOneNode( _ff, self.FormatParser['attr'] )[0]
            if False == OMAPParser.OMAPFormat.has_key( _FRAMELABEL ):
                OMAPParser.OMAPFormat[_FRAMELABEL] = {}
            if False == OMAPParser.OMAPLogShow.has_key( _FRAMELABEL ):
                OMAPParser.OMAPLogShow[_FRAMELABEL] = {}
            if False == OMAPParser.OMAPSearchShow.has_key( _FRAMELABEL ):
                OMAPParser.OMAPSearchShow[_FRAMELABEL] = {}
            
            _tmpList = []
            for _item in self.FormatParser['attrLabel']:
                _node = _f.getNodeInNode( _ff, _item )
                #['.//LABEL', './/TYPE', './/BYTE', './/BIT', './/LENGTH', ".//PAGE", ".//LINE", ".//COL"]    
                try:
                    _tmpList.append( _f.getNodeText( _node ) )
                except AttributeError, e:
                    _tmpList.append( "0" )
                    print _ff, _item, _node, _tmpList, e
            _page = int( _tmpList[5] )
            _row = int( _tmpList[6] )
            _col = int( _tmpList[7] )
            _content1 = [_tmpList[0], _tmpList[1]] + [int( _i ) for _i in _tmpList[2:5]]            
            
            if False == OMAPParser.OMAPLogShow[_FRAMELABEL].has_key( _page ):
                OMAPParser.OMAPLogShow[_FRAMELABEL][_page] = {}
                    
            OMAPParser.OMAPLogShow[_FRAMELABEL][_page][( _row, _col )] = _content1
            
            _label = _tmpList[0]
            _content2 = [_tmpList[1]] + [int( _i ) for _i in _tmpList[2:5]]
            OMAPParser.OMAPFormat[_FRAMELABEL][_label] = _content2
            
            OMAPParser.OMAPSearchShow[_FRAMELABEL][_label] = [_page, _row, _col]
#        
#        print OMAPParser.OMAPFormat
#        print len(OMAPParser.OMAPFormat['iTC_ATP_UP'])
#        print len(OMAPParser.OMAPFormat['iTC_ATP_DOWN'])
#        print tempTypelist
#        print len(tempTypelist)
#        print OMAPParser.OMAPSearchShow
    
    @classmethod
    def GetSearchVariantInfo( cls, Framelabel, variant ):
        "Get Search Variant Info"
        _rev = []  ##[[label,page,row,col]]
        _variant_UPPER = variant.upper() #转换成大写以便搜索,实现大小写识别模糊
        for _item in OMAPParser.OMAPSearchShow[Framelabel]:
            if _variant_UPPER in _item.upper():
                _rev.append( [_item] + OMAPParser.OMAPSearchShow[Framelabel][_item] )
        return _rev
    
    @classmethod
    def LoadOMAPData( self, folder ):    
        "load OMAP Data"
        _OMAPLogData = {}
        _OMAPPosData = {}
        _OMAPTimeData = {}
        _DecompressOMAPFlag = {}
        for root, dirs, files in os.walk( folder ):
            for _file in files:
                if ".xml" in _file:#只读取xml文件
                    _filepath = os.path.join( root, _file )
                    _label, _Data, _Poslist, _Time = self.importXMLOMAPFile( _filepath )
                    if _Data != None and _label != None:
#                        print _label
                        if False == _OMAPLogData.has_key( _label ):
                            _OMAPLogData[_label] = _Data
                            _OMAPPosData[_label] = _Poslist
                            _OMAPTimeData[_label] = _Time
                            _DecompressOMAPFlag[_label] = False
                elif '.omap' in _file[-5:]:#压缩格式的omap文件
                    _filepath = os.path.join( root, _file )
                    _label, _Data, _Poslist, _Time = self.importCompressOMAPFile( _filepath )
                    if _Data != None and _label != None:
#                        print _label
                        if False == _OMAPLogData.has_key( _label ):
                            _OMAPLogData[_label] = _Data
                            _OMAPPosData[_label] = _Poslist
                            _OMAPTimeData[_label] = _Time
                            _DecompressOMAPFlag[_label] = True
                    
            return _OMAPLogData, _OMAPPosData, _OMAPTimeData, _DecompressOMAPFlag

    @classmethod
    def LoadZipOMAPData( self, folder ):    
        "load OMAP Data"
        _OMAPLogData = {}
        _path = os.path.join( folder, "OMAPData.zip" )
#        t1 = time.time()
        if True == os.path.exists( _path ):
            _fUNZip = zipfile.ZipFile( _path, "r", zipfile.ZIP_DEFLATED )
#            for _file in _fUNZip.namelist():
#            _fUNZip.extract(_file, path = folder) #先解压后读取
            _fUNZip.extractall( path = folder ) #先解压后读取
#                _ftemp = _fUNZip.open(_file)
#                _ftemppath = os.path.join(folder, _file)
#                _label, _Data = self.importOMAPFile(_ftemppath)
#                if _Data != None and _label != None:
##                    print _label
#                    if False == OMAPParser.OMAPLogData.has_key(_label):
#                        OMAPParser.OMAPLogData[_label] = _Data
#                _ftemp.close()
            _delfilelist = _fUNZip.namelist()
            _fUNZip.close()
            _OMAPLogData, _OMAPPosData, _OMAPTimeData, _DecompressOMAPFlag = self.LoadOMAPData( folder )
            #删除解压的文件
            for _file in _delfilelist:
                _temppath = os.path.join( folder, _file )
                filehandle.deleteFile( _temppath )
        
        return _OMAPLogData, _OMAPPosData, _OMAPTimeData, _DecompressOMAPFlag
#        print time.time() - t1                     
        
    @classmethod
    def getOMAPFrameList( cls, OMAPLogData ):
        "get OMAP Frame list"
        _rev = []
        for _key in OMAPLogData:
            _rev.append( _key )
        return _rev
    
    @classmethod
    def getOMAPFrameSize( cls, OMAPLogData, FrameLabel ):
        "get OMAP Frame Size"
        try:
            return len( OMAPLogData[FrameLabel] )
        except:
            print "getOMAPFrameSize error."
            return 1 

    @classmethod
    def getOMAPFramePageSize( cls, FrameLabel ):
        "get OMAP Frame Size"
        try:
            _pageSize = 1
            for _key in OMAPParser.OMAPLogShow[FrameLabel]:
                if _pageSize < _key:
                    _pageSize = _key
            return _pageSize
        except:
            print "getOMAPFramePageSize error."
            return 1         
    
#    @classmethod
#    def ClearLoadOMAPData( cls ):
#        "clear load OMAP Data"
#        OMAPParser.OMAPLogData = {}
    
    #---------------------------------------
    #返回显示在界面上的显示数据，主要通过FrameLabel和Page获得
    #返回数据格式：{(row,col):(label,Value),}
    #---------------------------------------
    @classmethod
    def getShowDataListByPage( cls, OMAPLogData, FrameLabel, Page, Num, CompressFlag ):
        "get show data"
#        try:
        _data = OMAPLogData[FrameLabel][Num] #某一帧数据"00000"
#        print _data
        #获取当前页的数据
        try:
            _Config = OMAPParser.OMAPLogShow[FrameLabel][Page] #{( rows, col ):[Label, Type, Byte, Bit, Length]}
        except KeyError, e:
            _Config = {}
            
#        print _Config
        _rev = {}
        for _key in _Config:
#            print _key
            _rev[_key] = ( _Config[_key][0], cls.getShowDataValue( _data, *( _Config[_key] + [CompressFlag[FrameLabel]] ) ) )
#        print _rev
        return _rev
#        except:
#            return {}
            
    
    @classmethod
    def getShowDataValue( cls, data, Label, Type, Byte, Bit, Length, compressFlag ):
        "get Show Data Value"
        _handle = commlib.getValueFromStrByInfo if compressFlag else\
                    commlib.getValueFromHexStrByInfo   
        try:
            _content = [ Type, Byte, Bit, Length]
            if False == OMAPParser.Enu_dic.has_key( Type ):#_content[-1] >= 8
                if 'Hexa' in Type:
                    return _handle( data,
                                    Byte,
                                    Bit,
                                    Length,
                                    'Hexa' )
                elif 'Binary' in Type:
                    return _handle( data,
                                    Byte,
                                    Bit,
                                    Length,
                                    'Binary' )
                elif 'Date Time' in Type:
                    _tmp = _handle( data,
                                    Byte,
                                    Bit,
                                    Length,
                                    '!i' )
                    if 0 > _tmp:
                        return str( _tmp )
                    else:
                        return time.strftime( '%Y-%m-%d %X', time.localtime( _tmp ) )
                
                try:#处理有type的
                    _value = _handle( data,
                                      Byte,
                                      Bit,
                                      Length,
                                      OMAPParser.OMAP_UNPACK_TYPE[( _content[0], _content[-1] )] )
                except KeyError, e:#没有type的长度小于8的
                    if _content[3] > 0:
                        _value = _handle( data,
                                          Byte,
                                          Bit,
                                          Length,
                                          '!B' )
                    else:
                        if 0 != Length: 
                            print "getShowDataValue error1:", _content
                        _value = 0
                return str( _value )
    
            else:
                if 8 >= _content[3]:
                    _Type = "!B"
                else:
                    _Type = OMAPParser.OMAP_UNPACK_TYPE[ _content[-1] ]

                _value = _handle( data,
                                  Byte,
                                  Bit,
                                  Length,
                                  _Type )
                
                try:
                    return OMAPParser.Enu_dic[_content[0]][_value]
                except KeyError, e:
                    print "unKnow type:", _content, e
                    return str( _value )
        except:
            if 0 != Length:
                print "getValueByName error2:", Label, Type
            return "0"
    
    #------------------------------------------------------------------
    #获取两个值，一个是str类型的值，一个是数字类型的值
    #------------------------------------------------------------------
    @classmethod
    def getStringAndNumDataValue( cls, data, Label, Type, Byte, Bit, Length, compressFlag ):
        "get Two Show Data Value"
        _handle = commlib.getValueFromStrByInfo if compressFlag else\
                    commlib.getValueFromHexStrByInfo
        try:
            _content = [ Type, Byte, Bit, Length]
            if False == OMAPParser.Enu_dic.has_key( Type ):#_content[-1] >= 8
                if 'Hexa' in Type:
                    _data = _handle( data,
                                     Byte,
                                     Bit,
                                     Length,
                                     'Hexa' )
                    return _data, int( _data, 16 )
                elif 'Binary' in Type:
                    _data = _handle( data,
                                     Byte,
                                     Bit,
                                     Length,
                                     'Binary' )
                    return _data, int( _data, 2 )
                elif 'Date Time' in Type:
                    _tmp = _handle( data,
                                    Byte,
                                    Bit,
                                    Length,
                                    '!i' )
                    
                    if 0 > _tmp:
                        return str( _tmp ), _tmp
                    else:
                        return time.strftime( '%Y-%m-%d %X', time.localtime( _tmp ) ), _tmp
                    
                try:#处理有type的
                    _value = _handle( data,
                                      Byte,
                                      Bit,
                                      Length,
                                      OMAPParser.OMAP_UNPACK_TYPE[( _content[0], _content[-1] )] )
                except:#没有type的长度小于8的
                    if _content[3] > 0:
                        _value = _handle( data,
                                          Byte,
                                          Bit,
                                          Length,
                                          '!B' )
                    else:
                        if 0 != Length: 
                            print "getShowDataValue error:", _content
                        _value = 0
                            
                return str( _value ), _value
        
            else:
                if 8 >= _content[3]:
                    _Type = "!B"
                else:
                    _Type = OMAPParser.OMAP_UNPACK_TYPE[ _content[-1] ]

                _value = _handle( data,
                                  Byte,
                                  Bit,
                                  Length,
                                  _Type )
                try:
                    return OMAPParser.Enu_dic[_content[0]][_value], _value
                except KeyError, e:
                    print "unKnow type:", _content, e
                    return str( _value ), _value
        except:
            if 0 != Length:
                print "getValueByName error:", Label, Type
            return "0", 0
    
    @classmethod
    def getShowDataValueByLabel( cls, OMAPLogData, FrameLabel, Page, Num, label, CompressFlag ):
        "get show data"
        _data = OMAPLogData[FrameLabel][Num] #某一帧数据"00000"
        #获取当前页的数据
        try:
            _Config = OMAPParser.OMAPLogShow[FrameLabel][Page] #{( rows, col ):[Label, Type, Byte, Bit, Length]}
        except KeyError, e:
            _Config = {}
            
        _rev = []
        for _key in _Config:
            if _Config[_key][0] == label:
                _rev.append( cls.getShowDataValue( _data, *( _Config[_key] + [ CompressFlag[FrameLabel]] ) ) )

        return _rev
    
    @classmethod
    def getShowDataVariantNameList( cls, FrameLabel ):
        "get show data variant name list"
        _list = cls.OMAPSearchShow[FrameLabel].keys()
        _list.sort()
        return _list
    
    @classmethod
    def getShowDataValueListByLabel( cls, OMAPLogData, FrameLabel, Label, CompressFlag ):
        "get show data"
        _oneFrameData = OMAPLogData[FrameLabel] #某一帧数据"00000"
        #获取该数据的偏移相关信息
        ( _page, _row, _col ) = cls.OMAPSearchShow[FrameLabel][Label]
        _Config = OMAPParser.OMAPLogShow[FrameLabel][_page][( _row, _col )] #{( rows, col ):[Label, Type, Byte, Bit, Length]}
            
        _revStr = []#字符串列
        _revInt = []#数据列
        for _data in _oneFrameData:
            _tmpValue = cls.getStringAndNumDataValue( _data, *( _Config + [CompressFlag[FrameLabel]] ) )
                
            _revStr.append( _tmpValue[0] )
            _revInt.append( _tmpValue[1] )
        return _revStr, _revInt     
    
    @classmethod
    def TranStrToInt( self, Type, str, Len = None ):
        "tranform string to int"
        _str = ""
        if None == str:
            return "0"
#        print "TranStrToInt:", Type, str, Len 
        if None == Len:
            Len = len( str ) / 2
        
        if Len == 3:#24的要补值
            str = "00" + str
            
        for _i in range( Len ):
#            print _i
            _str += chr( int( str[2 * _i: 2 * ( _i + 1 )], 16 ) )
        return struct.unpack( Type, _str )[0]
#        ord( "a" ), chr( i )

    @classmethod
    def importCompressOMAPFile( cls, path ):
        "import Compress OMAP File"
        _Data = []
        _Poslist = []
        _Time = []
        try:
            _fOMAP = open( path, "rb" )
            _content = _fOMAP.read()
            #读取头部信息
            _label = _content[20:50].strip()
            _frameSize = int( _content[50:60] )
            _count = int( _content[60:70] )
            
            _contentData = cls.__ZLIBDll.inflateStr( _content[120:] )
#            _fOMAPtmp = open( path + "tmp1", "wb" )   
#            _fOMAPtmp.write( _content[120:] )
#            _fOMAPtmp.close()
#            cls.__ZLIBDll.inflate( path + "tmp1", path + "tmp2" ) 
#            _fOMAPtmp = open( path + "tmp2", "rb" )
#            _contentData = _fOMAPtmp.read()
#            _fOMAPtmp.close()
#            filehandle.deleteFile( path + "tmp1" )
#            filehandle.deleteFile( path + "tmp2" )
            _fOMAP.close()
        
            #读取数据
            for _i in range( _count ):
                _Data.append( _contentData[( _frameSize + 25 ) * _i:
                                           ( _frameSize + 25 ) * _i + _frameSize ] )
                _Time.append( _contentData[( _frameSize + 25 ) * _i + _frameSize:
                                           ( _frameSize + 25 ) * ( _i + 1 )  ].strip() )

#            _fOMAP.close()
            
            if True == os.path.exists( path + ".info" ):
                _fInfo = open( path + ".info", "rb" )
                _info = _fInfo.read()
                _fInfo.close()
                for _i in range( _count ):
                    _Poslist.append( ( str( struct.unpack( "!I", _info[8 * _i:8 * _i + 4] )[0] ),
                                       str( struct.unpack( "!f", _info[8 * _i + 4:8 * _i + 8] )[0] ) ) )
                    
                
            else:
                for _i in range( _count ):
                    _Poslist.append( ( "No Position", "No Position" ) )                
                       
            return _label, _Data, _Poslist, _Time
        except:
            return None, None, None, None        
        
    @classmethod
    def importXMLOMAPFile( self, path ):
        "import XML OMAP File"
        _Data = []
        _Poslist = []
        _Time = []
        try:
            _f = XmlParser()
            _f.loadXmlFile( path )
            
            _frameNode = _f.getElementByName( ".//FRAME" )
            _label = _f.getAttrListOneNode( _frameNode, ["label"] )[0]
            _CHs = _f.getAllElementByName( ".//CH" )
            _Datas = _f.getAllElementByName( ".//DATA" )
            _Times = _f.getAllElementByName( ".//TIME" )
            for _d in _Datas:
                _Pos = _f.getAttrListOneNode( _d, ["blockid", "abscissa"] )
                if _Pos != [None, None]:
                    _Poslist.append( _Pos )
                else:
                    _Poslist.append( ( "No Position", "No Position" ) )

            for _ch in _CHs:
                _Data.append( _f.getNodeText( _ch ) )
                
            for _t in _Times:
                _Time.append( _f.getNodeText( _t ) )
                
            return _label, _Data, _Poslist, _Time
        except:
            return None, None, None, None
        
        
    def joinPath( self, logfolder ):
        "join path to save path"
        self.OMAPSave_Path = commlib.joinPath( logfolder , "OMAPData.zip" ) 
        for _ID in self.__omapHandle:
            self.__omapHandle[_ID][-2] = commlib.joinPath( logfolder , self.__omapHandle[_ID][-2] ) 

    def StartListening( self ):
        "start listen OMAP."
        #开启OMAP接收数据socket,所有的socket在simulator里面已经开启了
        self.__socket = None
        try:
#            self.__socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
#            self.__socket.bind( ( self.__IP, self.__PORT ) )
            self.__socket = self.__TPSNode.getSocketByLocalID( self.__IPAddrID )
        except socket.error, e:
            print 'addr %s create socket error %s' % ( self.__IPAddrID, e )
            return
#        self.__socket.setblocking( 0 )  #设置成非阻塞模式
        self.__socket.setsockopt( socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 64 ) #设置缓存大小为64k以前的太小了
        self.__socket.settimeout( 1 )
        
        while self.__Listening:
#            _data = None
            _rs, _ws, _es = select.select( [self.__socket], [], [], 1 )
            for _sock in _rs:
                #print 'read socket ', _sock.getsockname(), 'index, ', _socketList.index(_sock)
                try:
#                    _data = self.__socket.recv( self.maxMessageSize )
                    _data = _sock.recv( self.maxMessageSize )
                except socket.error , e:
                    print 'socket:', self.__socket.getsockname(), ' recv data error ', e
                    _data = None            
                if _data != None:
                    self.handleData( _data )
        
        print "end OMAP socket."
        
#        self.__socket.close()
        self.__socket = None    
    
    #处理omap数据
    def handleData( self, data ):
        "handle omap data."
        if None == data:
            return
        _rms_sigLen = 30
        #获取消息ID
        _ID = struct.unpack( "!B", data[28] )[0]
#        print 'omap', _ID 
        #将数据给OMAP
        try:
            OMAPParser.OMAPQue[_ID].put( data[_rms_sigLen:] )   
        except KeyError, e:
            pass
        
    @classmethod
    def getValueByName( cls, data, FrameLabel, Name ):
        "get Value by Framelabel and Name"
        try:
            _content = OMAPParser.OMAPFormat[FrameLabel][Name]
            if _content[-1] >= 8:
#                print OMAPParser.OMAP_UNPACK_TYPE[( _content[0], _content[-1] )] 
                try:
                    _value = commlib.getValueFromStrByInfo( data,
                                                            _content[1],
                                                            _content[2],
                                                            _content[-1],
                                                            OMAPParser.OMAP_UNPACK_TYPE[( _content[0], _content[-1] )] )
#                    _value = struct.unpack( OMAPParser.OMAP_UNPACK_TYPE[( _content[0], _content[-1] )], \
#                                           data[_content[1]: _content[1] + ( _content[-1] / 8 )] )[0]
                except:
                    _value = commlib.getValueFromStrByInfo( data,
                                                            _content[1],
                                                            _content[2],
                                                            _content[-1],
                                                            '!B' )

#                    _value = struct.unpack( '!B', \
#                                           data[_content[1]: _content[1] + ( _content[-1] / 8 )] )[0]
                if OMAPParser.OMAP_UNPACK_TYPE.has_key( ( _content[0], _content[-1] ) ):
                    return str( _value )
                else:
                    return OMAPParser.Enu_dic[_content[0]][_value]
            else:
                _value = commlib.getValueFromStrByInfo( data,
                                                        _content[1],
                                                        _content[2],
                                                        _content[-1],
                                                        '!B' )
                try:
                    return OMAPParser.Enu_dic[_content[0]][_value]
                except KeyError, e:
                    print "unKnow type:", _content[0], e
                    return str( _value )
        except:
            print "getValueByName error:", FrameLabel, Name
            return "0"
    
    @classmethod
    def refreshDataList( cls, FrameLabel, data ):
        "refresh Data List"
        cls.OMAPShow_mutex.acquire()
        for _item in OMAPParser.OMAPShow[FrameLabel]:
            OMAPParser.OMAPShow[FrameLabel][_item] = cls.getValueByName( data, FrameLabel, _item )
#        print FrameLabel , OMAPParser.OMAPShow[FrameLabel]
        cls.OMAPShow_mutex.release()
    
        
    def StartOMAP( self, ID ):
        "start omap."
        #根据队列的个数开启线程记录omap
        OMAPParser.OMAPSave_mutex[ID] = threading.Lock()
        _OMPInfoData = []    #[]
        _LastTime = None #记录在_tempV中存储的OMAP消息的loophour最小的值
        _CurTime = None
        _WholeNum = None
        _CurSer = None
        _tempV = [None] * self.__OMAPToleratenceNum
        index = 0
        OMAPParser.OMAPSave_mutex[ID].acquire()
        #开启数据存储文件句柄
        _file = open( self.__omapHandle[ID][-2] + "dgztmp", "wb" ) #未压缩的数据
        while True:
            #获得消息，无消息是阻塞
            try:
                _msg = OMAPParser.OMAPQue[ID].get()
            except KeyError, e:
                print OMAPParser.OMAPQue, e
            #接受的消息的长度如果小于6则表示退出omap记录
            if len( _msg ) < 6:
                break
            
            #获取消息头
            _OMAPHead = struct.unpack( "!IBB", _msg[0:6] )
            _CurTime = _OMAPHead[0]
            _WholeNum = _OMAPHead[1]
            _CurSer = _OMAPHead[2]

            if None == _LastTime and _CurTime < 10:#去除掉上一次用例残留消息的可能性
                _LastTime = _CurTime
            elif None == _LastTime:
                continue
            
            if _CurTime >= _LastTime + self.__OMAPToleratenceNum:
                #要从数据中剔除一包，出现丢帧现象
                for _i in range( _CurTime - _LastTime - self.__OMAPToleratenceNum + 1 ):
                    _tempV.pop( 0 )
                    _tempV.append( None )
                    print "lost OMAP msg! Num:", _LastTime
                    _LastTime += 1
                    
                _tempV[-1] = [0] * _WholeNum 
                #储存数据
                _tempV[-1][_CurSer - 1] = _msg[6:]
                _LastTime += self.saveFullFrame( _tempV, _file, _OMPInfoData, ID )
            else:
                try:
                    if None != _tempV[_CurTime - _LastTime]:
                        _tempV[_CurTime - _LastTime][_CurSer - 1] = _msg[6:]
                    else:
                        _tempV[_CurTime - _LastTime] = [0] * _WholeNum 
                        _tempV[_CurTime - _LastTime][_CurSer - 1] = _msg[6:]
                            
    #                _LastTime += self.saveFullFrame( _tempV, _OMPData, ID )
                    _LastTime += self.saveFullFrame( _tempV, _file, _OMPInfoData, ID )
                except IndexError, e:
                    print "StartOMAP", _CurTime - _LastTime, _CurTime, _LastTime
            
        #跳出循环之后进行储存数据处理
#        OMAPParser.OMAPSave_mutex[ID].acquire()
#        self.SaveOMAPData( self.__omapHandle[ID][-2], _OMPData, ID )
        _file.close()
        #开始压缩
        self.SaveOMAPCompressData( self.__omapHandle[ID][-2], _OMPInfoData, ID )
        OMAPParser.OMAPSave_mutex[ID].release()
        _OMPData = []
    
    #-----------------------------------------------------
    #遍历OMAP记录的缓冲区，将最老的，接受完成的进行存储
    #filehandle:为存储数据的句柄
    #OMAPInfoData,每帧数据中的基本信息[info,...]
    #info:[time,block,abs]
    #ID为OMAP消息ID
    #-----------------------------------------------------
    def saveFullFrame( self, FrameContainer, filehandle, OMAPInfoData, ID ):
        "save Full Frame"
        _index = None
        for _i, _content in enumerate( FrameContainer ):
            if self.checkOneFrameFull( _content ):
                _tempMsg = ""
                for _temp in _content:

                    _tempMsg = _tempMsg + _temp
                if self.__needDeCompressFlag:
                    _tempMsg1 = OMAPParser.__decompressDll.getDecompressStr( _tempMsg, len( _tempMsg ), int( self.__omapHandle[ID][3] ) )
                else:
                    _tempMsg1 = _tempMsg
#                OMAPData.append( [commlib.GetCurTime(), self.getHexStr( _tempMsg1, int( self.__omapHandle[ID][3] ) ) ] + self.GetCurPosition() )
                OMAPInfoData.append( [commlib.GetCurTime()] + self.GetCurPosition() )
                #写入数据
                _curtime = commlib.GetCurTime()
                _time = " " * ( 25 - len( _curtime ) ) + _curtime
                filehandle.write( _tempMsg1 + _time )
                
                self.refreshDataList( self.getNameByID( ID ), _tempMsg )

                _index = _i + 1
            else:
                break
        
        if None != _index:
            for _i in range( _index ):
                FrameContainer.pop( 0 )
                FrameContainer.append( None )

            return _index
        else:
            return 0

    #-----------------------------------------------------
    #校验某帧消息是否收到
    #-----------------------------------------------------
    def checkOneFrameFull( self, FrameList ):
        "check one frame full"
        if None == FrameList:
            return False
        elif 0 in FrameList:
            return False
        elif None in FrameList:
            return False
        else:
            return True
    
    #---------------------------------
    #将数据转换为16进制显示的字符，数据不够的将补零
    #--------------------------------
    def getHexStr( self, data, Len ):
        "get Hex str."
        _left = Len - len( data )
        if _left >= 0:
            return binascii.hexlify( data ) + "00" * _left
        else:
            print "getHexStr wrong!!! OUT of range."

    #------------------------------------------------------------------
    #@按照OMAP的iTC记录格式存储数据,
    #Data：[[date,data],...]
    #------------------------------------------------------------------    
    def SaveOMAPCompressData( self, path, omapInfoData, ID ):
        "save OMAP Data in OMAP compress Form"
        if False == self.__ZLIBDll.deflate( path + "dgztmp", path, level = 9 ):
            print "SaveOMAPCompressData Error!"
            filehandle.deleteFile( path + "dgztmp" )
            return
        filehandle.deleteFile( path + "dgztmp" )
        #开始写头部分
        _Head = ""
        _Head += " " * ( 20 - len( self.__omapHandle[ID][2] ) ) + self.__omapHandle[ID][2]
        _Head += " " * ( 30 - len( self.__omapHandle[ID][0] ) ) + self.__omapHandle[ID][0]
        _Head += "0" * ( 10 - len( self.__omapHandle[ID][3] ) ) + self.__omapHandle[ID][3]
        _Head += "0" * ( 10 - len( str( len( omapInfoData ) ) ) ) + str( len( omapInfoData ) )
        _Head += " " * ( 25 - len( omapInfoData[0][0] ) ) + omapInfoData[0][0]
        _Head += " " * ( 25 - len( omapInfoData[-1][0] ) ) + omapInfoData[-1][0]       
       
        #写入头部分
        _file = open( path, "rb" )
        _content = _file.read()
        _file.close()
        _content = _Head + _content
        _file = open( path, "wb" )
        _file.write( _content )
        _file.close()
    
        #写位置信息文件
        _file = open( path + ".info", "wb" )
        for _info in omapInfoData:
            try:
                _file.write( struct.pack( "!I", int( _info[1] ) ) )
                _file.write( struct.pack( "!f", float( _info[2] ) ) )
            except:
                _file.write( struct.pack( "!I", 0 ) )
                _file.write( struct.pack( "!f", 0 ) )
        _file.close()
    
    
    #------------------------------------------------------------------
    #@按照OMAP XML的记录格式存储数据
    #Data：[[date,data],...]
    #------------------------------------------------------------------    
    def SaveOMAPData( self, path, Data, ID ):
        "save OMAP Data in OMAP Form"
        if 0 == len( Data ):
            return
        
        _file = open( path, "w" )
        
        _order = etree.Element( "ORDER" )        
        
        #写Frame
        _Frame = etree.SubElement( _order, "FRAME" )
        _Frame.set( "type", self.__omapHandle[ID][2] )
        _Frame.set( "label", self.__omapHandle[ID][0] )
        _Frame.set( "framelength", self.__omapHandle[ID][3] )
        _Frame.set( "datacount", str( len( Data ) ) )
        _Frame.set( "starttime", Data[0][0] )
        _Frame.set( "endtime", Data[-1][0] )
        
        #写Comment
        _Comment = etree.SubElement( _order, "COMMENT" )
        
        #写数据
        for _d in Data:
            _data = etree.SubElement( _order, "DATA" )
            _data.set( "blockid", _d[2] )
            _data.set( "abscissa", _d[3] )
            _time = etree.SubElement( _data, "TIME" )
            _time.text = _d[0]
            _ch = etree.SubElement( _data, "CH" )
            _ch.text = _d[1]
        
        _OMAP_String = etree.tostring( _order, pretty_print = True, encoding = "GB2312" )
        _file.write( _OMAP_String )
        _file.close()
        
    def OMAPRun( self ):
        "omap run"
        for _ID in self.__omapHandle:
            #开启存储线程
            _thread = MThread( self.StartOMAP, ( _ID, ), "OMAP" + str( _ID ) )
#            _thread.isDaemon()
#            _thread.setDaemon( True )
#            _thread.start()        
            _thread.StartThread()
              
    def OMAPListen( self ):
        "omap listen"
        _thread = MThread( self.StartListening, "", "OMAP Listen" )
#        _thread.isDaemon()
#        _thread.setDaemon( True )
#        _thread.start()
        _thread.StartThread()          
    
    @classmethod
    def getShowData( cls, FrameLabel ):
        "get Show Data."
        cls.OMAPShow_mutex.acquire()
        _rev = cls.OMAPShow[FrameLabel]
        cls.OMAPShow_mutex.release()
        return _rev
    
    def OMAPEnd( self ):
        "omap run"
        self.__Listening = False
        for _ID in self.__omapHandle:
            #发送关闭OMAP命令
            OMAPParser.OMAPQue[_ID].put( "ST" )
        
        time.sleep( 1 ) #等待数据的存储开始  
        #将OMAP数据进行压缩并删除原有数据
        _fZip = zipfile.ZipFile( self.OMAPSave_Path, "w", zipfile.ZIP_DEFLATED )        
        for _ID in self.__omapHandle:
            if True == os.path.exists( self.__omapHandle[_ID][-2] ):
                OMAPParser.OMAPSave_mutex[_ID].acquire() #保证还没save完成之前不进行压缩
                _folder, _filename = os.path.split( self.__omapHandle[_ID][-2] )
                _fZip.write( self.__omapHandle[_ID][-2], _filename )
                _fZip.write( self.__omapHandle[_ID][-2] + ".info", _filename + ".info" )
                OMAPParser.OMAPSave_mutex[_ID].release()
                #压缩完成删除源文件
                filehandle.deleteFile( self.__omapHandle[_ID][-2] )
                filehandle.deleteFile( self.__omapHandle[_ID][-2] + ".info" )
        _fZip.close()
#        time.sleep( 0.1 )
        OMAPParser.OMAPQue = {}
        #清空数据
        OMAPParser.OMAPSave_mutex = {}


class OMAPFigureDataHandle():
    '''
    OMAP Figure Data Handle
    '''
    
    #用于保存当前显示的配置信息
    #具体格式如下:
    #{FrameLabel:{Variantlabel:VariantConfig,...},...}
    #VariantConfig:[Max,Min,linestyle,linewidth,color,showflag]
    #color:(0.1,0.1,0.1),showflag表示当前变量是否显示到figure上去
    __configDic = {} #用于保存当前显示的配置信息
    
    #用于保存所有显示的线的根节点
    #具体格式如下:
    #{FrameLabel:{label:lineobj,...},...}
    __linesDic = {} #用于保存当前显示的配置信息    
    
    #用于保存现在在用或者曾今用过的变量的数据
    #具体格式如下：
    #{Framelabel:{Variantlabel:[StringList,NumList],...},...}
    __omapDataDic = {}
    
    
    #用于记录当前的信息
    __OMAPLogData = None
    __OMAPTimeData = None
    
    
    #区分比较明显的color
    __colorList = [( 1, 0, 0 ), ( 0, 1, 0 ), ( 0, 0, 1 ),
                   ( 1, 0.5, 0 ), ( 1, 0, 0.5 ), ( 0, 1, 0.5 ),
                   ( 0, 0.5, 1 ), ( 0.5, 1, 0 ), ( 0.5, 0, 1 ) ]
    
    
    def __init__( self ):
        self.__configDic = {}
        self.__linesDic = {}
        self.__omapDataDic = {}
    
    def attachLogData( self, OMAPLog, OMAPTimeData, OMAPCompressFlag ):
        "attach log data"
        self.__OMAPLogData = OMAPLog
        self.__OMAPTimeData = OMAPTimeData
        self.__OMAPCompressFlag = OMAPCompressFlag
    
    def getFrameSize( self, FrameLabel ):
        return OMAPParser.getOMAPFrameSize( self.__OMAPLogData, FrameLabel ) 
    
    def getCurTimeString( self, FrameLabel, CurNum ):
        return self.__OMAPTimeData[FrameLabel][CurNum]
    
    #---------------------------------------------------------------
    #注意这里的变量名字列表为去除掉已经选中的之后的列表
    #---------------------------------------------------------------
    def getOMAPVariantList( self, FrameLabel ):
        "get OMAP Variant List"
        _NameList = OMAPParser.getShowDataVariantNameList( FrameLabel )
        #去掉已经选中的配置
        if self.__configDic.has_key( FrameLabel ):
            _selectNameList = self.__configDic[FrameLabel].keys()
        else:
            _selectNameList = []
#        print "---------", _selectNameList
        for _name in _selectNameList:
            _index = _NameList.index( _name )
            _NameList.pop( _index )
            
        _NameList.sort()
        
        return _NameList
    
    
    def removeVariantToConfigDic( self, FrameLabel, Label ):
        "remove variant to config dic"
        self.__configDic[FrameLabel].pop( Label )
        
    def addVariantToConfigDic( self, FrameLabel, Label ):
        "add variant to config dic"
        #omapdatadic先获取label的所有值,已经存在的时候不需要重复计算
        if self.__omapDataDic.has_key( FrameLabel ):
            if not self.__omapDataDic[FrameLabel].has_key( Label ):
                self.__omapDataDic[FrameLabel][Label] = OMAPParser.getShowDataValueListByLabel( self.__OMAPLogData,
                                                                                                FrameLabel,
                                                                                                Label,
                                                                                                self.__OMAPCompressFlag )
            
        else:
            self.__omapDataDic[FrameLabel] = {}
            self.__omapDataDic[FrameLabel][Label] = OMAPParser.getShowDataValueListByLabel( self.__OMAPLogData,
                                                                                            FrameLabel,
                                                                                            Label,
                                                                                            self.__OMAPCompressFlag )
#            print self.__omapDataDic[FrameLabel][Label]
        #configdic
        #[Max,Min,linestype,linewidth,color,showflag]
        #计算最大与最小值
        _Numlist = self.__omapDataDic[FrameLabel][Label][1]
#        print _Numlist
        _Max = max( _Numlist )
        _Min = min( _Numlist )
        if self.__configDic.has_key( FrameLabel ):
            if not self.__configDic[FrameLabel].has_key( Label ):
                self.__configDic[FrameLabel][Label] = [_Max + 1, _Min - 1, "-", 1.5, self.getRandomColor( FrameLabel ), True] #取默认值
            
        else:
            self.__configDic[FrameLabel] = {}
            self.__configDic[FrameLabel][Label] = [_Max + 1, _Min - 1, "-", 1.5, self.getRandomColor( FrameLabel ), True] #取默认值,后面color可能会从列表中区获取
    
    #--------------------------------------------------------------
    #获取当前grid中显示的值
    #--------------------------------------------------------------
    def getGridShowData( self, FrameLabel, CurNum ):
        if not self.__configDic.has_key( FrameLabel ):
            return []
        _NameList = self.__configDic[FrameLabel].keys()
        _NameList.sort()
        
        _rev = []
        for _item in _NameList:
            _rev.append( [_item, self.__omapDataDic[FrameLabel][_item][0][CurNum]] )
        return _rev
    
    #---------------------------------------------------------------
    #重新设置__configDic
    #---------------------------------------------------------------
    def resetConfigDic( self, configDic ):
        self.__configDic = configDic
        #更新self.__omapDataDic,将没有的数据导入进来,否则会影响后面的计算
        for _FrameLabel in self.__configDic:
            for _Label in self.__configDic[_FrameLabel]:
                if self.__omapDataDic.has_key( _FrameLabel ):
                    if not self.__omapDataDic[_FrameLabel].has_key( _Label ):
                        self.__omapDataDic[_FrameLabel][_Label] = OMAPParser.getShowDataValueListByLabel( self.__OMAPLogData,
                                                                                                          _FrameLabel,
                                                                                                          _Label,
                                                                                                          self.__OMAPCompressFlag )
                    
                else:
                    self.__omapDataDic[_FrameLabel] = {}
                    self.__omapDataDic[_FrameLabel][_Label] = OMAPParser.getShowDataValueListByLabel( self.__OMAPLogData,
                                                                                                      _FrameLabel,
                                                                                                      _Label,
                                                                                                      self.__OMAPCompressFlag )

    #---------------------------------------------------------------
    #获取当前某一configDic中的label的list
    #---------------------------------------------------------------
    def getConfigLabelList( self, FrameLabel ):
        if self.__configDic.has_key( FrameLabel ):
            return self.__configDic[FrameLabel].keys()
        else:
            return []
    
    #---------------------------------------------------------------
    #修改line的showflag属性
    #---------------------------------------------------------------
    def modifyLineShowFlag( self, FrameLabel, label, value ):
        self.__configDic[FrameLabel][label][-1] = value
        self.__linesDic[FrameLabel][label].set_visible( value )

    #---------------------------------------------------------------
    #修改line的Max属性
    #---------------------------------------------------------------
    def modifyLineMaxValue( self, FrameLabel, label, maxValue, plotFunc, timeInterval, Num ):
        self.__configDic[FrameLabel][label][0] = maxValue
        #先删除
        self.__linesDic[FrameLabel][label].remove()
        #再添加
        self.addOneLineIntoAxes( FrameLabel, label, plotFunc, timeInterval, Num )

    #---------------------------------------------------------------
    #修改line的Min属性
    #---------------------------------------------------------------
    def modifyLineMinValue( self, FrameLabel, label, minValue, plotFunc, timeInterval, Num ):
        self.__configDic[FrameLabel][label][1] = minValue    
        #先删除
        self.__linesDic[FrameLabel][label].remove()
        #再添加
        self.addOneLineIntoAxes( FrameLabel, label, plotFunc, timeInterval, Num )


    #---------------------------------------------------------------
    #修改line的linestyle属性
    #---------------------------------------------------------------
    def modifyLineStyle( self, FrameLabel, label, linestyle ):
        self.__configDic[FrameLabel][label][2] = linestyle  
        self.__linesDic[FrameLabel][label].set_linestyle( linestyle )
        
    #---------------------------------------------------------------
    #修改line的linewidth属性
    #---------------------------------------------------------------
    def modifyLineWidth( self, FrameLabel, label, lineWidth ):
        self.__configDic[FrameLabel][label][3] = lineWidth
        self.__linesDic[FrameLabel][label].set_linewidth( lineWidth )  

    #---------------------------------------------------------------
    #修改line的color属性
    #---------------------------------------------------------------
    def modifyLineColor( self, FrameLabel, label, lineColor ):
        self.__configDic[FrameLabel][label][4] = lineColor
        self.__linesDic[FrameLabel][label].set_color( lineColor )    
            
    #-------------------------------------------------------------
    #获得一条线的所有属性[Max,Min,linestyle,linewidth,color,showflag]
    #-------------------------------------------------------------
    def getLineAllInfo( self, FrameLabel, label ):
        if not ( self.__configDic.has_key( FrameLabel ) and \
                self.__configDic[FrameLabel].has_key( label ) ):
            return None 
        return self.__configDic[FrameLabel][label]
        
    #-------------------------------------------------------------
    #获取现在图中所有线的基本信息,包括线的颜色和形状和是否显示
    #-------------------------------------------------------------
    def getAllLineInfo( self, FrameLabel ):
        _rev = []
        if not self.__configDic.has_key( FrameLabel ):
            return _rev
        _NameList = self.__configDic[FrameLabel].keys()
        _NameList.sort()
        
        for _label in _NameList:
            _info = self.__configDic[FrameLabel][_label]
            _rev.append( [_label + _info[2] + _info[2] + _info[2], _info[4], _info[-1]] )
        return _rev
    
    #-------------------------------------------------------------
    #随机获得一个颜色,如果没有超过基本色，则使用基本色，反之随机获取
    #-------------------------------------------------------------
    def getRandomColor( self, FrameLabel ):
#        return ( 1, 0.5, 0.5 )
        if len( self.__colorList ) > len( self.__configDic[FrameLabel] ):
            return self.__colorList[len( self.__configDic[FrameLabel] )]
        else:
            return ( random.random(), random.random(), random.random() )
    
    def delOneLineFromAxes( self, FrameLabel, label ):
        self.__linesDic[FrameLabel][label].remove()
        self.__linesDic[FrameLabel].pop( label )
    
    def setSelectionMarker( self, FrameLabel, label ):
        "set selection"
        for _label in self.__linesDic[FrameLabel]:
            self.__linesDic[FrameLabel][_label].set_marker( None )
        self.__linesDic[FrameLabel][label].set_marker( '.' )

    
    def addOneLineIntoAxes( self, FrameLabel, label, plotFunc, timeInterval, Num = 0 ):
        if not ( self.__configDic.has_key( FrameLabel ) and \
                 self.__configDic[FrameLabel].has_key( label ) ):
            print "addOneLineIntoAxes Error: not have Lines config", FrameLabel, label
            return
        
        _info = self.__configDic[FrameLabel][label] #[Max,Min,linestype,linewidth,color,showflag]

        _DataX = []
        _DataY = []            
        _numDataList = self.__omapDataDic[FrameLabel][label][1]
        for _i, _num in enumerate( _numDataList ):
            _DataY.append( float ( _num - _info[1] ) / ( _info[0] - _info[1] ) )
            _DataX.append( ( _i - Num ) * timeInterval )
        if not self.__linesDic.has_key( FrameLabel ):
            self.__linesDic[FrameLabel] = {}
        self.__linesDic[FrameLabel][label] = plotFunc( dataX = _DataX,
                                                       dataY = _DataY,
                                                       style = _info[2],
                                                       color = _info[4],
                                                       linewidth = _info[3] )
        self.__linesDic[FrameLabel][label].set_visible( _info[-1] )
    
    def removeAllLines( self, FrameLabel ):
        #清空记录的画图的线
        if not self.__linesDic.has_key( FrameLabel ):
            return
        for _label in self.__linesDic[FrameLabel]:
            self.__linesDic[FrameLabel][_label].remove()
        self.__linesDic[FrameLabel] = {}
        
    #-------------------------------------------------------------
    #根据配置的数据画图
    #-------------------------------------------------------------
    def plotHandle( self, FrameLabel, plotFunc, timeInterval, Num = 0 ):
        #获取所有需要画图的数据
        #清空记录的画图的线
        self.__linesDic = {}
        if not self.__configDic.has_key( FrameLabel ):
            return
        
        for _label in self.__configDic[FrameLabel]:
            self.addOneLineIntoAxes( FrameLabel, _label, plotFunc, timeInterval, Num )
    
    def getConfigDic( self ):
        return self.__configDic

class OMAPFigureConfigHandle():
    '''
    OMAP Figure Config Handle
    '''

    #存储所有的已经存储好的配置
    #{ConfigName:[{FrameLabel:{Variantlabel:VariantConfig,...}},Desription],...}
    #VariantConfig:[Max,Min,linestyle,linewidth,color,showflag]    
    __OMAPFigureConfigDic = None
    
    def __init__( self ):
        pass
    
    @classmethod
    def importOMAPFigureFile( self, path ):
        "import OMAP Figure File"
        self.__OMAPFigureConfigDic = {}
        self.__OMAPFigureConfigDic = XMLDeal.importOMAPFigureConfig( path )
    
    @classmethod
    def renameConfig( cls, oldName, newName ):
        if cls.__OMAPFigureConfigDic.has_key( newName ):
            print "renameConfig Error, the config Name", newName, " exist already!"
            return False
        cls.__OMAPFigureConfigDic[newName] = cls.__OMAPFigureConfigDic[oldName] 
        cls.__OMAPFigureConfigDic.pop( oldName ) #删除原来的那个
        return True
    
    @classmethod
    def addNewOMAPFigureConfig( self, configName, configDic, Description ):
        "add New OMAP Figure File"
#        print "addNewOMAPFigureConfig", self.__OMAPFigureConfigDic, configName
        if self.__OMAPFigureConfigDic.has_key( configName ):
            print "addNewOMAPFigureConfig already has configName:", configName
            return None
        else:
            self.__OMAPFigureConfigDic[configName] = [copy.deepcopy( configDic ), Description]
            return True
    
    @classmethod
    def coverAnOMAPFigureConfig( self, configName, configDic, Description ):
        "cover an OMAP Figure File"
        self.__OMAPFigureConfigDic[configName] = [copy.deepcopy( configDic ), Description]
    
    @classmethod
    def delNewOMAPFigureConfig( self, configName ):
        "delete New OMAP Figure File"
        if self.__OMAPFigureConfigDic.has_key( configName ):
            self.__OMAPFigureConfigDic.pop( configName )
        else:
            print "delNewOMAPFigureConfig doesn't have configName:", configName
            return            
    
    @classmethod
    def saveOMAPFigureFile( self, path ):
        "save OMAP Figure File"
        XMLDeal.ExportOMAPFigureConfig( path, self.__OMAPFigureConfigDic )
        
    
    @classmethod
    def getConfigNameList( cls ):
        _list = cls.__OMAPFigureConfigDic.keys()
        _list.sort()
        return _list
    
    @classmethod
    def getConfigByName( cls, configName ):
        if cls.__OMAPFigureConfigDic.has_key( configName ):
            return copy.deepcopy( cls.__OMAPFigureConfigDic[configName][0] )
        else:
            return None
    
    @classmethod
    def setConfigDescription( cls, configName, Description ):
        if cls.__OMAPFigureConfigDic.has_key( configName ):
            cls.__OMAPFigureConfigDic[configName][1] = Description
        else:
            print "setConfigDescription Error, not have configName:", configName
        
    @classmethod
    def getConfigDescriptionByName( cls, configName ):
        if cls.__OMAPFigureConfigDic.has_key( configName ):
            return cls.__OMAPFigureConfigDic[configName][1] 
        else:
            return None
if __name__ == '__main__':
#    import time
#    t1 = time.time()
    _map = OMAPParser()
    _map.importConfig( r"../TPConfig/setting/omap_config.xml" )
#    _map.importFormat( r"../TPConfig/OMAPFormat.xml" )
#    print time.time() - t1
#    _map.importEnuDic( r"../TPConfig/Enumerate.xml" )
