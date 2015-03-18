#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     rs.py
# Description:  rs设备仿真     
# Author:       KunPeng Xiong
# Version:      0.0.1
# Created:      2011-07-21
# Company:      CASCO
# LastChange:   None
# History:
#               updata 2011-08-09
#               添加EB后是继续操作
#----------------------------------------------------------------------------
from base.loglog import LogLog
from base.basedevice import BaseDevice
from base.senariopreproccess import Senariopreproccess
from lxml import etree
import sys
import struct
from base import commlib
import binascii
import time
import math
import Queue
import datetime
from base import simdata

from Car import Car
from Loop import Loop
from GpsAndOdometer import GpsAndOdometer

class RS( BaseDevice ):
    """
    RS Simulator
    """
    #平台内部传递的消息，所带的消息头，loophour,msgId
    msgHead = '!IH'
    
    #路径信息
    blocklist = []
    direct = 1
    startlocus = []
    trainLen = 0
    cog_dir = None
    _item = None
    
    #脚本预处理
    Presenario = None
    
    #Simulator消息ID
    simulatorID = 99
    
    #手动停车
    manualStop = 80
    
    #自动运行
    autoRun = 81
    
    #更新齿数消息ID
    cycleCog = 90
    
    #周期更新消息ID
    cycleUpDataId = 92
    
    #初始化ID
    cycleStartID = 91
    
    #周期结束
    cycleEndID = 93
    
    #循环执行
    cycleRepeate = 95
    
    #loophour初始化命令
    cycleIniloophour = 94
    
    #checkrule开始
    checkruleflag = False
    
    #VIOM给RS的消息ID
    VIOMtoRSMesID = 5893
    
    #RSTOSDTS_CONTROL MSG ID
    RSTOSDTSMsgID = 300

    #RESETATP MSG ID
    RESETATPMsgID = 260
        
    #HMI发送给rs的消息id
    HMI2RSMesId = 51233
    
    
    __GPS1MsgId = 1001
    __GPS2MsgId = 1002
    __LOOPMsgId = 1003
    __LOOPMsgId1 = 1006
    __LOOPMsgId2 = 1007
    __LOOPMsgId3 = 1008
    __ODMMsgId = 1004
    
    #设置周期时间，ms
    looptime = 100.0   #修改为100ms
    
    loophour = None
    
    #跑车脚本信息
    trainRunScenario = []
    
    #相关标志位：
    #是否使用跑车脚本标志位
    #初始的时候默认为使用跑车脚本，当遇到紧急制动或者界面控制时，跑车脚本将失效
    USESenario = True 
    #紧急制动标志位，的那个出现紧急制动时将对此位置True
    Emergency_brake = False 
    #界面控制标志位，通过界面控制时将该位置True
    Interface_control = False
    #一般的制动
    Normal_brake = False
    
    #界面控制的加速度
    HMIaccel = None
    #log实例
    __log = None
    
    #EB后的启动命令:启动之后将以一定的加速度，到达目的位置
    Emergency_brake_after = False
    
    #EB后启动的第一个loophour
    EB_after_loophour = None
    
    #EB后的Route_locus
    EB_Route_locus = None
    
    #EB后车启动后的终点坐标
    EB_EndPos = None
    #EB后的加速度
    EBAfter_accel = 0.8   #m/s2
    #EA后的最大速度
    EBAfter_Maxspd = 6 #m/s
    #跑车变化点的信息：
    #[[time,position,speed,acceleration],...],time单位为ms,其余单位偶读为国际标准单位
    Route_locus = []
    
    #脚本读取时使用的信息
    nodePaths = {
                'expectspeed': '/speed/value',
                'EndPos': '/speed/EB',
                'viom_setting_in':'/VIOM_Settings/VIOM_IN/Item',
                'viom_setting_out':'/VIOM_Settings/VIOM_OUT/Item'
                }
    attributes = {
                'expectspeed': ['@type', '@coordinate', \
                                 '@accelerated', '@expectCoor', '@expectSpeed', '@dewelltime'],
                'EndPos': '@Endcoordinate',
                'viom_setting':['@Index', '@Name', '@VIOM']
                }
    var_type = {'int':int, 'string':str, 'float':float}
    
    #VIOM IN的变量名字列表
    VIOM_IN_Name = ['IN_ANCS1', 'IN_ANCS2', 'IN_ACS1', 'IN_ACS2', 'IN_BM1', 'IN_BM2', 'IN_CBTC1', 'IN_CBTC2', \
                    'IN_EDDNO1', 'IN_EDDNO2', 'IN_KSON1', 'IN_KSON2', 'IN_REV1', 'IN_REV2', \
                    'IN_RM_PB1', 'IN_RM_PB2', 'IN_RMF1', 'IN_RMF2', 'IN_TDCL1', 'IN_TDCL2', \
                    'IN_TI1', 'IN_TI2', 'IN_ZVBA11', 'IN_ZVBA21', 'IN_ZVBA12', 'IN_ZVBA22']
    
    #记录上周期的位置信息
    __RSLastPosState = None
    
    __bigCount = None#大周期数
    
    gps = None
    car = None
    loop = None
    __smallCount = None#小周期数
    
    __cogSmallNumberList = None#齿数列表 （50个小周期行车齿数）

    _SSAId = None
    
    _ssaTempId = None
    _count = None #小周期定时器
    
    _IdList = 0
    
    _continuousSSA = None
#    toHMIQ = None
    def __init__( self, name, id ):
        "init"
        self.__bigCount = 0
        self.car = Car('car')
        self.car.deviceInit()
        self.gps = GpsAndOdometer('Gps')
        self.gps.deviceInit()
        self.loop = Loop('loop')
        self.loop.deviceInit()
        BaseDevice.__init__( self, name, id )
        self.__smallCount = 0
        self._SSAId = 0
        self._ssaTempId = 0
        self._count = 0
        self._Id = 0
        self._continuousSSA = {}
        self._item = 0
        self.__cogSmallNumberList = []
        
        
    def logMes( self, level, mes ):
        " log mes"
        #LogLog.orderLogger(self.getDeviceName())
        self.__log.logMes( level, mes )
    
    def deviceInit( self, *args, **kwargs ):
        " RS init"
        #TODO 导入变量、应用消息、设备数据解析、控制脚本解析、离线数据计算等
        self.USESenario = True 
        self.Emergency_brake = False 
        self.Interface_control = False
        self.Emergency_brake_after = False
        self.__RSLastPosState = None
        
#        self.toHMIQ = Queue.Queue()
        
        self.clearDataDic()
        #print 'rs kwargs', kwargs
        self.importVarint( kwargs['varFile'] )
        self.importMsg( kwargs['msgFile'] )
        self.importDefSce( kwargs['scenario'] )   #获得跑车脚本信息
        self.importRuleDic( kwargs['rules'] )
        
        #初始化log
        #self.__log = LogLog(kwargs['logpath'], type(self).__name__, 'w')
        self.__log = LogLog()
        self.__log.orderLogger( kwargs['log'], type( self ).__name__ )
        
        #界面控制的加速度初始化
        self.HMIaccel = None
        #跑车依据初始化
        self.Interface_control = False
        self.EB_after_loophour = False
        self.Emergency_brake = False
        self.USESenario = True
        self.Normal_brake = False 
        #获得运行路径信息
        self.blocklist = simdata.TrainRoute.getBlockinfolist()
        self.startlocus = simdata.TrainRoute.getStartBlockAbs()
        self.direct = simdata.TrainRoute.getRouteDirection()
        self.trainLen = simdata.TrainRoute.getTrainLength()
        self.cog_dir = simdata.TrainRoute.getCogDirection()
                             
        self.addDataKeyValue( 'cog_direction', self.cog_dir )
        
        #对跑车脚本的进行预处理
        self.importexpectspeed( kwargs['expectSpeed'] )
        self.Presenario = Senariopreproccess()
        #self.Presenario.getblockinfolist(kwargs['track_map'], kwargs['track_maptxt'])
        self.defScenario = self.Presenario.getsortedscenario( self.defScenario, self.direct )
        
#        print 'rs dic', self.getVarDic()
#        print 'rs msg', self.getMsgDic()
#        print 'rs self.defScenario:', self.defScenario
#        print 'rs expectSpeed', self.trainRunScenario
        
        #对跑车脚本进行计算，获得跑车的加速度变化节点
        self.getRoutelocus()
        
        if None == self.Route_locus:
            return False        
        
        #将初始的跑车位置信息给__data的相关变量,可能需要添加
        
        
        #初始化loophour为1
        self.loophour = 1
        self.addDataKeyValue( 'loophour', self.loophour )
        #读取VIOM配置信息
        self.importVIOMSetting( kwargs['viom_setting'] )
        
        self._IdList = GpsAndOdometer._IdAndSSA[0]
        self._continuousSSA = GpsAndOdometer._continuousSSA
        
