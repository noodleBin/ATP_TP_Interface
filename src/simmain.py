#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     simmain.py
# Description:  ATP测试平台入口文件      
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      2011-07-25
# Company:      CASCO
# LastChange:   
# History:      create 2011-07-25
#----------------------------------------------------------------------------
from base.simulator import Simulator
from base.loglog import LogLog
from tracksider import TrackSider
from base import commlib 
from viom import VIOM
from lc import LC
from rs import RS
from ccnv import CCNV
from datp import DATP
from zc import ZC
from ci import CI
import sys
import struct
import time
import Queue
import os
from base import simdata
import threading
from base.caseprocess import CaseParser
from Car import Car
from GpsAndOdometer import GpsAndOdometer
# from Loop import Loop
import datetime
#import threading


lock = threading.Lock()

class TPSim( Simulator ):
    """
    ATP Test Platform Simulator
    """
    __count = None
    loophour = None
    queMsgHead = None
    loadDeviceList = None
    loadDeviceDic = None
    sigID = None
    rmsID = None
    
    #平台内部传递的消息，所带的消息头，loophour,msgId
    msgHead = '!IH'
    __GPS1MsgId = 1001
    __GPS2MsgId = 1002
    __LOOPMsgId = 1003
    __LOOPMsgId1 = 1006
    __LOOPMsgId2 = 1007
    __LOOPMsgId3 = 1008
    __ODMMsgId = 1004
    
    __startTime = None
    #ts2cbk beacon message
    ts2cbkMes = None
    tps2sdtsMes = None
    
    #消息长度
    queHeadLen = None

    #接收atp消息的SN计数
    _atpSN = None
    
    #给ci的psdid
    __PSDID = None 
    #当前通信的CI_ID
    __CI_ID = None
    #当前ci的id
    #__cilogicID = None
    #ci消息的冗余层，信号层
    ci_rms = {0:None, 1:None}
    ci_sig = {0:None, 1:None}
    
    #ci Sacem消息的冗余层，信号层
    ci_rms_Sacem = None
    ci_sig_Sacem = None
           
    #日志
    myLogger = None
    
    #保存SN的计算通道，一个通道一个
    SN_dic = {"rs2cbk":0,
              "viom1a2atp":0,
              "viom1b2atp":0,
              "viom2a2atp":0,
              "viom2b2atp":0,
              "ccnv2atp":0,
              "datp2atp":0,
              "lc2ccnv":0,
              "zc2ccnv":0,
              "citoccnv":0,
              "rs2atp":0,
              "rs2hmi":0}
    
    #通道对应关系，通道与平台msgid的对应关系
    Channel_Id_dic = {( 257, 260, 513, 261 ):"rs2cbk",
                      ( 5889, ):"viom1a2atp",
                      ( 5890, ):"viom1b2atp",
                      ( 5891, ):"viom2a2atp",
                      ( 5892, ):"viom2b2atp",
                      ( 5121, ):"ccnv2atp",
                      ( 1793, ):"datp2atp",
                      ( 10241, ):"lc2ccnv",
                      ( 7681, ):"zc2ccnv",
                      ( 15361, 15362, 15363, 15364 ):"citoccnv",
                      ( 300, ):"rs2atp",
                      ( 293, ):"rs2hmi"
                      }
    
    #计算SN是用到的互斥量
    SN_mutex = threading.Lock()
    
    #周期
    cycle = 100 #ms
    
    deviceRunstart = None
    sendStartCommand = None
    #是否创建socket
    createSocketFlag = None
    createSerialFlag = None

    #SSA id 最后一个ID
    _id = None
    _totalMile = None
    
    deviceInitPara_base = {'ts':{'varFile':r'/setting/ts_variant.xml', \
                            'msgFile':r'/setting/ts_message.xml', \
                            'scenario':r'/scenario/ts_scenario.xml', \
                            'bmBeaconFile':r'/scenario/bm_beacons.xml', \
                            'bmBeaconMesFile':r'/scenario/beacon_msg_setting.xml', \
                            'log':r'/log/ts.log', \
                            },
                    'lc':{'varFile':r'/setting/lc_variant.xml', \
                          'msgFile':r'/setting/lc_message.xml', \
                          'scenario':r'/scenario/lc_scenario.xml', \
                          'log':r'/log/lc.log', \
                          'tsrFile':r'/scenario/lc_tsr_setting.xml', \
                          'sacemFile':"/setting/sacem_devicelist.xml", \
                          'binFile':"LC_SACEM_CNF.bin" 
                         },
                    'rs':{'varFile':r'/setting/rs_variant.xml', \
                          'msgFile':r'/setting/rs_message.xml', \
                          'scenario':r'/scenario/rs_scenario.xml', \
                          'expectSpeed':r'/scenario/rs_expectSpeed.xml', \
                          'viom_setting':r'/scenario/rs_viom_setting.xml', \
                          'rules':r'/scenario/rs_rules.xml', \
                          'log':r'/log/rs.log'},
                    'zc':{'varFile':r'/setting/zc_variant.xml', \
                          'msgFile':r'/setting/zc_message.xml', \
                          'scenario':r'/scenario/zc_scenario.xml', \
                          'variant_scenario':r'/scenario/zc_variant_scenario.xml', \
                          'variniFile':r'/scenario/zc_variant_ini.xml', \
                          'log':r'/log/zc.log',
                          'sacemFile':"/setting/sacem_devicelist.xml" },
                    'viom':{'varFile':r'/setting/viom_variant.xml', \
                            'msgFile':r'/setting/viom_message.xml', \
                            'scenario':r'/scenario/viom_scenario.xml', \
                            'log':r'/log/viom.log', \
                            'sacemFile':"/setting/sacem_devicelist.xml" },
                    'ccnv':{'varFile':r'/setting/ccnv_variant.xml', \
                            'msgFile':r'/setting/ccnv_message.xml', \
                            'scenario':r'/scenario/ccnv_scenario.xml', \
                            'rules':r'/scenario/ccnv_rules.xml', \
                            'log' :r'/log/ccnv.log'
                            },
                    'datp':{'varFile':r'/setting/datp_variant.xml', \
                            'msgFile':r'/setting/datp_message.xml', \
                            'scenario':r'/scenario/datp_scenario.xml', \
                            'log':r'/log/datp.log', \
                            'sacemFile':r"/setting/sacem_devicelist.xml" 
                            },
                    'ci':{'varFile' : r'/setting/ci_variant.xml', \
                          'msgFile': r'/setting/ci_message.xml', \
                          'scenario' :r'/scenario/ci_scenario.xml', \
                          'log' :r'/log/ci.log' , \
                          'fsfb2': r'/setting/fsfb2_devicelist.xml', \
                          'variant_scenario':r'/scenario/ci_variant_scenario.xml', \
                          'variniFile':r'/scenario/ci_variant_ini.xml', \
                          'sacemFile':r"/setting/sacem_devicelist.xml" 
                          },
                    'tps':{'varFile': r'/setting/tps_variant.xml', \
                            'msgFile': r'/setting/tps_message.xml', \
                            'netWorkFile': r'/setting/tps_networks.xml', \
                            'paraFile': r'/setting/tps_parameter.xml', \
                            'track_map':r'/datafile/atpCpu1Binary.txt', \
                            'train_route': r'/scenario/train_route.xml', \
                            'track_maptxt': r'/datafile/atpText.txt', \
                            'log': r'/log/tps.log', \
                            'telnet': r'/setting/telnet_config.xml', \
                            'omap': r'/setting/omap_config.xml' 
                          }
                    }
    deviceInitPara = {}
    
    __SettingFileName = ['varFile', 'msgFile', 'netWorkFile', 'telnet' , 'sacemFile', 'omap', 'fsfb2']
    
    car = None
    gps = None
    loop = None
    
    def __init__( self, name, id ):
        "TPsim init"
        Simulator.__init__( self, name, id )
        self.createSocketFlag = True
        self._atpSN = -1
        self.deviceRunstart = False
        self.sendStartCommand = True
        self.__startTime = 0
        self.loophour = 0
        self.__count = 0
        self._id = 0
        self._totalMile = 0
        self.car = Car('car')
