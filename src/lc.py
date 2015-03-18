#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     lc.py
# Description:  lc设备仿真     
# Author:       OUYANG Min
# Version:      0.0.3
# Created:      2011-07-18
# Company:      CASCO
# LastChange:   create 2011-07-18
# History:          
#update 2011-07-19 更新脚本导入例子，和消息处理说明
#update 2011-07-19 更新了坐标转化的例子
#update 2011-09-02 更新脚本读取
#update 2011-09-06 更新SACEM校验模块
#----------------------------------------------------------------------------

from base.loglog import LogLog
from base.basedevice import BaseDevice
from base.senariopreproccess import Senariopreproccess
from base import commlib
from base.xmlparser import XmlParser
import sys
import struct
import binascii
import safetylayerdll
from base import simdata

class LC( BaseDevice ):
    """
    LC Simulator
    """
    #平台内部传递的消息，所带的消息头，loophour,msgId
    qMsgHead = None
    
    #周期更新消息ID
    cycMsgId = None
    #周期更新命令
    cycUpdate = None
    #运行结束命令
    cycEnd = None
    #loophour初始化命令
    cycIniloophour = None    
    #RS位置消息
    rsPosMsgId = None
    #CC version message from ATP
    ccVerMsgId = None

    loophour = 0
    Log = None
    
    #本周起开始和结束时的位置
    sPos = None
    ePos = None
    sacemdll = None
    
    #TSR setting
    tsrItem = None
    
    var_type = {'int':int, 'string':str, 'float':float}
    
    #Device SSTY,LogID,SSID
    lcPara = None
    ccPara = None
    
    tsrSetting = {
            'TSR_PARA':{'path':'.//TSR_PARA',
                    'attr':'Value'
                  }
            }

    tsrVariant = [1, 0, 0, 0] * 3000
    
    def __init__( self, name, id ):
        "init"
        BaseDevice.__init__( self, name, id )
    
    def logMes( self, level, mes ):
        " log mes"
        self.Log.logMes( level, mes )
    
    def deviceInit( self, *args, **kwargs ):
        " LC init"
        self.Log = LogLog()
        self.Log.orderLogger( kwargs['log'], type( self ).__name__ )
        
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        self.importVarint( kwargs['varFile'] )
        self.importMsg( kwargs['msgFile'] )
        self.importDefSce( kwargs['scenario'] )
        
        #self.trainRoute = commlib.loadTrainRout(kwargs['trainrouteFile'])
        self.blockList = simdata.TrainRoute.getBlockinfolist()
        self.trainDirection = simdata.TrainRoute.getRouteDirection()
        #print self.trainRoute, self.blockList, self.trainDirection
        
        self.scePrepro = Senariopreproccess()
        #self.scePrepro.getblockinfolist(kwargs['track_map'], kwargs['track_maptxt'])
