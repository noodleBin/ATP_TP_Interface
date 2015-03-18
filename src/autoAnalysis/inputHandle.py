#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     inputHandle.py
# Description:  
# Author:       Sonnie Chen
# Version:      0.0.1
# Created:      2012-12-04
# Company:      CASCO
# LastChange:   create 2012-12-04
# History:          
#----------------------------------------------------------------------------
from expressionparser import ExpressionParser
from base.xmldeal import XMLDeal
from base.xmlparser import XmlParser
import struct
import os
import zipfile
from base import filehandle
from base import commlib
from base.omapparser import OMAPParser 
from base import simdata


class OMAPInput():
    """
    OMAP Input
    """
    OMAPLogData = {}
    OMAPPosData = {}
    
    OMAPFormat = {} #OMAP消息对应的解析格式，{FRAMELABEL:{Label:[Type,Byte,Bit,Length],...},...],...} #Label必须唯一否则会被覆盖

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
    
    def __init__( self ):
        pass
   
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
    def LoadZipOMAPData( self, folder ):    
        "load OMAPdATA.ZIP"
        #_OMAPLogData = {}
        _path = os.path.join( folder, "OMAPData.zip" )

        if True == os.path.exists( _path ):
            _fUNZip = zipfile.ZipFile( _path, "r", zipfile.ZIP_DEFLATED )

            _fUNZip.extractall( path = folder ) 

            _delfilelist = _fUNZip.namelist()
            _fUNZip.close()
            OMAPInput.OMAPLogData, OMAPInput.OMAPPosData = self.LoadOMAPData( folder )
            #delete unzipped temp files
            for _file in _delfilelist:
                _temppath = os.path.join( folder, _file )
                filehandle.deleteFile( _temppath )
#        print "OMAPInput.OMAPPosData", OMAPInput.OMAPPosData
        #return _OMAPLogData, _OMAPPosData        
    
    @classmethod
    def LoadOMAPData( self, folder ):    
        "load OMAP Data"
        _OMAPLogData = {}
        _OMAPPosData = {}
        for root, dirs, files in os.walk( folder ):
            for _file in files:
                if ".xml" in _file:#only XML files
                    _filepath = os.path.join( root, _file )
                    _label, _Data, _Poslist = self.importOMAPFile( _filepath )
                    if _Data != None and _label != None:
#                        print _label
                        if False == _OMAPLogData.has_key( _label ):
                            _OMAPLogData[_label] = _Data
                            _OMAPPosData[_label] = _Poslist
                    
            return _OMAPLogData, _OMAPPosData
    
    @classmethod
    def importOMAPFile( self, path ):
        "import OMAP File"
        _Data = []
        _Poslist = []
        try:
            _f = XmlParser()
            _f.loadXmlFile( path )
            
            _frameNode = _f.getElementByName( ".//FRAME" )
            _label = _f.getAttrListOneNode( _frameNode, ["label"] )[0]
            _CHs = _f.getAllElementByName( ".//CH" )
            _Datas = _f.getAllElementByName( ".//DATA" )
            for _d in _Datas:
                _Pos = _f.getAttrListOneNode( _d, ["blockid", "abscissa"] )
                if _Pos != [None, None]:
                    _Poslist.append( _Pos )
                else:
                    _Poslist.append( ( "No Position", "No Position" ) )

            for _ch in _CHs:
                _Data.append( _f.getNodeText( _ch ) )
            return _label, _Data, _Poslist
        except:
            return None, None, None

    @classmethod
    def importFormat( self, path ):
        "import Format"
        #{FRAMELABEL：{Page:{(rows,col):[Label,Type,Byte,Bit,Length]}
        OMAPInput.OMAPFormat = {}
        #已经读取了的话不需要再读
        if len( OMAPParser.OMAPFormat ) > 0:     
            OMAPInput.OMAPFormat = OMAPParser.OMAPFormat 
            return
    
        _f = XmlParser()
        _f.loadXmlFile( path )
        
        _Format = _f.getAllElementByName( self.FormatParser['path'] )