#         self.car.deviceInit()
        self.gps = GpsAndOdometer('gps')
#         self.gps.deviceInit()
        
#         self.loop = Loop('loop')
#         self.loop.deviceInit()
    
    def ReInitTPS( self ):
        "Re Init TPS"
#        self.createSocketFlag = True
        self.createSerialFlag = True
        self._atpSN = -1
        self.deviceRunstart = False
        self.sendStartCommand = True
        self.__startTime = 0
        self.loophour = 0        
        
    #------------------------------------------------------------
    #获取初始化的路劲配置参数，casepath：[LogPath,ScriptPath,DownLogPath],endtype:End1,End2分别表示END1，END2
    #------------------------------------------------------------    
    def joinDevInitPath( self, casepath, endtype ):
        "join device initial path by case path"
        _logpath = casepath[0]
        _scriptpath = casepath[1]
        _DownLogPath = casepath[2]
        self.deviceInitPara = {}
        
        for _dev in self.deviceInitPara_base:
            self.deviceInitPara[_dev] = {}
            for _paraKey in self.deviceInitPara_base[_dev]:
                if "binFile" == _paraKey and "lc" == _dev:#LC的配置文件单独处理
                    _tmp = os.path.split( os.path.split( CaseParser.getCurRunCaseMappath()[0] )[0] )[0]
                    self.deviceInitPara[_dev][_paraKey] = os.path.join( _tmp, "LC_SACEM_CNF.bin" )
                elif _paraKey == "log":
                    self.deviceInitPara[_dev][_paraKey] = commlib.joinPath( _logpath, self.deviceInitPara_base[_dev][_paraKey] )
                elif _paraKey in self.__SettingFileName: #平台内部配置
                    self.deviceInitPara[_dev][_paraKey] = r"./TPConfig" + self.deviceInitPara_base[_dev][_paraKey] 
                elif 'paraFile' == _paraKey:
                    self.deviceInitPara[_dev]['paraFile'] = ( r"./TPConfig/setting/" + "tps_parameter_end1.xml" ) if "1" in endtype else  ( r"./TPConfig/setting/" + "tps_parameter_end2.xml" )
                elif 'track_map' == _paraKey:
                    self.deviceInitPara[_dev]['track_map'] = os.path.split( CaseParser.getCurRunCaseMappath()[0] )[0]
