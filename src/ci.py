#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     lc.py
# Description:  lc设备仿真     
# Author:       OUYANG Min
# Version:      0.0.2
# Created:      2011-07-18
# Company:      CASCO
# LastChange:   create 2011-07-18
# History:          
#update 2011-07-19 更新脚本导入例子，和消息处理说明
#update 2011-07-19 更新了坐标转化的例子
#----------------------------------------------------------------------------
from base.loglog import LogLog
from base.basedevice import BaseDevice
from base.senariopreproccess import Senariopreproccess
from base import commlib
import sys
import struct
import binascii
from safetylayerdll import GM_FSFB2_DLL
from base import simdata
from base.xmlparser import XmlParser
import safetylayerdll
from base.xmldeal import XMLDeal
from crc import CRC

class CI( BaseDevice ):
    """
    CI Simulator
    """
    #平台内部传递的消息，所带的消息头，loophour,msgId
    msgHead = '!IH'
    
    #周期更新消息ID
    cycleMsgId = 99
    
    #loophour初始化命令
    cycleIniloophour = 94

    var_type = {'int':int, 'string':str, 'float':float}
    
    #RS发过来的消息
    __RsPosMesID = 258
    
    #ccnv给ci的消息id
    __ccnvtoCIMesID = 2310
    
    #CI与CC Sacem消息的相关ID
    __CC2CIVariantContainerMsgID = 2313
    __CC2CIVariantRequestMsgID = 4
    __CC2CIVariantReportMsgID = 103
#    __CC2CIVariantRequestMsgID = 2314
    __CI2CCVariantReportMsgID = 15363
