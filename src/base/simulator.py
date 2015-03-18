#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     simulator.py
# Description:  模拟器基础类      
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      2011-07-19
# Company:      CASCO
# LastChange:   
# History:      create 2011-07-19
#----------------------------------------------------------------------------
from basedevice import BaseDevice
from xmlparser import XmlParser 
from mthread import MThread
import socket
import select
import binascii
import struct
import serial
import time
from test.test_typechecks import Integer

class Simulator( BaseDevice ):
    """
    Simulator use for driving devices
    """
    
    #网络配置   
    __ipAddr = None
    __listen = None
    __chanel = None
    
    #socket
    __socket = None
    
    #device parameter
    __devPara = None
    
    listenThread = None
    
    maxMessageSize = 1024
    
    #控制是否监听
    __endFlag = None
    netWorkFile = {
            'ip':{'path':'.//IP_Address',
                'attr':['ID', 'Name', 'IP', 'Port', 'Location']},
            'serial':{'path':'.//Serial_Address',
                'attr':['ID', 'Name', 'COM', 'Rate']},
            'Listening':{'path':'.//Listening',
                'attr':['ID', 'Local_Addr_ID', 'Handle']},
            'channel':{'path':'.//Channel',
                'attr':['ID', 'Name', 'Local_Addr_ID', 'Remote_Addr_ID', 'Protocol']}
            }
    
    devParaFile = {'dev':{'path':'.//Dev',
                       'attr':['Name', 'SSTY', 'LogID', 'SSID']},
                'msg':{'path':'.//MsgID',
                       'attr':['ID', 'SRC', 'DST', 'RMSV', 'SIGV', 'APPT', 'MSGID']}}
    
    def __init__( self, name, id ):
        "default init"
        BaseDevice.__init__( self, name, id )
        self.__ipAddr = {}
        self.__serAddr = {}
        self.__listen = {}
        self.__chanel = {}
        self.__socket = []
        self.__serial=[]
        self.__devPara = {}
        self.__endFlag = True
    # --------------------------------------------------------------------------
    ##
    # @Brief 解析网络配置文件
    #
    # @Param netFile
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def importNetworkSetting( self, netFile ):
        "import networking setting file"
        _f = XmlParser()
        _f.loadXmlFile( netFile )
        # Serial_Address    
        _ser = _f.getAttrListManyElement(self.netWorkFile['serial']['path'],
                self.netWorkFile['serial']['attr'])
        for _i in _ser:
            self.__serAddr[_i[0]] = _i[1:]  
        #socket
        _lis = _f.getAttrListManyElement( self.netWorkFile['Listening']['path'],
                self.netWorkFile['Listening']['attr'] )
        for _s in _lis:
            self.__listen[_s[0]] = _s[1:]

        #channel
        _channel = _f.getAttrListManyElement( self.netWorkFile['channel']['path'],
                self.netWorkFile['channel']['attr'] )
        for _c in _channel:
            self.__chanel[_c[0]] = _c[1:]
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 创建socket绑定地址
    #
    # @Returns True or None
    # --------------------------------------------------------------------------
    def createSocket( self ):
        " create socket for local ip address"
        self.__socket = []
        for _d in self.__ipAddr:
            if self.__ipAddr[_d][3] == 'Local':
                try:
                    _sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
                    _sock.bind( ( self.__ipAddr[_d][1], int( self.__ipAddr[_d][2] ) ) )
                    self.__socket.append( [_d, _sock] ) 
                except socket.error, e:
                    print 'addr %s create socket error %s' % ( self.__ipAddr[_d][1], e )
        if len( self.__socket ) > 0:
            return True
        else:
            return None
        
    # --------------------------------------------------------------------------
    # #
    # @Brief 创建serial绑定地址
    #
    # @Returns True or None
    # --------------------------------------------------------------------------
    def createSerial(self):
        " create Serial port for local Serial"
        
        # print 'self.__serAddr:', self.__serAddr
        for _d in self.__serAddr:
            # print 'create Serial!!!!!!!!!!'

            try:
                _ser = serial.Serial()  # 建立端口
                _ser.port = int(self.__serAddr[_d][1])
                _ser.baudrate = int(self.__serAddr[_d][2])
                _ser.timeout = 0  # 非阻塞
                _ser.parity = serial.PARITY_NONE
                _ser.open()
                self.__serial.append([_d, _ser]) 

            except Exception, e:
                print 'addr %s create serial error %s' % (self.__serAddr[_d][1], e)
        if len(self.__serial) > 0:
#             print 'createSerial:self.__serial ',self.__serial
            return True
        else:
            return None
        
    # --------------------------------------------------------------------------
    # #
    # @Brief 通过指定的通道发送消息
    #
    # @Param channel
    # @Param data
    #
    # @Returns True or None
    # --------------------------------------------------------------------------
    def serialSend(self, channel, data):
        " send message by serial"
        if len(self.__serial) == 0:
            print 'warning no serial can be used'
            return False                  
        
        # 源serial可写
#        _serialList = [_ser]
#        _rs, _ws, _es = select.select([], _serialList, [])
        _Locallist=[]
        for key in self.__serAddr:
            _Locallist.append(key)

        if False ==channel in _Locallist:
            print 'change config file'
            return False

        _ser = self.__serial[channel-1][1]
        _sendtime = time.clock()

        try:
            _len=_ser.write(data)
#             print '******************send data len is: _sendmes:',_len,repr(data)
        except Exception, e:
            print 'serial:', ' send data error ', e
            return False
        return True
    
    #serial read.add by Jory
    def serialRev(self,channel,data):
        if len(self._serial)==0:
            print 'warning no serial can be used'
            return False
        _serIndex=[_s[0] for _s in self._serial].index(self._chanel[channel][1])
        _ser=self._serial[_serIndex][1]
        
        try:
            _ser.read(data)
        except Exception,e:
            print 'serial:',' send data error ',e
            return False
        return True
    
    def startListen( self ):
        " start listen local Addr"
        _Locallist=[]
        for key in self.__serAddr:
            _Locallist.append(key)

        _serialList = [_s[1] for _s in self.__serial if _s[0] in _Locallist]   #串口
        self.__endFlag = True   
        _loopdata=[]    
        _loopdataTer=[]
        while self.__endFlag:
            for va in _serialList:
                try:             
                    _rs=va.inWaiting()
                    
                    if _rs!=0:
#                         print '_rs:',_rs
                        _data = va.read(_rs)
                        #组包
#                         for item in _data:
#                             print 'item',struct.unpack("!B",item)[0]

#                         print '2_loopdata,struct.unpack("!B",_data[_rs-1])[0]',_loopdata,struct.unpack("!B",_data[_rs-1])[0]
                        
                        if 2==struct.unpack("!B",_data[0])[0]:
                            _loopdata=None
                            _loopdata=_data
#                             print '2_loopdata,struct.unpack("!B",_data[0])[0]',_loopdata,struct.unpack("!B",_data[0])[0]
                        elif 3==struct.unpack("!B",_data[_rs-1])[0]:
                            _loopdata+=_data
                            _loopdataTer=_loopdata
#                             print '<<<<<<<<<<<<<<<<<<<<<_loopdataTer,struct.unpack("!B",_data[_rs-1])[0]',_loopdataTer,struct.unpack("!B",_data[_rs-1])[0]
                               
#                             Handel function
                            _handelKey = self.__serial[_serialList.index(va)][0]
                            getattr(self, 'handle_' + str(self.__listen[_handelKey][1]), \
                                    self.defaultHandel)(_loopdataTer) 
                        else:
                            _loopdata+=_data
#                             print '000_loopdata',_loopdata
                        _data = None
                except:
#                     print 'inWaiting error'
                    continue                
        time.sleep(0.01)

        # 关闭串口
        for _ser in _serialList:
            if _ser.isOpen():
                _ser.close()
        print 'end Listening...'
        
    def startListenThread( self ):
        "create thread and listening"

        self.listenThread = MThread( self.startListen, '', 'sim_listening_thread' )
#        self.listenThread.isDaemon()
#        self.listenThread.setDaemon( True )
#        self.listenThread.start()
        self.listenThread.StartThread( "ABOVE_NORMAL" ) #监听线程的优先级要高一点
    
    def joinListenThread( self ):
        "Wait until the thread terminates"
        self.listenThread.join()
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 创建线程，并且将线程实例添加到字典，key-线程名
    #
    # @Returns True or None
    # --------------------------------------------------------------------------       
    def createThread( self, thread_func, thread_arg, thread_name ):
        "create thread and add instance of thread to dic"
        _thread = MThread( thread_func, thread_arg, thread_name )
