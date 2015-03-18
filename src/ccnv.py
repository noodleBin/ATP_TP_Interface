# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     ccnv.py
# Description:  ccnv设备仿真     
# Author:       Tiantian He
# Version:      0.0.1
# Created:      2011-07-19
# Company:      CASCO
# LastChange:   create 2011-07-26
# History:      将初始时间1,2；最大时间常数1,2写入variants.xml
#               添加强制转换操作
#               为deviceInit添加返回值
#               2011-7-26
#----------------------------------------------------------------------------

from base.loglog import LogLog
from base.basedevice import BaseDevice
from base import commlib
from base.senariopreproccess import Senariopreproccess
from base import simdata
import struct
import sys
import time
class CCNV( BaseDevice ):
    """
    CCNV Simulator
    """
    
    #周期更新消息ID
    cycleMsgId = 99
    
    #loophour初始化命令
    cycleIniloophour = 94
    
    #RS每周期发过来的跑车消息ID
    ccnvDisMsgId = 258
    #ccnv非安全请求消息ID
    ccnvReqId = 5121

    #ccnv初始化报文消息ID
    ccnvRepId = 9218
    
    ccnvRepIniId = 9217
    
    #HMI给ccnv的消息id
    HMI2ccnvId = 51235
    
    #HMI给ccnv消息
    HMI2ccnvInfo = None
    
    #平台内部传递的消息，所带的消息头，loophour,msgId
    msgHead = '!IH'
    
    #从train_route.xml文件中读取到得 列车运行信息
    trainRoute = None
    #从train_route.xml文件中读取到得 BlockList
    blockList = None
    #从train_route.xml文件中读取到得 列车运行方向
    trainDirection = None
    
    #Senariopreproccess的实例
    scePrepro = None
    
    #本周起开始和结束时的位置
    __StartPos = None
    __EndPos = None
    
    var_type = {'int':int, 'string':str, 'float':float}
    
    #log实例
    __log = None
    
    #loophour放在variant.xml中
#    loophour = None

        
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
        "ccnv init"
        #TODO 导入变量、应用消息、设备数据解析、控制脚本解析、离线数据计算等
        self.__log = LogLog()
        self.__log.orderLogger( kwargs['log'], type( self ).__name__ )
        #周期开始位置初始化
        self.__StartPos = None
        self.__EndPos = None
        #初始化HMI的ccnv消息
        self.HMI2ccnvInfo = None
        
#        self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        self.importVarint( kwargs['varFile'] )
        self.importMsg( kwargs['msgFile'] )
        self.importDefSce( kwargs['scenario'] )
#        print self.getDataDic()
#        print self.getMsgDic()
#        print self.getVarDic()
        
        #self.trainRoute = commlib.loadTrainRout(kwargs['trainrouteFile'])
#        print self.trainRoute
        #self.blockList = self.trainRoute[0]
        self.trainDirection = simdata.TrainRoute.getRouteDirection()
#        print self.blockList, self.trainDirection
        
        self.scePrepro = Senariopreproccess()
#        self.scePrepro.getblockinfolist( kwargs['binFile'], kwargs['binFiletxt'] )
#        print self.defScenario
        self.defScenario = self.scePrepro.getsortedscenario( self.defScenario, self.trainDirection )
#        print self.defScenario
        
#        self.loophour = 0
#        ccnv规则1的条件
        self.addDataKeyValue( 'loophour', 1 )
        
        #逻辑规则
        self.importRuleDic( kwargs['rules'] )
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
    # @Brief 解析带头信息的应用消息， 应用消息为非安全消息
    #
    # @Param msg
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def unpackAppMsgHasHead( self, msg ):
        "unpacking message"
#        self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        _head = struct.unpack( self.msgHead, msg[0:struct.calcsize( self.msgHead )] )
        if _head[1] == self.ccnvRepId or _head[1] == self.ccnvRepIniId:
            __MesID = struct.unpack( '!B', msg[struct.calcsize( self.msgHead )] )[0]
            self.logMes( 4, "receive ATP to CCNV Message!" )
#            print "receive ATP to CCNV Message!"
            return None
        else:
            __MesID = _head[1]
        
        return _head + self.unpackAppMsg( __MesID, msg[struct.calcsize( self.msgHead ):] )

    def deviceRun( self, *args, **kwargs ):
        "CCNV run"
        #logmsg
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        #DOIT
        #print "ccnv running..."
        _CCNV_Cycle = 1 # CCNV周期为100ms
        _Base_Time_Index = 0 #基础计数器
        while True:            
            #等待，获取消息    
            _msg = self.unpackAppMsgHasHead( self.inQ.get() )
            #print 'ccnv recv', _msg
            
            if None == _msg:
                continue
            
            #RS跑车消息处理
            if _msg[1] == self.ccnvDisMsgId:
                "Status_REPORT"
                #print "receiving RS running report"