#         self._IdList = self.gps.getSSAAndId()[0]
#         self._continuousSSA = self.gps.getContinuousSSA()
        print '----------rs _IdList------------',self._IdList
        print '----------------rs device init OK-------------------',self._continuousSSA
        return True
    
    def reInitial(self):
        self._IdList = GpsAndOdometer._IdAndSSA[0]
        self._continuousSSA = GpsAndOdometer._continuousSSA
#         self._IdList = self.gps.getSSAAndId()[0]
#         self._continuousSSA = self.gps.getContinuousSSA()
        print '----------reinitial rs _IdList------------',self._IdList
        print '----------------reinitial rs device init OK-------------------',self._continuousSSA
    
    #在setMsgValue中添加value
    def packGPS2Msg(self,loophour,msgId,*args):
        "packing GPS2 message"
#         self.addDataKeyValue('UTCTime', args[0])
#         self.addDataKeyValue('Latitude', args[1])
#         self.addDataKeyValue('Lat_Hemi', args[2])
#         self.addDataKeyValue('Longitude', args[3])
#         self.addDataKeyValue('Long_Hemi', args[4])
       
        _Mes = self.packAppMsg(msgId,',',args[0],',','A',',',args[1],',',args[2],',',args[3],',',args[4],',','100',\
                               ',','200',',',args[5],',','35',',','E*56\r\n')
        
        _head = struct.pack( self.msgHead, loophour, msgId)
#         _head = '$GPRMC'

        return _head + _Mes
   
    #在setMsgValue中添加value 
    def packGPS1Msg(self,loophour,msgId,*args):
        "packing GPS1 message"
       
#         self.addDataKeyValue('', r"$GPGGA")
#         self.addDataKeyValue('UTCTime', args[0])
#         self.addDataKeyValue('Latitude', args[1])
#         self.addDataKeyValue('Lat_Hemi', args[2])
#         self.addDataKeyValue('Longitude', args[3])
#         self.addDataKeyValue('Long_Hemi', args[4])
       
        _Mes = self.packAppMsg(msgId,',',args[0],',',args[1],',',args[2],',',args[3],',',args[4],',','2',\
                               ',','08',',','1.2',',','10',',','M',',','-29.6',',','M',',','1.3',\
                               ',','0333*5F\r\n')
        
        _head = struct.pack( self.msgHead, loophour, msgId )
#         _head = '$GPGGA'
        return _head + _Mes
    
    #send loop 0x80
    def packLOOPMsg(self,loophour,msgId, *args ):
        "packing LOOP message"
#         self.addDataKeyValue('IsOver_Loop', args[0])
#         self.addDataKeyValue('Lastloop_Nr', args[1])
#         self.addDataKeyValue('LoopZone_Nr', args[2])
#         self.addDataKeyValue('Series_Nr', args[3])
        
        #CRC check
        _CalcCRC=0x01^0x80^args[0]^args[1]^args[2]^args[3]
#         print "LOOP crc is:",_CalcCRC
        
        _Mes = self.packAppMsg(msgId,args[0],args[1],args[2],args[3],args[4],args[5],args[6],args[7],_CalcCRC,0x03)    
        _head = struct.pack( self.msgHead, loophour, msgId )
        return _head + _Mes
    
    def packODMMsg(self,loophour,msgId,*args):
        "packing ODM message"
        _Mes=[]  
        _temp = [0,0]   
        #add struct
        array50=args[0]
#         print'-----arrat[50]----',len(array50)
#         fmt1 = '!H'
#         for i in range(50):
#             _mes_in1 = struct.pack(fmt1,array50[i][0])
#             _mes_in2 = struct.pack(fmt1,array50[i][1])
#             _temp[0] = _mes_in1
#             _temp[1] = _mes_in2
#             _Mes.append(_temp)
            
        _tmp = ''
        for _d in array50:
            _tmp += struct.pack('!2H', *_d)
#         for i in range(0,49):
#             _Mes+=struct.pack('!HH',array50[i][0],array50[i][1])
#         print '3----------------------------',repr(_tmp),type(_tmp)
 
#         _Mes = self.packAppMsg(msgId,_Mes)
        _head = struct.pack( self.msgHead, loophour, msgId)
        _tail = struct.pack('!B',0xe7)
        return _head  + _tmp + _tail
    
      
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
        return _head + self.unpackAppMsg( _head[1], msg[struct.calcsize( self.msgHead ):] )

    def deviceRun( self, *args, **kwargs ):
        "RS run"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        self._Numofvitalviomflag = 0 #记录获得的viom包的个数，要收到两包viomvital的时候才进行处理
        while True:
            #获得消息，无消息是阻塞
            _msg = self.unpackAppMsgHasHead( self.inQ.get())
            #周期更新消息
            if _msg[1] == self.simulatorID:
#                 self.__bigCount += 1
#                 self.gps.CreateGpsAccordingSingularMap(self.__bigCount,3)

                if self.autoRun == _msg[2] or self.cycleCog == _msg[2]:
                    _time = datetime.datetime.now()
#                     print '-----------calculate cog---------',_time
#                     self.__smallCount += 1
#                     self.__cogSmallNumberList = self.car.getCurrentComprehensiveInfoPer10ms(self.__smallCount)
#                     if self.car.getStopFlag() == True:
                    if Car._carStop == True:
                        self._count += 1
                        self.__cogSmallNumberList = self.car.getCogListWhenStop()
                        print '------------rs auto stop---------------'
                        if Car._mode == 'auto':
                            if self._count == Car._stop_time/Car._sTimer:
                                Car._carBrack = False
                                self.car.setStopFlag(False)
                                Car._carStop = False
                                self.car.setAcelPositiveFlag(True)
                                print '--------self.getSSAList-----',self.gps.getSSAList()
                                if self._SSAId != len(self._IdList) - 1:#self._IdList [24, 25, 31, 35, 37, 42, 44]
                                    self._SSAId += 1
                                self.__smallCount = 0
                                self._count =0
                                print '--------self._SSAId-----',self._SSAId
                            
                        elif Car._mode == 'manual':
                            if Car._carBrack == True:
                                Car._carBrack = False
                                self.car.setStopFlag(False)
                                Car._carStop = False
                                self.car.setAcelPositiveFlag(True)
                                print '--------self.getSSAList-----',self.gps.getSSAList()
                                if self._SSAId != len(self._IdList) - 1:#self._IdList [24, 25, 31, 35, 37, 42, 44]
                                    self._SSAId += 1
                                self.__smallCount = 0
                                self._count =0
                                print '--------self._SSAId-----',self._SSAId
                            pass
                    else:
                        self.__smallCount += 1
#                         _id = self.car.getSSAList()[self._SSAId + 1]
                        _id = self._IdList[self._SSAId + 1]
                        self._ssaTempId  = _id
                        self.__cogSmallNumberList = self.car.StopRunningStatus(self.__smallCount,self._continuousSSA[_id][0][1],False)
#                         self.__cogSmallNumberList = self.car.StopRunningStatus(self.__smallCount,3059.8,False)
                elif self.manualStop == _msg[2]:
                    _time = datetime.datetime.now()
#                     if self.car.getStopFlag() == True:
                    if Car._carStop == True:
                        self._count += 1
                        self.__cogSmallNumberList = self.car.getCogListWhenStop()
                        print '------------rs manual stop---------------'
                        if Car._manualStart == True:
                            print '--------rs start button pressed------'
                            self.car.setStopFlag(False)
                            Car._carStop = False
                            Car._manualStop = False
                            self.car.setAcelPositiveFlag(True)
                            self.__smallCount = 0
                            self._count =0
                            pass
                    else:
                        self.__smallCount += 1
#                         _id = self.car.getSSAList()[self._SSAId + 1]
                        _id = self._IdList[self._SSAId + 1]
                        self._ssaTempId  = _id
#                         self.__cogSmallNumberList = self.car.getCurrentComprehensiveInfoPer20ms(self.__smallCount,self._continuousSSA[_id][0][1])
                        self.__cogSmallNumberList = self.car.StopRunningStatus(self.__smallCount,self._continuousSSA[_id][0][1],True)
                    pass
                if self.cycleUpDataId == _msg[2] or self.cycleStartID == _msg[2]:
#                     if self.car.getStopFlag() != True:
#                         self.__bigCount += 1
                    self.car.setCurrentMileage(self.car._currentSmallMileage)
                    print '-cog number-',self.__cogSmallNumberList #每个100ms一个周期 获取齿数列表 获取完了清空列表 准备下一个周期获取
                    print '---length---',len(self.__cogSmallNumberList)
                    _amountMile = self.car.getAmountMile()
                    print '-------------------------------Current speed------------------------->>>',self.car.getCurrentV()
                    print '-------------------------------Amount mileage------------------------>>>',_amountMile
                    print '-------------------------------Stop running area--------------------->>>',self._continuousSSA[self._ssaTempId][0][1]