#        tempTypelist = []
        for _ff in _Format:
            _FRAMELABEL = _f.getAttrListOneNode( _ff, self.FormatParser['attr'] )[0]
            if False == OMAPInput.OMAPFormat.has_key( _FRAMELABEL ):
                OMAPInput.OMAPFormat[_FRAMELABEL] = {}

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
            
            
            _label = _tmpList[0]
            _content2 = [_tmpList[1]] + [int( _i ) for _i in _tmpList[2:5]]
            OMAPInput.OMAPFormat[_FRAMELABEL][_label] = _content2
            

#        
#        print OMAPParser.OMAPFormat
#        print len(OMAPParser.OMAPFormat['iTC_ATP_UP'])
#        print len(OMAPParser.OMAPFormat['iTC_ATP_DOWN'])
#        print tempTypelist
#        print len(tempTypelist)
#        print OMAPParser.OMAPSearchShow

    @classmethod
    def importEnuDic( self, path ):
        "import Enu_dic"
        OMAPInput.Enu_dic = {}
        if len( OMAPParser.Enu_dic ) > 0:     
            OMAPInput.Enu_dic = OMAPParser.Enu_dic 
            return
        
        _f = XmlParser()
        _f.loadXmlFile( path )
        
        _Enus = _f.getAllElementByName( self.EnuXMLParser['path'] )
#        tempTypelist = []
        for _Enu in _Enus:
            _typekey = "Enu-" + _f.getAttrListOneNode( _Enu, self.EnuXMLParser['attr'] )[0]
            OMAPInput.Enu_dic[_typekey] = {}
            #添加枚举
            _Datas = _f.getNodeListInNode( _Enu, self.EnuXMLParser['subLabel'] )
            for _data in _Datas:
                _attrs = _f.getAttrListOneNode( _data, self.EnuXMLParser['subLabelattr'] )
                _code = int( _attrs[0] )
                _label = _attrs[1]
                OMAPInput.Enu_dic[_typekey][_code] = _label
                

    @classmethod
    def getShowDataValue( cls, data, FrameLabel, Name ):
        "get Show Data Value"    
        try:
            _content = OMAPInput.OMAPFormat[FrameLabel][Name]
    #        print 'data', len( data ), data
    #        print "content", _content
            if False == OMAPInput.Enu_dic.has_key( _content[0] ):#_content[-1] >= 8
    #                print OMAPParser.OMAP_UNPACK_TYPE[( _content[0], _content[-1] )] 
                if 'Hexa' in _content[0]:
                    return [data[2 * _content[1]: 2 * ( _content[1] + ( _content[-1] / 8 ) )], \
                            data[2 * _content[1]: 2 * ( _content[1] + ( _content[-1] / 8 ) )]]
                elif 'Binary' in _content[0]:
                    return [commlib.Hex2Bin( data[2 * _content[1]: 2 * ( _content[1] + ( _content[-1] / 8 ) )], _content[-1] ), \
                            commlib.Hex2Bin( data[2 * _content[1]: 2 * ( _content[1] + ( _content[-1] / 8 ) )], _content[-1] )]
                
                try:#处理有type的
                    _value = cls.TranStrToInt( OMAPInput.OMAP_UNPACK_TYPE[( _content[0], _content[-1] )], \
                                               data[2 * _content[1]: 2 * ( _content[1] + ( _content[-1] / 8 ) )] )
                except:#没有type的长度小于8的
#                    print data[2 * _content[1]: 2 * ( _content[1] + ( _content[-1] / 8 ) )]
                    if _content[-1] > 0:
                        _data = chr( int( data[2 * _content[1]: 2 * ( _content[1] + 1 )], 16 ) ) 
                        _value = commlib.getBitValueByLenOff( _data, _content[2], _content[3] )
                    else:
                        if 0 != _content[-1]: 
                            print "getShowDataValue error:", _content
                        _value = 0
    #                _value = cls.TranStrToInt( '!B', data[2 * _content[1]: 2 * ( _content[1] + ( _content[-1] / 8 ) )] )
                        
                return [ _value, str( _value ) ]
    
            else:
                if 8 >= _content[3]:
                    _data = chr( int( data[2 * _content[1]: 2 * ( _content[1] + 1 )], 16 ) ) 
                    _value = commlib.getBitValueByLenOff( _data, _content[2], _content[3] )
                else:
                    _value = cls.TranStrToInt( OMAPInput.OMAP_UNPACK_TYPE[ _content[-1] ], \
                                               data[2 * _content[1]: 2 * ( _content[1] + ( _content[-1] / 8 ) )] )
                try:
                    return [_value, OMAPInput.Enu_dic[_content[0]][_value]]
                except KeyError, e:
                    print "unKnow type:", _content, e
                    return str( _value )
        except:
            if 0 != _content[-1]:
                print "getValueByName error:", Name, _content[0]
            return "0"

    @classmethod
    def getValueByName( cls, data, FrameLabel, Name ):
        "get Value by Framelabel and Name"
        try:
            _content = OMAPInput.OMAPFormat[FrameLabel][Name]
            print _content
            if _content[-1] >= 8:
#                print OMAPParser.OMAP_UNPACK_TYPE[( _content[0], _content[-1] )] 
                try:
                    _value = struct.unpack( OMAPInput.OMAP_UNPACK_TYPE[( _content[0], _content[-1] )], \
                                           data[_content[1]: _content[1] + ( _content[-1] / 8 )] )[0]
                except:
                    _value = struct.unpack( '!B', \
                                           data[_content[1]: _content[1] + ( _content[-1] / 8 )] )[0]
                if OMAPInput.OMAP_UNPACK_TYPE.has_key( ( _content[0], _content[-1] ) ):
                    return str( _value )
                else:
                    return [str( _value ), OMAPInput.Enu_dic[_content[0]][_value]]
            else:
                _value = commlib.getBitValueByLenOff( data[_content[1]], _content[2], _content[3] )
                try:
                    return [str( _value ), OMAPInput.Enu_dic[_content[0]][_value]]
                except KeyError, e:
                    print "unKnow type:", _content[0], e
                    return str( _value )
        except:
            print "getValueByName error:", FrameLabel, Name
            return "0"
        
    def ifOmapData( self, varName, cycNo ):
#        print OMAPInput.getShowDataValue( OMAPInput.OMAPLogData['iTC_ATP_UP'][cycNo], 'iTC_ATP_UP', varName )
        return OMAPInput.getShowDataValue( OMAPInput.OMAPLogData['iTC_ATP_UP'][cycNo], 'iTC_ATP_UP', varName )

    def ifOmapCycleNo( self, cycStart, cycEnd, distStart, distEnd ): # unit: mm
        if cycStart == None:
            cycStart = 0
            print "input begin cycle of script is None!!!"
        if distStart == None:
            distStart = simdata.TrainRoute.getabsolutedistance( int( OMAPInput.OMAPPosData['iTC_ATP_UP'][0][0] ), \
                                                               int( float( OMAPInput.OMAPPosData['iTC_ATP_UP'][0][1] ) ) )
            print "input begin position of script is None!!!"
            print OMAPInput.OMAPPosData['iTC_ATP_UP'][0][0], \
            OMAPInput.OMAPPosData['iTC_ATP_UP'][0][1], distStart
        if cycEnd == None:
            
            cycEnd = len( OMAPInput.OMAPLogData['iTC_ATP_UP'] ) - 1
            print "input last cycle of script is None!!!", cycEnd
            
        if distEnd == None:          
            distEnd = simdata.TrainRoute.getabsolutedistance( int( OMAPInput.OMAPPosData['iTC_ATP_UP'][-1][0] ), \
                                                              int( float( OMAPInput.OMAPPosData['iTC_ATP_UP'][-1][1] ) ) )
            print "input last position of script is None!!!"
            print OMAPInput.OMAPPosData['iTC_ATP_UP'][-1][0], \
            OMAPInput.OMAPPosData['iTC_ATP_UP'][-1][1], distEnd
            
        #transform omap log per frame position to absolute distance
        i = 0
        _index1Found = False
        _index2Found = False
        for pos in OMAPInput.OMAPPosData['iTC_ATP_UP']:
            if simdata.TrainRoute.getabsolutedistance( int( pos[0] ), int( float( pos[1] ) ) ) >= distStart \
             and simdata.TrainRoute.getabsolutedistance( int( pos[0] ), int( float( pos[1] ) ) ) <= distEnd:
                if _index1Found == True:
                    pass
                else:
                    _index1 = i
                    _index1Found = True
                _index2 = i
                _index2Found = True
            i = i + 1
            
        print "index", _index1, _index2
        if _index1Found == False:
            _index1 = 0
            print "input begin position of script cannot be found"
        if _index2Found == False:
            _index2 = len( OMAPInput.OMAPLogData['iTC_ATP_UP'] ) - 1
            print "input last position of script cannot be found"
        
        # No intersection 
        if cycEnd <= _index1 or _index2 <= cycStart:
            print "No intersection"
            return [0, len( OMAPInput.OMAPLogData['iTC_ATP_UP'] ) - 1]
        
        # get intersection
        rtStart = max( cycStart, _index1 )
        rtEnd = min( cycEnd, _index2 )
        
        print rtStart, rtEnd
        return [rtStart, rtEnd]

            
        
        
