# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     datp.py
# Description:  datp设备仿真     
# Author:       Tiantian He
# Version:      0.0.3
# Created:      2011-07-23
# Company:      CASCO
# LastChange:   create 2011-07-26
# History:      将初始时间1,2；最大时间常数1,2写入variants.xml
#               添加强制转换操作
#               为deviceInit添加返回值
#               2011-7-26
#               添加sacem  by xiongkunpeng
#               2011-9-15
#----------------------------------------------------------------------------

from base.loglog import LogLog
from base.basedevice import BaseDevice
from base import commlib
from base.senariopreproccess import Senariopreproccess
import sys
import struct
import binascii
import safetylayerdll
from base import simdata

class DATP( BaseDevice ):
    """
    DATP Simulator
    """
    
    #周期更新消息ID
    cycleMsgId = 99
    
    #loophour初始化命令
    cycleIniloophour = 94
    
    #RS每周期发过来的跑车消息ID
    datpDisMsgId = 258
    #datp发送的同步消息ID
    datpSendSynMsgId = 1793
    #datp接受的同步消息ID
    datpRevSynMsgId = 9220
    
    #datp给atp的同步消息ID
    ToAtpSynMsgID = 21
    #平台内部传递的消息，所带的消息头，loophour,msgId
    msgHead = '!IH'    

    #本周起开始和结束时的位置
    __StartPos = None
    __EndPos = None
    
    #从train_route.xml文件中读取到得 列车运行信息
    #trainRoute = None
    #从train_route.xml文件中读取到得 BlockList
    #blockList = None
    #从train_route.xml文件中读取到得 列车运行方向
    trainDirection = None
    
    #log实例
    __log = None
    
    #Senariopreproccess的实例
    scePrepro = None
    
    #HMI至datp的消息id
    HMI2datpId = 51236
    
    #HMI至datp的消息 
    HMI2datpInfo = None
    
    #远近ATP端选择字, 
    #end_1 = None
    
    var_type = {'int':int, 'string':str, 'float':float}
    
    #sacem checksum计算的的实例
    Sacemdll = None
    
    #===========================================================================
    # 实例化时传入name和id，并调用
    #===========================================================================
    def __init__( self, name, id ):
        "init"
        BaseDevice.__init__( self, name, id )
        
    def logMes( self, level, mes ):
        "log Mes"
        #LogLog.orderLogger(self.getDeviceName())
        self.__log.logMes( level, mes )
    
    def deviceInit( self, *args, **kwargs ):
        "datp init"
        #TODO 导入变量、应用消息、设备数据解析、控制脚本解析、离线数据计算等
        self.__log = LogLog()
        self.__log.orderLogger( kwargs['log'], type( self ).__name__ )
        
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        self.importVarint( kwargs['varFile'] )
        self.importMsg( kwargs['msgFile'] )
        self.importDefSce( kwargs['scenario'] )
        #初始化HMI消息
        self.HMI2datpInfo = None        
         
        #周期开始位置初始化
        self.__StartPos = None
        self.__EndPos = None

        #self.trainRoute = commlib.loadTrainRout(kwargs['trainrouteFile'])
        self.blockList = simdata.TrainRoute.getBlockinfolist()
        self.trainDirection = simdata.TrainRoute.getRouteDirection()
#        print self.blockList, self.trainDirection
        self.scePrepro = Senariopreproccess()
        #self.scePrepro.getblockinfolist(kwargs['binFile'], kwargs['binFiletxt'])
#        print self.defScenario
        self.defScenario = self.scePrepro.getsortedscenario( self.defScenario, self.trainDirection )

        #SacemDLL初始化
        self.Sacemdll = safetylayerdll.GM_SACEM_Dll( 'datp', kwargs["sacemFile"] )
        #SACEM DLL初始化
        if False == self.Sacemdll.SACEM_Init_Dll():
            self.logMes( 1, "SACEM Initializing failed!" ) 

#        self.loophour = 0
        self.addDataKeyValue( 'loophour', 1 )
               