#                     print '-------------------------------Stop running area--------------------->>>',3059.8
#                     print self.__cogSmallNumberList
                    
                    self.logMes( 4, '--loophour--%d' % ( self.loophour ) )
#                     print '--loophour--%d'% ( self.loophour ), _msg
#                     print '-------------------------------------------gps----------------------------->'
                    _time = datetime.datetime.now()
#                     print '<==========current time is ======>',_time
                    _gps = self.gps.CreateGpsAccordingSingularMap(_amountMile,3)
#                     print "=======gps=======",_gps
                      
                    #获取本周期需要改变的变量列表
                    _position = [int( round( self.getDataValue( 'coordinates_1' ) ) ), int( round( self.getDataValue( 'coordinates_2' ) ) )]
                    _change_Item = self.Presenario.getNormalChangeItem( _position, self.defScenario )
                    #print 'rs self.defScenario:', self.defScenario
                    #根据changeItem去改变相关的值
                    _VIOM_change = False
                    #print 'rs self.getVarDic():', self.getVarDic()
                    for _item in _change_Item:
                        _typename = self.getVarDic()[_item[0]][0]
                        self.addDataKeyValue( _item[0], self.var_type[_typename]( _item[1] ) )
                        if _item[0] in self.VIOM_IN_Name:
                            _VIOM_change = True
                       
                    #获取根据loophour修改的值：
                    _Time_change_Item = self.Presenario.getTimeChangeItem( self.loophour, self.TimeScenario )
                    for _item in _Time_change_Item:
                        _typename = self.getVarDic()[_item[0]][0]
                        self.addDataKeyValue( _item[0], self.var_type[_typename]( _item[1] ) )
                        if _item[0] in self.VIOM_IN_Name:
                            _VIOM_change = True
                       
                    #更新self.__RSLastPosState
                    self.__RSLastPosState = []
                    self.__RSLastPosState.append( self.getDataValue( 'coordinates_1' ) )
                    self.__RSLastPosState.append( self.getDataValue( 'coordinates_2' ) )
                    #send GPS1,GPS2,ODM
                    _Sendmsg = self.packGPS1Msg( self.loophour, self.__GPS1MsgId, _gps[0],_gps[1],_gps[2],_gps[3],_gps[4])
#                     _Sendmsg = self.packGPS1Msg( self.loophour, self.__GPS1MsgId, 1,2,1,1,2)
#                     print '------_send msg gps1----------',_Sendmsg
                    self.getDataValue( "siminQ" ).put( _Sendmsg )
#                     print '------------GPS1------',repr(_Sendmsg)

                    _time = time.strftime("%Y%m%d")[2:]
                    _Sendmsg = self.packGPS2Msg( self.loophour, self.__GPS2MsgId, _gps[0],_gps[1],\
                                                 _gps[2],_gps[3],_gps[4],_time)
                    self.getDataValue( "siminQ" ).put(_Sendmsg)  
#                     print '-----------GPS2------',repr(_Sendmsg)        
#                     
                    _Sendmsg = self.packODMMsg( self.loophour, self.__ODMMsgId, self.__cogSmallNumberList)
                    self.getDataValue( "siminQ" ).put( _Sendmsg )
#                     print '-----------ODM------',repr(_Sendmsg) 
                      
                    self.car.reSetCogSmallNumberList()
                      
                    #更新loophour     
                    self.loophour += 1
                    self.addDataKeyValue( 'loophour', self.loophour )
                    #self.logMes(4, "end time %f" % (time.time()))
                
                elif self.cycleRepeate == _msg[2]:
                    self.loophour = 0
                    self.__smallCount = 0
                    self.__bigCount = 0
                    self._SSAId = 0
                    self.car.reInit()
                    _idList = GpsAndOdometer._lineList
                    print '------repeat--------',_idList
                    if self._item != len(_idList) and len(_idList) != 1:
                        self._item += 1
                        self.gps.ReInitVariant(self._item)
                        self.loop.ReInitVariant(self._item)
                    elif self._item == len(_idList) - 1:
                        self._item = 0 #循环执行
                        self.gps.ReInitVariant(self._item)
                        self.loop.ReInitVariant(self._item)
                    else:#循环执行
                        self._item = 0
                        self.gps.ReInitVariant(self._item)
                        self.loop.ReInitVariant(self._item)
                        pass
                    self.gps.reSetData()
                    self.gps.reSetFirstGPSLength()
                    self.reInitial()
#                     self._IdList = self.gps.getSSAAndId()[0]
#                     self._continuousSSA = self.gps.getContinuousSSA()
                    print '-------------clcleRepeate-----------------'
                    pass
                
                elif self.cycleIniloophour == _msg[2]:
                    self.loophour = 1
                    self.addDataKeyValue( 'loophour', self.loophour )
                         
                elif self.cycleEndID == _msg[2]:
                    self.logMes( 4, 'RS END' )
                    self.outQ.put( "END Case" ) #发送结束用例消息
                    break
 
            elif self.__LOOPMsgId1== _msg[1] :
                #判断是否有环线 且 LN VN一致 add
#                 print '==============LN VN============='
#                 _Sendmsg = self.packLOOPMsg( self.loophour, self.__LOOPMsgId, 1,2,1,1,0,0,0,0)#add loop
                _Flag = 0
                _Id = 0
                _flagAndId = [0,0]
                _flagAndId = self.loop.judgeLoopInWhatRange(self.car.getAmountMile(), 5)
                _Flag = _flagAndId[0]
                _Id = _flagAndId[1]
                _Sendmsg = self.packLOOPMsg( self.loophour, self.__LOOPMsgId, _Flag,_Id,1,1,0,0,0,0)#add loop
                self.getDataValue( "siminQ" ).put( _Sendmsg )
                print '==============LN VN============='
                #更新loophour     
                self.loophour += 1
                self.addDataKeyValue( 'loophour', self.loophour )
                pass
                #self.logMes(4, "end time %f" % (time.time())) 

        print "RS Running End."
    
    def sendLoop(self,_cycleId,_error):
        _Flag = 0
        _Id = 0
        _flagAndId = [0,0]
        _flagAndId = self.loop.judgeLoopInWhatRange(_cycleId, _error)
        _Flag = _flagAndId[0]
        _Id = _flagAndId[1]
        _Sendmsg = self.packLOOPMsg( self.loophour, self.__LOOPMsgId, _Flag,_Id,1,1,0,0,0,0)#add loop
        self.getDataValue( "siminQ" ).put( _Sendmsg )
        print '==============LN VN============='
        #更新loophour
        self.loophour += 1
        self.addDataKeyValue( 'loophour', self.loophour )
        pass
    
    #-----------------------------------------------------------------------------
    #@紧急制动后的运行路线，到达目的地
    #@其中加速度为0.8，最大速度为6.0m/s
    #-----------------------------------------------------------------------------
    def getaccelstatusafterEB( self ):
        "get status after EB"
        self.logMes( 4, 'RS' + '.' + sys._getframe().f_code.co_name )
        return self.getaccelstatusFromRoute( self.EB_Route_locus )
        
    #---------------------------------------------------------------------------------
    #@紧急制动情况下的位置计算
    #@注：紧急制动情况下，加速度为-1，直至车的速度为0
    #返回拐点类型：0：无拐点，1有拐点
    #---------------------------------------------------------------------------------
    def getaccelstatusinEB( self ):
        "获取紧急停车情况下的位置和状态信息"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        #获取紧急制动加速度
        _EBaccel = float( self.getDataValue( 'EB_accel' ) )   #m/s2
        
        if _EBaccel >= 0:
            self.logMes( 4, 'Error EB_accel!!!!' )
            return None

        #_type = None
        _startSpd = self.getDataValue( 'End_Speed' )     #上周期结束时的速度
    
        return self.calAccel_InBrake( _EBaccel, _startSpd )  
    #-----------------------------------------------------------------
    #@处理刹车情况时的车状态
    #@输入：
    #@accel:刹车的加速度为负值，表示速度的绝对值减小
    #@speed:当前速度为有符号数:正数表示速度方向为正，负数表示速度方向为负
    #@返回值，类型type：0无拐点，1有拐点
    #-----------------------------------------------------------------
    def calAccel_InBrake( self, accel, speed ):
        "calculate accel in brake situation."
        #获取上周期结束时的位置和速度
        _stratPos = self.getDataValue( 'coordinates_2' ) / 1000.0 #上周期的终点做为本周期的起点m
        _startSpd = speed     #上周期结束时的速度
        spd_dir = 1 if speed >= 0 else -1 #取速度方向
        _time = self.looptime / 1000.0
        
        if abs( _startSpd ) <= 0.000001: #停止不动
            self.writeData_WithoutSP( _stratPos,
                                     _stratPos,
                                     _startSpd,
                                     0,
                                     0 )