#                    print CaseParser.getCurRunCaseMappath()[0], CaseParser.getCurRunCaseMappath()[1]
                elif 'track_maptxt' == _paraKey:
                    self.deviceInitPara[_dev]['track_maptxt'] = os.path.split( CaseParser.getCurRunCaseMappath()[1] )[0]
                else:
                    self.deviceInitPara[_dev][_paraKey] = commlib.joinPath( _scriptpath, self.deviceInitPara_base[_dev][_paraKey] )
        
#        print self.deviceInitPara
        
        
    def logMes( self, level, mes ):
        " log mes"
        self.myLogger.logMes( level, mes )

    def deviceInit( self, *args, **kwargs ):
        "simulator load setting file and prepare data"
        #simulator的InQ,对于发送给ccvn的数据，都需要压入改队列中进行发送
        self.inQ = Queue.Queue()  #清空队列，以便继续使用
        self.NBOfviom = 0
        self.myLogger = LogLog()
        self.myLogger.orderLogger( kwargs['log'], self.getDeviceName() )
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        self.importVarint( kwargs['varFile'] )
        self.importMsg( kwargs['msgFile'] )
        self.importNetworkSetting( kwargs['netWorkFile'] )
        self.importDevPara( kwargs['paraFile'] )        
        #set var
        self.loophour = 0
        self.queMsgHead = self.getDataValue( 'queMsgHead' )
        self.rmsID = self.getDataValue( 'rmsHead' )
        self.sigID = self.getDataValue( 'sigHead' )
        self.queHeadLen = struct.calcsize( self.queMsgHead )
        
        self.ts2cbkMes = ''
        self.tps2sdtsMes = ''
            
        #加载地图信息
        _track_map = commlib.joinPath( CaseParser.getCurCasePath()[1] , kwargs['track_map'] )
        _track_maptxt = commlib.joinPath( CaseParser.getCurCasePath()[1] , kwargs['track_maptxt'] ) 
        _train_route = commlib.joinPath( CaseParser.getCurCasePath()[1] , kwargs['train_route'] ) 
        simdata.MapData.loadMapData( _track_map, _track_maptxt )
        simdata.TrainRoute.loadTrainData( _train_route )    
        #加载设备，运行设备的deviceinit
        self.loadDevice()
        print '===========================simmain deviceInit'
        print '-----simmain init----',GpsAndOdometer._IdAndSSA
        self._id = GpsAndOdometer._IdAndSSA[0][-1]
        self._totalMile = GpsAndOdometer._continuousSSA[self._id][0][1]
        print 'get continuous ssa-----',GpsAndOdometer._continuousSSA
        print '------total mile----',self._totalMile
        print '----simmain----_id----------',self._id

        print "++++++++++++++++++++++startListen"
        if self.createSerialFlag:
            self.createSerial()
            self.createSerialFlag = False
        