#        print self.getDataValue('CurrentTime'), self.getDataValue('LatestTimeOtherCore')           
        return True
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 打包应用消息，添加头信息，无需进行安全协议打包
    #
    # @Param loophour
    # @Param msgId
    # @Param args
    #
    # @Returns msg
    # --------------------------------------------------------------------------
    def packAppMsgHasHead( self, loophour, msgId, *args ):
        "packing APP message"
#        self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        _head = struct.pack( self.msgHead, loophour, msgId )
        return _head + self.packAppMsg( msgId, *args )
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 解析带GAPP头信息的应用消息， 应用消息为非安全消息
    #
    # @Param msg
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def unpackAppMsgHasHead( self, msg ):
        "unpacking message"
#        self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        _head = struct.unpack( self.msgHead, msg[0:struct.calcsize( self.msgHead )] )
#        self.logMes( 4, 'datp message: ' + 'message length:' + str( len( msg ) ) + 'mesID: ' + str( _head[1] ) )
        return _head + self.unpackAppMsg( _head[1], msg[struct.calcsize( self.msgHead ):] )
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 更新本地和另一端ATP的当前运行时间
    #
    # @Param end: 远近端
    #
    # @Returns 
    # --------------------------------------------------------------------------
#    def updateCurrentTime( self, end ):
#        if( end == 1 ):
#            if( self.getDataValue( 'CurrentTime' ) > self.getDataValue( 'CC1_MAX_TIME' ) ):
#                self.addDataKeyValue( 'CurrentTime', self.getDataValue( 'CC1_INIT_TIME' ) )
#            else:
#                tempCurrentTime = self.getDataValue( 'CurrentTime' ) + 1
#                self.addDataKeyValue( 'CurrentTime', tempCurrentTime )
##            if( self.getDataValue( 'LatestTimeOtherCore' ) > self.getDataValue( 'CC2_MAX_TIME' ) ):
##                self.addDataKeyValue( 'LatestTimeOtherCore', self.getDataValue( 'CC2_INIT_TIME' ) )
##            else:
##                tempLastestTimeOtherCore = self.getDataValue( 'LatestTimeOtherCore' ) + 1
##                self.addDataKeyValue( 'LatestTimeOtherCore', tempLastestTimeOtherCore )
#        elif( end == 2 ):
#            if( self.getDataValue( 'CurrentTime' ) > self.getDataValue( 'CC2_MAX_TIME' ) ):
#                self.addDataKeyValue( 'CurrentTime', self.getDataValue( 'CC2_INIT_TIME' ) )
#            else:
#                tempCurrentTime = self.getDataValue( 'CurrentTime' ) + 1
#                self.addDataKeyValue( 'CurrentTime', tempCurrentTime )
##            if( self.getDataValue( 'LatestTimeOtherCore' ) > self.getDataValue( 'CC1_MAX_TIME' ) ):
##                self.addDataKeyValue( 'LatestTimeOtherCore', self.getDataValue( 'CC1_INIT_TIME' ) )
##            else:
##                tempLastestTimeOtherCore = self.getDataValue( 'LatestTimeOtherCore' ) + 1
##                self.addDataKeyValue( 'LatestTimeOtherCore', tempLastestTimeOtherCore )
#        else:
#            #异常处理
#            self.logMes( 1, 'end1 and end2 error' )

    #-------------------------------------------------------------------
    #@获取发送的ccloophour，该值将根据ResponseEND进行判断处理
    #-------------------------------------------------------------------
    def getccloophour( self, baseloophour ):
        "get cc loophour by response end"
        #先对baseloophour进行求余运算
        baseloophour = baseloophour % self.getDataValue( 'ATP_MAX_TIME' )
        
        if 1 == self.getDataValue( 'Active_ATP' ):
            return baseloophour
        elif 2 == self.getDataValue( 'Active_ATP' ):
            return baseloophour + self.getDataValue( 'ATP_MAX_TIME' )
        else:
            self.logMes( 1, 'Error Value : ResponseEND！！！' )
            return None

    
    def deviceRun( self, *args, **kwargs ):
        "DATP run"
        #logmsg
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        #DOIT
        #print 'datp running...'
        self.DATP_ID_TYPE = self.getDataValue( 'parDic' )['datp']
        self.ATP_ID_TYPE = self.getDataValue( 'parDic' )['atp']
        _DATP_Cycle = 1 #CCNV的周期为100ms
        _Base_Time_Index = 0 #基础计数器
        while True:
            #等待，获取消息
