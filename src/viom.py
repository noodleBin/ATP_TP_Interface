#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     viom.py
# Description:  viom模块    
# Author:       Chen Qing'an
# Version:      0.0.1
# Created:      2011-07-19
# Company:      CASCO
# LastChange:   create 2011-07-19
# History:
#----------------------------------------------------------------------------

from base.loglog import LogLog
from base.basedevice import BaseDevice
from base.senariopreproccess import Senariopreproccess
from base import simdata
from base.xmlparser import XmlParser
from base import commlib
import sys
import struct
import safetylayerdll

class VIOM( BaseDevice ):
    
    """
    VIOM Simulator
    """
    #平台内部传递的消息，所带的消息头，loophour,msgId
    __msgHead = '!IH'
    
    #sacem校验的实例
    _Samcedll = None
    
    #ATP给VIOM车载安全码位消息ID
    toVIOMVitalMsgId = 9219
    
    #CCNV给VIOM车载非安全码位消息ID
    #toVIOMNoVitalMsgId = None    
    
    var_type = {'int':int, 'string':str, 'float':float}
    #Rs给VIOM车载码位消息ID
    RsMsgId = 259
    
    #Rs给VIOM车辆位置消息ID
    LocationMsgId = 258
    
    #VIOM给RS安全消息ID
    toRsVitalMsgId = 5893
    
    #VIOM给RS非安全消息ID
    #toRsnoVitalMsgId = None    
    
    #VIOM给ATP消息ID
    toAtpMsgId_1A = 5889
    toAtpMsgId_1B = 5890
    toAtpMsgId_2A = 5891
    toAtpMsgId_2B = 5892
    
    #周期更新消息ID
    cycleMsgId = 99
    
    #HMI发送过来的消息ID
    HMItoVIOMId = 51234
    
    #HMI发送来的数据
    HMIVIOMInfo = None
    
    #loophour初始化命令
    cycleIniloophour = 94

    loophour = None
    
    #trainInfo = None
    
    #储存上周期从ATP收到的码位消息   
    saveMsg = None
    
    #向RS发送码位消息标志位
    outputFlag = 0
    
    #码位相异标志位
    changelist = None 
    
    SceParser = {
            'pos':{'path':'.//Position',
                    'attr':['Block_id', 'Abscissa', 'Delay']
                  },
            'time':{'path':'.//Time',
                    'attr':['Loophour']
                  },
            'set':{'path':'.//Set',
                   'attr':['type', 'viom', 'target', 'Index', 'value' ]
                }
            }
    
    ptype = {'int':int, 'string':str, 'float':float}
    
    #预处理脚本
    PreSena = None
    
    #VIOM脚本
#    VIOMScenario = None
#    TimeScenario = None
    #log实例
    __Mylog = None
    
    #相异位
    __viomDiff = {"vital":{"viom1":{"a_up":0 , "a_down" :0, "b_up":0, "b_down":0},
                          "viom2":{"a_up":0 , "a_down" :0, "b_up":0, "b_down":0}},
                 "novital":{"viom1":{"a_up":0 , "a_down" :0, "b_up":0, "b_down":0},
                            "viom2":{"a_up":0 , "a_down" :0, "b_up":0, "b_down":0}}}
    #atptoViom MEssage ID
    atpTOViomMesID = 12
    ViomToatpMesID = 11

    def __init__( self, name, id ):
        "init"
        BaseDevice.__init__( self, name, id )
    
    def logMes( self, level, mes ):
        " log mes"
        #LogLog.orderLogger(self.getDeviceName())
        self.__Mylog.logMes( level, mes )

    def initViomDiff(self):
        self.__viomDiff = {"vital":{"viom1":{"a_up":0 , "a_down" :0, "b_up":0, "b_down":0},
                          "viom2":{"a_up":0 , "a_down" :0, "b_up":0, "b_down":0}},
                             "novital":{"viom1":{"a_up":0 , "a_down" :0, "b_up":0, "b_down":0},
                                        "viom2":{"a_up":0 , "a_down" :0, "b_up":0, "b_down":0}}}
    
    def deviceInit( self, *args, **kwargs ):
        " VIOM init"
        #TODO 导入变量、应用消息、设备数据解析、控制脚本解析、离线数据计算等
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        self.clearDataDic()
        self.initViomDiff()
        self.importVarint( kwargs['varFile'] )
        self.importMsg( kwargs['msgFile'] )
        self.importDefSce( kwargs['scenario'] )
        #self.importVIOMSec(kwargs['viom_scenario'])
        self.loophour = 1
        self.addDataKeyValue( 'loophour', self.loophour )
        #初始化HMI发送的消息
        self.HMIVIOMInfo = None
        
        self.__Mylog = LogLog()
        self.__Mylog.orderLogger( kwargs['log'], type( self ).__name__ )
        #获得运行路径
        #self.trainInfo = commlib.loadTrainRout('./scenario/train_route.xml')
        #self.trainInfo = commlib.loadTrainRout(kwargs['train_route'])
        
        #blocklist = self.trainInfo[0]
        self.PreSena = Senariopreproccess()
        #self.PreSena.getblockinfolist(kwargs['track_map'], kwargs['track_maptxt'])
        
        self.defScenario = self.PreSena.getsortedscenario( self.defScenario, \
                                                          simdata.TrainRoute.getRouteDirection() )
        
        self._Samcedll = safetylayerdll.GM_SACEM_Dll( 'viom', kwargs["sacemFile"] )
        #SACEM DLL初始化
        if False == self._Samcedll.SACEM_Init_Dll():
            self.logMes( 1, "SACEM Initializing is failed!" ) 
            
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
        _head = None     
        _head = struct.pack( self.__msgHead, loophour, msgId )