#        print self.defScenario
        self.defScenario = self.scePrepro.getsortedscenario( self.defScenario, self.trainDirection )
        #print self.defScenario
        #import TSR
        self.importTSRSetting( kwargs['tsrFile'] )

        self.addDataKeyValue( 'loophour', 1 )
        self.qMsgHead = self.getDataValue( 'qMsgHead' )
        self.cycMsgId = self.getDataValue( 'cycMsgId' )
        self.cycEnd = self.getDataValue( 'cycEndCmd' )
        self.cycUpdate = self.getDataValue( 'cycUpdateCmd' )
        self.rsPosMsgId = self.getDataValue( 'rsPosMsgId' )    
        self.ccVerMsgId = self.getDataValue( 'ccVerMsgId' )    
        
        self.sacemdll = safetylayerdll.GM_SACEM_Dll( 'lc', kwargs["sacemFile"] )
        #SACEM DLL初始化
        if False == self.sacemdll.SACEM_Init_Dll( kwargs["binFile"].encode( "utf-8" ) ):
            self.logMes( 1, "SACEM Initializing is failed!" ) 
            print "SACEM Initializing is failed!" 
        return True

    # --------------------------------------------------------------------------
    ##
    # @Brief 打包应用消息，且加上平台内部消息头
    #
    # @Param loophour
    # @Param msgId
    # @Param args
    #
    # @Returns msg
    # --------------------------------------------------------------------------
    def packAppMsgHasHead( self, loophour, msgId, *args ):
        "packing message and add head"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        _head = struct.pack( self.qMsgHead, loophour, msgId )
        self.logMes( 4, '_head' + binascii.hexlify( _head ) )
        return _head + self.packAppMsg( msgId, *args )
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 解析带平台内部消息头的应用消息
    #
    # @Param msg
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def unpackAppMsgHasHead( self, msg ):
        "unpacking message has head"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        _head = struct.unpack( self.qMsgHead, msg[0:struct.calcsize( self.qMsgHead )] )
        self.logMes( 4, '_head_list ' + repr( _head ) )
        return _head + self.unpackAppMsg( _head[1], msg[struct.calcsize( self.qMsgHead ):] )
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 加载TSR setting文件
    #
    # @Returns True or None
    # --------------------------------------------------------------------------
    def importTSRSetting( self, tsrFile ):
        "import tsrsetting xml file"
        _f = XmlParser()
        _f.loadXmlFile( tsrFile )
        self.tsrItem = {}
        for _item in _f.getAllElementByName( self.tsrSetting['TSR_PARA']['path'] ):
            _tmp = []
            _key = None
            for _e in _item.iter():
                    if _e.tag != 'TSR_PARA':
                        if _e.tag == 'Index':
                            _key = int( _e.get( self.tsrSetting['TSR_PARA']['attr'] ) )
                        elif  _e.tag == 'Intermediate_Block_ID_Of_TSR':
                            _route = _e.get( self.tsrSetting['TSR_PARA']['attr'] )
                            if _route == '':
                                _tmp.append( [] )
                            else:
                                try:
                                    _tmp.append( [int( _s ) for _s in _route.strip().split( ',' )] )
                                except ValueError, e:
                                    print 'tsr list input error', e
                                    return None                    
                        else:
                            _tmp.append( int( _e.get( self.tsrSetting['TSR_PARA']['attr'] ) ) )
            self.tsrItem[_key] = _tmp

        _f.closeXmlFile()
        return True

    # --------------------------------------------------------------------------
    ##
    # @Brief 打包lc to cc data synchronize message 
    #
    # @Returns 消息字符串
    # --------------------------------------------------------------------------
    def packingDataSyncMes( self, LCId = None ):
        "packing data synchronize message" 
        #消息内容
        _tmpCCLoophour = self.getccloophour( self.getDataValue( 'CCloopHour' ), LCId ) + \
                         ( self.getDataValue( 'detaccloophour_DataSync' ) if LCId in self.getModifyLCIDList() else 0 )
        _dataSyn = [self.getDataValue( 'SynchroDate' ), \
                    _tmpCCLoophour] #加deta，初始值为0
        if ( 1 == self.getDataValue( 'CheckSumENABLE_DataSync' ) and \
            LCId in self.getModifyLCIDList() ) or \
            LCId not in self.getModifyLCIDList(): #计算checksum
            self.lcPara = self.getDataValue( 'parDic' )['lc']
            _lc_id = self.lcPara[2] if None == LCId else LCId
            _checksum = self.sacemdll.SACEM_Tx_Msg_Dll( self.getDataValue( 'dataSyncMsgId_SACEM' ),
                                                         self.lcPara[0], _lc_id,
                                                         self.ccPara[0], self.ccPara[2], _dataSyn )
        else:
            _checksum = ( 0, 0, 0, 0, 0, 0 ) 
                   
        _msg = self.packAppMsg( self.getDataValue( 'dataSyncMsgId' ), *( _dataSyn + list( _checksum ) ) )
        return _msg

    
    # --------------------------------------------------------------------------
    ##
    # @Brief 打包CC版本授权消息
    #
    # @Return 消息字符串 
    # --------------------------------------------------------------------------
    def packingVerCCAuth( self, LCId = None ):
        "packing version authorization message"
        _zcVital = [self.getDataValue( 'ZC1_Vital_Authorization' ),
                self.getDataValue( 'ZC2_Vital_Authorization' ),
                self.getDataValue( 'ZC3_Vital_Authorization' ),
                self.getDataValue( 'ZC4_Vital_Authorization' ),
                self.getDataValue( 'ZC5_Vital_Authorization' ),
                self.getDataValue( 'ZC6_Vital_Authorization' ),
                self.getDataValue( 'ZC7_Vital_Authorization' ),
                self.getDataValue( 'ZC8_Vital_Authorization' ),
                self.getDataValue( 'ZC9_Vital_Authorization' ),
                self.getDataValue( 'ZC10_Vital_Authorization' ),
                self.getDataValue( 'ZC11_Vital_Authorization' ),
                self.getDataValue( 'ZC12_Vital_Authorization' ),
                self.getDataValue( 'ZC13_Vital_Authorization' ),
                self.getDataValue( 'ZC14_Vital_Authorization' ),
                self.getDataValue( 'ZC15_Vital_Authorization' ),
                self.getDataValue( 'ZC16_Vital_Authorization' )]
        _zcVitalInt = commlib.transform_BitlistToInt( _zcVital )

        _zcNovital = [self.getDataValue( 'ZC1_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC2_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC3_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC4_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC5_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC6_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC7_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC8_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC9_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC10_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC11_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC12_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC13_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC14_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC15_NO_Vital_Authorization' ),
                self.getDataValue( 'ZC16_NO_Vital_Authorization' )]
        _zcNoVitalInt = commlib.transform_BitlistToInt( _zcNovital )

        #Version for CC report Authorization
        _tmpCCLoophour = self.getccloophour( self.getDataValue( 'CCloopHour' ), LCId ) + \
                         ( self.getDataValue( 'detaccloophour_VerCCAuth' ) if LCId in self.getModifyLCIDList() else 0 )
        
        if ( 1 == self.getDataValue( 'CheckSumENABLE_VerCCAuth' ) and \
            LCId in self.getModifyLCIDList() ) or \
            LCId not in self.getModifyLCIDList():
            self.lcPara = self.getDataValue( 'parDic' )['lc']
            _lc_id = self.lcPara[2] if None == LCId else LCId
            _checksum = self.sacemdll.SACEM_Tx_Msg_Dll( self.getDataValue( 'verAutMsgId_SACEM' ),
                                                        self.lcPara[0], _lc_id,
                                                        self.ccPara[0], self.ccPara[2],
                                                        _zcVital + [_tmpCCLoophour] )
        else:
            _checksum = ( 0, 0, 0, 0, 0, 0 )
        
        _verAuth = self.packAppMsg( self.getDataValue( 'verAutMsgId' ),
                _zcVitalInt, _zcNoVitalInt, _tmpCCLoophour, *_checksum )
        return _verAuth

    
    # --------------------------------------------------------------------------
    ##
    # @Brief 打包TSR消息
    #
    # @Returns 消息字符串
    # --------------------------------------------------------------------------
    def packingTsrMes( self, LCId = None ):
        "packing tsr message"
        if 1 == LCId and "" != self.getDataValue( 'TsrList1' ):
            _t = self.getDataValue( 'TsrList1' )
        elif 2 == LCId and "" != self.getDataValue( 'TsrList2' ):
            _t = self.getDataValue( 'TsrList2' )
        else:
            _t = self.getDataValue( 'TsrList' )
        #注意列表的指针性，以下处理方式会有问题