#                更改_data中相应的值即可，无需pack
                self.logMes( 4, "Receiving RS running Message, MsgId = " + str( _msg[1] ) + \
                            " loophour = " + str( _msg[0] ) + \
                            " Block Coordinates_1 = " + str( _msg[3] ) + \
                            " Block Coordinates_2 = " + str( _msg[4] ) )
                #记录开始和结束时间
                self.__StartPos = _msg[3]
                self.__EndPos = _msg[4]
               
#                print self.getDataValue('NTPtime')
#                print self.getDataValue('SynchroDate')
#                print self.getDataValue('PSDplatformAoperation.ClosingOrder')
                
                #根据周期起始坐标和结束坐标计算RSspeed（(end-start)/0.1， 单位为毫米每秒）， 作为ccnv规则库中的条件
                _RSspeed = abs( ( _msg[4] - _msg[3] ) * 10 )  #取绝对值
                self.addDataKeyValue( 'RSspeed', _RSspeed )
                #print 'RSSpeed11:', self.getDataValue('RSspeed')
#               print self.getDataValue('RSspeed')
            
            #接收HMI消息
            if _msg[1] == self.HMI2ccnvId:
                print 'ccnv', _msg
                self.HMI2ccnvInfo = self.packAppMsgHasHead( self.getDataValue( 'loophour' ), \
                                                           self.ccnvReqId, \
                                                           *_msg[2:] )
            #初始化消息处理
            if _msg[1] == self.ccnvRepId or _msg[1] == self.ccnvRepIniId:
                if _msg[2] == 1:
                    "CCNV Initialization Report" 
                    self.logMes( 4, "Receiving CCNV Initialization Report Message, MsgId = " + str( _msg[1] ) + \
                                " loophour = " + str( _msg[0] ) + \
                                " CC_SSID = " + str( _msg[2] ) + \
                                " CC_Train_Type = " + str( _msg[3] ) + \
                                " CC_core_id = " + str( _msg[4] ) + \
                                " CC_Inner_IP_blue = " + str( _msg[5] ) + \
                                " CC_Inner_IP_red = " + str( _msg[6] ) + \
                                " CC_Outer_IP_blue = " + str( _msg[7] ) + \
                                " CC_Outer_IP_red = " + str( _msg[8] ) + \
                                " CC_DLU_IP_blue = " + str( _msg[9] ) + \
                                " CC_DLU_IP_red = " + str( _msg[10] ) )
    #                print "receiving CCNV Initialization Report"
                            
                #ATP运行状态消息处理
                if _msg[2] == 2:
                    "receiving ST_NO_VITAL_REPORT"
                    #在界面显示ATP运行状态
                    self.logMes( 4, "Receiving ATP running status Report, MsgId = " + str( _msg[1] ) + \
                                " loophour = " + str( _msg[0] ) )
    #                print "receing ATP running status report"
            
            #周期更新消息处理
            if _msg[1] == self.cycleMsgId:
                "周期更新, 结束运行消息"
                if _msg[2] == 92:
                    _Base_Time_Index += 1
                    #检测是否有改值    
                    setValues = self.scePrepro.getNormalChangeItem( [self.__StartPos, self.__EndPos], self.defScenario )
                    #print setValues
                    for setValue in setValues:
                        _typename = self.getVarDic()[setValue[0]][0]
                        self.addDataKeyValue( setValue[0], self.var_type[_typename]( setValue[1] ) )
                        self.logMes( 4, '--loophour:' + str( self.getDataValue( 'loophour' ) ) + '-----''change item:' + setValue[0] + setValue[1] )
    
                    setValues = self.scePrepro.getTimeChangeItem( _Base_Time_Index, self.TimeScenario )
                    #print setValues
                    for setValue in setValues:
                        _typename = self.getVarDic()[setValue[0]][0]
                        self.addDataKeyValue( setValue[0], self.var_type[_typename]( setValue[1] ) )  
                    
                    #"周期更新"
                    self.logMes( 4, "Receiving loophour Update Message, MsgId = " + str( _msg[1] ) + \
                                " loophour = " + str( _msg[0] ) )                    

                    #其余的则是在设备周期下进行