#            self.inQ.put(self.packAppMsgHasHead(444, self.cycleMsgId, 92))
            _msg = self.unpackAppMsgHasHead( self.inQ.get() )
#            print _msg
            
            #接收到TS发过来的beaconID
            if _msg[1] == 514:
                self.logMes( 4, "Receiving TS beaconID" )
                self.addDataKeyValue( 'BeaconId', _msg[3] )
            
            #接收远端ATP同步消息处理
            if _msg[1] == self.datpRevSynMsgId:
                "Rev Syn Report"
                self.logMes( 4, "Receiving ATP Synchronization Report, MsgId = " + str( _msg[1] ) + \
                           " loophour = " + str( _msg[0] ) )
                self.logMes( 4, "Mes " + repr( _msg ) )
                #获取lasttimeothercore
                self.addDataKeyValue( 'LatestTimeOtherCore', _msg[2] )

                #读取SafetyApplicationVersion的值
                if 0 == self.getDataValue( 'SafetyParVersion_Modify' ):
                    self.addDataKeyValue( 'SafetyParameterVersion', _msg[45] )
                
                #读取SafetyApplicationVersion的值
                if 0 == self.getDataValue( 'SafetyAppVersion_Modify' ):
                    self.addDataKeyValue( 'SafetyApplicationVersion', _msg[46] )
                    
                #读取RadarRawSpeed的值
                if 0 == self.getDataValue( 'RadarRawSpeed_Modify' ):
                    self.addDataKeyValue( 'RadarRawSpeed', _msg[49] )
                
                #print "atp2datp message:", _msg[2:]
                _retcdw = self.Sacemdll.SACEM_Rx_Msg_Dll( self.ToAtpSynMsgID, self.ATP_ID_TYPE[0], self.ATP_ID_TYPE[2], self.DATP_ID_TYPE[0], self.DATP_ID_TYPE[2], _msg[2:] )
                if None == _retcdw:
                    self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name + 'sacem check failed' )
            
            if _msg[1] == self.HMI2datpId:
                _tmp = _msg[2:]
                #计算checksum
                _checkSum = self.Sacemdll.SACEM_Tx_Msg_Dll( self.ToAtpSynMsgID, \
                                                           self.DATP_ID_TYPE[0], \
                                                           self.DATP_ID_TYPE[2], \
                                                           self.ATP_ID_TYPE[0], \
                                                           self.ATP_ID_TYPE[2], \
                                                           list( _tmp ) )
                
                self.HMI2datpInfo = self.packAppMsgHasHead( self.getDataValue( 'loophour' ), \
                                                           self.datpSendSynMsgId, \
                                                           *( _tmp + _checkSum ) )               
                    
            #RS跑车消息处理
            if _msg[1] == self.datpDisMsgId:
                "RS Status_REPORT"
                #print "receiving RS running report"
                #更改_data中相应的值即可，无需pack
                self.logMes( 4, "Receiving RS running Message, MsgId = " + str( _msg[1] ) + \
                            " loophour = " + str( _msg[0] ) + \
                            " Block Coordinates_1 = " + str( _msg[3] ) + \
                            " Block Coordinates_2 = " + str( _msg[4] ) )
                #将位置付给变量
                self.__StartPos = _msg[3]
                self.__EndPos = _msg[4]                                    
            
            #周期更新消息处理
            if _msg[1] == self.cycleMsgId:
                #"周期更新, 结束运行消息"
                if _msg[2] == 92:
                    _Base_Time_Index += 1
                    #改值按照100ms进行
                    #检测是否有改值
                    setValues = self.scePrepro.getNormalChangeItem( [self.__StartPos, self.__EndPos], self.defScenario )
    #                print setValues
                    for setValue in setValues:
                        _typename = self.getVarDic()[setValue[0]][0]
                        self.addDataKeyValue( setValue[0], self.var_type[_typename]( setValue[1] ) )
                        if 'ATP_MAX_TIME' == setValue[0]: #ATP_MAX_TIME的修改需要传输给commlib的ATP_MAX_TIME变量
                            commlib.ATP_MAX_TIME = self.var_type[_typename]( setValue[1] )
                        
                    setValues = self.scePrepro.getTimeChangeItem( _Base_Time_Index, self.TimeScenario )
    #               print setValues
                    for setValue in setValues:
                        _typename = self.getVarDic()[setValue[0]][0]
                        self.addDataKeyValue( setValue[0], self.var_type[_typename]( setValue[1] ) ) 
                        if 'ATP_MAX_TIME' == setValue[0]:#ATP_MAX_TIME的修改需要传输给commlib的ATP_MAX_TIME变量
                            commlib.ATP_MAX_TIME = self.var_type[_typename]( setValue[1] )
                    
                    #"周期更新"
                    self.logMes( 4, "Receiving loophour Update Message, MsgId = " + str( _msg[1] ) + \
                                " loophour = " + str( _msg[0] ) ) 
                    
                    #其余的则是在设备周期下进行