class UsrDefInput():
    """
    MAP Input
    """
    MapConstParser = { 'subLabel': './/Const',
                       'attr': ['Id', 'Val', 'Type', 'Des']
                      }
#    ConstDict = {}
    
    
    def __init__( self ):
        pass
        
    
    def loadUsrDefDat( self, path , ReadDes = True ):
        
        self.ConstDict, self.UsrDefDict = XMLDeal.importAnalysisVar( path, ReadDes )
#        print self.UsrDefDict
#        print _a
#        for _tmp in _a:
#            _c = ExpressionParser.transRuleDicToString( _a[_tmp])
#            print "C",_c
#            _c1 = ExpressionParser.transExpStrIntoListStr(_c)
#            print "c1",_c1
#            _c2 = ExpressionParser.transInfixExpToSuffixExp(_c1 )
#            print "c2",_c2
#            _c3 = ExpressionParser.transSuffixExpToRuleDic(_c2)
#            print "c3", ExpressionParser.transRuleDicToString(_c3)
            
        

#        _f = XmlParser()
#        _f.loadXmlFile( path )
#        
#        _consts = _f.getAllElementByName( self.MapConstParser['subLabel'] )
#        
#        for _const in _consts:
#            _id = _f.getAttrListOneNode( _const, self.MapConstParser['attr'] )[0]
#            if _f.getAttrListOneNode( _const, self.MapConstParser['attr'] )[-1] == 'int':
#                self.ConstDict[_id] = [int( _f.getAttrListOneNode( _const, self.MapConstParser['attr'] )[1] ), \
#                                          _f.getAttrListOneNode( _const, self.MapConstParser['attr'] )[-1]]
#            elif _f.getAttrListOneNode( _const, self.MapConstParser['attr'] )[-1] == 'float':
#                self.ConstDict[_id] = [float( _f.getAttrListOneNode( _const, self.MapConstParser['attr'] )[1] ), \
#                                          _f.getAttrListOneNode( _const, self.MapConstParser['attr'] )[-1]]
#            else:
#                self.ConstDict[_id] =  [_f.getAttrListOneNode( _const, self.MapConstParser['attr'] )[1], \
#                                           _f.getAttrListOneNode( _const, self.MapConstParser['attr'] )[-1]]
#        print MapInput.ConstDic         
    
    
    def savUsrDefDat( self, ConstDict, UsrDefDict ):
        XMLDeal.ExportAnalysisVar( r'../autoAnalysis/config/usrData2.xml', ConstDict, UsrDefDict, WriteDes = False )
         
    def getDictKW( self ):
        return self.ConstDict.keys()
        
    def getUsrDefDictKW( self ):
        return self.UsrDefDict.keys()
    
    def getMapConstbyName( self, name ):
#        print self.ConstDict
        if self.ConstDict.has_key( name ):
#            print self.ConstDict[name][0]
            return self.ConstDict[name][0]
        else:
            print( "'%s' do no Exist!" % ( name ) )
            return None
        
    def getMapConstTypebyName( self, name ):
        if self.ConstDict.has_key( name ):
#            print self.ConstDict[name][0]
            return self.ConstDict[name][1]
        else:
            print( "'%s' do no Exist!" % ( name ) )
            return None
        
    def getMapConstDesbyName( self, name ):
        if self.ConstDict.has_key( name ):
            return self.ConstDict[name][-1]
    
    # 由表达式的名字得到字符串形式的表达式    
    def getMapUsrDefbyName( self, name ):
        if self.UsrDefDict.has_key( name ):
            return ExpressionParser.transRuleDicToString( self.UsrDefDict[name][0] )
        
    # 由字符串得到字典形式的表达式
    def getMapUsrDefDictbyStr( self, str ):
        return ExpressionParser.transStringToRuleDic( str )
    
    def getMapUsrDefDesbyName( self, name ):
        if self.UsrDefDict.has_key( name ):
            return self.UsrDefDict[name][-1]
    
    def ifMapConst( self, name ):