#    __CI2CCVariantRequestMsgID = 15364
    
    #计算checkSum时需要的ID,用来寻找配置文件时使用
    __CC2CIVariantReportSacemID = 103
    __CC2CIVariantRequestSacemID = 4
    __CI2CCVariantReportSacemID = 104
    __CI2CCVariantRequestSacemID = 3
        
    #记录log日志的句柄
    _Log = None
    
    #FSFB2DLL实例
    __FSFB2_DLL = None 
    
    #脚本处理实例
    PreSena = None
    
    #loophour
    loophour = 0
    
    CIOutQ = {}
    CISendMessage = True  #控制CI500ms发一次数据
    
    #控制ci通信的相关变量
    __psdID = {0:0, 1:0} #分别存储
    __FSFB2Msg = {0:"", 1:""}
    __citoatpmsg = {0:"", 1:""}
    __getATPTOCIMsgFlag = {0:False, 1:False}
    
    #屏蔽门和nodeid的对应关系，nodeid：psdid
    __NodeIDDic = {8:1, 9:2, 10:3, 13:4, 14:5,
                   20:6, 21:7, 22:8, 29:9, 30:10,
                   36:11, 37:12, 38:13, 44:14, 15:15,
                   16:16, 23:17, 24:18, 25:19, 31:20,
                   32:21, 39:22, 40:23, 41:24, 45:25 }
    
    
    #Variant scenario存放列表
    #[[block, abs, delay_cycle,[[CBI_ID,Index,value],...]]...]
    V_Scenario = []
    V_SceParser = {'pos':{'path':'.//Position',
                          'attr':['Block_id', 'Abscissa', 'Delay']},
                   'set':{'path':'.//Set',
                          'attr':['CBI_ID', 'Index', 'Value']}
                   }
    
    #变量初始化列表
    VatiantIniDic = None  #{CBI_ID:[VariantNum,ValueIniList],...}
    Ini_Parser = {"path":r'.//CBI',
                  "attr":["ID", "VariantNum", "Value" ]}

    #Sacem Dll 句柄
    Sacemdll = None
    
    #设置CRCM错误时使用
    CRCMError = None
    def __init__( self, name, id ):
        "init"
        BaseDevice.__init__( self, name, id )
    
    def logMes( self, level, mes ):
        " log mes"
        self._Log.logMes( level, mes )
    
    def deviceInit( self, *args, **kwargs ):
        " CI init"
        self._Log = LogLog()
        self._Log.orderLogger( kwargs['log'] , type( self ).__name__ )
        #TODO 导入变量、应用消息、设备数据解析、控制脚本解析、离线数据计算等
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        self.importVarint( kwargs['varFile'] )
        self.importMsg( kwargs['msgFile'] )
        self.importDefSce( kwargs['scenario'] )
        self.importVarSce( kwargs['variant_scenario'] )
        self.importVarIni( kwargs['variniFile'] )
        
        #blocklist = self.trainInfo[0]
        self.PreSena = Senariopreproccess()
        #self.PreSena.getblockinfolist(kwargs['track_map'], kwargs['track_maptxt'])
        
        self.defScenario = self.PreSena.getsortedscenario( self.defScenario, \
                                                          simdata.TrainRoute.getRouteDirection() )

        #for variant
        self.V_Presenario = Senariopreproccess()
        #self.V_Presenario.getblockinfolist(kwargs['track_map'], kwargs['track_maptxt'])
        self.V_Scenario = self.V_Presenario.getsortedscenario( self.V_Scenario, \
                                                              simdata.TrainRoute.getRouteDirection() )

        #SacemDLL初始化
        self.Sacemdll = safetylayerdll.GM_SACEM_Dll( 'ci', kwargs["sacemFile"] )
        #SACEM DLL初始化
        if False == self.Sacemdll.SACEM_Init_Dll():
            self.logMes( 1, "SACEM Initializing failed!" ) 

        #加载dll,DLL只加载一次
        if None == CI.__FSFB2_DLL:
            CI.__FSFB2_DLL = GM_FSFB2_DLL( "ci", CI.fsfb2CallBackFun, kwargs['fsfb2'] )
        CI.__FSFB2_DLL.fsfb2Init()
        
        return True
    
    
    
    # --------------------------------------------------------------------------
    ##
    # @Brief FSFB2回调函数 -用于发送FSFB2消息时将生成的FSFB2消息给信号层打包
    #
    # @Param upperLevelLogicAddr int16 
    # @Param msgID uint8
    # @Param pData uint8 *
    # @Param pData uint16
    #
    # @Returns if false return None
    # --------------------------------------------------------------------------      
    @staticmethod
    def fsfb2CallBackFun( upperLevelLogicAddr, msgID, pData, dataSize ):
        "call back function for GM_FSFB2_Init"
                
#        print 'fsfb2CallBackFun', upperLevelLogicAddr, msgID, pData, dataSize
        
        #将数据pData打包
        _packdata = ''
        for i in range( dataSize ):
            _packdata += struct.pack( "B", pData[i] )
            
#        print 'snd fsfb2', commlib.str2hexlify( _packdata ), len( _packdata )
        if 1 == CI.CRCMError and 128 == struct.unpack( "!B", _packdata[1] )[0]:
            _ErrorCRCM = struct.pack( "!2I", 0, 0 )
            _packdata = _packdata[0:12] + _ErrorCRCM + _packdata[-4:]
            #要重新计算CRC
            _crc = CRC.CRC_Calculate_10811_LSB_CRC16( _packdata[0:-2], len( _packdata[0:-2] ) )
            _packdata = _packdata[0:-2] + struct.pack( "!H", _crc )
                
        #获取side的边
        _psdid = CI.__NodeIDDic[upperLevelLogicAddr]
        _side = simdata.MapData.getPSDSide( _psdid )
        _msgid = 15361 if 0 == _side else 15362
        #打包消息    
        _Mes = struct.pack( "!IH", 0, _msgid ) + _packdata
        
        
        #将数据给模拟器发送
        CI.CIOutQ["ci"].put( _Mes )
        CI.CISendMessage = False
        
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
        _head = struct.pack( self.msgHead, loophour, msgId )
        
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
        _head = struct.unpack( self.msgHead, msg[0:struct.calcsize( self.msgHead )] )
        if( self.__ccnvtoCIMesID == _head[1] ):
            #ccnv给ci的开关门控制消息,去除平台头的第一个字节为psdID