#        _TSRVariant = LC.tsrVariant #获取初始值
        _TSRVariant = [1, 0, 0, 0] * 3000
            
        _tsrPart1 = ''
        _tsrPart2 = ''
        _tsrPart3 = ''        
        
        if _t != '':
            try:
                _tsrList = [int( _s ) for _s in _t.strip().split( ',' )]
            except ( ValueError, AttributeError ), e:
                print 'tsr list input error', e
                return None

           
            #tsrNum
            _tsrPart1 = self.packAppMsg( 3, len( _tsrList ) )
            #每一包TSR
            for _t in _tsrList:
                if self.tsrItem.has_key( _t ):
                    #speed,First_Block_ID_Of_TSR,Start_Abscissa_On_First_Block_Of_TSR,
                    #Number_Of_Intermediate_Blocks_Of_TSR
                    _tsrPart2 += self.packAppMsg( 4, self.tsrItem[_t][0],
                                                  self.tsrItem[_t][1],
                                                  self.tsrItem[_t][2],
                                                  self.tsrItem[_t][3] )
                    _TSRVariant = self.ModifyTSRVariant( _TSRVariant, \
                                           self.tsrItem[_t][1], \
                                           self.tsrItem[_t][0], \
                                           self.tsrItem[_t][2], \
                                           simdata.TrainRoute.getBlockLength_05( self.tsrItem[_t][1] ) )
                    #Intermediate_Block_ID_Of_TSR
                    if  len( self.tsrItem[_t][4] ):
                        for _b in self.tsrItem[_t][4]:
                            _tsrPart2 += self.packAppMsg( 5, _b )
                            _TSRVariant = self.ModifyTSRVariant( _TSRVariant, \
                                                   _b, \
                                                   self.tsrItem[_t][0], \
                                                   0, \
                                                   simdata.TrainRoute.getBlockLength_05( _b ) )
                    #Last_Block_ID_Of_TSR,End_Abscissa_On_Last_Block_Of_TSR
                    _tsrPart2 += self.packAppMsg( 6, self.tsrItem[_t][5], self.tsrItem[_t][6] )
                    _TSRVariant = self.ModifyTSRVariant( _TSRVariant, \
                                           self.tsrItem[_t][5], \
                                           self.tsrItem[_t][0], \
                                           - 1, \
                                           self.tsrItem[_t][6] )
                else:
                    self.logMes( 4, 'tsr index not in tsrItem' )
        else:
            #tsrNum
            _tsrPart1 = self.packAppMsg( 3, 0 )
        
        #添加loophour
        _tmpCCLoophour = self.getccloophour( self.getDataValue( 'CCloopHour' ), LCId ) + \
                         ( self.getDataValue( 'detaccloophour_Tsr' ) if LCId in self.getModifyLCIDList() else 0 )
        
        _tmpMsg = _TSRVariant + [_tmpCCLoophour]