#        self.logMes(4, binascii.hexlify(_head))
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
        _head = None
        _head = struct.unpack( self.__msgHead, msg[0:struct.calcsize( self.__msgHead )] )
        #self.logMes(4, 'to VIOM: ' + commlib.str2hexlify(msg))
        return _head + self.unpackAppMsg( _head[1], msg[struct.calcsize( self.__msgHead ):] )

    def deviceRun( self, *args, **kwargs ):
        "VIOM run"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        #print 'viom running...'
        _viomtoRsFlag = False
        _Pos = None
        #获得设备SSID，SSTYPE
        self._tempviom1a = self.getDataValue( 'parDic' )['viom_1_A']
        self._tempviom1b = self.getDataValue( 'parDic' )['viom_1_B']
        self._tempviom2a = self.getDataValue( 'parDic' )['viom_2_A']
        self._tempviom2b = self.getDataValue( 'parDic' )['viom_2_B']
        self._tempatp = self.getDataValue( 'parDic' )['atp']        
        _VIOM_Cycle = 1 #CCNV的周期为200ms
        _Base_Time_Index = 0 #基础计数器        
        while True:
            #获得消息，无消息是阻塞
            _msg = self.unpackAppMsgHasHead( self.inQ.get() )
            
            #收到ATP给VIOM的vital消息
            if ( _msg[1] == self.toVIOMVitalMsgId ):
                #安全码位,收到字节发送给RS
                self.unpackingAtpMsg( _msg )#解包ATP的消息,并压入rs中
                      
            #收到RS发给VIOM的码位消息
            if ( _msg[1] == self.RsMsgId ):
                #存入__data相关变量中
                self.unpackingRsMsg( *_msg )
                
            #收到RS发给VIOM的车辆位置消息
            if ( _msg[1] == self.LocationMsgId ):
                #根据车辆的位置消息更新变量值
                _Pos = [_msg[3], _msg[4]]
                
            #处理界面消息 
            if ( _msg[1] == self.HMItoVIOMId ):
                #存储数据，用于发送使用
                self.HMIVIOMInfo = _msg[2:]

            #周期更新消息
            if _msg[1] == self.cycleMsgId:
                if _msg[2] == 92:
                    _Base_Time_Index += 1
                    
                    #本周期修改值（根据viom脚本）
                    if None != _Pos:
                        self.updateProc( _Pos, _Base_Time_Index )
                    
                    #其余的则是在设备周期下进行
                    if _Base_Time_Index % _VIOM_Cycle != 1 and _VIOM_Cycle != 1:
                        continue
                                       
                    _msg2 = self.packingToAtpMsg()#向ATP发送码位消息

                                        
                    self.logMes( 4, 'viom2atp message: ' + repr( _msg2 ) )
                    
                    if 1 == self.getDataValue( 'SendMesENABLE' ):  #判断是否发送消息
                        for _m in _msg2:
                            self.logMes( 4, 'viom2atp message: ' + commlib.str2hexlify( _m ) )
                            self.getDataValue( 'siminQ' ).put( _m )
                    #self.outQ.put(_msg2)
                    self.loophour += 1
                    self.logMes( 4, '--loophour--%d' % ( self.loophour ) )
                    self.addDataKeyValue( 'loophour', self.loophour + self.getDataValue( 'detaviomloophour' ) )
                    
                elif _msg[2] == self.cycleIniloophour:
                    self.loophour = 1
                    self.addDataKeyValue( 'loophour', self.loophour )
                    
                elif _msg[2] == 93 :
                    break
                
        print 'end viom running...'
                
                
    #---------------------------------------------------------------------------
    #@Brief将单字节表示的码位转换成单bit表示的码位
    #@param ravmsg: byte型码位
    #@return: bit型码位
    #---------------------------------------------------------------------------                       
    def byteToBit( self, *args ):
        "pack byte type message to bit"
        _buf = []
        _indcdw = 0
        _shift = 0
        _indbyte = 0
        _ac = 0
        _numcode = len( args )
        if ( ( _numcode / 8 ) == 0 ):
            pass
        else:
            for _ac in range( 0, ( 8 - ( _numcode % 8 ) ) ):
                args += ( 0, 0 )
        while( _indcdw < _numcode ):
            _buf.append( 0 )
            for _shift in range( 7, -1, -1 ):          
                _buf[_indbyte] |= ( args[_indcdw] << _shift )
                _indcdw = _indcdw + 1
            _indbyte = _indbyte + 1   
        return _buf
    
    
    #---------------------------------------------------------------------------
    #@Brief将单bit表示的码位转换成单字节表示的码位
    #@param ravmsg: bit型码位
    #@return: byte型码位
    #---------------------------------------------------------------------------                
    def bitToByte( self, *args ):
        "pack bit type message to byte"
        _unzip = []
        _indcdw = 0
        _indbyte = 2
        _indbit = 0
        _bitshift = 0
        _bitmasc = 0
        _numbyte = len( args )#计算码位长度
        
        for _indbyte in range( 0, _numbyte ):
            _bitshift = 7
            _bitmasc = 0x80
            for _indbit in range( 0, 8 ):
                _unzip.append( 0 )
                _unzip[_indcdw] = ( ( args[_indbyte] & _bitmasc ) >> _bitshift )
                _bitmasc >>= 1
                _bitshift -= 1
                _indcdw = _indcdw + 1 
        return _unzip    
 
    #---------------------------------------------------------------------------
    #@Brief将ATP发给VIOM的消息进行解包处理，并将消息压入给rs
    #@param msg: 收到的消息体
    #---------------------------------------------------------------------------    
    def unpackingAtpMsg( self, msg ):  
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        #计算安全码位消息：将bit转化为Byte
        rcvmsg = list( msg )
        _viom1subtype = 1
        _viom2subtype = 2
        _SSTYPE = None
        _SSID = None
        _VIOMByteList = self.BYTETOListBit( rcvmsg[3:6] )
        #将 safetimechecked 和 mastercore从组合码位中取出来
        _safetimecheckedup = 0 if rcvmsg[12] & 128 == 0 else 1
        _safetimecheckeddown = 0 if rcvmsg[12] & 64 == 0 else 1
        _mastercore = 0 if rcvmsg[12] & 32 == 0 else 1
        