#            self.__getATPTOCIMsgFlag = True
            #存储msg值变量中
            _psdid = struct.unpack( "!B", msg[6] )[0] #去掉平台头的六字节
            #计算是左侧还是右侧门
            
            _side = simdata.MapData.getPSDSide( _psdid )
            
#            print "_psdid:", _psdid, "_side:", _side
            #存储数据
            self.__getATPTOCIMsgFlag[_side] = True
            self.__FSFB2Msg[_side] = msg
            self.__psdID[_side] = _psdid #struct.unpack( "!B", msg[6] )[0] #去掉平台头的六字节
            CI.__FSFB2_DLL.validFsfb2Msg( _psdid,
                                            msg[struct.calcsize( self.msgHead ) + 1:],
                                            len( msg ) - struct.calcsize( self.msgHead ) - 1 )
            return None
        
        elif self.__CC2CIVariantContainerMsgID == _head[1]:
            _cbiid = struct.unpack( "!B", msg[6] )[0] #去掉平台头的六字节 
            return _head + ( _cbiid, ) + ( msg[7:], )
        
        return _head + self.unpackAppMsg( _head[1], msg[struct.calcsize( self.msgHead ):] )
    
    #------------------------------------------------------------------------------
    #@读入ci_variant_ini.xml中的信息
    #格式如下：{CBI_ID:[VariantNum,ValueIniList],...}
    #注意Len(ValueIniList)=512
    #------------------------------------------------------------------------------           
    def importVarIni( self, path ):
        "import Variant initialization"
        self.VatiantIniDic = XMLDeal.importCIVariantIni( path )
            
    #------------------------------------------------------------------------------
    #@读入ci_variant_scenario.xml中的有关脚本信息，并存如变量V_secnario中
    #格式如下：[[BlockID,Absicssa,delay,[[CBI_ID,Index,value],...]],...]
    #------------------------------------------------------------------------------           
    def importVarSce( self, VarsceFile ):
        "import Variant format scenario"
#        print "VarsceFile", VarsceFile
        self.V_Scenario = XMLDeal.importCIVarSce( VarsceFile )
        
    #---------------------------------------------------------------
    #解析由CC发送过来的container消息，并校验相关的校核字
    #msg为应用消息
    #返回True时表示具有request消息
    #---------------------------------------------------------------
    def unpackCCContainerMsg( self, msg, CBI_ID ):
        "unpack container message"
        _MsgId = struct.unpack( '!B', msg[0] )[0]
        
        if _MsgId == self.__CC2CIVariantRequestMsgID:
            _tmpMsg = self.unpackAppMsg( self.__CC2CIVariantRequestMsgID, msg[0:11] )
            self.logMes(1, "cbi variant request:"+str(CBI_ID)+repr(_tmpMsg))
#            print "unpackCCContainerMsg1", CBI_ID, _tmpMsg
            self.unpackVariantRequest( _tmpMsg, CBI_ID )
            
            _leftMsg = msg[11:]
            
            if len( _leftMsg ) > 0:
                _Len = self.unpackVariantReport( _leftMsg, CBI_ID )
            return True
        
        elif _MsgId == self.__CC2CIVariantReportMsgID:
            _Len = self.unpackVariantReport( msg, CBI_ID )
            
            _leftMsg = msg[_Len:]
            
            if len( _leftMsg ) > 0:
                _tmpMsg = self.unpackAppMsg( self.__CC2CIVariantRequestMsgID, _leftMsg[0:11] )