#        print len( _TSRVariant ), _TSRVariant[0:1200]
        if ( 1 == self.getDataValue( 'CheckSumENABLE_Tsr' ) and\
            LCId in self.getModifyLCIDList() ) or \
            LCId not in self.getModifyLCIDList():
            self.lcPara = self.getDataValue( 'parDic' )['lc']
            _lc_id = self.lcPara[2] if None == LCId else LCId
            _TSRSacemID = self.getDataValue( 'tsrMsgId_SACEM' ) if 1 == _lc_id else 137
            _checksum = self.sacemdll.SACEM_Tx_Msg_Dll( _TSRSacemID,
                                                        self.lcPara[0], _lc_id,
                                                        self.ccPara[0], self.ccPara[2],
                                                        _tmpMsg )
        else:
            _checksum = ( 0, 0, 0, 0, 0, 0 )
                
        #TSRNUM = 0
        _tsrPart3 = self.packAppMsg( 7,
                                     _tmpCCLoophour,
                                     *_checksum )

        return _tsrPart1 + _tsrPart2 + _tsrPart3

    #------------------------------------------------------
    #@修改需要进行发送的tsr
    #------------------------------------------------------
    def ModifyTSRVariant( self, VariantList, blockid, speed, startAbs, endAbs ):
        "Modify TSR Variant."
        VariantList[( blockid - 1 ) * 4 + 0] = 0
        VariantList[( blockid - 1 ) * 4 + 1] = speed
        if -1 != startAbs:
            VariantList[( blockid - 1 ) * 4 + 2] = self.transformSemiMto_mm( startAbs )
    
        if -1 != endAbs:
            VariantList[( blockid - 1 ) * 4 + 3] = self.transformSemiMto_mm( endAbs )
        