#            self.addDataKeyValue('coordinates_1', _stratPos * 1000) #转换为毫米
#            self.addDataKeyValue('coordinates_2', _stratPos * 1000) #转换为毫米
#            self.addDataKeyValue('CBK_coordinates', _stratPos) #单位m
#            self.addDataKeyValue('CBK_acceleration', 0) #单位m/s2
#            self.addDataKeyValue('CBK_speed', _startSpd) #单位m/s
#            self.addDataKeyValue('Start_Speed', _startSpd) #单位m/s
#            self.addDataKeyValue('End_Speed', 0) #单位m/s
            #无拐点
            return 0
        
        _accel = spd_dir * accel #加速度取反
        
        if spd_dir * ( _startSpd + _time * _accel ) >= 0:#尚未减速到0
            _endPos = _stratPos + _startSpd * _time + _accel * _time * _time / 2.0 
            _endSpd = _startSpd + _time * _accel
            
            self.writeData_WithoutSP( _stratPos,
                                     _endPos,
                                     _startSpd,
                                     _accel,
                                     _endSpd )
#            self.addDataKeyValue('coordinates_1', _stratPos * 1000) #转换为毫米
#            self.addDataKeyValue('coordinates_2', _endPos * 1000) #转换为毫米
#            self.addDataKeyValue('CBK_coordinates', _stratPos) #单位m
#            self.addDataKeyValue('CBK_acceleration', _accel) #单位m/s2
#            self.addDataKeyValue('CBK_speed', _startSpd) #单位m/s
#            self.addDataKeyValue('Start_Speed', _startSpd) #单位m/s
#            self.addDataKeyValue('End_Speed', _endSpd) #单位m/s   
            
            #无拐点
            return 0
                     
        else: #本周期可以减速到0以下
            _change_time = ( 0 - _startSpd ) / _accel  
            _endPos = _stratPos + _startSpd * _time + _accel * _change_time * _change_time / 2.0
            
            self.writeData_WithSP( _stratPos,
                                  _endPos,
                                  _startSpd,
                                  _accel,
                                  0,
                                  _change_time,
                                  0 )     
#            self.addDataKeyValue('coordinates_1', _stratPos * 1000) #转换为毫米
#            self.addDataKeyValue('coordinates_2', _endPos * 1000) #转换为毫米
#            self.addDataKeyValue('CBK_coordinates_1', _stratPos) #单位m
#            self.addDataKeyValue('CBK_coordinates_2', _endPos) #单位m
#            self.addDataKeyValue('CBK_speed_1', _startSpd) #单位m/s                
#            self.addDataKeyValue('CBK_acceleration_1', _accel) #单位m/s2
#            self.addDataKeyValue('CBK_acceleration_2', 0)  #单位m/s2 
#            self.addDataKeyValue('CBK_time', int(_change_time * 1000.0)) #单位ms
#            self.addDataKeyValue('Start_Speed', _startSpd) #单位m/s
#            self.addDataKeyValue('End_Speed', 0) #单位m/s
        
            #有拐点
            return 1
    
    #---------------------------------------------------------------------------------
    #@通过界面获得的加速度参数来计算跑车信息
    #@输入：_accel:界面获取的加速度信息，单位m/s2
    #返回:有、无拐点信息，这里我们假设界面设置的，都无拐点
    #---------------------------------------------------------------------------------
    def getaccelstatusinInerface( self, _accel ):
        "从界面获取的设置信息计算跑车信息"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        _startPos = self.getDataValue( 'coordinates_2' ) / 1000.0 #上周期的终点做为本周期的起点m
        _startSpd = self.getDataValue( 'End_Speed' )     #上周期结束时的速度
        _time = self.looptime / 1000.0   #s
        _endPos = _startPos + _startSpd * _time + _accel * _time * _time / 2.0
        _endSpd = _startSpd + _accel * _time
        self.writeData_WithoutSP( _startPos,
                                 _endPos,
                                 _startSpd,
                                 _accel,
                                 _endSpd )
#        self.addDataKeyValue('coordinates_1', _startPos * 1000) #转换为毫米
#        self.addDataKeyValue('coordinates_2', _endPos * 1000) #转换为毫米
#        self.addDataKeyValue('CBK_coordinates', _startPos) #单位m
#        self.addDataKeyValue('CBK_acceleration', _accel) #单位m/s2
#        self.addDataKeyValue('CBK_speed', _startSpd) #单位m/s
#        self.addDataKeyValue('Start_Speed', _startSpd) #单位m/s
#        self.addDataKeyValue('End_Speed', _endSpd) #单位m/s        
        
        return 0 #无拐点  
    
    
    
    #---------------------------------------------------------------------------------
    #@读取RS与VIOM接口的配置文件以获知VIOM码位的与变量的对应关系
    #@读取的数据将存入字典data中：
    #key：'VIOM_IN_Setting','VIOM_OUT_Setting'
    #@内容'VIOM_IN_Setting'：{'Name':Index,...}
    #@输入VIOMSettingfile，xml文件路径
    #---------------------------------------------------------------------------------
    def importVIOMSetting( self, VIOMSettingfile ):
        "载入VIOM接口配置信息"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        tree = etree.parse( VIOMSettingfile )
        #先读取VIOMIN的相关配置
        r = tree.xpath( self.nodePaths['viom_setting_in'] )
        #print r
        _dic_in = {}
        for node in r:  
            _para_name = node.xpath( self.attributes['viom_setting'][1] )[0]
            _para_index = int( node.xpath( self.attributes['viom_setting'][0] )[0] )
            _para_VIOM = int( node.xpath( self.attributes['viom_setting'][2] )[0] )
            _dic_in[_para_name] = [_para_index, _para_VIOM]
        
        #读取VIOMOUT的相关配置
        r = tree.xpath( self.nodePaths['viom_setting_out'] )
        _dic_out = {}
        for node in r:  
            _para_name = node.xpath( self.attributes['viom_setting'][1] )[0]
            _para_index = int( node.xpath( self.attributes['viom_setting'][0] )[0] )
            _para_VIOM = int( node.xpath( self.attributes['viom_setting'][2] )[0] )
            _dic_out[_para_name] = [_para_index, _para_VIOM]
        
        #将结果添加到__data中
        self.addDataKeyValue( 'VIOM_IN_Setting', _dic_in )
        self.addDataKeyValue( 'VIOM_OUT_Setting', _dic_out )
        #print _dic_in
        #print _dic_out
    
    #----------------------------------------------------------------------------
    #@根据VIOMIN的各个变量的值结合存放的位置，将其组成一个32字节的列表
    #VIOM1的状态放在前面，VIOM2的状态放在后面,最终放入__data的VIOM_IN中
    #----------------------------------------------------------------------------
    def getVIOM_IN( self ):
        "获取VIOM_IN数据"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        _Indexinfo = self.getDataValue( 'VIOM_IN_Setting' )   #获取index列表{name:[index,viom],...}

        #初始化列表
        _tmp = [0] * 128
        for _key in _Indexinfo:
            if _Indexinfo[_key][0] >= 0: #有效的 index