#                print "unpackCCContainerMsg2", CBI_ID, _tmpMsg
                self.unpackVariantRequest( _tmpMsg, CBI_ID )
                return True
        return False
        
    #---------------------------------------------
    #MsgList全部是应用消息组成的string
    #---------------------------------------------
    def unpackVariantReport( self, msg, CBI_ID ):
        "unpack CC to CI variant report"
        _variantsMsgId, _variantsMsgLen = struct.unpack( '!2B', msg[:2] )
        _variants = 128 * [0]
        if self.__CC2CIVariantReportMsgID == _variantsMsgId:
            _format = '!2BH' + str( _variantsMsgLen - 14 ) + 'B' + 'I6B'
            _Len = struct.calcsize( _format )
            _variantsMsg = list( struct.unpack( _format, msg[0:_Len] ) )
            _numOfVariant = _variantsMsg[2]
            _variantsBytes = _variantsMsg[3:-7]
            for _c in range( _variantsMsgLen - 14 ):
                _variants[_c * 8 + 7] = _variantsBytes[_c] % 2
                _variants[_c * 8 + 6] = ( _variantsBytes[_c] >> 1 ) % 2
                _variants[_c * 8 + 5] = ( _variantsBytes[_c] >> 2 ) % 2
                _variants[_c * 8 + 4] = ( _variantsBytes[_c] >> 3 ) % 2
                _variants[_c * 8 + 3] = ( _variantsBytes[_c] >> 4 ) % 2
                _variants[_c * 8 + 2] = ( _variantsBytes[_c] >> 5 ) % 2
                _variants[_c * 8 + 1] = ( _variantsBytes[_c] >> 6 ) % 2
                _variants[_c * 8 + 0] = ( _variantsBytes[_c] >> 7 ) % 2     
    #        print _variants
            _CI_loophour = _variantsMsg[-7]
            
            _tmpMsg = _variantsMsg[0:3] + _variants + _variantsMsg[-7:]

            #校验checksum的正确性
            self.CI_ID_TYPE = self.getDataValue( 'parDic' )['ci']
            retcdw = self.Sacemdll.SACEM_Rx_Msg_Dll( self.__CC2CIVariantReportSacemID, \
                                                     self.CCNV_ID_TYPE[0], \
                                                     self.CCNV_ID_TYPE[2], \
                                                     self.CI_ID_TYPE[0], \
                                                     CBI_ID, \
                                                     #self.CI_ID_TYPE[2], \
                                                     _tmpMsg[2:] )                         
            if None == retcdw:
                print "unpackVariantReport fail"
                self.logMes( 1, "Unpacking Variant is failed!" + repr( _tmpMsg[2:] ) + repr( self.CI_ID_TYPE ) )         
            
            return _Len
        else:
            print 'unpackVariantReport variant msg id is error'
            return None
    
    #---------------------------------------------
    #MsgList全部是应用消息组成的List
    #---------------------------------------------
    def unpackVariantRequest( self, MsgList, CBI_ID ):
        "unpack CC to CI variant request"
        _tempMes = MsgList[1:]
        
        self.addDataKeyValue( "CCLoopHourForCCReq", _tempMes[0] )
        
        self.CI_ID_TYPE = self.getDataValue( 'parDic' )['ci']
        _retcdw = self.Sacemdll.SACEM_Rx_Msg_Dll( self.__CC2CIVariantRequestSacemID, \
                                                 self.CCNV_ID_TYPE[0], \
                                                 self.CCNV_ID_TYPE[2], \
                                                 self.CI_ID_TYPE[0], \
                                                 #self.CI_ID_TYPE[2], \
                                                 CBI_ID, \
                                                 _tempMes )                         
        if None == _retcdw:
            print "unpackVariantRequest fail!"
            self.logMes( 1, "Unpacking is failed!" ) 
            
    def packVariantRequest( self, CBI_ID ):
        "pack CI to CC variant request"
        _MsgId = 3
        _CILoopHour = self.getDataValue( "loophour" ) + self.getDataValue( "detaCILoopHour" ) \
                        if CBI_ID in self.getModifyCBIIDList() else self.getDataValue( "loophour" )
        
        if ( 1 == self.getDataValue( 'CheckSumENABLE_Req' ) and \
            CBI_ID in self.getModifyCBIIDList() ) or \
            CBI_ID not in self.getModifyCBIIDList():
            self.CI_ID_TYPE = self.getDataValue( 'parDic' )['ci']
            _checkSum = self.Sacemdll.SACEM_Tx_Msg_Dll( self.__CI2CCVariantRequestSacemID, \
                                                        self.CI_ID_TYPE[0], \
                                                        CBI_ID, \
                                                        self.CCNV_ID_TYPE[0], \
                                                        self.CCNV_ID_TYPE[2], \
                                                        [_CILoopHour] )
        else:
            _checkSum = ( 0, 0, 0, 0, 0, 0 )
        
        _Mes = [_MsgId, _CILoopHour] + list( _checkSum )
        
        _tmpMsg = self.packAppMsgHasHead( _CILoopHour,
                                          self.__CI2CCVariantReportMsgID,
                                          *_Mes )
        
        return _tmpMsg
    
    #------------------------------------------------------------------------------
    #@根据当前CC请求数据的CBI_ID组包Variant消息
    #------------------------------------------------------------------------------
    def packVariantreport( self, CBI_ID ):
        "pack CI to CC Variant report"
        _Variant = self.VatiantIniDic[CBI_ID][1]
        _Len = self.VatiantIniDic[CBI_ID][0]
        _Num = self.VatiantIniDic[CBI_ID][0]
        _Mes = ""  #存储variant report 包
            
        _MesID = 104
        _MesLen = _Len / 8 if _Len % 8 == 0 else _Len / 8 + 1
        _VarNum = _Num
        _tmpVar = _Variant
        _byte_Var = []   #存储压缩的variant
        #将变量值压成bit
        for _i in range( _MesLen ):
            _tmpbyte = _tmpVar[_i * 8] * 128 + \
                        _tmpVar[_i * 8 + 1] * 64 + \
                        _tmpVar[_i * 8 + 2] * 32 + \
                        _tmpVar[_i * 8 + 3] * 16 + \
                        _tmpVar[_i * 8 + 4] * 8 + \
                        _tmpVar[_i * 8 + 5] * 4 + \
                        _tmpVar[_i * 8 + 6] * 2 + \
                        _tmpVar[_i * 8 + 7]
            _byte_Var.append( _tmpbyte )
        _format = '!BBH' + str( _MesLen ) + 'B' + 'I6B'