#        _thread.isDaemon()
#        _thread.setDaemon( True )
        self.addDataKeyValue( thread_name, _thread )
        return None
    # --------------------------------------------------------------------------
    ##
    # @Brief 启动线程
    # @param thread_name: 线程名
    # @Returns True or None
    # --------------------------------------------------------------------------    
    def startThread( self, thread_name, Priorty = "NORMAL" ):
        "start thread by thread name"
        _thread = self.getDataValue( thread_name )
        if _thread:
            _thread.StartThread( Priorty )
        else:
            print 'warning thread name %s no this thread' % ( thread_name )
            return None
        return True
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 等待线程
    # @param thread_name: 线程名
    # @Returns True or None
    # --------------------------------------------------------------------------              
    def joinThread( self, thread_name ):
        "join thread by thread name"
        _thread = self.getDataValue( thread_name )
        if _thread:
            _thread.join()
        else:
            print 'warning thread name %s no this thread' % ( thread_name )
            return None
        return True
       
    # --------------------------------------------------------------------------
    ##
    # @Brief 通过指定的通道发送消息
    #
    # @Param channel
    # @Param data
    #
    # @Returns True or None
    # --------------------------------------------------------------------------
    def udpSend( self, channel, data ):
        " send message by udp socket"
        if len( self.__socket ) == 0:
            print 'warning no socket can be used'
            return None
        #查找源socket
        _sockInde = [_s[0] for _s in self.__socket].index( self.__chanel[channel][1] )
        _srcSock = self.__socket[_sockInde][1]                    
        
        #dstAddr
        _dst = self.__ipAddr[self.__chanel[channel][2]]
        if _dst[3] == 'Remote':
            _dstIP, _dstPort = _dst[1], _dst[2]
        else:
            return None

        #源socket可写
        _sockList = [_srcSock]
        _rs, _ws, _es = select.select( [], _sockList, [] )
         
        #send
        #print 'send socket ', _ws[0].getsockname(), 'dst ip %s port %s' % (_dstIP, _dstPort)
        try:
            _ws[0].sendto( data, ( _dstIP, int( _dstPort ) ) )
        except socket.error, e:
            print 'socket:', _ws[0].getsockname(), ' send data error ', e
            return None
        return True
    
            
    def importDevPara( self, paraFile ):
        "import device parameter file"
        _f = XmlParser()
        _f.loadXmlFile( paraFile )
        
        _para = _f.getAttrListManyElement( self.devParaFile['dev']['path'],
                self.devParaFile['dev']['attr'] )
        for _p in _para:
            self.__devPara[_p[0]] = [int( _i ) for _i in _p[1:4]]
            _tuple = tuple( [int( _i ) for _i in _p[1:4]] )
            self.__devPara[_tuple] = _p[0]
        
        _para = _f.getAttrListManyElement( self.devParaFile['msg']['path'],
                self.devParaFile['msg']['attr'] )
        for _p in _para:
            _tmp = _p[1:3]
            _tmp += [int( _i ) for _i in _p[3:7]]
            self.__devPara[int( _p[0] )] = _tmp
            _tuple = tuple( _p[1:3] + [int( _p[6] )] )
            #_tuple = tuple(_p[1:3])
            self.__devPara[_tuple] = int( _p[0] )
        return True
            
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 模拟器每个定时中断处理消息
    # 
    # @Param sn
    # @Param tpMsgid  平台内部消息ID
    # @Param mesLen 消息字节长度
    # @Param rmsID 冗余消息ID
    # @Param sigID 信号层消息ID
    # 
    # @Returns 
    # --------------------------------------------------------------------------    
    def packRmsSigHead( self, sn, tpMsgid, mesLen, rmsID, sigID, SrcLogID = None, SrcSSID = None, DstLogID = None, DstSSID = None ):
        " pack RMS and SIG by msgid"
        #print self.__devPara[tpMsgid][2:5], self.__devPara[self.__devPara[tpMsgid][0]], self.__devPara[self.__devPara[msgid][1]]
        _version, _itfver, _appType, _appMsgID = self.__devPara[tpMsgid][2:6]
        _src = self.__devPara[self.__devPara[tpMsgid][0]]
        _dst = self.__devPara[self.__devPara[tpMsgid][1]]
        
        #默认不进行修改，如果有修改则进行修改
        if None != SrcLogID:
            _src[1] = SrcLogID
        if None != SrcSSID:
            _src[2] = SrcSSID
        if None != DstLogID:
            _dst[1] = DstLogID
        if None != DstSSID:
            _dst[2] = DstSSID            
            
        try:
            _sig = self.packAppMsg( sigID, _itfver, mesLen, \
                               _src[0], _src[1], _src[2], \
                               _dst[0], _dst[1], _dst[2], \
                               0, 0, _appMsgID, _appType )
        
            _rms = self.packAppMsg( rmsID, _version, mesLen + struct.calcsize( self.getMsgDic()[sigID]['format'] ), \
                               _src[0] * 256 + _src[2], _dst[0] * 256 + _dst[2], sn )
        except struct.error, e:
            print 'packRmsSigHead error:', e
            return None
        return _rms + _sig
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 模拟器每个定时中断处理消息
    # 
    # @Param sn
    # @Param RMSID  冗余层信号ID
    # @Param SIGID  信号层ID
    # @Param Mes    冗余层和信号层数据
    # 
    # @Returns      解码好的冗余层和信号层数据
    # --------------------------------------------------------------------------    
    def unpackRmsSigHead( self, RMSID, SIGID, Mes ):
        " unpack RMS and SIG"
        _rmsLen = struct.calcsize( self.getMsgDic()[RMSID]['format'] )
        _sigLen = struct.calcsize( self.getMsgDic()[SIGID]['format'] )
        _rms = self.unpackAppMsg( RMSID, Mes[:_rmsLen] )
        _sig = self.unpackAppMsg( SIGID, Mes[_rmsLen:] )
        return _rms, _sig
    
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
        _head = struct.pack( self.queMsgHead, loophour, msgId )
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
        _head = struct.unpack( self.queMsgHead, msg[0:struct.calcsize( self.msgHead )] )
        return _head + self.unpackAppMsg( _head[1], msg[struct.calcsize( self.msgHead ):] )
   
    # --------------------------------------------------------------------------
    ##
    # @Brief 解析队列消息头
    #
    # @Param data
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def unPackQueHead( self, mes ):
        "unpacking queue head"
        return struct.unpack( self.queMsgHead, mes )

    # --------------------------------------------------------------------------
    ##
    # @Brief 打抱队列消息头
    #
    # @Param data
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def packQueHead( self, loophour, msgid ):
        "unpacking queue head"
        return struct.pack( self.queMsgHead, loophour, msgid )
    
    
    def getIPDic( self ):
        "get ip address dic"
        return self.__ipAddr
    
    def getListenDic( self ):
        "get listen socket dic"
        return self.__listen
    
    def getChanelDic( self ):
        "get channel dic"
        return self.__chanel
        
    def getParaDic( self ):
        "get channel dic"
        return self.__devPara
    
    def getSocketByLocalID( self, LocalID ):
        "get Socket By Local ID"
        #查找源socket