#         self.omap.OMAPListen()
        self.startListenThread()
        
    def ReInitDevice(self):
        self._id = GpsAndOdometer._IdAndSSA[0][-1]
        self._totalMile = GpsAndOdometer._continuousSSA[self._id][0][1]
        print '----simmain----_id----------',self._id
        print 'get continuous ssa-----',GpsAndOdometer._continuousSSA
    # --------------------------------------------------------------------------
    ##
    # @Brief 加载设备 每类型设备仅有一个实例
    #
    # @Returns True or False
    # --------------------------------------------------------------------------
    def loadDevice( self ):
        "load device by deviceType"
        self.loadDeviceDic = {}
        self.loadDeviceList = [_s for _s in self.getDataValue( 'loadDevice' ).strip().split( ',' )]
        #print 'self.loadDeviceList', self.loadDeviceList
        _class = None
        for _d in self.loadDeviceList:
            if _d == 'ts':
                _class = TrackSider
            elif _d == 'lc':
                _class = LC
            elif _d == 'rs':
                _class = RS
            elif _d == 'viom':
                _class = VIOM
            elif _d == 'ccnv':
                _class = CCNV
            elif _d == 'datp':
                _class = DATP
            elif _d == 'zc':
                _class = ZC
            elif _d == 'ci':
                _class = CI
            else:
                self.logMes( 1, 'tps load device failed type is unkown device:%s' % ( _d ) )
                _class = None
            if _class:
                _ins = _class( _d, self.getDataValue( 'defDeviceId' ) )
                if _ins.deviceInit( **self.deviceInitPara[_d] ) == True:
                    self.loadDeviceDic[_d] = _ins
                else:
                    self.logMes( 1, 'tps load device failed  device init error device:%s' % ( _d ) )
                    return None 
        
        #添加设备实例字典到设备
        for _d in self.loadDeviceDic:
            self.loadDeviceDic[_d].addDataKeyValue( 'devDic', self.loadDeviceDic )
            #将simulator的inQ压给各个设备
            self.loadDeviceDic[_d].addDataKeyValue( 'siminQ', self.inQ )
#             print 'dev ins:', _d, self.loadDeviceDic[_d].getDataValue('devDic') 
            
            #添加设备参数字典 SStype,Logid，SSid
            self.loadDeviceDic[_d].addDataKeyValue( 'parDic', self.getParaDic() )
            #创建线程
#            self.createThread( self.loadDeviceDic[_d].deviceRun, '', 'thread_' + _d )
            self.createThread( self.loadDeviceDic[_d].deviceRunWithExceptHandle,
                               '', 'thread_' + _d )
            self.startThread( 'thread_' + _d, "ABOVE_NORMAL" ) #各设备的优先级也要高一点
        return True
    
    
    def getDeviceList( self ):
        "get Device list."
        _rev = []
        for _key in self.loadDeviceDic:
            _rev.append( _key )
        return _rev
    
    #---------------------------------------------------------------------------
    #@发送重新启动下位机消息
    #---------------------------------------------------------------------------
    def ReBootDownCommand( self ):
        "ReBoot Down Command."
        #生成重启指令消息，msgid = 260
        _msg = struct.pack( "!IHB", 0, 260, 0 )
        
        #发送重启指令
        self.inQ.put( _msg )
                

    #---------------------------------------------------------------------------
    #@通过telnet重启下位机，本函数用于
    #---------------------------------------------------------------------------
    def ReBootHardWare( self, log ):
        "ReBoot HardWare using telnet."
#         self.telnet.ConnectTelnet( log ) 
        self.telnet.CloseTelnet() 
        time.sleep( 20 ) #重启完成后等待20s

    # --------------------------------------------------------------------------
    ##
    # @Brief 模拟器每个定时中断处理消息
    #
    # @Param args
    # @Param kwargs
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def deviceRun( self, *args, **kwargs ):
        " simulator running in each cycle" 
        pass

    def SendDeviceUpdateMessage(self):
        "Send Device Updata Message"
        while True:
#             if lock.acquire():
#                 pass
            time.sleep(Car._sTimer)
            self.__count = self.__count + 1