#        print '------------Variant:--------', _byte_Var
        #计算两个checkSum
        _CCLoopHour = self.getccloophour( self.getDataValue( "CCLoopHourForCCReq" ) + self.getDataValue( "detaCCLoopHourForCCReq" ) \
                                          if CBI_ID in self.getModifyCBIIDList() else self.getDataValue( "CCLoopHourForCCReq" ),
                                          CBI_ID )
        _tmpVariants = [_Len] + _tmpVar + [_CCLoopHour] 
        if( 1 == self.getDataValue( 'CheckSumENABLE_Var' )and \
            CBI_ID in self.getModifyCBIIDList() ) or \
            CBI_ID not in self.getModifyCBIIDList():
            self.CI_ID_TYPE = self.getDataValue( 'parDic' )['ci']
            _checkSum = self.Sacemdll.SACEM_Tx_Msg_Dll( self.__CI2CCVariantReportSacemID, \
                                                        self.CI_ID_TYPE[0], \
                                                        #self.CI_ID_TYPE[2], \
                                                        CBI_ID, \
                                                        self.CCNV_ID_TYPE[0], \
                                                        self.CCNV_ID_TYPE[2], \
                                                        _tmpVariants )
        else:
            _checkSum = ( 0, 0, 0, 0, 0, 0 )

        _Var_Mes = [_MesID, 14 + _MesLen, _Len] + \
                    _byte_Var + \
                    [_CCLoopHour] + \
                    list( _checkSum )

        _Mes = struct.pack( _format, *_Var_Mes ) 
        _Head = struct.pack( "!IH",
                             self.getDataValue( "loophour" ),
                             self.__CI2CCVariantReportMsgID )
        return _Head + struct.pack( '!B', CBI_ID ) + _Mes

    def ReadAtptoFSFB2Msg( self , msg ):
        "read FSFB2 message!"
        #获取side
        _psdid = struct.unpack( "!B", msg[6] )[0] #去掉平台头的六字节
        _side = simdata.MapData.getPSDSide( _psdid )
        
        _re = CI.__FSFB2_DLL.getFsfb2Msg( _psdid, \
                                            msg[struct.calcsize( self.msgHead ) + 1:], \
                                            len( msg ) - struct.calcsize( self.msgHead ) - 1 )