#        if(rcvmsg[12] == 128):
#            rcvmsg[12] = 1     
        _checkbody = _VIOMByteList + list( rcvmsg[6:12] ) + \
                     [_safetimecheckedup, _safetimecheckeddown, _mastercore] + list( rcvmsg[13:] )
        self.logMes( 4, 'checksum check:' + repr( _checkbody ) )
        #判断上下模块的一致性，不一致则取为0
        _viomtors = [0] * 10
        for _Index in range( 0, 10 ):
            if _VIOMByteList[_Index] != _VIOMByteList[10 + _Index]:
                _viomtors[_Index] = 0
            else:
                _viomtors[_Index] = _VIOMByteList[_Index]
        
        #print 'viom msg id:', rcvmsg[2]
        #判断是VIOM1还是VIOM2
        if _viom1subtype == rcvmsg[2]: #viom1
            #获取viomtors消息包
            _msg = self.packAppMsgHasHead( self.loophour, self.toRsVitalMsgId, \
                                          18, \
                                          *_viomtors )
            #记录atploophour
            self.addDataKeyValue( 'Vital_ATPLoophour1', rcvmsg[6] )
            #压入各自的队列中
            self.getDataValue( 'devDic' )['rs'].inQ.put( _msg ) 
            #计算校验checkSum的参数
            _SSTYPE = self.getDataValue( 'parDic' )['viom_1_A'][0]
            _SSID = self.getDataValue( 'parDic' )['viom_1_A'][2]

        elif _viom2subtype == rcvmsg[2]: #viom2
            #获取viomtors消息包
            _msg = self.packAppMsgHasHead( self.loophour, self.toRsVitalMsgId, \
                                          19, \
                                          *_viomtors )
            #记录atploophour
            self.addDataKeyValue( 'Vital_ATPLoophour2', rcvmsg[6] )
            
            #压入各自的队列中
            self.getDataValue( 'devDic' )['rs'].inQ.put( _msg ) 
                 
            #计算校验checkSum的参数
            _SSTYPE = self.getDataValue( 'parDic' )['viom_2_A'][0]
            _SSID = self.getDataValue( 'parDic' )['viom_2_A'][2]      
              
        #校验checkSum
        #print self.getDataValue('parDic')['atp'], _SSTYPE, _SSID
        _reVal = safetylayerdll.GM_SACEM_Shb_Recv2App_Type()
        _reVal = self._Samcedll.SACEM_Rx_Msg_Dll( self.atpTOViomMesID, \
                                                 self.getDataValue( 'parDic' )['atp'][0], \
                                                 self.getDataValue( 'parDic' )['atp'][2], \
                                                 _SSTYPE,
                                                 _SSID,
                                                 _checkbody )     
        if None == _reVal:
            self.logMes( 1, 'atp2viom: ' + 'Unpacking False,codewords is wrong' )   


    #---------------------------------------------------------------------------
    #将3Byte的码位转换为list[],ByteList：[byte1,byte2,byte3]
    #---------------------------------------------------------------------------
    def BYTETOListBit( self, ByteList ):
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        if 3 != len( ByteList ):
            print "BYTETOListBit error!!!"
            return None
        
        _BitList = [0] * 24 
        _ByteWord = ( ByteList[0] * 256 + ByteList[1] ) * 256 + ByteList[2]
        
        for _index in range( 0, 24 ):
            _BitList[23 - _index] = _ByteWord % 2
            _ByteWord = _ByteWord / 2
            
        return _BitList[0:20] #20个码位
        
    #---------------------------------------------------------------------------
    #@Brief从字典里获得发送码位消息，并打包成消息体
    #@param 
    #@return:返回打包好的发向Rs的消息体
    #--------------------------------------------------------------------------- 
    def packingToRsMsg( self ):
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        _trMsg = [17]
        
        #检测up和down模块,不一致则都去安全码位，也即false
        for _index in range( 0, 20 ):
            _VIOMup_name = self.VIOMuplist[_index]
            _VIOMdown_name = self.VIOMdownlist[_index]
            if self.getDataValue( _VIOMup_name ) != self.getDataValue( _VIOMdown_name ):
                #不同的值则修改为0,反之不改值
                self.addDataKeyValue( _VIOMup_name, 0 )
                self.addDataKeyValue( _VIOMdown_name, 0 )
        
        for _msgcount in range( len( self.msglist2 ) ):
            _trMsg.append( self.getDataValue( self.msglist2[_msgcount] ) )

        #print "sendMsg", _trMsg
        
        _trMsgBody = self.packAppMsgHasHead( self.loophour, self.toRsMsgId, *_trMsg )
        return _trMsgBody
 
    #---------------------------------------------------------------------------
    #@Brief从字典里获得发送码位消息，并根据从相异脚本得到的相异标志位生成发送个ATP的码位消息体
    #@param 
    #@return:返回打包好的发向ATP的消息体
    #---------------------------------------------------------------------------    
    def packingToAtpMsg( self ):
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        #将VIOM的码位转换为bit
        #转换viom1a的码位
        self.addDataKeyValue( 'VIOM1a_UP_BIT_Vital_ToATP', \
                              self.BTYE2QWORD( self.getDataValue( 'VIOM1a_UP_BYTE_Vital_ToATP' ) ) )
        self.addDataKeyValue( 'VIOM1a_DOWN_BIT_Vital_ToATP', \
                              self.BTYE2QWORD( self.getDataValue( 'VIOM1a_DOWN_BYTE_Vital_ToATP' ) ) )
        #转换viom1b的码位
        self.addDataKeyValue( 'VIOM1b_UP_BIT_Vital_ToATP', \
                              self.BTYE2QWORD( self.getDataValue( 'VIOM1b_UP_BYTE_Vital_ToATP' ) ) )
        self.addDataKeyValue( 'VIOM1b_DOWN_BIT_Vital_ToATP', \
                              self.BTYE2QWORD( self.getDataValue( 'VIOM1b_DOWN_BYTE_Vital_ToATP' ) ) )
        #转换viom2a的码位
        self.addDataKeyValue( 'VIOM2a_UP_BIT_Vital_ToATP', \
                              self.BTYE2QWORD( self.getDataValue( 'VIOM2a_UP_BYTE_Vital_ToATP' ) ) )
        self.addDataKeyValue( 'VIOM2a_DOWN_BIT_Vital_ToATP', \
                              self.BTYE2QWORD( self.getDataValue( 'VIOM2a_DOWN_BYTE_Vital_ToATP' ) ) )
        #转换viom2b的码位
        self.addDataKeyValue( 'VIOM2b_UP_BIT_Vital_ToATP', \
                              self.BTYE2QWORD( self.getDataValue( 'VIOM2b_UP_BYTE_Vital_ToATP' ) ) )
        self.addDataKeyValue( 'VIOM2b_DOWN_BIT_Vital_ToATP', \
                              self.BTYE2QWORD( self.getDataValue( 'VIOM2b_DOWN_BYTE_Vital_ToATP' ) ) )
        
        #进行相异操作
        _viom1a_vital_up = self.getDataValue( 'VIOM1a_UP_BIT_Vital_ToATP' ) ^ self.__viomDiff['vital']['viom1']['a_up']
        #print '-------viom------------', self.getDataValue( 'VIOM1a_UP_BIT_Vital_ToATP' ) , self.__viomDiff['vital']['viom1']['a_up']
        _viom1b_vital_up = self.getDataValue( 'VIOM1b_UP_BIT_Vital_ToATP' ) ^ self.__viomDiff['vital']['viom1']['b_up']

        _viom1a_vital_down = self.getDataValue( 'VIOM1a_DOWN_BIT_Vital_ToATP' ) ^ self.__viomDiff['vital']['viom1']['a_down']
        _viom1b_vital_down = self.getDataValue( 'VIOM1b_DOWN_BIT_Vital_ToATP' ) ^ self.__viomDiff['vital']['viom1']['b_down']

        _viom2a_vital_up = self.getDataValue( 'VIOM2a_UP_BIT_Vital_ToATP' ) ^ self.__viomDiff['vital']['viom2']['a_up']
        _viom2b_vital_up = self.getDataValue( 'VIOM2b_UP_BIT_Vital_ToATP' ) ^ self.__viomDiff['vital']['viom2']['b_up']

        _viom2a_vital_down = self.getDataValue( 'VIOM2a_DOWN_BIT_Vital_ToATP' ) ^ self.__viomDiff['vital']['viom2']['a_down']
        _viom2b_vital_down = self.getDataValue( 'VIOM2b_DOWN_BIT_Vital_ToATP' ) ^ self.__viomDiff['vital']['viom2']['b_down']
        
        _revMsg = []
        #计算checkSum
        _tempMes1a = commlib.transform_Qto64Bit( _viom1a_vital_up & _viom1a_vital_down ) + \
                          [self.getDataValue( 'viom_status' ), self.getDataValue( 'other_cc_connected' ),
                           self.getDataValue( 'loophour' ) + self.getDataValue( "detaviomloophour_1A" ),
                           self.getDataValue( 'Vital_ATPLoophour1' ) + self.getDataValue( 'detaccloophour' ) + self.getDataValue( "detaccloophour_1A" )]
        if 1 == self.getDataValue( 'CheckSumENABLE_1A' ):                 
            _checksum1a = self._Samcedll.SACEM_Tx_Msg_Dll( self.ViomToatpMesID, \
                                                          self._tempviom1a[0], \
                                                          self._tempviom1a[2], \
                                                          self._tempatp[0], \
                                                          self._tempatp[2], \
                                                          _tempMes1a )
        else:
            _checksum1a = ( 0, 0, 0, 0, 0, 0 )
            
        _tempMes1b = commlib.transform_Qto64Bit( _viom1b_vital_up & _viom1b_vital_down ) + \
                          [self.getDataValue( 'viom_status' ), self.getDataValue( 'other_cc_connected' ),
                           self.getDataValue( 'loophour' ) + self.getDataValue( "detaviomloophour_1B" ),
                           self.getDataValue( 'Vital_ATPLoophour1' ) + self.getDataValue( 'detaccloophour' ) + self.getDataValue( "detaccloophour_1B" )]
        
        if 1 == self.getDataValue( 'CheckSumENABLE_1B' ):                  
            _checksum1b = self._Samcedll.SACEM_Tx_Msg_Dll( self.ViomToatpMesID, \
                                                          self._tempviom1b[0], \
                                                          self._tempviom1b[2], \
                                                          self._tempatp[0], \
                                                          self._tempatp[2], \
                                                          _tempMes1b )        
        else:
            _checksum1b = ( 0, 0, 0, 0, 0, 0 )
        _tempMes2a = commlib.transform_Qto64Bit( _viom2a_vital_up & _viom2a_vital_down ) + \
                          [self.getDataValue( 'viom_status' ), self.getDataValue( 'other_cc_connected' ),
                           self.getDataValue( 'loophour' ) + self.getDataValue( "detaviomloophour_2A" ),
                           self.getDataValue( 'Vital_ATPLoophour2' ) + self.getDataValue( 'detaccloophour' ) + self.getDataValue( "detaccloophour_2A" )]
        
        if 1 == self.getDataValue( 'CheckSumENABLE_2A' ):                 
            _checksum2a = self._Samcedll.SACEM_Tx_Msg_Dll( self.ViomToatpMesID, \
                                                          self._tempviom2a[0], \
                                                          self._tempviom2a[2], \
                                                          self._tempatp[0], \
                                                          self._tempatp[2], \
                                                          _tempMes2a )            
        else:
            _checksum2a = ( 0, 0, 0, 0, 0, 0 )
        
        _tempMes2b = commlib.transform_Qto64Bit( _viom2b_vital_up & _viom2b_vital_down ) + \
                          [self.getDataValue( 'viom_status' ), self.getDataValue( 'other_cc_connected' ),
                           self.getDataValue( 'loophour' ) + self.getDataValue( "detaviomloophour_2B" ),
                           self.getDataValue( 'Vital_ATPLoophour2' ) + self.getDataValue( 'detaccloophour' ) + self.getDataValue( "detaccloophour_2B" )]
        
        if 1 == self.getDataValue( 'CheckSumENABLE_2B' ):                  
            _checksum2b = self._Samcedll.SACEM_Tx_Msg_Dll( self.ViomToatpMesID, \
                                                          self._tempviom2b[0], \
                                                          self._tempviom2b[2], \
                                                          self._tempatp[0], \
                                                          self._tempatp[2], \
                                                          _tempMes2b )  
        else:
            _checksum2b = ( 0, 0, 0, 0, 0, 0 )

        #获得VIOMToatp包
        _Mes_1A = [_viom1a_vital_up & _viom1a_vital_down, \
                self.getDataValue( 'viom_status' ), self.getDataValue( 'other_cc_connected' ), \
                self.getDataValue( 'loophour' ) + self.getDataValue( "detaviomloophour_1A" ),
                self.getDataValue( 'Vital_ATPLoophour1' ) + self.getDataValue( 'detaccloophour' ) + self.getDataValue( "detaccloophour_1A" )] + list( _checksum1a ) 
        _Mes_1B = [_viom1b_vital_up & _viom1b_vital_down, \
                self.getDataValue( 'viom_status' ), self.getDataValue( 'other_cc_connected' ), \
                self.getDataValue( 'loophour' ) + self.getDataValue( "detaviomloophour_1B" ),
                self.getDataValue( 'Vital_ATPLoophour1' ) + self.getDataValue( 'detaccloophour' ) + self.getDataValue( "detaccloophour_1B" )] + list( _checksum1b )
        _Mes_2A = [_viom2a_vital_up & _viom2a_vital_down, \
                self.getDataValue( 'viom_status' ), self.getDataValue( 'other_cc_connected' ), \
                self.getDataValue( 'loophour' ) + self.getDataValue( "detaviomloophour_2A" ),
                self.getDataValue( 'Vital_ATPLoophour2' ) + self.getDataValue( 'detaccloophour' ) + self.getDataValue( "detaccloophour_2A" )] + list( _checksum2a )
        _Mes_2B = [_viom2b_vital_up & _viom2b_vital_down, \
                self.getDataValue( 'viom_status' ), self.getDataValue( 'other_cc_connected' ), \
                self.getDataValue( 'loophour' ) + self.getDataValue( "detaviomloophour_2B" ),
                self.getDataValue( 'Vital_ATPLoophour2' ) + self.getDataValue( 'detaccloophour' ) + self.getDataValue( "detaccloophour_2B" )] + list( _checksum2b ) 
        
        if 1 == self.getDataValue( 'SendMesENABLE_1A' ):
            _rMsg_1A = self.packAppMsgHasHead( self.loophour, self.toAtpMsgId_1A, *_Mes_1A )
            _revMsg.append( _rMsg_1A )        
        if 1 == self.getDataValue( 'SendMesENABLE_1B' ):
            _rMsg_1B = self.packAppMsgHasHead( self.loophour, self.toAtpMsgId_1B, *_Mes_1B )
            _revMsg.append( _rMsg_1B )
        if 1 == self.getDataValue( 'SendMesENABLE_2A' ):
            _rMsg_2A = self.packAppMsgHasHead( self.loophour, self.toAtpMsgId_2A, *_Mes_2A )
            _revMsg.append( _rMsg_2A )
        if 1 == self.getDataValue( 'SendMesENABLE_2B' ):
            _rMsg_2B = self.packAppMsgHasHead( self.loophour, self.toAtpMsgId_2B, *_Mes_2B )
            _revMsg.append( _rMsg_2B )
            
        return _revMsg

    #---------------------------------------------------------------------------
    #将列表：包含16个码位转换为一个word，列表的最左边为最高为，右边为最低位
    #BYTEList:长度必须为16，否则报错
    #返回，word数据
    #---------------------------------------------------------------------------
    def BTYE2WORD( self, BYTEList ):
        "get word from 16 byte"
        if 16 != len( BYTEList ):
            print "VIOM list length error!!!"
            return None
        
        _WORD = 0
        #计算word
        for _Byte in BYTEList:
            _WORD = _WORD * 2 + _Byte #每次进位并加尾部
        
        return  _WORD

    #---------------------------------------------------------------------------
    #将列表：包含16个码位转换为一个word，列表的最左边为最高为，右边为最低位
    #BYTEList:长度必须为16，否则报错
    #返回，word数据
    #---------------------------------------------------------------------------
    def BTYE2QWORD( self, BYTEList ):
        "get word from 16 byte"
        if 64 != len( BYTEList ):
            print "VIOM list length error!!!"
            return None
        
        _WORD = 0
        #计算word
        for _Byte in BYTEList:
            _WORD = _WORD * 2 + _Byte #每次进位并加尾部
        
        return  _WORD
    
    #---------------------------------------------------------------------------
    #@Brief将从Rs发过来的码位消息打印到日志里，并更新到字典里
    #@param 
    #@return:返回码位
    #---------------------------------------------------------------------------    
    def unpackingRsMsg( self, *rcvMsg ):
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        _unpackMsgbody = [0]
        _codewords = rcvMsg[3:]
        self.logMes( 4, 'Rs codewords' + repr( rcvMsg ) )#将收到的消息打印到日志上
        #存入VIOM1的安全消息
        self.addDataKeyValue( 'VIOM1a_UP_BYTE_Vital_ToATP', _codewords[0:64] )
        self.addDataKeyValue( 'VIOM1b_UP_BYTE_Vital_ToATP', _codewords[0:64] )     
        self.addDataKeyValue( 'VIOM1a_DOWN_BYTE_Vital_ToATP', _codewords[0:64] )
        self.addDataKeyValue( 'VIOM1b_DOWN_BYTE_Vital_ToATP', _codewords[0:64] )       
        #存入VIOM2的安全消息
        self.addDataKeyValue( 'VIOM2a_UP_BYTE_Vital_ToATP', _codewords[64:128] )
        self.addDataKeyValue( 'VIOM2b_UP_BYTE_Vital_ToATP', _codewords[64:128] )
        self.addDataKeyValue( 'VIOM2a_DOWN_BYTE_Vital_ToATP', _codewords[64:128] )
        self.addDataKeyValue( 'VIOM2b_DOWN_BYTE_Vital_ToATP', _codewords[64:128] )
 
    #---------------------------------------------------------------------------
    #@Brief根据档前位置获取改变的值
    #@param ravmsg: 收到的消息体
    #@return: 
    #---------------------------------------------------------------------------      
    def updateProc( self, Pos, BaseTime ):
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        _changeitem = []
        _changeitem = self.PreSena.getNormalChangeItem( Pos, self.defScenario )
        #print 'change item:', _changeitem
        for _item in _changeitem:
            if "vital-viom" in _item[0]:
                #设置相异码位
                _temp = [_s for _s in _item[0].strip().split( '-' )]
                self.__viomDiff[_temp[0]][_temp[1]][_temp[2]] = int( _item[1], 2 )
                
            else: #正常改值
                _typename = self.getVarDic()[_item[0]][0]
                self.addDataKeyValue( _item[0], self.var_type[_typename]( _item[1] ) )

