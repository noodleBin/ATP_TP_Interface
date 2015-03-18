#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     beacon.py
# Description:  beacon设备仿真      
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      date
# Company:      CASCO
# LastChange:   Created 2011-04-12
# History:      add
#----------------------------------------------------------------------------
from base.basedevice import BaseDevice
from base.loglog import LogLog
from base.check_words import  Check_Words_Genegator
from lxml import etree
import struct
import base.commlib
import sys

class Beacon( BaseDevice ):
    """
    beacon device class
    """
    
    nodePath = {
                'Beacon': '/BM_Beacon/Beacon',
                'Beacon_Msg': '/Beacon_Msg_Setting/Beacon_Msg',
                }
    attributes = {                
                'Beacon': ( '@ID', '@direction', '@VARnumber' ),
                'Variant': ( '@Index', '@Value' ),
                'Beacon_Msg': ( '@Beacon_ID', '@Beacon_Name', '@Disabled', '@Msg_Beacon_ID', '@Use_Default_Msg', '@Available', '@Check_Word_1', '@Check_Word_2' , '@deta_dis' )
                }
    
    myBMBeacons = {}
    myBeaconMsgs = {}
    myParasTable = {}
    myParaTypeTable = {}
    cw_generator = Check_Words_Genegator()
    
    beaconFormat = '!3H2B3IB2I'
    setting_msg = ''
    
    def __init__( self, name, id ):
        BaseDevice.__init__( self, name, id )

    @classmethod
    def BeaconDicinit( self ):
        "beacon Dic init."
        self.myBMBeacons = {}
        self.myBeaconMsgs = {}
        self.myParasTable = {}
        self.myParaTypeTable = {}
        
    def logMes( self, level, mes ):
        " log mes"
        LogLog.orderLogger( self.getDeviceName() )
        LogLog.logMes( level, mes )
    
    def getBeaMes( self ):
        " get beacon message"
        return self.getDataValue( 'msg' ) 
    
    def getBeaPostion( self ):
        return self.getDataValue( 'kp_i' ) 
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 获得信标的方向
    #
    # @Returns 0-up,1-down,2-all
    # --------------------------------------------------------------------------
    def getBeaconDire( self ):
        return self.getDataValue( 'dire' )

    # --------------------------------------------------------------------------
    ##
    # @Brief 判断信标的方向是否与列车运行方向一致
    #
    # @Param curDir 车辆运行方向 direction 1-up 0-down
    # @Returns True or False
    # --------------------------------------------------------------------------
    def ifDireMath( self, curDir ):
        " if dire match"
        _dir = self.getBeaconDire()
        if _dir != curDir:
            return True
        else:
            return False
    
    #@classmethod
    def generate_Beacon_Codes( self, beacon_id ):
        #self.my_Log('FuncInfo', type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        _str_beacon_id = str( beacon_id )
        
        #print self.myBMBeacons.has_key(_str_beacon_id)
        if self.myBMBeacons.has_key( _str_beacon_id ) == False:
            return 0
        _codes = self.myBMBeacons[_str_beacon_id]
#        print '_codes[2]', _codes[2] 
        re_codes = 0
        for _code in _codes[2]:
            _temp = int( _code[1] )
            if _temp == -1:
                re_codes = re_codes * 2 + int( 0 )
            else:
                re_codes = re_codes * 2 + int( _temp )
        return re_codes
    
    #@classmethod
    def generate_CWs( self, beacon_id , Real_beacon_id ):
        #self.my_Log('FuncInfo', type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        _str_beacon_id = str( Real_beacon_id )  #用原始beaconid去判断信标是否为BM信标
        if self.myBeaconMsgs.has_key( _str_beacon_id ) == False or\
            ( self.myBeaconMsgs[_str_beacon_id][5] == "" and 
             self.myBeaconMsgs[_str_beacon_id][6] == "" ):
            #需要计算checksum
            if self.myBMBeacons.has_key( _str_beacon_id ) == False:
                _list = [beacon_id, 0, 0, 0, 0, \
                                    0, 0, 0, 0, \
                                    0, 0, 0, 0, \
                                    0, 0, 0, 0, self.myParasTable['def_msg_flag']]
                _temp1, _temp2 = self.cw_generator.generate_check_words( _list )
                self.myParasTable['check_word_1'] = _temp1
                self.myParasTable['check_word_2'] = _temp2
            else:            
                _codes = self.myBMBeacons[_str_beacon_id][2]
                
        #        print "codes", _codes
                _list = []
                _list.append( beacon_id )
                for _code in _codes:
                    _temp = int( _code[1] )
                    if _temp == -1:
                        _list.append( 0 )
                    else:
                        _list.append( _temp )
                        
                _list.append( self.myParasTable['def_msg_flag'] )
                
                #print "list", _list, self.myParasTable['def_msg_flag']
                _temp1, _temp2 = self.cw_generator.generate_check_words( _list )
                
                self.myParasTable['check_word_1'] = _temp1
                self.myParasTable['check_word_2'] = _temp2
        else:#通过配置改值
            self.myParasTable['check_word_1'] = int( self.myBeaconMsgs[_str_beacon_id][5] )
            self.myParasTable['check_word_2'] = int( self.myBeaconMsgs[_str_beacon_id][6] )            
            
    #@classmethod
    def generate_Beacon_Msg( self, beacon_id ):
        self.myParasTable['Beacon_ID'] = beacon_id
        self.myParasTable['Beacon_codes'] = self.generate_Beacon_Codes( beacon_id )