#        print 'VariantList:', VariantList[( blockid - 1 ) * 4 + 0:( blockid - 1 ) * 4 + 4], startAbs, endAbs
        return VariantList
    #------------------------------------------------
    #@将单位为0.5m的转换为2-18m
    #------------------------------------------------
    def transformSemiMto_mm( self , m ):    
        "将单位由m转换为minimeters"
        return int( m * 500 )
        
    def deviceRun( self, *args, **kwargs ):
        "LC run"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        #获得设备参数 SSTY,SSID
        self.lcPara = self.getDataValue( 'parDic' )['lc']
        self.ccPara = self.getDataValue( 'parDic' )['ccnv']
        _LC_Cycle = 200 #LC的周期为20s
        _Base_Time_Index = 0 #基础计数器
        _SendMsg = False
        
        _SendLCList = [] #用于存储需要发送的LC的消息ID
        _sendDelay = 0
        while( 1 ):
            #获得消息，无消息是阻塞
            _msg = self.unpackAppMsgHasHead( self.inQ.get() )

            #TODO:
            #处理消息
            
            #界面消息，给对应的var赋值
            #self.addDataKeyValue(key,value)
            
            #车辆的位置消息，处理脚本
            if _msg[1] == self.rsPosMsgId:
                self.logMes( 4, "Recv RS pos mes, MsgId = " + str( _msg[1] ) + \
                            " loophour = " + str( _msg[0] ) + \
                            " startPos = " + str( _msg[3] ) + \
                            " endPos = " + str( _msg[4] ) )
                self.sPos = _msg[3]
                self.ePos = _msg[4]
            
            #CC版本消息
            if _msg[1] == self.ccVerMsgId:
                if  ( True == _SendMsg and 1 < _Base_Time_Index ) or 1 == self.getDataValue( "SendLCMsgRepeatlyFlag" ) :
                    self.logMes( 4, "Recv cc version message" + repr( _msg ) )
                    _SendMsg = False
                    #ccloophour加上周期延迟
                    self.addDataKeyValue( 'CCloopHour_CC', _msg[25] )
                    self.addDataKeyValue( 'CCloopHour', _msg[25] )
                    #print 'lc ccloophour', self.getDataValue('CCloopHour_CC')

                    #消息校验
                    _ccVerRep = _msg[2:20] + _msg[25:32]
                    self.lcPara = self.getDataValue( 'parDic' )['lc']
                    _retcdw = self.sacemdll.SACEM_Rx_Msg_Dll( self.getDataValue( 'ccVerMsgId_SACEM' ),
                                                              self.ccPara[0], self.ccPara[2],
                                                              self.lcPara[0], self.lcPara[2], _ccVerRep )
                    if None == _retcdw:
                        print "cc to lc ccVerRep sacem check failed!"
                        self.logMes( 1, "cc to lc ccVerRep sacem check failed!" )
    
                    _SendLCList += [int( _lcid ) for _lcid in self.getDataValue( "SendLClist" ).split( ',' )] 
                                    
            #周期更新消息
            if _msg[1] == self.cycMsgId:
                if _msg[2] == self.cycUpdate:
                    #根据消息列表发送消息
                    _sendDelay = max( 0, _sendDelay - 1 )
                    if len( _SendLCList ) > 0 and _sendDelay == 0:
                        _tmpLCID = _SendLCList[0]
                        _SendLCList = _SendLCList[1:]
                        _Head = self.packAppMsg( self.getDataValue( 'Lc2AtpMesID' ), \
                                                self.loophour,
                                                self.getDataValue( 'Lc2AtpMesID' ) )
                        _msg1 = self.packingDataSyncMes( LCId = _tmpLCID )              
                        _msg2 = self.packingVerCCAuth( LCId = _tmpLCID )
                        if 1 == self.getDataValue( "SendTSRMesENABLE" ):
                            _msg3 = self.packingTsrMes( LCId = _tmpLCID )
                        else:
                            _msg3 = ''
                        if ( None not in [_msg1 , _msg2 , _msg3] ) and \
                           1 == self.getDataValue( 'SendMesENABLE' ):
                            _idMsg = struct.pack( "!B", _tmpLCID )
                            self.getDataValue( 'siminQ' ).put( _Head + _idMsg + _msg1 + _msg2 + _msg3 )
                        _sendDelay = self.getDataValue( 'LCSendMessageDelay' )
                    
                    _Base_Time_Index += 1
                    #改值按照100ms进行                    
                    #检测是否有改值    
                    setValues = self.scePrepro.getNormalChangeItem( [self.sPos, self.ePos],
                                                                    self.defScenario )
                    for setValue in setValues:
                        if setValue[0] == 'TsrList':
                            self.addDataKeyValue( setValue[0], setValue[1] )
                        else:
                            _typename = self.getVarDic()[setValue[0]][0]
                            self.addDataKeyValue( setValue[0], self.var_type[_typename]( setValue[1] ) )                                         

                    setValues = self.scePrepro.getTimeChangeItem( _Base_Time_Index, self.TimeScenario )
                    #print setValues
                    for setValue in setValues:
                        _typename = self.getVarDic()[setValue[0]][0]
                        self.addDataKeyValue( setValue[0], self.var_type[_typename]( setValue[1] ) )  

                    
                    #其余的则是在设备周期下进行
                    if _Base_Time_Index % _LC_Cycle != 1:
                        continue
                    _SendMsg = True
                    
                    self.loophour += 1
                    self.addDataKeyValue( 'loophour', self.loophour )
                    self.addDataKeyValue( 'SynchroDate', int( _Base_Time_Index / 3.36 ) ) #周期为336,ms
                                    
                elif _msg[2] == self.cycEnd:
                    break
        print "lc Running End"

    #-------------------------------------------------------------------
    #@获取发送的ccloophour，该值将根据ResponseEND进行判断处理
    #-------------------------------------------------------------------
    def getccloophour( self, ccloophour, LCID = None ):
        "get cc loophour by response end"