#            #设置相异码位
#            if 1 == int(_item[4]): #设置对应位为1，用或
#                self.__viomDiff[_item[0]][_item[1]][_item[2]] = self.__viomDiff[_item[0]][_item[1]][_item[2]] | \
#                                                                (1 << (15 - int(_item[3])))
#            elif 0 == int(_item[4]): #设置对应位为0，用与
#                self.__viomDiff[_item[0]][_item[1]][_item[2]] = self.__viomDiff[_item[0]][_item[1]][_item[2]] & \
#                                                                (65535 - (1 << (15 - int(_item[3]))))#16个1，并将对应位改为0
                
        _Timechangeitem = self.PreSena.getTimeChangeItem( BaseTime, self.TimeScenario )
        for _item in _Timechangeitem:
            if "vital-viom" in _item[0]:
                #设置相异码位
                _temp = [_s for _s in _item[0].strip().split( '-' )]
                self.__viomDiff[_temp[0]][_temp[1]][_temp[2]] = int( _item[1], 2 )
                
            else: #正常改值
                _typename = self.getVarDic()[_item[0]][0]
                self.addDataKeyValue( _item[0], self.var_type[_typename]( _item[1] ) )
#
#            #设置相异码位
#            if 1 == int(_item[4]): #设置对应位为1，用或
#                self.__viomDiff[_item[0]][_item[1]][_item[2]] = self.__viomDiff[_item[0]][_item[1]][_item[2]] | \
#                                                                (1 << (15 - int(_item[3])))
#            elif 0 == int(_item[4]): #设置对应位为0，用与
#                self.__viomDiff[_item[0]][_item[1]][_item[2]] = self.__viomDiff[_item[0]][_item[1]][_item[2]] & \
#                                                                (65535 - (1 << (15 - int(_item[3]))))
            
    #-----------------------------------------------------------------------------
    #导入VIOM相异的脚本，格式为[[BlockID,Absicssa,delay,[[type,viom,target,Index,value],...]],...]
    #-----------------------------------------------------------------------------
    def importVIOMSec( self, ViomsceFile ):
        "import Variant format scenario"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        self.defScenario = [] #清空
        self.TimeScenario = []
        _f = XmlParser()
        _f .loadXmlFile( ViomsceFile )
        #获得所有Position节点
        _posNdoe = _f.getAllElementByName( self.SceParser['pos']['path'] )
        for _pn in _posNdoe:
            _l = []
            _pna = _f.getAttrListOneNode( _pn, self.SceParser['pos']['attr'] )
            _l.append( _pna[0] )
            _l.append( _pna[1] )
            _l.append( _pna[2] )
            
            #获得所有该Position下Set节点的属性
            _seta = [_f.getAttrListOneNode( _set, self.SceParser['set']['attr'] ) \
                    for _set in _f.getNodeListInNode( _pn, self.SceParser['set']['path'] )]       
            _l.append( _seta )
            self.defScenario.append( _l )  
        
        #获得所有Time节点
        _timeNode = _f.getAllElementByName( self.SceParser['time']['path'] )
        for _tn in _timeNode:
            #获Position得属性
            _l = []
            _pna = _f.getAttrListOneNode( _tn, self.SceParser['time']['attr'] )
            #将loophour以及delay转化为int
            _l.append( int( _pna[0] ) )
             
            #获得所有该Position下Set节点的属性
            _seta = [_f.getAttrListOneNode( _set, self.SceParser['set']['attr'] ) \
                    for _set in _f.getNodeListInNode( _tn, self.SceParser['set']['path'] )]           
            _l.append( _seta )
            self.TimeScenario.append( _l )                 
           
    def deviceEnd( self ):
        "device end"
        self.__Mylog.fileclose()            

if __name__ == '__main__':
    viom = VIOM( 'viom', 1 )
    viom.deviceInit( varFile = r'./setting/viom_variant.xml', \
                    msgFile = r'./setting/viom_message.xml', \
                    scenario = r'./scenario/viom_scenario.xml', \
                    log = r'./log/viom.log' )
    print 'over device init'
    print 'data dic', viom.getDataDic()
    print 'var dic', viom.getVarDic()
    print 'msg dic', viom.getMsgDic()
    print 'def scenario', viom.defScenario
    print 'time scenario', viom.TimeScenario 
#    print viom.BYTETOListBit([1, 3, 4])   