#                    if _Base_Time_Index % _DATP_Cycle != 1:
#                        continue
                                       
                    #更新loophour
                    _loophour = self.getDataValue( 'loophour' )
                    _loophour += 1
                    self.addDataKeyValue( 'loophour', _loophour )
#                    print self.getDataValue('loophour')
                    
                    #更新本地和另一端ATP的当前运行时间
                    #self.updateCurrentTime(self.end_1)
                    self.addDataKeyValue( 'CurrentTime', \
                                          self.getccloophour( self.getDataValue( 'loophour' ) ) )
#                    print self.getDataValue('CurrentTime')
              
                    if None == self.HMI2datpInfo:
                        #pack and send message
                        #计算checksum
                        _tmpMes = [self.getDataValue( 'CurrentTime' ) + self.getDataValue( 'deta_CurrentTime' ), \
                                   self.getDataValue( 'LatestTimeOtherCore' ) + self.getDataValue( 'deta_LatestTimeOtherCore' ), \
                                   self.getDataValue( 'CoreId' ), \
                                   self.getDataValue( 'BeaconId' ), \
                                   self.getDataValue( 'EnableDoorOpeningA' ), \
                                   self.getDataValue( 'EnableDoorOpeningB' ), \
                                   self.getDataValue( 'PSDmanagerOpeningOrder' ), \
                                   self.getDataValue( 'PSDidSideA' ), \
                                   self.getDataValue( 'PSDvaliditySideA' ), \
                                   self.getDataValue( 'PSDclosedSideA' ), \
                                   self.getDataValue( 'PSDidSideB' ), \
                                   self.getDataValue( 'PSDvaliditySideB' ), \
                                   self.getDataValue( 'PSDclosedSideB' ), \
                                   self.getDataValue( 'ZCVersion[0]' ), \
                                   self.getDataValue( 'ZCVersion[1]' ), \
                                   self.getDataValue( 'ZCVersion[2]' ), \
                                   self.getDataValue( 'ZCVersion[3]' ), \
                                   self.getDataValue( 'ZCVersion[4]' ), \
                                   self.getDataValue( 'ZCVersion[5]' ), \
                                   self.getDataValue( 'ZCVersion[6]' ), \
                                   self.getDataValue( 'ZCVersion[7]' ), \
                                   self.getDataValue( 'ZCVersion[8]' ), \
                                   self.getDataValue( 'ZCVersion[9]' ), \
                                   self.getDataValue( 'ZCVersion[10]' ), \
                                   self.getDataValue( 'ZCVersion[11]' ), \
                                   self.getDataValue( 'ZCVersion[12]' ), \
                                   self.getDataValue( 'ZCVersion[13]' ), \
                                   self.getDataValue( 'ZCVersion[14]' ), \
                                   self.getDataValue( 'ZCVersion[15]' ), \
                                   self.getDataValue( 'LocatedOnKnownPath' ), \
                                   self.getDataValue( 'LocatedWithMemLocation' ), \
                                   self.getDataValue( 'LocationExt2Abscissa' ), \
                                   self.getDataValue( 'LocationExt2Block' ), \
                                   self.getDataValue( 'LocationEnd2Orientation' ), \
                                   self.getDataValue( 'LocationUncertainty' ), \
                                   self.getDataValue( 'LocationExt1Abscissa' ), \
                                   self.getDataValue( 'LocationExt1Block' ), \
                                   self.getDataValue( 'LocationEnd1Orientation' ), \
                                   self.getDataValue( 'SleepZoneId' ), \
                                   self.getDataValue( 'SleepZoneVersion' ), \
                                   self.getDataValue( 'MotionSinceLastRelocated' ), \
                                   self.getDataValue( 'MotionSinceMemoryLocated' ), \
                                   self.getDataValue( 'TrainFilteredStopped' ), \
                                   self.getDataValue( 'SafetyParameterVersion' ), \
                                   self.getDataValue( 'SafetyApplicationVersion' ), \
                                   self.getDataValue( 'CC_SSID' ), \
                                   self.getDataValue( 'OverlapExpired' ), \
                                   self.getDataValue( 'RadarRawSpeed' )]
                        #print "datp message:", _tmpMes
                        
                        if 1 == self.getDataValue( 'CheckSumENABLE' ):
                            _checkSum = self.Sacemdll.SACEM_Tx_Msg_Dll( self.ToAtpSynMsgID, \
                                                           self.DATP_ID_TYPE[0], \
                                                           self.DATP_ID_TYPE[2], \
                                                           self.ATP_ID_TYPE[0], \
                                                           self.ATP_ID_TYPE[2], \
                                                           _tmpMes )
                        else:
                            _checkSum = ( 0, 0, 0, 0, 0, 0 )
                            
                        _msgSend = self.packAppMsgHasHead( self.getDataValue( 'loophour' ), \
                                                          self.datpSendSynMsgId, \
                                                          *( _tmpMes + list( _checkSum ) ) )
                        
                        self.logMes( 4, 'send to atp mes:' + repr( _tmpMes + list( _checkSum ) ) )
                    else:
                        _msgSend = self.HMI2datpInfo
                    
                    if 1 == self.getDataValue( 'SendMesENABLE' ): #判断是后发送数据
                        self.getDataValue( 'siminQ' ).put( _msgSend )
                        #self.outQ.put(_msgSend)
                    #reset beaconID in cycle end
                    self.addDataKeyValue( 'BeaconId', 0 )
                    #print "pack message", len(_msgSend), binascii.hexlify(_msgSend)

                elif _msg[2] == self.cycleIniloophour:
                    self.addDataKeyValue( 'loophour', 1 )   
                    
                elif _msg[2] == 93:
                    #"结束运行"
                    self.logMes( 4, "Receiving Ending Message, MsgId = " + str( _msg[1] ) + \
                                " loophour = " + str( _msg[0] ) )
                    break
        print 'end datp running...'
    def deviceEnd( self ):
        "Ending device"
        #TODO
        self.__log.fileclose()
            
if __name__ == '__main__': 
    datp = DATP( 'datp', 7 )
    datp.deviceInit( varFile = r'./setting/datp_variant.xml', \
                    msgFile = r'./setting/datp_message.xml', \
                    scenario = r'./scenario/datp_scenario.xml', \
                    log = r'./log/datp.log' )
#    datp.deviceRun()
#            self.inQ.put(self.packAppMsgHasHead(333, self.datpDisMsgId, 15, 230000, 240000))
#            self.inQ.put(self.packAppMsgHasHead(333, self.datpRevSynMsgId, \
#                                                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, \
#                                                11, 12, 13, 14, 15, 16, 17, 18, 19, 20, \
#                                                21, 22, 23, 24, 25, 26, 27, 28, 29, 30, \
#                                                31, 32, 33, 34))
#            self.inQ.put(self.packAppMsgHasHead(444, self.cycleMsgId, 92))
#            self.inQ.put(self.packAppMsgHasHead(444, self.cycleMsgId, 93))