#             if self.car.getAllowStopFlag() == True:
#             print '-------allow stop-------',Car._allowstop
            if Car._manualStop == True:
#                 print '-------------manual stop----------'
                _cmd = self.packAppMsgHasHead( self.loophour, self.getDataValue( 'cmdMsgId' ), self.getDataValue( 'manualStop' ))
            elif Car._allowstop == True:
#                 print '-------------auto run-------------'
                _cmd = self.packAppMsgHasHead( self.loophour, self.getDataValue( 'cmdMsgId' ), self.getDataValue( 'autoRun' ))
            else:
#                 print '-------------cog run -------------'
                _cmd = self.packAppMsgHasHead( self.loophour, self.getDataValue( 'cmdMsgId' ), self.getDataValue( 'cmdCog' ) )
            self.loadDeviceDic['rs'].inQ.put( _cmd )
            if self.__count == 50 :
                _time = datetime.datetime.now()
                print '---simmain SendDeviceUpdataMsg---',_time
                self.logMes( 4, '--loophour--%d --time-- %f' % ( self.loophour, time.clock() ) )
                self.__count = 0
                self.loophour += 1
                #给车辆发送启动命令
                _cmd = self.packAppMsgHasHead( self.loophour, self.getDataValue( 'cmdMsgId' ), self.getDataValue( 'cmdStart' ) )
                self.loadDeviceDic['rs'].inQ.put( _cmd )
                
                if 0<= (self._totalMile - Car.getAmountMile()) <= 12:
                    print '1 stop---------------'
                    self.car.ReSetAmountMile()
                    _idList = GpsAndOdometer._lineList
                    if len(_idList) != 0:
                        self.loophour = 0
                        self.__count = 0
                        time.sleep(5)
                        _cmd = self.packAppMsgHasHead( self.loophour, self.getDataValue( 'cmdMsgId' ), self.getDataValue( 'cmdRepeate' ) )
                        self.loadDeviceDic['rs'].inQ.put( _cmd )
                        time.sleep(5)
                        self.ReInitDevice()
                        print '-------repeat--------'
                        continue
                    else:
                        _cmd = self.packAppMsgHasHead( self.loophour, self.getDataValue( 'cmdMsgId' ), self.getDataValue( 'cmdEnd' ) )
                        self.loadDeviceDic['rs'].inQ.put( _cmd )

    def deviceSerialSendMsg(self):
        print "send serial message"
        
        while self.deviceRunstart:
            _Newmes = self.inQ.get()
            if None==_Newmes:
                continue
            #解消息头 
            try:           
                _mHead = self.unPackQueHead( _Newmes[0:self.queHeadLen] )
            except:
                print _Newmes
                
            if "END Case" == _Newmes:  #结束发送消息进程
                print "End MSG deviceSendMsg!"
                break

            if self.__GPS1MsgId == _mHead[1]:#GPGGA
                #package
#                 _head = self.packAppMsg( self.__GPS1MsgId, '$GPGGA')
                _head = '$GPGGA'
                _sendmes = _head+_Newmes[6:]
                self.serialSend(2, _sendmes)
#                 print '---gps1 _sendmes---'
                print '---gps1 _sendmes---',_sendmes
                
            if self.__GPS2MsgId==_mHead[1]:#GPRMC
                #package
#                 _head = self.packAppMsg( self.__GPS2MsgId, '$GPRMC')
                _head = '$GPRMC'
                _sendmes = _head+_Newmes[6:] 
                self.serialSend(2, _sendmes)
#                 print '---gps2 _sendmes---'
                print '---gps2 _sendmes---',_sendmes
                
            if self.__LOOPMsgId==_mHead[1]:#LOOP
                #package
                _head = self.packAppMsg( self.__LOOPMsgId, 0x02, 0x01,0x80)
                _sendmes = _head+_Newmes[6:]
#                 print '---loop _head---',repr(_head)
#                 print '---loop _sendmes---',repr(_sendmes)          
                self.serialSend(1, _sendmes)
#                 print '---loop _sendmes---'
#                 print '---loop _sendmes---',repr(_sendmes)

            if self.__ODMMsgId==_mHead[1]:
#                package
                _head = self.packAppMsg( self.__ODMMsgId, 0x7e,_mHead[0], 0x32)
#                 print '-----cycle number---',_mHead[0]
                _sendmes = _head+_Newmes[6:] 
                self.serialSend(3, _sendmes)