#        print "decode ci message", _side, _re
        self.logMes( 4, "decode ci message" + repr( _re ) )
        #根据side计算psd status
        _psd_status = self.getDataValue( "Cur_PSD_Status_Left" ) if  0 == _side else self.getDataValue( "Cur_PSD_Status_Right" )           
        if _re != None:
            if _psd_status in [0, 1]:
                if 1 not in _re: #全为false不操作，保持原值
                    self.__citoatpmsg[_side] = ( ( _psd_status, 0, _psd_status, 0 ), )
                else: #进行操作，以关门变量作为值返回
                    self.__citoatpmsg[_side] = ( ( _re[0], 0, _re[0], 0 ), )
            else:
                self.__citoatpmsg[_side] = ( ( _psd_status - 2, 0, _psd_status - 2, 0 ), )
        else:
            self.__citoatpmsg[_side] = ( ( _psd_status - 2, 0, _psd_status - 2, 0 ), )

    def deviceRun( self, *args, **kwargs ):
        "CI run"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        #将输出队列进行绑定
        CI.CIOutQ["ci"] = self.getDataValue( 'siminQ' )
        _Pos = None
        _CI_Cycle = 5 #CI的周期为500ms
        _Base_Time_Index = 0 #基础计数器
        #控制发消息变量
        __psdID = {0:0, 1:0} #分别存储
        __FSFB2Msg = {0:"", 1:""}
        __citoatpmsg = {0:"", 1:""}
        __getATPTOCIMsgFlag = {0:False, 1:False}
        #获得设备SSID，SSTYPE
        self.CI_ID_TYPE = self.getDataValue( 'parDic' )['ci']
        self.CCNV_ID_TYPE = self.getDataValue( 'parDic' )['ccnv']
        _Cur_CBI_IDList = [] #当前通信的CBIID，在收到ATP发送的variant request时，将CBIID放入到其中               
        
        while( 1 ):
            #获得消息，无消息是阻塞
            _msg = self.unpackAppMsgHasHead( self.inQ.get() )
            
            if None == _msg:
                continue
            
            if _msg[1] == self.__RsPosMesID:
                _Pos = [_msg[3], _msg[4]]
                
            if _msg[1] == self.__CC2CIVariantContainerMsgID:
                _CBI_ID = _msg[2]  #struct.unpack( '!B', _msg[2][0] )[0]
#                print "receive cc 2 ci message!"
                #解析消息
                if True == self.unpackCCContainerMsg( _msg[-1], _CBI_ID ):
                    if _CBI_ID not in _Cur_CBI_IDList:
                        _Cur_CBI_IDList.append( _CBI_ID )