#                if _Indexinfo[_key][0] <= 7:
#                    _index = 7 - _Indexinfo[_key][0]
#                else:
#                    _index = 8 + (7 - (_Indexinfo[_key][0] - 8))
                
                _tmp[_Indexinfo[_key][0] + 64 * _Indexinfo[_key][1]] = self.getDataValue( _key )
            
        ##将_tmp放入__data
        self.addDataKeyValue( 'VIOM_IN', _tmp )
    
    
    #-----------------------------------------------------------------------------
    #@从20个元素的列表(或元组)VIOM输出中获取相关变量信息，并出入对应的__data数据中
    #-----------------------------------------------------------------------------
    def getInfofromVIOM_Out( self, _VIOM_OUT, _subtype ):
        "从_VIOM_OUT数据中获取相关变量"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        _Indexinfo = self.getDataValue( 'VIOM_OUT_Setting' ) #获取index列表{name:[index,viom],...}
        
        if 18 == _subtype:
            for _key in _Indexinfo:
                if 0 == _Indexinfo[_key][1]: #viom1
                    if _Indexinfo[_key][0] >= 0: #有效的 index
                        self.addDataKeyValue( _key, _VIOM_OUT[_Indexinfo[_key][0]] )
            #vital包加1
            self._Numofvitalviomflag += 1
            #将输入存入__data中
            self.addDataKeyValue( 'VIOM_Vital_OUT1', _VIOM_OUT ) 

        elif 19 == _subtype:
            for _key in _Indexinfo:
                if 1 == _Indexinfo[_key][1]: #viom2
                    if _Indexinfo[_key][0] >= 0: #有效的 index
                        self.addDataKeyValue( _key, _VIOM_OUT[_Indexinfo[_key][0]] )
            #vital包加1
            self._Numofvitalviomflag += 1
            #将输入存入__data中
            self.addDataKeyValue( 'VIOM_Vital_OUT2', _VIOM_OUT )
                
        
        if 2 == self._Numofvitalviomflag:
            self._Numofvitalviomflag = 0

    
    #---------------------------------------------------------------------------------
    #@根据loophour计算本周期发送给CBK的拐点相关信息
    #@这里需要用到全局变量Route_locus：[[time,position,speed,acceleration],...]
    #@函数将改变的值存入到__data中，主要包括拐点信息以及起始和结束位置信息
    #@返回拐点类型：0,：无拐点，1：有拐点,错误返回None
    #---------------------------------------------------------------------------------
    def getcuraccelstatus( self ):
        "获取当前的100ms区间的加速度信息"
        self.logMes( 4, 'RS' + '.' + sys._getframe().f_code.co_name )
        return self.getaccelstatusFromRoute( self.Route_locus )            
        

    #---------------------------------------------------------------------------------
    #@读取跑车脚本信息并存放在变量trainRunScenario中
    #@para：filePath，跑车脚本的存放路径
    #@returns
    #---------------------------------------------------------------------------------            
    def importexpectspeed( self, speedfile ):
        "载入跑车脚本信息"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        self.trainRunScenario = []
        tree = etree.parse( speedfile )
        r = tree.xpath( self.nodePaths['expectspeed'] )
        #print r
        for node in r:   
            _list = []
            for p in self.attributes['expectspeed']:  
                #print p
                _para = node.xpath( p )                   
                if _para != []:
                    if p == '@type':
                        _list.append( int( _para[0] ) )                        
                    else:
                        _list.append( float( _para[0] ) )
            self.trainRunScenario.append( _list )  
        #载入EB后的目标位置
        if len( tree.xpath( self.nodePaths['EndPos'] ) ) > 0: 
            self.EB_EndPos = int( 1000.0 * float( tree.xpath( self.nodePaths['EndPos'] )[0].xpath( self.attributes['EndPos'] )[0] ) )
        else:
            self.EB_EndPos = None
    #------------------------------------------------------------------------
    #@获取EB后的EB_Route_locus，若位置大于目的位置则报错，且设置EB_Route_locus为None
    #@时间是以ms为单位，距离m，速度m/s，加速度m/s2
    #其中时间为相对于
    #------------------------------------------------------------------------ 
    def getEBRoutelocus( self ):
        "get Route locus after EB"
        if None == self.EB_EndPos:  #无该脚本设置
            self.EB_Route_locus = None
            return
        _startcoordination = self.getDataValue( 'coordinates_2' )
        _endcoordination = self.EB_EndPos
        _Maxspd = self.EBAfter_Maxspd
        _accel = self.EBAfter_accel
        self.EB_Route_locus = []
        _starttime = ( self.EB_after_loophour - 1 ) * self.looptime
        
        if _startcoordination > _endcoordination:
            print "End coordination should be lager than ", _startcoordination
            self.logMes( 4, "End coordination should be lager than " + str( _startcoordination ) )
            self.EB_Route_locus = None
            return  
        
        #判断是否中间有匀速过程   
        _detadis = _Maxspd * _Maxspd / _accel
        if _detadis < ( _endcoordination - _startcoordination ): #包含匀速环节
            #第一阶段，加速过程
            _locus = [_starttime, _startcoordination / 1000.0, 0, _accel]
            self.EB_Route_locus.append( _locus )
            #第二阶段，匀速过程
            _detatime = _starttime + 1000.0 * _Maxspd / _accel
            _coordination = _startcoordination / 1000.0 + _Maxspd * _Maxspd / _accel / 2.0
            
            _locus = [_detatime, _coordination , _Maxspd, 0]
            
            self.EB_Route_locus.append( _locus )
            #第三阶段，减速过程
            _detatime = _detatime + \
                        ( _endcoordination - _startcoordination - _detadis * 1000.0 ) / _Maxspd
            
            _coordination = _endcoordination / 1000.0 - _Maxspd * _Maxspd / _accel / 2.0
             
            _locus = [_detatime, _coordination, _Maxspd, -1 * _accel]
            
            self.EB_Route_locus.append( _locus )
            #第四阶段，停止
            _detatime = _detatime + 1000.0 * _Maxspd / _accel
            _locus = [_detatime, _endcoordination / 1000.0, 0, 0]
            self.EB_Route_locus.append( _locus )
            
        else: #没有匀速阶段
            _detatime = 1000.0 * math.sqrt( ( _endcoordination - _startcoordination ) / _accel / 2000.0 )
            #第一阶段，加速
            _locus = [_starttime, _startcoordination / 1000.0, 0, _accel]
            self.EB_Route_locus.append( _locus )
            #第二阶段,减速
            _coord = _startcoordination / 1000.0 + _accel * _accel * _detatime / 2000.0
            _locus = [_starttime + _detatime, _coord, _accel * _detatime / 1000.0, -1 * _accel]
            self.EB_Route_locus.append( _locus )
            #第三阶段，停止
            _locus = [_starttime + 2 * _detatime, _endcoordination / 1000.0, 0, 0]
            self.EB_Route_locus.append( _locus )
            
    #----------------------------------------------------------------------------------
    #@根据跑车脚本trainRunScenario信息获取本次跑车信息中的加速度改变时的位置速度加速度信息
    #@并存入Route_locus全局变量中，变量格式[[time,position,speed,acceleration],...]
    #@注:这里的时间是以ms为单位，距离m，速度m/s，加速度m/s2
    #----------------------------------------------------------------------------------          
    def getRoutelocus( self ):
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        #初始化当前的位置、速度、加速度为0，时间也从0开始        
        
        #以后这些值应该作为输入参数输入进来
        _cur_coor = 0
        _cur_speed = 0
        _cur_accel = 0
        _cur_time = 0       #ms
        _tmplocus = []      #用于存放临时数据
        self.Route_locus = []

        #读取trainRunScenario计算Route_locus
        for _scen in self.trainRunScenario:
            #print _scen
            #print self.Route_locus
            if 1 == _scen[0]:  #类型1[type,start,end,endspeed,dewelltime]:距离单位m，时间单位100ms        
                _status = self.calRouteLocus_InCoorType( _scen,
                                                        self.Route_locus,
                                                        [_cur_time, _cur_coor, _cur_speed, _cur_accel] )
                
                if None == _status:
                    self.Route_locus = None
                    break
                else:
                    [_cur_time, _cur_coor, _cur_speed, _cur_accel] = _status
                    
            elif 0 == _scen[0]: #类型0[type,startpos,accel,endspeed]:距离单位m，时间单位100ms
                _status = self.calRouteLocus_InAccelType( _scen,
                                                         self.Route_locus,
                                                         [_cur_time, _cur_coor, _cur_speed, _cur_accel] )
                
                if None == _status:
                    self.Route_locus = None
                    break
                else:
                    [_cur_time, _cur_coor, _cur_speed, _cur_accel] = _status
                    
            else:#数据错误
                self.logMes( 4, 'ERROR: Wrong rs_expectSpeed.xml' )
                print "wrong type!"
                self.Route_locus = None
                break
                         
        #添加最后一段匀速过程
        if self.Route_locus == None:
            return
        if 0 == _scen[0] or 1 == _scen[0]:#类型0或1
            _tmplocus = [_cur_time, _cur_coor, _cur_speed, 0]
            self.Route_locus.append( _tmplocus )
        else:
            self.logMes( 4, 'ERROR: Wrong rs_expectSpeed.xml' )
            print 'wrong type!'
            self.Route_locus = None   

    #-----------------------------------------------------------------
    #@计算跑车脚本形式为1时的locus,并添加到Route_loucs
    #@输入：
    #@info:类型1节点信息格式为:[type,start,end,endspeed,dwelltime]
    #@Route_locus:需要添加节点的Route_locus:[[time,position,speed,acceleration],...]
    #@cur_status:当前车的状态，[time,pos,speed,accel]，time的单位为毫秒，是其余为国际标准单位
    #@返回计算后的当前车状态，[time,pos,speed,accel]，time的单位为毫秒，是其余为国际标准单位
    #@有错误的是否返回None
    #-----------------------------------------------------------------
    def calRouteLocus_InCoorType( self, info, Route_locus, cur_status ):
        "calculate route locus in coordination type."
        if None == Route_locus:
            self.logMes( 4, 'ERROR: Route_locus is None!' )
            return None
        
        _tmplocus = []      #用于存放临时数据            
        if None == cur_status:
            self.logMes( 4, 'ERROR: Route_locus is None!' )
            return None
        else:
            #获取当前状态值
            [_cur_time, _cur_coor, _cur_speed, _cur_accel] = cur_status
        
        #获取类型1的信息
        _scen = info
        
        #判断配置xml是否误
        if ( _cur_speed > 0 )and( _cur_coor > _scen[1] + 0.000001 ): #检验数据是否有误
            self.logMes( 4, 'ERROR: Wrong rs_expectSpeed.xml' )
            print str( _scen[1] ) + ' should be larger than ' + str( _cur_coor )
            #Route_locus = None
            return None
        elif ( _cur_speed < 0 )and( _cur_coor < _scen[1] - 0.000001 ): #检验数据是否有误
            #print '1111111111111111111111111'
            self.logMes( 4, 'ERROR: Wrong rs_expectSpeed.xml' )
            print str( _scen[1] ) + ' should litter than ' + str( _cur_coor )
            #Route_locus = None
            return None
        elif abs( _scen[3] ) > 0.000001 and _scen[4] != 0: #检验数据是否有误
            self.logMes( 4, 'ERROR: Wrong rs_expectSpeed.xml' )
            print "dwelltime should be zero"
            #Route_locus = None
            return None
        
        #判断脚本中间是否有间隙有则表示有匀速过程
        if ( _cur_speed > 0 ) and( _cur_coor < _scen[1] - 0.000001 ): #正向运行
            _tmplocus = [_cur_time, _cur_coor, _cur_speed, 0]
            _cur_time = _cur_time + 1000 * ( _scen[1] - _cur_coor ) / _cur_speed  #ms
            _cur_accel = 0
            _cur_coor = _scen[1]
            Route_locus.append( _tmplocus )
                    
        elif( _cur_speed < 0 ) and( _cur_coor > _scen[1] + 0.000001 ): #倒车
            _tmplocus = [_cur_time, _cur_coor, _cur_speed, 0]
            _cur_time = _cur_time + 1000 * ( _scen[1] - _cur_coor ) / _cur_speed  #ms
            _cur_accel = 0
            _cur_coor = _scen[1]
            Route_locus.append( _tmplocus )
                    
        #将读取的值放入局部变量中以便后续处理
        _cur_coor = _scen[1]
        _end_coor = _scen[2]
        _end_speed = _scen[3]
        _dwelltime = _scen[4]
                
        #根据起点和终点的位置和速度计算加速度
        _cur_accel, _Run_time = self.getaccelfrominfo( _cur_coor,
                                                      _end_coor,
                                                      _cur_speed,
                                                      _end_speed )
        if abs( _Run_time ) > 0.000001:#为零则不进行处理                
            _tmplocus = [_cur_time, _cur_coor, _cur_speed, _cur_accel]
            _cur_coor = _end_coor
            _cur_speed = _end_speed
            _cur_time = _cur_time + _Run_time #ms
            #添加节点
            Route_locus.append( _tmplocus )
                    
        if _Run_time < 0:
            self.logMes( 4, "跑车脚本有误！！！！" )
            return None
                
        if _dwelltime > 0:#停留时间
            _tmplocus = [_cur_time, _cur_coor, 0, 0] #停止不动，速度和加速度都为0
            _cur_time = _dwelltime * 100 + _cur_time
            _cur_speed = 0
            _cur_accel = 0
            Route_locus.append( _tmplocus )
            
        return [_cur_time, _cur_coor, _cur_speed, _cur_accel]
    
    #-----------------------------------------------------------------
    #@计算跑车脚本形式为0时的locus,并添加到Route_loucs
    #@输入：
    #@info:类型0节点信息格式为:[type,startpos,accel,endspeed]:距离单位m，时间单位100ms
    #@Route_locus:需要添加节点的Route_locus:[[time,position,speed,acceleration],...]
    #@返回计算后的当前车状态，[time,pos,speed,accel]，time的单位为毫秒，是其余为国际标准单位
    #@有错误的是否返回None
    #-----------------------------------------------------------------
    def calRouteLocus_InAccelType( self, info, Route_locus, cur_status ):
        "calculate route locus in accel type."
        if None == Route_locus:
            self.logMes( 4, 'ERROR: Route_locus is None!' )
            return None
        
        _tmplocus = []      #用于存放临时数据            
        if None == cur_status:
            self.logMes( 4, 'ERROR: Route_locus is None!' )
            return None
        else:
            #获取当前状态值
            [_cur_time, _cur_coor, _cur_speed, _cur_accel] = cur_status
        
        #获取类型0的信息
        _scen = info
        
        #判断配置xml是否误
        if ( _cur_speed > 0 ) and ( _cur_coor > _scen[1] + 0.00001 ): #检验数据是否有误
            self.logMes( 4, 'ERROR: Wrong rs_expectSpeed.xml' )
            print str( _scen[1] ) + ' should larger than ' + str( _cur_coor )
            #Route_locus = None
            return None
        elif ( _cur_speed < 0 )and( _cur_coor < _scen[1] - 0.000001 ): #检验数据是否有误
            self.logMes( 4, 'ERROR: Wrong rs_expectSpeed.xml' )
            print str( _scen[1] ) + ' should litter than ' + str( _cur_coor )
            #Route_locus = None
            return None
                
        #判断脚本中间是否有间隙有则表示有匀速过程
        if ( _cur_speed > 0 )and( _cur_coor < _scen[1] - 0.000001 ):
            _tmplocus = [_cur_time, _cur_coor, _cur_speed, 0]
            _cur_time = _cur_time + 1000 * ( _scen[1] - _cur_coor ) / _cur_speed  #ms
            _cur_accel = 0
            _cur_coor = _scen[1]
            Route_locus.append( _tmplocus )
        elif ( _cur_speed < 0 )and( _cur_coor > _scen[1] + 0.0001 ):
            _tmplocus = [_cur_time, _cur_coor, _cur_speed, 0]
            _cur_time = _cur_time + 1000 * ( _scen[1] - _cur_coor ) / _cur_speed  #ms
            _cur_accel = 0
            _cur_coor = _scen[1]
            Route_locus.append( _tmplocus )
            
        #将读取的值放入局部变量中以便后续处理
        _cur_coor = _scen[1]
        _cur_accel = _scen[2]
        _end_speed = _scen[3]
                
        if ( abs( _cur_accel ) < 0.000001 ):  # and (abs(_cur_speed - _end_speed) > 0.0001):#检测数据是否错误
            self.logMes( 4, 'ERROR: Wrong rs_expectSpeed.xml' )
            print str( _cur_accel ) + ' should larger than zero'
            #Route_locus = None
            return None
                
        _tmplocus = [_cur_time, _cur_coor, _cur_speed, _cur_accel]   
                
        Route_locus.append( _tmplocus ) 
        #计算加速时间后的时间
        _detatime = ( _end_speed - _cur_speed ) / _cur_accel
        _cur_time = _cur_time + 1000 * _detatime  #ms
        #计算距离
        _cur_coor = _cur_coor + ( _end_speed + _cur_speed ) * _detatime / 2.0
        _cur_speed = _end_speed  
        
        return [_cur_time, _cur_coor, _cur_speed, _cur_accel]
    
    #-----------------------------------------------------------------
    #@根据起始和终点的位置以及速度计算加速度
    #单位分别为m，m/s，m/s2
    #@_startpos：起始位置：m
    #@_endpos：结束位置：m
    #@_startvel：起始速度：m/s
    #@_endvel：结束速度：m/s
    #@返回：过程的加速度，运行的时间
    #-------------------------------------------------------------------        
    def getaccelfrominfo( self, _startpos, _endpos, _startvel, _endvel ):
        "get acceleration"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        #print "------------------",_startpos,_endpos,_startvel,_endvel
        if abs( _startvel + _endvel ) < 0.0001:
            return 0, 0
        _time = 2000.0 * ( _endpos - _startpos ) / ( _startvel + _endvel ) #这里将秒转化为毫秒
        if abs( _time ) < 0.0001:
            return 0, 0
        _accel = 1000.0 * ( _endvel - _startvel ) / _time
        return _accel, _time 
    
    def deviceEnd( self ):
        "device end"
        self.__log.fileclose()
    
    #---------------------------------------------------------------------------
    #@根据当前速度以及加速度方向，获取齿轮是正转还是反转
    #@返回：正转为1，反转为-1
    #---------------------------------------------------------------------------  
    def getcogDir( self, speed, accel = 0 ):
        "get current cog direction"
        if speed > 0:
            return self.getDataValue( 'cog_direction' )
        elif speed < 0:
            return -1 * self.getDataValue( 'cog_direction' )
        else: #speed == 0,用加速度看
            if accel >= 0:
                return self.getDataValue( 'cog_direction' )
            else:
                return -1 * self.getDataValue( 'cog_direction' )
        
    #----------------------------------------------------------------
    #根据start_time和end_time查询所在位置（在Routelocus中的位置）
    #@输入：
    #@start_time:开始时间，ms
    #@end_time:结束时间，ms
    #@Routelocus:节点信息、:格式为[[time,position,speed,acceleration],...]
    #@返回：
    #@start_index:start_time所在Routelocus列表位置的index
    #@start_find:start_time所在Routelocus列表中可以找到（在两个时间标签中间），则为True
    #@end_index:end_time所在Routelocus列表位置的index
    #@end_find:end_time所在Routelocus列表中可以找到（在两个时间标签中间），则为True
    #----------------------------------------------------------------
    def getIndexFromLocus( self, start_time, end_time, Routelocus ):
        "get start time and end time index from locus!"
        if None in [start_time, end_time, Routelocus]:
            return None, None, None, None
        #获取当前的时间节点
        _start_index = 0
        _start_find = False
        _end_index = 0
        _end_find = False
        #找到_start_time，_end_time所在的位置（在Route_locus中的位置）
        for _index, _locus in enumerate( Routelocus ):
            if ( False == _start_find ) and ( start_time < _locus[0] ):
                _start_index = _index - 1
                _start_find = True
            if ( False == _end_find ) and ( end_time < _locus[0] ):
                _end_index = _index - 1
                _end_find = True
            if _start_find and _end_find:
                break
            
        return _start_index, _start_find, _end_index, _end_find

    #-----------------------------------------------------------------------------
    #@根据Route_locus使计算当前的加速度等信息
    #@Route_locus:依据的locus
    #-----------------------------------------------------------------------------
    def getaccelstatusFromRoute( self, Route_locus ):
        "get status from Route locus！"
        type = None
        #获取当前的位置，速度
        if Route_locus == None:
            print 'error EB End Position!!!'
            self.logMes( 4, 'error EB End Position!!!' )
        else:
            _start_time = ( self.loophour - 1 ) * self.looptime  #ms
            _end_time = self.loophour * self.looptime #ms  改成变量
            #找到_start_time，_end_time所在的位置（在Route_locus中的位置）
            _start_index, _start_find, \
            _end_index, _end_find = self.getIndexFromLocus( _start_time, \
                                                           _end_time, \
                                                           Route_locus )
        
            if ( _start_index < 0 ) or ( _end_index < 0 ):
                self.logMes( 4, 'acceleration infomation can not find!' )
                return None
            elif _start_find and _end_find: #在中间的情况
                if _start_index == _end_index:#无拐点
                    type = self.calAccel_InMid_WithoutSP( _start_time,
                                                         _end_time,
                                                         Route_locus[_start_index] )
                    
                elif _start_index < _end_index:  #有拐点
                    type = self.calAccel_InMid_WithSP( _start_time,
                                                      _end_time,
                                                      Route_locus[_start_index],
                                                      Route_locus[_end_index] )
                    
            elif ( False == _start_find ) and  ( False == _end_find ): #在最后的情况,无拐点,且为匀速
                type = self.calAccel_InEnd_WithoutSP( _start_time,
                                                    _end_time,
                                                    Route_locus[-1] )      
                 
            elif ( True == _start_find ) and  ( False == _end_find ):  #在最后的情况,有拐点
                type = self.calAccel_InEnd_WithSP( _start_time,
                                                  _end_time,
                                                  Route_locus[_start_index],
                                                  Route_locus[-1] )
        
        return type

    #--------------------------------------------------------------
    #@计算加速度信息函数
    #@处理在中间且无拐点时的情况
    #@start_time:周期开始时间
    #@end_time:周期结束时间
    #@locus:无拐点信息节点[time,position,speed,acceleration]
    #@return: type = 0
    #--------------------------------------------------------------
    def calAccel_InMid_WithoutSP( self, start_time, end_time, locus ):
        "calculate accel in the middle of the locus and without spinodal!"
        #获取当前的加速度
        _accel = locus[3]  #获取加速度
        #计算本周期的开始的距离
        _deta_time = ( start_time - locus[0] ) / 1000.0  #转换为s
        _ini_speed = locus[2]
        _start_coor = locus[1] + _deta_time * _ini_speed + \
                      _accel * _deta_time * _deta_time / 2.0
                    
        #获取周期开始时的速度
        _speed = _ini_speed + _deta_time * _accel
                    
        #计算周期结束时的距离
        _deta_time = ( end_time - locus[0] ) / 1000.0  #转换为s
        _end_coor = locus[1] + _deta_time * _ini_speed + \
                    _accel * _deta_time * _deta_time / 2.0
        _end_speed = _ini_speed + _deta_time * _accel               
        #存储以上数据至变量data中
        self.writeData_WithoutSP( _start_coor,
                                 _end_coor,
                                 _speed,
                                 _accel,
                                 _end_speed )