#                    if _Base_Time_Index % _CCNV_Cycle != 1:
#                        continue
                    #规则处理
                    self.checkRule()
                    #print self.getDataValue('loophour')
                    #print self.getDataValue('OdometerRef1SpeedUnderThreshold')  
                    if None == self.HMI2ccnvInfo:
                        #对发送的数据进行组合再发送
                        _NTPTime = -1 if 1 == self.getDataValue("NTPError") else int( time.time() ) + self.getDataValue( "DeltaNTPtimeToAtp" )
                        _msgSend = self.packAppMsgHasHead( self.getDataValue( 'loophour' ), \
                                                          self.ccnvReqId, \
                                                          self.getDataValue( 'SelectedFrontEnd' ) * 16 + \
                                                          self.getDataValue( 'OdometerRef1SpeedUnderThreshold' ) * 8 + \
                                                          self.getDataValue( 'OdometerRef1Available' ) * 4 + \
                                                          self.getDataValue( 'OdometerRef2SpeedUnderThreshold' ) * 2 + \
                                                          self.getDataValue( 'OdometerRef2Available' ), \
                                                          self.getDataValue( 'EmergencyBrakingNotRequestedToAtp' ) * 128 + \
                                                          self.getDataValue( 'VitalParkingBrakingNotRequested' ) * 64 + \
                                                          self.getDataValue( 'MasterCCcore' ) * 32 + \
                                                          self.getDataValue( 'RouteSetNotNeeded' ) * 16 + \
                                                          self.getDataValue( 'TrainInCorrectlyDockedZone' ) * 8 , \
                                                          self.getDataValue( 'PSDplatformAoperation.Id' ), \
                                                          self.getDataValue( 'PSDplatformBoperation.Id' ), \
                                                          self.getDataValue( 'PSDplatformAoperation.OpeningOrder' ) * 128 + \
                                                          self.getDataValue( 'PSDplatformBoperation.OpeningOrder' ) * 64 + \
                                                          self.getDataValue( 'PSDplatformAoperation.ClosingOrder' ) * 32 + \
                                                          self.getDataValue( 'PSDplatformBoperation.ClosingOrder' ) * 16, #+ \
#                                                          self.getDataValue( 'ATBselectedDrivingMode' ) * 16 + \
#                                                          self.getDataValue( 'ATBdrivingModeSetRequested' ) * 32 + \
#                                                          self.getDataValue( 'ATBdrivingModeUnsetRequested' ) * 64 + \
#                                                          self.getDataValue( 'RebootRequest' ) * 128, \
#                                                          self.getDataValue( 'loophour' ), \
                                                          #self.getDataValue( 'loophour' ), \
                                                          _NTPTime, \
                                                          self.getDataValue( 'VIOM1EnableOut' ), \
                                                          self.getDataValue( 'VIOM2EnableOut' ), \
                                                          self.getDataValue( 'VIOM3EnableOut' ), \
                                                          self.getDataValue( 'VIOM4EnableOut' ), \
                                                          self.getDataValue( 'NVID1' ), \
                                                          self.getDataValue( 'NVID2' ), \
                                                          self.getDataValue( 'NVID3' ), \
                                                          self.getDataValue( 'NVID4' ), \
                                                          self.getDataValue( 'NVID5' ), \
                                                          self.getDataValue( 'Cancel_signal' ) * 128 + \
                                                          self.getDataValue( 'Overlap_release' ) * 64 + \
                                                          self.getDataValue( 'Communicate_with_PSD' ) * 32,
                                                          self.getDataValue( "Variant_request_CBI_id[0]" ),
                                                          self.getDataValue( "Variant_request_CBI_id[1]" )           
                                                          )

                    else:
                        _msgSend = self.HMI2ccnvInfo
                    
                    #更新loophour
                    _loophour = self.getDataValue( 'loophour' )
                    _loophour += 1
                    self.addDataKeyValue( 'loophour', _loophour )
                    
                    if 0 == self.getDataValue( "ModifyNTPTimeEnable" ):#不能修改的时候通过本身的loophour自动更新NTPtime
                        self.addDataKeyValue( "NTPtimeToAtp", _loophour )
                        
#                    print self.getDataValue('loophour')

                    if 1 == self.getDataValue( 'SendMesENABLE' ):
                        self.getDataValue( 'siminQ' ).put( _msgSend )
                        #self.outQ.put( _msgSend )      
                                                          
                    #print "pack message", len(_msgSend), binascii.hexlify(_msgSend)
                    #print 'RSSpeed:', self.getDataValue('RSspeed')
                
#                elif _msg[2] == self.cycleIniloophour:#初始化loophour
#                    self.addDataKeyValue( 'loophour', 1 )
                        
                elif _msg[2] == 93:
                    "结束运行"
                    self.logMes( 4, "Receiving Ending Message, MsgId = " + str( _msg[1] ) + \
                                " loophour = " + str( _msg[0] ) )
                    break                                        
        print "end ccnv running..."
        
    def deviceEnd( self ):
        " ending device"
        self.__log.fileclose()
                                
if __name__ == '__main__': 
    ccnv = CCNV( 'ccnv', 20 )
    ccnv.deviceInit( varFile = r'./setting/ccnv_variant.xml', \
                    msgFile = r'./setting/ccnv_message.xml', \
                    scenario = r'./scenario/ccnv_scenario.xml', \
					rules = r'./scenario/ccnv_rules.xml', \
                    log = r'./log/ccnv.log' )
#    ccnv.deviceRun()
 