#        print "myBeaconMsgs", self.myBeaconMsgs
        
        _strbeaid = str( beacon_id )
        self.addDataKeyValue( 'Disable', 0 ) #设置初始值
        self.addDataKeyValue( 'deta_beacon_distance', 0 ) #初始值为0
        #根据beaconMsg设置故障的beacon消息
        if self.myBeaconMsgs.has_key( _strbeaid ):
            self.myParasTable['def_msg_flag'] = int( self.myBeaconMsgs[_strbeaid][3] )
            self.myParasTable['available'] = int( self.myBeaconMsgs[_strbeaid][4] )
            
            try:#查看是否需要改beacon id
                self.myParasTable['Beacon_ID'] = int( self.myBeaconMsgs[_strbeaid][2] )
            except ValueError, e:
                print type( self ).__name__ + '.' + sys._getframe().f_code.co_name , e
            
            #查看是否需要发送改消息包
            self.addDataKeyValue( 'Disable', int( self.myBeaconMsgs[_strbeaid][1] ) ) #设置Disable，为1的是否该信标不发送             
            
            try:
                self.addDataKeyValue( 'deta_beacon_distance', int( self.myBeaconMsgs[_strbeaid][7] ) )
            except ValueError, e:
                self.addDataKeyValue( 'deta_beacon_distance', 0 )
                
        else:
            self.myParasTable['def_msg_flag'] = 0
            if self.getDataValue( 'type' ) == 4:
                self.myParasTable['available'] = 1
            else:
                self.myParasTable['available'] = 0
            
        
        self.generate_CWs( self.myParasTable['Beacon_ID'], beacon_id )
        
        _Msg_Data = struct.pack( self.beaconFormat, self.myParasTable['Beacon_ID'], \
                                self.myParasTable['Beacon_codes'], 0, \
                                self.myParasTable['def_msg_flag'], \
                                self.myParasTable['available'], 0, 0, 0, 0, \
                                self.myParasTable['check_word_1'], self.myParasTable['check_word_2']
                                )
        #print "beaconmsg",binascii.hexlify(_Msg_Data)
        return _Msg_Data
    
    
    
    @classmethod
    def loadBMBeacons( self, filePath ):
        #print '>>> load_BM_Beacon'
        tree = etree.parse( filePath )
        r = tree.xpath( self.nodePath['Beacon'] )
        for node in r:   
            _key = ''
            _sub_key = ''
            _list = []
            for p in self.attributes['Beacon']:  
                _para = node.xpath( p )                   
                if p[1:] == 'ID':
                    _key = str( _para[0] )
                else:
                    _list.append( str( _para[0] ) )
            _sec_list = []
            for subnode in node.xpath( 'Variant' ):
                _sublist = []
                for subp in self.attributes['Variant']:
                    _para = subnode.xpath( subp )    
                    _sublist.append( str( _para[0] ) )
                _sec_list.append( _sublist )
            _list.append( _sec_list )
            self.myBMBeacons[_key] = _list   
#        print 'myBMBeacons', self.myBMBeacons
    
    @classmethod
    def loadBeaconMsgSetting( self, filePath ):
        #print '>>> load_Beacon_Msg_Setting'
        self.myBeaconMsgs = {}   #清空数据
        
        tree = etree.parse( filePath )
        r = tree.xpath( self.nodePath['Beacon_Msg'] )
        for node in r:   
            _key = ''
            _sub_key = ''
            _list = []
            for p in self.attributes['Beacon_Msg']:  
                _para = node.xpath( p )    
                if _para != []:
                    if p[1:] == 'Beacon_ID':
                        _key = str( _para[0] )
                    else:
                        _list.append( str( _para[0] ) )   
                else:
                    _list.append( '' )
            self.myBeaconMsgs[_key] = _list   
            
#        print self.myBeaconMsgs
    
    def createBeaconMsg( self ):
        #self.my_Log('FuncInfo', type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        
        #print "beaconID",self.getDeviceId(),self.getDataDic()['type']
        
        _beacon_id = self.getDeviceId()
        #print "beacon ID", _beacon_id
        _temp_msg = self.generate_Beacon_Msg( _beacon_id )
        #print "================================"
        
        #print "beaconmsg", binascii.hexlify(_temp_msg)
        self.addDataKeyValue( 'msg', _temp_msg )     

if __name__ == '__main__':
    pass
    bea = Beacon( 'beacon', 2000 )
    bea.addDataKeyValue( 'type', 4 )
    Beacon.loadBeaconMsgSetting( r'./scenario/beacon_msg_setting.xml' )
    Beacon.loadBMBeacons( r'./scenario/bm_beacons.xml' )
    bea.createBeaconMsg()
    print base.commlib.str2hexlify( bea.getDataValue( 'msg' ) )