#        self.addDataKeyValue('coordinates_1', _start_coor * 1000) #转换为毫米
#        self.addDataKeyValue('coordinates_2', _end_coor * 1000) #转换为毫米
#        self.addDataKeyValue('CBK_coordinates', _start_coor) #单位m
#        self.addDataKeyValue('CBK_acceleration', _accel) #单位m/s2
#        self.addDataKeyValue('CBK_speed', _speed) #单位m/s
#        self.addDataKeyValue('Start_Speed', _speed) #单位m/s
#        self.addDataKeyValue('End_Speed', _end_speed) #单位m/s  
        
        #返回无拐点类型0
        return 0

    #--------------------------------------------------------------
    #@计算加速度信息函数
    #@处理在中间且有拐点时的情况
    #@start_time:周期开始时间
    #@end_time:周期结束时间
    #@start_locus:起始信息节点[time,position,speed,acceleration]
    #@end_locus:结束信息节点[time,position,speed,acceleration]
    #@return: type = 1
    #--------------------------------------------------------------
    def calAccel_InMid_WithSP( self, start_time, end_time, start_locus, end_locus ):
        "calculate accel in the middle of the locus and without spinodal!"
        #获取拐点前的加速度
        _accel_before = start_locus[3]  #获取加速度
        #计算本周期的开始的距离
        _deta_time = ( start_time - start_locus[0] ) / 1000.0  #转换为s
        _ini_speed = start_locus[2]
        _start_coor = start_locus[1] + _deta_time * _ini_speed + \
                      _accel_before * _deta_time * _deta_time / 2.0
                    
        #获取周期开始时的速度
        _speed = _ini_speed + _deta_time * _accel_before
        _change_time = ( end_locus[0] - start_time ) / 1000.0   #拐点开始时间s
                    
        #计算计算拐点后周期结束时的距离
        _accel_after = end_locus[3]  #获取加速度
        _deta_time = ( end_time - end_locus[0] ) / 1000.0  #转换为s
        _end_coor = end_locus[1] + _deta_time * end_locus[2] + \
                    _accel_after * _deta_time * _deta_time / 2.0
        _end_speed = _speed + _change_time * _accel_before + \
                    _accel_after * _deta_time             
        #存储以上数据至变量data中
        self.writeData_WithSP( _start_coor,
                              _end_coor,
                              _speed,
                              _accel_before,
                              _accel_after,
                              _change_time,
                              _end_speed )