#        print LocalID
#        print [_s[0] for _s in self.__socket]
        _sockIndex = [_s[0] for _s in self.__socket].index( LocalID )
        return self.__socket[_sockIndex][1]
        
    def stopListen( self ):
        "stop listening"
        self.__endFlag = False
    
    def CloseAllSocket( self ):
        "close all socket."
        _socketList = [_s[1] for _s in self.__socket]
        
        for _socket in _socketList:
            _socket.close()        
        print "Close All Socket."

    # --------------------------------------------------------------------------
    ##
    # @Brief 默认消息处理方法，若未指定消息处理方法，该方法将被调用
    #
    # @Param data
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def defaultHandel( self, data ):
        " default message handle"
        if None == data:
            print 'empty data from atp!'
        else:
            print 'Warning this msg -- %s -- no special handle' % ( binascii.hexlify( data ) )
    

if __name__ == '__main__':
    s = Simulator( 'sim', 1 )
#    s.importNetworkSetting(r'../setting/tps_networks.xml')
    s.importDevPara( r'../setting/tps_parameter.xml' )
    print 'para dic', s.getParaDic()
#    s.createSocket()
    #s.startListenThread() 
#    s.udpSend('1', 'test')
    #s.udpSend('2', 'test')
    #s.udpSend('3', 'test')
    #s.joinListenThread()