#        print self.ConstDict
        return self.getMapConstbyName( name )
    
    def ifMapConstType( self, name ):
        return self.getMapConstTypebyName( name )
    
    def ifMapConstDes( self, name ):
        return self.getMapConstDesbyName( name )
    
    def ifMapUsrDef( self, name ):
        return self.getMapUsrDefbyName( name )
    
    def ifMapUsrDefDes( self, name ):
        return self.getMapUsrDefDesbyName( name )
    
    def ifMapUsrDefDict( self, str ):
        return self.getMapUsrDefDictbyStr( str )
    
    def addOneEle( self , name, value, type, des ):
        if not self.ConstDict.has_key( name ):
            self.ConstDict[name] = [value, type, des]
#            print "add one element"
#        print "addOneEle",MapInput.ConstDict
            return 0
    
    def addOneUsrDef( self, name, ruleDict, des ):
        if not self.UsrDefDict.has_key( name ):
            self.UsrDefDict[name] = [ruleDict, des]
            return 0
    
    def delOneEle( self, name ):
        if self.ConstDict.has_key( name ):
            self.ConstDict.pop( name )
            print "delete one element"
            return 0
    
    def delOneUsrDef( self, name ):
        if self.UsrDefDict.has_key( name ):
            self.UsrDefDict.pop( name )
            return 0
    
    def modOneEle( self, name, value, type, des ):
        if self.ConstDict.has_key( name ):
            self.ConstDict[name] = [value, type, des]
            print "modify one element"
            return 0
        else:
            print "modify error, ID modified"
            return -1
    
    def modOneUsrDef( self, name, ruleDict, des ):
        if self.UsrDefDict.has_key( name ):
            self.UsrDefDict[name] = [ruleDict, des]
            print "modify one user defined element"
            return 0
        else:
            return -1
            
    def getUsrDict( self ):
        return self.UsrDefDict
    
if __name__ == '__main__':
    
    test = UsrDefInput()
    test.loadUsrDefDat( r'config/usrData.xml' )
    test.addOneEle( 'const', 2, 'int', 'abc' )
    test.delOneEle( 'const' )
    test.modOneEle( 'const1', 99, 'int', 'efg' )
    print test.ifMapConst( 'const1' )
    print test.ifMapConst( 'const2' )
    print test.ifMapConst( 'abc' )
    print test.ifMapConstType( 'const1' )
    print test.getDictKW()
    print test.getUsrDefDictKW()
    print test.getMapUsrDefbyName( 'Var1' )
    
#    MapInput.loadMapConst(r'config/map.xml')
    print test.ConstDict


#    simdata.MapData.loadMapData(r'config/atpCpu1Binary.txt', r'config/atpText.txt')
  
#    simdata.TrainRoute.loadTrainData('config/train_route.xml') 
    
    
    
#    OMAPInput.importEnuDic(r'config/Enumerate.xml')
#    OMAPInput.importFormat(r'config/OMAPFormat.xml')
#    OMAPInput.LoadZipOMAPData(r'config')
    
#    test = OMAPInput()
    #test.interfaceOmapCycleNo(None,None,None, None)
    #test.interfaceOmapCycleNo(None, 96, 70000, None)
    
#    test.ifOmapData('VIOM1_AtpLoopHour', 0)
#    test.ifOmapData('TrainEnd1Orientation', 0)
#    test.ifOmapData('DoorOpeningEnabledSideB', 0)
#    test.ifOmapData('TrainEnd2Abscissa', 500)
#    test.ifOmapData('TrainEnd2BlockID', 500)
#    test.ifOmapData('MinCalibration', 500)
#    test.ifOmapData('SignalOverrun', 500)
#    test.ifOmapData('VIOM1_Trace', 500)
#    test.ifOmapData('LockedTestBytes[0]', 500)