#        if 1 == self.getDataValue( 'ResponseEND' ):
#            return ccloophour
#        elif 2 == self.getDataValue( 'ResponseEND' ):  #响应远端
#            return ccloophour - 1073741824 / 2  if ccloophour >= 1073741824 / 2 else ccloophour + 1073741824 / 2
#        else:
#            self.logMes( 1, 'Error Value : ResponseEND!!!' )
#            return None
        _responseEnd = self.getDataValue( 'ResponseEND' ) if LCID not in self.getModifyLCIDList() else self.getDataValue( "ModifyResponseEND" )
        return commlib.getResponseCCLoophour( _responseEnd, ccloophour )

    
    def getModifyLCIDList( self ):
        "get modify LC ID List"
        try:
            return [int( _i ) for _i in self.getDataValue( "ModifyLCList" ).split( "," )]
        except:
            return []

    def deviceEnd( self ):
        " ending device"
        self.Log.fileclose()         
    
if __name__ == '__main__':
    lc = LC( 'lc', 1 )
    lc.deviceInit( varFile = r'./setting/lc_variant.xml', \
                   msgFile = r'./setting/lc_message.xml', \
                   scenario = r'./scenario/lc_scenario.xml', \
                   log = r'./log/lc.log', \
                   tsrFile = r'./scenario/lc_tsr_setting.xml' )
    print 'over device init'
    print 'data dic', lc.getDataDic()
    print 'var dic', lc.getVarDic()
    print 'msg dic', lc.getMsgDic()
    print 'def scenario', lc.defScenario
    print 'tsr setting', lc.tsrItem

    #_appMsg = lc.packAppMsgHasHead(123, 1, 0xff, 0xee)
    #print 'pack message', len(_appMsg), binascii.hexlify(_appMsg)
    #print 'unpack message', lc.unpackAppMsgHasHead(_appMsg)
    
    #blocklist = [4, 5, 6, 7, 8]
    #d = Senariopreproccess(r'./scenario/train_route.xml')
    #d.getblockinfolist(blocklist, './datafile/atpCpu1Binary.txt')
    #print 'block list', d.blockinfolist
    #方向 1-up -1-down
    #print 'absolute distance', d.getabsolutedistance(5, 20, -1)
    #读取列车路径
    #print 'train route ', commlib.loadTrainRout('./scenario/train_route.xml')