#        self.addDataKeyValue('coordinates_1', _start_coor * 1000) #转换为毫米
#        self.addDataKeyValue('coordinates_2', _end_coor * 1000) #转换为毫米
#        self.addDataKeyValue('CBK_coordinates_1', _start_coor) #单位m
#        self.addDataKeyValue('CBK_coordinates_2', _end_coor) #单位m
#        self.addDataKeyValue('CBK_speed_1', _speed) #单位m/s                
#        self.addDataKeyValue('CBK_acceleration_1', _accel_before) #单位m/s2
#        self.addDataKeyValue('CBK_acceleration_2', _accel_after)  #单位m/s2 
#        self.addDataKeyValue('CBK_time', int(1000.0 * _change_time)) #单位ms
#        self.addDataKeyValue('Start_Speed', _speed) #单位m/s
#        self.addDataKeyValue('End_Speed', _end_speed) #单位m/s

        #返回有拐点类型1
        return 1

    #-------------------------------------------------------------
    #@将无拐点时的变量放入__data中
    #@输入:
    #start_coor:周期起始位置，单位m
    #end_coor:周期结束位置，单位m
    #speed:速度，单位m/s
    #accel:加速度，单位m/s2
    #end_speed：周期结束时的速度，m/s
    #-------------------------------------------------------------
    def writeData_WithoutSP( self, start_coor, end_coor, speed, accel, end_speed ):
        "write data to data variant without spinodal."
        self.addDataKeyValue( 'coordinates_1', start_coor * 1000 ) #转换为毫米
        self.addDataKeyValue( 'coordinates_2', end_coor * 1000 ) #转换为毫米
        self.addDataKeyValue( 'CBK_coordinates', start_coor ) #单位m
        self.addDataKeyValue( 'CBK_acceleration', accel ) #单位m/s2
        self.addDataKeyValue( 'CBK_speed', speed ) #单位m/s
        self.addDataKeyValue( 'Start_Speed', speed ) #单位m/s
        self.addDataKeyValue( 'End_Speed', end_speed ) #单位m/s 

    #-------------------------------------------------------------
    #@将有拐点时的变量放入__data中
    #@输入:
    #start_coor:周期起始位置，单位m
    #end_coor:周期结束位置，单位m
    #speed:速度，单位m/s
    #accel_before:初始加速度，单位m/s2
    #accel_after:第二加速度，单位m/s2
    #change_time:拐点时间，单位毫秒
    #Endspeed：周期结束时的速度，m/s
    #-------------------------------------------------------------
    def writeData_WithSP( self, start_coor, end_coor, speed, accel_before, accel_after, change_time, Endspeed ):
        "write data to data variant with spinodal."
        self.addDataKeyValue( 'coordinates_1', start_coor * 1000 ) #转换为毫米
        self.addDataKeyValue( 'coordinates_2', end_coor * 1000 ) #转换为毫米
        self.addDataKeyValue( 'CBK_coordinates_1', start_coor ) #单位m
        self.addDataKeyValue( 'CBK_coordinates_2', end_coor ) #单位m
        self.addDataKeyValue( 'CBK_speed_1', speed ) #单位m/s                
        self.addDataKeyValue( 'CBK_acceleration_1', accel_before ) #单位m/s2
        self.addDataKeyValue( 'CBK_acceleration_2', accel_after )  #单位m/s2 
        self.addDataKeyValue( 'CBK_time', int( 1000.0 * change_time ) ) #单位ms
        self.addDataKeyValue( 'Start_Speed', speed )  #单位m/s
        self.addDataKeyValue( 'End_Speed', Endspeed ) #单位m/s 
        
    #--------------------------------------------------------------
    #@计算加速度信息函数
    #@处理在最后且无拐点时的情况
    #@start_time:周期开始时间
    #@end_time:周期结束时间
    #@locus:无拐点信息节点[time,position,speed,acceleration]
    #@return: type = 0
    #--------------------------------------------------------------
    def calAccel_InEnd_WithoutSP( self, start_time, end_time, locus ):
        "calculate accel in the end of the locus and without spinodal!"
        #获取当前的加速度
        _accel = 0  #获取加速度
        #计算本周期的开始的距离
        _deta_time = ( start_time - locus[0] ) / 1000.0  #转换为s
        _speed = locus[2]
        _start_coor = locus[1] + _deta_time * _speed
                    
        #计算计算周期结束时的距离
        _deta_time = ( end_time - locus[0] ) / 1000.0  #转换为s
        _end_coor = locus[1] + _deta_time * _speed
                                    
        #存储以上数据至变量data中
        self.writeData_WithoutSP( _start_coor,
                                 _end_coor,
                                 _speed,
                                 _accel,
                                 _speed )