#                 print '---ODM _sendmes---'
#                 print '---ODM _sendmes---',repr(_sendmes)

    def deviceEnd( self, *args, **kwargs ):
        print " ending need to do"
        #TODO 结束线程
        _cmd = self.packAppMsgHasHead( self.loophour, self.getDataValue( 'cmdMsgId' ), self.getDataValue( 'cmdEnd' ) )
        for _d in self.loadDeviceList:
            #print '_cmd:', commlib.str2hexlify(_cmd)
            self.loadDeviceDic[_d].inQ.put( _cmd )
            self.loadDeviceDic[_d].deviceEnd()        
        self.stopListen()
        self.myLogger.fileclose()
        time.sleep( 2 )
    
    
    #监听从串口收到的GPS数据
    def handle_gps(self,data):
        "handle gps message1:GPGGA"
        if None == data:
            return
        #CRC check
        pass
        _cmd=struct.unpack("!B",data[0])[0]
        if "$GPGGA"==_cmd:
            self.sendStartCommand=False
        elif "$GPRMC"==_cmd:
            self.sendStartCommand=False
        else:
            print "handle_gps:unknown message!!!",commlib.str2hexlify(data)
        
    #监听从串口收到的LOOP命令数据
    def handle_loop(self,data):
        "handle loop message"
        if None == data:
            return 
        
        if 0x02 != struct.unpack("!B",data[0])[0] or 0x01 != struct.unpack("!B",data[1])[0]:
            print 'Loop head or tail is false,return'
            return
             
        _cmdId=struct.unpack("!B",data[2])[0]
        if 0x11==_cmdId:
#             if False==self.CheckCRC(18,data):
#                 return 
            self.sendStartCommand=False
            _tpdata = data[2:17]#18-4+1
            _head = struct.pack( self.msgHead, self.loophour, self.__LOOPMsgId1 )
            self.loadDeviceDic['rs'].inQ.put( _head+_tpdata )
        elif 0x12== _cmdId:
            #CRC check
            if False==self.CheckCRC(7,data):
                return
            self.sendStartCommand=False
            _tpdata = data[2:6]
            _head = struct.pack( self.msgHead, self.loophour, self.__LOOPMsgId2 )
            self.loadDeviceDic['rs'].inQ.put( _head+_tpdata )
        elif 0x13==_cmdId:
            if False==self.CheckCRC(5,data):
                return
            self.sendEndCommand=False
            _tpdata = data[2:4]
            _head = struct.pack( self.msgHead, self.loophour, self.__LOOPMsgId3 )
            self.loadDeviceDic['rs'].inQ.put( _head+_tpdata )
#       elif 0x80== _cmdId:
#             self.sendEndCommand=False
        else:
            print "handle_loop:unknown message!!!",commlib.str2hexlify(data)
    
    def handle_odm(self,data):
        "handle odm message，not decided"
        if None == data:
            return
        
        if 0x05 != struct.unpack("!B",data[0])[0] or 0x06 != struct.unpack("!B",data[2])[0]:
            print "handle_odm:unknown message!!!",commlib.str2hexlify(data)
            return
        #CRC check
          
        _cmd=struct.unpack("!B",data[1])[0]
        self.sendStartCommand=False
        
    
    def CheckCRC(self,datalen,data):
        _CalcCRC=0
        
        _datam = data[1:datalen-3]
        for i in range(0,datalen-4):
            _CalcCRC=_CalcCRC^struct.unpack("!B",_datam[i])[0]           
           
        if _CalcCRC != struct.unpack("!B",data[datalen-2])[0]:
            print "LOOP crc is wrong,_CalcCRC:,data[datalen-2]",_CalcCRC,\
                struct.unpack("!B",data[datalen-2])[0]
            return False
    
        return True 

if __name__ == '__main__':
    tps = TPSim( 'tps', 1 )
    tps.deviceInit( varFile = r'./TPConfig/setting/tps_variant.xml', \
            msgFile = r'./TPConfig/setting/tps_message.xml', \
            netWorkFile = r'./TPConfig/setting/tps_networks.xml', \
            paraFile = r'./TPConfig/setting/tps_parameter_end1.xml', \
            track_map = r'./datafile/atpCpu1Binary.txt', \
            train_route = r'./scenario/train_route.xml', \
            track_maptxt = r'./datafile/atpText.txt', \
            log = r'./log/tps.log' )
    print 'dev para', tps.getParaDic()