#                    _msg = self.packVariantreport( _CBI_ID ) #有请求，则发送report消息
#                    CI.CIOutQ["ci"].put( _msg )                    

            #周期更新消息
            if _msg[1] == self.cycleMsgId:                    
                if _msg[2] == 92:
                    _Base_Time_Index += 1
                    #改值按照100ms进行                    
                    #本周期修改值（根据viom脚本）
                    _changeitem = []
                    _changeitem = self.PreSena.getNormalChangeItem( _Pos, self.defScenario )
                    for _item in _changeitem:
                        _typename = self.getVarDic()[_item[0]][0]
                        self.addDataKeyValue( _item[0], self.var_type[_typename]( _item[1] ) )

                    _Timechangeitem = self.PreSena.getTimeChangeItem( _Base_Time_Index, self.TimeScenario )
                    for _item in _Timechangeitem:
                        _typename = self.getVarDic()[_item[0]][0]
                        self.addDataKeyValue( _item[0], self.var_type[_typename]( _item[1] ) )                        
                    
                    _change_Variant = self.V_Presenario.getNormalChangeItem( _Pos, self.V_Scenario )
                    
                    #修改值    
                    if len( _change_Variant ) > 0:
                        _variant = self.VatiantIniDic  #获取所有的变量的字典
                        for _Item in _change_Variant:  #_Item:[CBIID,Index,value] 
                            #index是从1开始的，这里要减1
                            for _key in _variant:
                                if _key == int( _Item[0] ): #找到LinesectionID
                                    #修改对应的值
                                    _variant[_key][1][int( _Item[1] ) - 1] = int( _Item[2] )
                                    break #找到了，退出内部for,进行下一次值的修改
                        self.VatiantIniDic = _variant
                    
                    CI.CRCMError = self.getDataValue( "CRCMErrorFlag" )
                    #其余的则是在设备周期下进行
                    if _Base_Time_Index % _CI_Cycle != 1:
                        continue
                    #print "_Base_Time_Index", _Base_Time_Index
                    CI.__FSFB2_DLL.vsnUpdate()
                    CI.__FSFB2_DLL.Read_Flush()
                    if self.__getATPTOCIMsgFlag[0] == True and 1 == self.getDataValue( 'SENDMsgEnable_Left' ): #收到left消息
                        #print "send message!_Base_Time_Index:", _Base_Time_Index, self.__psdID
                        _psdid = self.__psdID[0] if self.getDataValue( 'Cur_PSD_ID' ) <= 0 else self.getDataValue( 'Cur_PSD_ID' )
                        self.ReadAtptoFSFB2Msg( self.__FSFB2Msg[0] )
                        CI.__FSFB2_DLL.putFsfb2Msg( _psdid, self.__citoatpmsg[0] ) 
                        CI.__FSFB2_DLL.Open_FSFB2_Send( _psdid )
#                        self.__getATPTOCIMsgFlag[0] = False
                    
                    if self.__getATPTOCIMsgFlag[1] == True and 1 == self.getDataValue( 'SENDMsgEnable_Right' ): #收到right消息
                        #print "send message!_Base_Time_Index:", _Base_Time_Index, self.__psdID
                        _psdid = self.__psdID[1] if self.getDataValue( 'Cur_PSD_ID' ) <= 0 else self.getDataValue( 'Cur_PSD_ID' )
                        self.ReadAtptoFSFB2Msg( self.__FSFB2Msg[1] )
                        CI.__FSFB2_DLL.putFsfb2Msg( _psdid, self.__citoatpmsg[1] ) 
                        CI.__FSFB2_DLL.Open_FSFB2_Send( _psdid ) 
#                        self.__getATPTOCIMsgFlag[1] = False
                    
                    CI.__FSFB2_DLL.Write_Flush()
                    
                    if self.__getATPTOCIMsgFlag[0] == True and 1 == self.getDataValue( 'SENDMsgEnable_Left' ):
                        _psdid = self.__psdID[0] if self.getDataValue( 'Cur_PSD_ID' ) <= 0 else self.getDataValue( 'Cur_PSD_ID' )
                        CI.__FSFB2_DLL.Close_FSFB2_Send( _psdid )
                        self.__getATPTOCIMsgFlag[0] = False
                                                 
                    if self.__getATPTOCIMsgFlag[1] == True and 1 == self.getDataValue( 'SENDMsgEnable_Right' ):
                        _psdid = self.__psdID[1] if self.getDataValue( 'Cur_PSD_ID' ) <= 0 else self.getDataValue( 'Cur_PSD_ID' )
                        CI.__FSFB2_DLL.Close_FSFB2_Send( _psdid )
                        self.__getATPTOCIMsgFlag[1] = False
                                                 
                    
                    #发送Variant Request消息