#        self.addDataKeyValue('coordinates_1', _start_coor * 1000) #转换为毫米
#        self.addDataKeyValue('coordinates_2', _end_coor * 1000) #转换为毫米
#        self.addDataKeyValue('CBK_coordinates', _start_coor) #单位m
#        self.addDataKeyValue('CBK_acceleration', _accel) #单位m/s2
#        self.addDataKeyValue('CBK_speed', _speed) #单位m/s
#        self.addDataKeyValue('Start_Speed', _speed) #单位m/s
#        self.addDataKeyValue('End_Speed', _speed) #单位m/s 

        #返回无拐点类型0
        return 0
    #--------------------------------------------------------------
    #@计算加速度信息函数
    #@处理在最后且有拐点时的情况
    #@start_time:周期开始时间
    #@end_time:周期结束时间
    #@start_locus:起始信息节点[time,position,speed,acceleration]
    #@end_locus:结束信息节点[time,position,speed,acceleration]
    #@return: type = 1
    #--------------------------------------------------------------
    def calAccel_InEnd_WithSP( self, start_time, end_time, start_locus, end_locus ):
        "calculate accel in the end of the locus and with spinodal!"
        #获取拐点前的加速度
        _accel_before = start_locus[3]  #获取加速度
        #计算本周期的开始的距离
        _deta_time = ( start_time - start_locus[0] ) / 1000.0  #转换为s
        _ini_speed = start_locus[2]
        _start_coor = start_locus[1] + _deta_time * _ini_speed + \
                      _accel_before * _deta_time * _deta_time / 2.0
                    
        #获取周期开始时的速度
        _speed = _ini_speed + _deta_time * _accel_before
        _change_time = ( end_locus[0] - start_time ) / 1000.0   #拐点开始时间s
        _Endspeed = _speed + _change_time * _accel_before
                
        #计算计算拐点后周期结束时的距离
        _accel_after = 0  #获取加速度
        _deta_time = ( end_time - end_locus[0] ) / 1000.0  #转换为s
        _end_coor = end_locus[1] + _deta_time * end_locus[2]
                
        #存储以上数据至变量data中
        self.writeData_WithSP( _start_coor,
                              _end_coor,
                              _speed,
                              _accel_before,
                              _accel_after,
                              _change_time,
                              _Endspeed )
        
#        self.addDataKeyValue('coordinates_1', _start_coor * 1000) #转换为毫米
#        self.addDataKeyValue('coordinates_2', _end_coor * 1000) #转换为毫米
#        self.addDataKeyValue('CBK_coordinates_1', _start_coor) #单位m
#        self.addDataKeyValue('CBK_coordinates_2', _end_coor) #单位m
#        self.addDataKeyValue('CBK_speed_1', _speed) #单位m/s                
#        self.addDataKeyValue('CBK_acceleration_1', _accel_before) #单位m/s2
#        self.addDataKeyValue('CBK_acceleration_2', _accel_after)  #单位m/s2 
#        self.addDataKeyValue('CBK_time', int(1000.0 * _change_time)) #单位ms
#        self.addDataKeyValue('Start_Speed', _speed)  #单位m/s
#        self.addDataKeyValue('End_Speed', _Endspeed) #单位m/s 

        #返回有拐点类型1
        return 1

    def getRadarStatus( self ):
        "get radar stauts"
        _rev = self.getDataValue( "Radar_Run_Direction" ) + \
                self.getDataValue( "Radar_Run_Direction_Valid" ) * 2 + \
                4 + \
                self.getDataValue( "Radar_Run_Status" ) * 8 + \
                self.getDataValue( "Radar_Run_Mode" ) * 64 + \
                self.getDataValue( "Radar_RS485_Check" ) * 256
        return _rev
    
if __name__ == '__main__':
    rs = RS( 'rs', 1 )
    
#     rs.deviceInit( varFile = r'./setting/rs_variant.xml', \
#                   msgFile = r'./setting/rs_message.xml', \
#                   scenario = r'./scenario/rs_scenario.xml', \
#                   expectSpeed = r'./scenario/rs_expectSpeed.xml', \
#                   viom_setting = r'./scenario/rs_viom_setting.xml', \
#                   rules = r'./scenario/rs_rules.xml', \
#                   log = r'./log/rs.log' )
    
    #print rs.Presenario.getBlockandAbs(300000)
    #print rs.EB_EndPos
    #rs.importRuleDic(r'./setting/rs_rules.xml')
    #print rs.Route_locus
    #print 'over device init'
    #print 'data dic', rs.getDataDic()
    #print 'var dic', rs.getVarDic()
    #print 'msg dic', rs.getMsgDic()
    #print 'def scenario', rs.defScenario
    #print 'train Run Scenario',rs.trainRunScenario
    #print 'Route locus',rs.Route_locus
    #print 'VIOM_Setting',rs.getDataValue('VIOM_IN_Setting'),rs.getDataValue('VIOM_OUT_Setting')
#    _appMsg = rs.packAppMsgHasHead(123,1,0xff,0xee)
#    print 'pack message', len(_appMsg), binascii.hexlify(_appMsg)
#    print 'unpack message', rs.unpackAppMsgHasHead(_appMsg)
#    rs.loophour = 2000
#    #print time.time()
#    print time.clock()
#    rs.getcuraccelstatus()
#    print time.clock()
#    rs.deviceEnd()
#    print time.time()
#    print rs.getDataValue('coordinates_1')
#    print rs.getDataValue('coordinates_2')