#                    if None != _Pos:
#                        for _CBI_ID in simdata.TrainRoute.getCBIInfo( _Pos[0] ):
#                            _tmpMsg = self.packVariantRequest( _CBI_ID )
#                            _tmpMsg = _tmpMsg[0:6] + struct.pack( '!B', _CBI_ID ) + _tmpMsg[6:] #加上CBI头
#                            CI.CIOutQ["ci"].put( _tmpMsg )
                    
                    for _CBI_ID in _Cur_CBI_IDList:
                        _msgRequest = ""
                        if ( 1 == self.getDataValue( 'SENDMsgENABLE_Req' )and \
                             _CBI_ID in self.getModifyCBIIDList() ) or \
                             _CBI_ID not in self.getModifyCBIIDList():
                            _msgRequest = self.packVariantRequest( _CBI_ID )[6:]
                        
                        _msgReport = ""
                        if ( 1 == self.getDataValue( 'SENDMsgENABLE_Var' )and \
                             _CBI_ID in self.getModifyCBIIDList() ) or \
                             _CBI_ID not in self.getModifyCBIIDList():
                            _msgReport = self.packVariantreport( _CBI_ID )[7:] #有请求，则发送report消息
                        
                        _Head = struct.pack( "!IH",
                                             self.getDataValue( "loophour" ),
                                             self.__CI2CCVariantReportMsgID )
                        
                        _msg = _Head + \
                               struct.pack( '!B', _CBI_ID ) + \
                               _msgRequest + \
                               _msgReport
                            
                        CI.CIOutQ["ci"].put( _msg )
                    
                    _Cur_CBI_IDList = [] #每周期清空                             
                    
#                    print "CIoutQ put!", commlib.str2hexlify( _tmpMsg )
                    
                    self.loophour += 1
                    self.logMes( 4, '--loophour--%d' % ( self.loophour ) )
                    self.addDataKeyValue( 'loophour', self.loophour )  
                                      
                elif _msg[2] == self.cycleIniloophour:
                    self.loophour = 1
                    self.addDataKeyValue( 'loophour', self.loophour )
                    
                elif _msg[2] == 93 :
                    break
        
        print "end ci Running!"

    #-------------------------------------------------------------------
    #@获取发送的ccloophour，该值将根据ResponseEND进行判断处理
    #-------------------------------------------------------------------
    def getccloophour( self, ccloophour, CBI_ID ):
        "get cc loophour by response end"
        _responseEnd = self.getDataValue( 'DefaultResponseEND' ) if CBI_ID not in self.getModifyCBIIDList() else self.getDataValue( 'ModifyResponseEND' )
        return commlib.getResponseCCLoophour( _responseEnd, ccloophour )
    
    def getModifyCBIIDList( self ):
        "get modify CBI ID List"
        try:
            return [int( _i ) for _i in self.getDataValue( "ModifyCIList" ).split( "," )]
        except:
            return []
        
    def deviceEnd( self ):
        " ending device"
        self._Log.fileclose() 
           
if __name__ == '__main__':
    ci = CI( 'ci', 1 )
    ci.deviceInit( varFile = r'./setting/ci_variant.xml', \
                   msgFile = r'./setting/ci_message.xml', \
                   scenario = r'./scenario/ci_scenario.xml', \
                   log = r'./log/ci.log' , \
                   fsfb2 = r'./setting/fsfb2_devicelist.xml' )
