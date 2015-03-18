#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     zc.py
# Description:  zc设备仿真     
# Author:       Kunpeng Xiong
# Version:      0.0.1
# Created:      2011-07-13
# Company:      CASCO
# LastChange:   date 2011-07-25
# History:          
#               update 2011-07-25 根据新格式修改原来的zc程序
#               update 2011-08-01 添加新log的支持
#----------------------------------------------------------------------------
from base.loglog import LogLog
from base.basedevice import BaseDevice
#from base.databaseparse import DataTrackMap
from base import simdata
from base.senariopreproccess import Senariopreproccess
from base import commlib
from base.xmlparser import XmlParser
import sys
import struct
import binascii
from lxml import etree
import safetylayerdll
from base.xmldeal import XMLDeal

class ZC( BaseDevice ):
    """
    ZC Simulator
    """
    #平台内部传递的消息，所带的消息头，loophour,msgId
    msgHead = '!IH'
    
    #Simulator消息ID
    simulatorID = 99
    
    #周期更新消息ID
    cycleUpDataId = 92
    
    #初始化ID
    cycleStartID = 91
    
    #周期结束
    cycleEndID = 93
    
    #loophour初始化命令
    cycleIniloophour = 94
    
    #location report Message ID
    LRMesID = 9221
    
    #RS的定位信息ID
    RS_CoorID = 258
    #周期更新标志
    loophour = None
    
    """
    2011.12.10 重构删除
    #路径信息
    blocklist = []
    direct = 1
    startlocus = []
    trainLen = 0
    #列车开始的位置（相对block起点）
    __startPos = None

    
    #trackmap中所需的一些信息
    #格式(id,length,sectionId,SINGindex_up,SINGindex_down,singularity_nb,\
    #    nun,nunidx,nunSecid,nur,nuridx,nurSecid,ndn,ndnidx,ndnSecid,ndr,ndridx,ndrSecid)
    blockinfo = None #block相关信息
    #(type,id,abscissa,PERcomputedEnergy_up,PERcomputedEnergy_downAttribute,Orientation)
    Sings = None     #奇点相关信息
    #(PSDID,Side,SectionID,VariantRank,...)
    PSDs = None      #屏蔽门相关信息
    """    
    #脚本预处理
    Presenario = None
    V_Presenario = None
    
    #Linesection与sings的对应关系
    #{linesectionID:[singindex,...]...}
    LineSN_Sings = {}    
    
    #Variant scenario存放列表
    #[[block, abs, delay_cycle,[[LineSectionID,Index,value],...]]...]
    V_Scenario = []
    V_SceParser = {
            'pos':{'path':'.//Position',
                    'attr':['Block_id', 'Abscissa', 'Delay']
                  },
            'set':{'path':'.//Set',
                   'attr':['LineScetionID', 'Index', 'Value']
                }
            }
    Ini_Parser = {'Ini_LineSection':r'/Ini_Config/LineSection',
                  'Ini_Variant':r'.//Variant',
                  'attr_LineSection':( '@ID' ),
                  'attr_Variant':( '@Type', '@Index', '@EquipmentID', '@Value' )}
    
    var_type = {'int':int, 'string':str, 'float':float}
    #存储初始化配置信息
    #{LineSectionID:[variant_index,type,id,value],...}
    Variant_Ini_Config = {}
    
    #[start,end]:单位毫米
    __pos = None
    
    #log实例
    __log = None
    
    #奇点类型
    Variant_Type = {0:'Block',
                2:'SGL_PROTECTION_ZONE',
                6:'SGL_SIGNAL',
                7:'SGL_SIGNAL_BM_INIT',
                8:'SGL_SIGNAL_OVERLAP',
                9:'SGL_SIGNAL_OVERLAP_BM',
#                10:'SGL_OVERLAP_END',
                12:'SGL_PSD_ZONE'}
    
    #sacem checksum计算的的实例
    Sacemdll = None
    
    #ZC和CC之间的消息ID
    LocreportID = 64
    EOAreportID = 20
    VariantreportID = 30
    
    def __init__( self, name, id ):
        "init"
        BaseDevice.__init__( self, name, id )
        #self.__startPos = 0
    
    def logMes( self, level, mes ):
        " log mes"
        #LogLog.orderLogger(self.getDeviceName())
        self.__log.logMes( level, mes )
    
    def deviceInit( self, *args, **kwargs ):
        " ZC init"
        #实例化log
        self.__log = LogLog()
        self.__log.orderLogger( kwargs['log'], type( self ).__name__ )
        
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        self.__pos = None
        self.importVarint( kwargs['varFile'] )
        self.importMsg( kwargs['msgFile'] )
        self.importDefSce( kwargs['scenario'] )
#        print "deviceInit", kwargs['variant_scenario']
        self.importVarSce( kwargs['variant_scenario'] ) 
        
        #----------------2011.12.10重构删除---------------    
        #获得运行路径信息
        #self.blocklist, self.startlocus, self.direct , self.trainLen , self.cog_dir = \
        #commlib.loadTrainRout(kwargs['train_route'])
        #-----------------------------------------------

        #实例化脚本预处理
        self.Presenario = Senariopreproccess()
        #self.Presenario.getblockinfolist(kwargs['track_map'], kwargs['track_maptxt'])
        #self.defScenario = self.Presenario.getsortedscenario(self.defScenario, self.direct)
        self.defScenario = self.Presenario.getsortedscenario( self.defScenario, \
                                                             simdata.TrainRoute.getRouteDirection() )
        #----------------2011,。12.10重构删除-----------------
        #计算列车启动时相对于blocklist起点的位置（用于计算EOA的blockID以及横坐标时使用）
#        self.__startPos = self.Presenario.getabsolutedistancefromBlock(self.startlocus[0], \
#                                                                       self.startlocus[1], \
#                                                                       self.direct) + self.trainLen
        #self.Presenario.getblockinfolist(kwargs['track_map'], kwargs['track_maptxt'])
        #---------------------------------------------------
        
        #for variant
        self.V_Presenario = Senariopreproccess()
        #self.V_Presenario.getblockinfolist(kwargs['track_map'], kwargs['track_maptxt'])
        self.V_Scenario = self.V_Presenario.getsortedscenario( self.V_Scenario, \
                                                              simdata.TrainRoute.getRouteDirection() )
 
        #------------------------2011.12.10重构删除--------------------------
        #从trackMap中读入有用的数据
        #_trackMap = DataTrackMap()
        #_trackMap.loadTrackMapFile(kwargs['track_map'], kwargs['track_maptxt'])
        #获取Block信息
        #self.blockinfo = _trackMap.getBlocks()
        #print self.blockinfo
        #获取奇点信息
        #self.Sings = _trackMap.getSings()
        #print self.Sings
        #获取屏蔽门信息
        #self.PSDs = _trackMap.getPsds()    
        #print self.PSDs
        #------------------------------------------------------------------
        
        #计算Index的对应关系
        self.getLineSN_Sings()
        
        #将ZC发送给CC的信息的初始值读入__data中
        self.getVariantIni( kwargs['variniFile'] )
        #SacemDLL初始化
        self.Sacemdll = safetylayerdll.GM_SACEM_Dll( 'zc', kwargs["sacemFile"] )
        #SACEM DLL初始化
        if False == self.Sacemdll.SACEM_Init_Dll():
            self.logMes( 1, "SACEM Initializing failed!" ) 
       
        self.loophour = 1
        self.addDataKeyValue( 'loophour', self.loophour )
        
        #后面会改成有一个错误标志变量，为0 时表示初始化成功，反之失败
        return True

    #---------------------------------------------------------------------------
    #@读取zx_variant_ini.xml,并将消息组成一个字典，存入__data中
    #@该元素的格式：
    #@'Variant':{linsectionID:[value,....],},其中列表长度为224
    #---------------------------------------------------------------------------
    def getVariantIni( self, variantfile ):
        "get initialization variant"
        _Initree = etree.parse( variantfile )
        _variant_dic = {}
        _variant_dic_len = {}
        _variant_dic_Num = {}
        for _node in _Initree.xpath( self.Ini_Parser['Ini_LineSection'] ):
            _ini_var_list = [0] * 224  #初始化变量
            _key = -1    #LineSectionID
            #print self.Ini_Parser['Ini_LineSection']
            _para = _node.xpath( self.Ini_Parser['attr_LineSection'] )[0]
            _key = int( _para[0] )
            _maxIndex = -1
            _NumofVar = 0
            #解码Variant
            for _Linenode in _node.xpath( self.Ini_Parser['Ini_Variant'] ):
                #读取配置信息
                _para_index = int( _Linenode.xpath( "@Index" )[0] ) - 1 #从0开始
                #print _para_index
                _para_value = int( _Linenode.xpath( "@Value" )[0] )
                #将value存入对应的位置
                _ini_var_list[_para_index] = _para_value
                _NumofVar = _NumofVar + 1
                if _maxIndex < _para_index + 1:  #取最大的长度
                    _maxIndex = _para_index + 1
            #将数据压入字典中
            _variant_dic[_key] = _ini_var_list
            _variant_dic_len[_key] = _maxIndex
            _variant_dic_Num[_key] = _NumofVar
        self.addDataKeyValue( 'Variants', _variant_dic )
        #print 'Variant', _variant_dic
        self.addDataKeyValue( 'Variant_Len', _variant_dic_len )
        self.addDataKeyValue( 'Variant_Num', _variant_dic_Num )

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
        #self.logMes(4, '_head' + binascii.hexlify(_head))
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
        #self.logMes(4, '_head_list ' + repr(_head))
        return _head + self.unpackAppMsg( _head[1], msg[struct.calcsize( self.msgHead ):] )

    def deviceRun( self, *args, **kwargs ):
        "ZC run"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        #获得设备SSID，SSTYPE
        self.ZC_ID_TYPE = self.getDataValue( 'parDic' )['zc']
        self.CCNV_ID_TYPE = self.getDataValue( 'parDic' )['ccnv']
                
        while( 1 ):
            #获得消息，无消息是阻塞
            _msg = self.unpackAppMsgHasHead( self.inQ.get() )

            #车辆的位置消息，处理脚本
            #本周期经过该位置，按照delay cycle设置变量
            if _msg[1] == self.LRMesID: #location report
                #将数据存入__data中
                self.addLocaReportintoData( _msg[2:] )
                #进行计算，并组包发送，发送EOA+Variant给CC
                _CC_Head = struct.pack( self.msgHead, self.loophour, 7681 ) #生成头部
                _VariantMes = self.getVariantreport()
                _EOAMes = self.getEOAreport()
                _CC_Mes = _CC_Head + _VariantMes + _EOAMes
                #self.logMes(4, 'ZC to CC' + binascii.hexlify(_CC_Mes))
                if 1 == self.getDataValue( 'SendMesENABLE' ): #是否发送消息
                    self.getDataValue( 'siminQ' ).put( _CC_Mes )
                    if 1 == self.getDataValue( "SendZCMsgRepeatly" ):
                        self.getDataValue( 'siminQ' ).put( _CC_Mes )
                    #self.outQ.put(_CC_Mes)
                    
            if _msg[1] == self.RS_CoorID:
                #读取定位信息
                self.__pos = [_msg[3], _msg[4]]   #[start,end]:单位毫米
                self.addDataKeyValue( 'StartCoor', _msg[3] )
               
            #周期更新消息
            if _msg[1] == self.simulatorID:
                if _msg[2] == self.cycleUpDataId:
                    #检测值的更新
                    _change_EOA = self.Presenario.getNormalChangeItem( self.__pos, self.defScenario )
                    _change_Time = self.Presenario.getTimeChangeItem( self.loophour, self.TimeScenario )
                    _change_Variant = self.V_Presenario.getNormalChangeItem( self.__pos, self.V_Scenario )
                    for _eoadis in _change_EOA:
                        #重新设置可视距离，单位为m
                        _typename = self.getVarDic()[_eoadis[0]][0]
                        self.addDataKeyValue( _eoadis[0], self.var_type[_typename]( _eoadis[1] ) )
                        
                    for _t in _change_Time:
                        _typename = self.getVarDic()[_t[0]][0]
                        self.addDataKeyValue( _t[0], self.var_type[_typename]( _t[1] ) )
                    
                    #修改值    
                    if len( _change_Variant ) > 0:
                        _variant = self.getDataValue( 'Variants' )  #获取所有的变量的字典
                        for _Item in _change_Variant:  #_Item:[linesectionID,Index,value] 
                            #index是从1开始的，这里要减1
                            for _key in _variant:
                                if _key == int( _Item[0] ): #找到LinesectionID
                                    #修改对应的值
                                    _variant[_key][int( _Item[1] ) - 1] = int( _Item[2] )
                                    break #找到了，退出内部for,进行下一次值的修改
                        #更新__data中的Variants值
                        self.addDataKeyValue( 'Variants', _variant )
                    #周期更新loophour加1
                    self.loophour += 1
                    self.addDataKeyValue( 'loophour', self.loophour )                    
                    
                elif _msg[2] == self.cycleIniloophour:#loophour初始化
                    self.loophour = 1
                    self.addDataKeyValue( 'loophour', self.loophour )
                    
                elif _msg[2] == self.cycleEndID:
                    #self.logMes(4, 'ZC device end!')
                    break

        print "End ZC Running."

    #------------------------------------------------------------------------------
    #@根据__data中的'Variant'信息，获取variant包的数据信息
    #------------------------------------------------------------------------------
    def getVariantreport( self ):
        "get Variant report"
        _Variant = self.getDataValue( 'Variants' )
        _Len = self.getDataValue( 'Variant_Len' )
        _Num = self.getDataValue( 'Variant_Num' )
        _Mes = ""  #存储variant report 包
        for _key in _Variant:
            if _key not in [int( _i ) for _i in self.getDataValue( 'LineSecList' ).strip().split( "," )]:
                continue
            
            _MesID = 30
            _MesLen = _Len[_key] / 8 if _Len[_key] % 8 == 0 else _Len[_key] / 8 + 1
            _VarNum = _Num[_key]
            _tmpVar = _Variant[_key]
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
            _format = '!BHHB' + str( _MesLen ) + 'B' + 'I6B'
#            print '------------Variant:--------', _byte_Var
            #计算对每个Variant包计算两个checkSum
            _tmpVariants = [_key, _Len[_key]] + _tmpVar + [int( self.loophour / 3.36 ) + self.getDataValue( "detaCreateVariantTime" )] 
            if 1 == self.getDataValue( 'CheckSumENABLE_Var' ):
                self.ZC_ID_TYPE = self.getDataValue( 'parDic' )['zc']
                _checkSum = self.Sacemdll.SACEM_Tx_Msg_Dll( self.VariantreportID, \
                                                           self.ZC_ID_TYPE[0], \
                                                           self.ZC_ID_TYPE[2], \
                                                           self.CCNV_ID_TYPE[0], \
                                                           self.CCNV_ID_TYPE[2], \
                                                           _tmpVariants )
            else:
                _checkSum = ( 0, 0, 0, 0, 0, 0 )

#            _Var_Mes = [_MesID, 16 + _MesLen, _key, _Num[_key]] + \
#                          _byte_Var + [self.loophour] + list(_checkSum)
#            if 1 == _key:
#                continue
            _Var_Mes = [_MesID, 16 + _MesLen, _key, _Len[_key]] + \
                        _byte_Var + [int( self.loophour / 3.36 ) + self.getDataValue( "detaCreateVariantTime" )] + list( _checkSum )
#            self.logMes(4, 'Variant:' + repr(_tmpVar))                      
#            self.logMes(4, 'Variant:' + repr(_Var_Mes))
            if _Mes:
                _Mes = _Mes + struct.pack( _format, \
                                      *_Var_Mes )
            else:
                _Mes = struct.pack( _format, \
                                      *_Var_Mes )                
        return _Mes
            
    #------------------------------------------------------------------------------
    #@处理解码后的Location report，并将其存入__data中
    #@输入:LocaReportMes为location report的应用数据
    #------------------------------------------------------------------------------
    def addLocaReportintoData( self, LocaReportMes ):
        "add location report into __data"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )
        self.addDataKeyValue( 'TrainID', LocaReportMes[0] )
        self.addDataKeyValue( 'HCID', LocaReportMes[1] )
        self.addDataKeyValue( 'HCO', LocaReportMes[2] )
        self.addDataKeyValue( 'HLBID', LocaReportMes[3] )
        self.addDataKeyValue( 'HLMAbs', LocaReportMes[4] )
        self.addDataKeyValue( 'HCS', LocaReportMes[5] )
        self.addDataKeyValue( 'TCID', LocaReportMes[6] )
        self.addDataKeyValue( 'TCO', LocaReportMes[7] )
        self.addDataKeyValue( 'TLBID', LocaReportMes[8] )
        self.addDataKeyValue( 'TLMAbs', LocaReportMes[9] )
        self.addDataKeyValue( 'TCS', LocaReportMes[10] )
        self.addDataKeyValue( 'LocaError', LocaReportMes[11] )
        self.addDataKeyValue( 'LocaStatus', LocaReportMes[12] )
        self.addDataKeyValue( 'ConfLoca', LocaReportMes[13] )
        self.addDataKeyValue( 'ImmStatus', LocaReportMes[14] )
        self.addDataKeyValue( 'RSNNS', LocaReportMes[15] )
        self.addDataKeyValue( 'CorrDocking', LocaReportMes[16] )
        self.addDataKeyValue( 'Trainspeed', LocaReportMes[17] )
        self.addDataKeyValue( 'MoniMode', LocaReportMes[18] )
        self.addDataKeyValue( 'SigOverride', LocaReportMes[19] )
        self.addDataKeyValue( "ATCControlledTrain", LocaReportMes[20] ) #add by 191
        self.addDataKeyValue( 'ZC_Vital_Author', LocaReportMes[21] )
        self.addDataKeyValue( 'Boolean', LocaReportMes[22] )            #add by 191
        self.addDataKeyValue( 'CC_loophour', LocaReportMes[23] )
        self.addDataKeyValue( 'Synchordate', LocaReportMes[24] )
        self.addDataKeyValue( 'checksum1_1', LocaReportMes[25] )
        self.addDataKeyValue( 'checksum1_2', LocaReportMes[26] )
        self.addDataKeyValue( 'checksum1_3', LocaReportMes[27] )
        self.addDataKeyValue( 'checksum2_1', LocaReportMes[28] )
        self.addDataKeyValue( 'checksum2_2', LocaReportMes[29] )
        self.addDataKeyValue( 'checksum2_3', LocaReportMes[30] )
        tempMes = list( LocaReportMes[0:21] ) + \
                  commlib.transform_Hto16Bit( LocaReportMes[21] ) + \
                  commlib.transform_Hto16Bit( LocaReportMes[22] ) + \
                  list( LocaReportMes[23:] )
        self.logMes( 4, "locationreport1:" + repr( LocaReportMes ) )
        self.logMes( 4, "locationreport2:" + repr( tempMes ) )
        #print '------data:', self.CCNV_ID_TYPE[0], self.CCNV_ID_TYPE[2], self.ZC_ID_TYPE[0], self.ZC_ID_TYPE[2]
        self.ZC_ID_TYPE = self.getDataValue( 'parDic' )['zc']
        retcdw = self.Sacemdll.SACEM_Rx_Msg_Dll( self.LocreportID, \
                                                self.CCNV_ID_TYPE[0], \
                                                self.CCNV_ID_TYPE[2], \
                                                self.ZC_ID_TYPE[0], \
                                                self.ZC_ID_TYPE[2], \
                                                tempMes )                         
        if None == retcdw:
            self.logMes( 1, "Unpacking is failed!" ) 

    #------------------------------------------------------------------------------
    #@读入zc_variant_scenario.xml中的有关脚本信息，并存如变量V_secnario中
    #格式如下：[[BlockID,Absicssa,delay,[[linesectionID,Index,value],...]],...]
    #------------------------------------------------------------------------------           
    def importVarSce( self, VarsceFile ):
        "import Variant format scenario"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        self.V_Scenario = XMLDeal.importZCVarSce( VarsceFile )

    #---------------------------------------------------------
    #@根据当前位置，以及可视距离，计算可视的blockID,以及_Absicssa
    #@返回Block ID以及Abscissa
    #---------------------------------------------------------
    def getEOABIDandAbs( self ):
        "get Block ID and Abscissa in EOA report"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        #_direct = self.direct
#        _direct = simdata.TrainRoute.getRouteDirection()
        _distance = self.getDataValue( 'EOAdistance' )  #mm
        #_start = self.getDataValue('StartCoor') + self.__startPos  #转换为相对于blocklist的位置
        _start = self.getDataValue( 'StartCoor' ) + simdata.TrainRoute.getStartDistance() + simdata.TrainRoute.getTrainLength() #转换为相对于blocklist的位置
        #_Route_blocklist = self.Presenario.blockinfolist  #[[blockID,length],...]
        _Route_blocklist = simdata.TrainRoute.getBlockinfolist()  #[[blockID,length],...]
        #print _Route_blocklist
        _BlockID = None
        _Absicssa = None
        _Wholedistance = 0
        _Find = False
        for _B_info in _Route_blocklist:
            if ( _start + _distance < _Wholedistance + _B_info[1] ):#找到该block
                _Find = True
                _BlockID = _B_info[0]
                if 1 == _B_info[-1]:#_direct:
                    _Absicssa = _start + _distance - _Wholedistance
                elif -1 == _B_info[-1]: #_direct:
                    _Absicssa = _B_info[1] - ( _start + _distance - _Wholedistance )
                else:
                    self.logMes( 4, 'direct error!!' )
                _Find = True    
                break    
            _Wholedistance = _Wholedistance + _B_info[1]     
        
        if _Find:
            return _BlockID, int( 2 * _Absicssa / 1000.0 ) #需要转化为m 并乘2，单位为0.5m
        else:
            self.logMes( 4, 'Can not find the block ID and absicssa!!' )
            return None, None

    #------------------------------------------------------------------------------
    #@计算EOA report,返回压缩好的EOA数据包
    #------------------------------------------------------------------------------
    def getEOAreport( self ):
        "get EOA report"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        _MesID = 20
        _MesLen = 31
        #_TrainFrontEnd = self.getDataValue('HCID')
        #_EOA_type = 2
        _EOA_type = self.getDataValue( 'EOAtype' )
        _WSEOA_type= self.getDataValue("WOSEOAtype")
        if 0 == self.getDataValue( 'EOAModifyEnable' ):
            _TrainFrontEnd = self.getDataValue( 'HCID' )
            _EOA_location_BlockID, _EOA_location_Abs = self.getEOABIDandAbs()
            _WOS_EOA_location_BlockID, _WOS_EOA_location_Abs = _EOA_location_BlockID, _EOA_location_Abs
        else:
            _TrainFrontEnd = self.getDataValue( 'TrainFE' )
            _EOA_location_BlockID = self.getDataValue( 'EOABID' )
            _EOA_location_Abs = self.getDataValue( 'EOAAbs' )
            _WOS_EOA_location_BlockID = self.getDataValue( 'WOSEOABID' )
            _WOS_EOA_location_Abs = self.getDataValue( 'WOSEOAAbs' )            
        _CC_loophour = self.getDataValue( 'CC_loophour' )
        if None == _EOA_location_BlockID:
            self.logMes( 4, 'Error in calculate BlockID and Abs' )
            #return None
            #超出的时候，则发送最底端数据
            #_EOA_location_BlockID = self.Presenario.blockinfolist[-1][0]
            _EOA_location_BlockID = simdata.TrainRoute.getBlockinfolist()[-1][0]
            _EOA_location_Abs = \
            int( simdata.TrainRoute.getBlockinfolist()[-1][1] / 500.0 ) if 1 == simdata.TrainRoute.getRouteDirection() else 0            
            _WOS_EOA_location_BlockID, _WOS_EOA_location_Abs = _EOA_location_BlockID, _EOA_location_Abs
        #将相关数据存入__data中
        self.addDataKeyValue( 'EOAMesID', _MesID )
        self.addDataKeyValue( 'EOAMesLen', _MesLen )
        self.addDataKeyValue( 'TrainFE', _TrainFrontEnd )
        self.addDataKeyValue( 'EOAtype', _EOA_type )
        self.addDataKeyValue( 'EOABID', _EOA_location_BlockID )
        self.addDataKeyValue( 'EOAAbs', _EOA_location_Abs )
        self.addDataKeyValue( 'WOSEOAtype', _WSEOA_type )
        self.addDataKeyValue( 'WOSEOABID', _WOS_EOA_location_BlockID )
        self.addDataKeyValue( 'WOSEOAAbs', _WOS_EOA_location_Abs )
        self.addDataKeyValue( 'CCloophour', _CC_loophour )
        self.addDataKeyValue( 'ZCLHEOAV', int( self.loophour / 3.36 ) + self.getDataValue( "detaCreateZCLHEOAVTime" ) )
        self.addDataKeyValue( 'ZCLHEOA', int( ( self.loophour - 1 ) / 3.36 ) + self.getDataValue( "detaCreateZCLHEOATime" ) )
        self.addDataKeyValue( 'ZCLHWOSEOA', int( ( self.loophour - 1 ) / 3.36 ) + self.getDataValue( "detaCreateZCLHWOSEOATime" ) )
#        self.addDataKeyValue('EOACheckS1', 0)
#        self.addDataKeyValue('EOACheckS2', 0)
        #计算checkSum
        _tempEOA = [_TrainFrontEnd, _EOA_type, _EOA_location_BlockID, \
                    _EOA_location_Abs, _WSEOA_type, _WOS_EOA_location_BlockID, \
                    _WOS_EOA_location_Abs, self.getccloophour( _CC_loophour ) + self.getDataValue( 'detaccloophour' ), \
                    self.getDataValue( 'ZCLHEOAV' ), self.getDataValue( 'ZCLHEOA' ), \
                    self.getDataValue( 'ZCLHWOSEOA' )]
        
        if 1 == self.getDataValue( 'CheckSumENABLE_EOA' ):
            self.ZC_ID_TYPE = self.getDataValue( 'parDic' )['zc']
            _checksum = self.Sacemdll.SACEM_Tx_Msg_Dll( self.EOAreportID, \
                                                       self.ZC_ID_TYPE[0], \
                                                       self.ZC_ID_TYPE[2], \
                                                       self.CCNV_ID_TYPE[0], \
                                                       self.CCNV_ID_TYPE[2], \
                                                       _tempEOA )
        else:
            _checksum = ( 0, 0, 0, 0, 0, 0 )
            
        self.logMes( 4, 'zc EOA message:' + repr( [_TrainFrontEnd,
                               _EOA_type,
                               _EOA_location_BlockID,
                               _EOA_location_Abs,
                               _WSEOA_type,
                               _WOS_EOA_location_BlockID,
                               _WOS_EOA_location_Abs,
                               self.getccloophour( _CC_loophour ) + self.getDataValue( 'detaccloophour' ),
                               self.getDataValue( 'ZCLHEOAV' ),
                               self.getDataValue( 'ZCLHEOA' ),
                               self.getDataValue( 'ZCLHWOSEOA' )] ) )
        self.logMes( 4, repr( _checksum ) )
        _Mes = self.packAppMsg( _MesID, \
                               _MesID, \
                               _MesLen, \
                               _TrainFrontEnd, \
                               _EOA_type, \
                               _EOA_location_BlockID, \
                               _EOA_location_Abs, \
                               _WSEOA_type, \
                               _WOS_EOA_location_BlockID, \
                               _WOS_EOA_location_Abs, \
                               self.getccloophour( _CC_loophour ) + self.getDataValue( 'detaccloophour' ), \
                               self.getDataValue( 'ZCLHEOAV' ), \
                               self.getDataValue( 'ZCLHEOA' ), \
                               self.getDataValue( 'ZCLHWOSEOA' ), \
                               *_checksum )
        
        return _Mes
        
    #-------------------------------------------------------------------------------
    #@根据由trackmap获得的数据信息：
    #@：sing：奇点信息，Psd：屏蔽门信息，以及已经生成的self.LineSN_Sings
    #@生成需要进行配置的Variant的信息并存入XML文件
    #-------------------------------------------------------------------------------
    def createnewIniVariantXML( self, Ini_FilePath ):
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        #_PSDData = self.PSDs
        _PSDData = simdata.MapData.getPsdData()
        #sing = self.Sings
        sing = simdata.MapData.getSingData()
        #格式(id,length,sectionId,SINGindex_up,SINGindex_down,singularity_nb,\
        # nun,nunidx,nur,nuridx,ndn,ndnidx,ndr,ndridx)
        #_block = self.blockinfo
        _block = simdata.MapData.getBlockData()  
        _VariantIni = {}   #{LineSectionID,[[variant_index,type,id,value],...],...}
        _TmpInfo = [] 
                            
        for _Index in self.LineSN_Sings:
            _exist_Index = []  #存储Index,避免重复
            #设置NextBlock Variant
            for _B_Info in _block:
                #查看next block 的ndridx是否有效
                if ( _B_Info[-1] == _Index )and( _B_Info[-2] >= 0 ) and ( _B_Info[-2] not in _exist_Index ):
                    #print "_B_Info1:", _B_Info
                    _TmpInfo = [_B_Info[-2], 'Block', _B_Info[0], 1]
                    _exist_Index.append( _B_Info[-2] )
                    if _VariantIni.has_key( _Index ):
                        _VariantIni[_Index] = _VariantIni[_Index] + [_TmpInfo] #添加
                    else:
                        _VariantIni[_Index] = [_TmpInfo] #创建    
                #查看next block 的ndnidx是否有效        
                if ( _B_Info[-4] == _Index )and( _B_Info[-5] >= 0 ) and ( _B_Info[-5] not in _exist_Index ):
                    #print "_B_Info4:", _B_Info
                    _TmpInfo = [_B_Info[-5], 'Block', _B_Info[0], 1]
                    _exist_Index.append( _B_Info[-5] )
                    if _VariantIni.has_key( _Index ):
                        _VariantIni[_Index] = _VariantIni[_Index] + [_TmpInfo] #添加
                    else:
                        _VariantIni[_Index] = [_TmpInfo] #创建 
                #查看next block 的nuridx是否有效         
                if ( _B_Info[-7] == _Index )and( _B_Info[-8] >= 0 ) and ( _B_Info[-8] not in _exist_Index ):
                    #print "_B_Info7:", _B_Info
                    _TmpInfo = [_B_Info[-8], 'Block', _B_Info[0], 1]
                    _exist_Index.append( _B_Info[-8] )
                    if _VariantIni.has_key( _Index ):
                        _VariantIni[_Index] = _VariantIni[_Index] + [_TmpInfo] #添加
                    else:
                        _VariantIni[_Index] = [_TmpInfo] #创建 
                #查看next block 的nunidx是否有效         
                if ( _B_Info[-10] == _Index )and( _B_Info[-11] >= 0 ) and ( _B_Info[-11] not in _exist_Index ):
                    #print "_B_Info11:", _B_Info
                    _TmpInfo = [_B_Info[-11], 'Block', _B_Info[0], 1]
                    _exist_Index.append( _B_Info[-11] )
                    if _VariantIni.has_key( _Index ):
                        _VariantIni[_Index] = _VariantIni[_Index] + [_TmpInfo] #添加
                    else:
                        _VariantIni[_Index] = [_TmpInfo] #创建    
                
            for _i in self.LineSN_Sings[_Index]:
                if( ( sing[_i][-3] >= 0 )and ( sing[_i][-3] not in _exist_Index ) ) or ( 12 == sing[_i][0] ): #屏蔽门单独处理
                    
                    if( 2 == sing[_i][0] ): #SGL_PROTECTION_ZONE
                        _exist_Index.append( sing[_i][-3] )
                        _TmpInfo = [sing[_i][-3], 'SGL_PROTECTION_ZONE', sing[_i][1], 1]
                    elif( 6 == sing[_i][0] ): #SGL_SIGNAL
                        _exist_Index.append( sing[_i][-3] )
                        _TmpInfo = [sing[_i][-3], 'SGL_SIGNAL', sing[_i][1], 1]
                    elif( 7 == sing[_i][0] ): #SGL_SIGNAL_BM_INIT
                        _exist_Index.append( sing[_i][-3] )
                        _TmpInfo = [sing[_i][-3], 'SGL_SIGNAL_BM_INIT', sing[_i][1], 1]
                    elif( 8 == sing[_i][0] ): #SGL_SIGNAL_OVERLAP
                        _exist_Index.append( sing[_i][-3] )
                        _TmpInfo = [sing[_i][-3], 'SGL_SIGNAL_OVERLAP', sing[_i][1], 1]
                    elif( 9 == sing[_i][0] ): #SGL_SIGNAL_OVERLAP_BM
                        _exist_Index.append( sing[_i][-3] )
                        _TmpInfo = [sing[_i][-3], 'SGL_SIGNAL_OVERLAP_BM', sing[_i][1], 1]
#                    elif(10 == sing[_i][0]): #SGL_OVERLAP_END
#                        _exist_Index.append(sing[_i][-2])
#                        _TmpInfo = [sing[_i][-2], 'SGL_OVERLAP_END', sing[_i][1], 1]
                    elif( 12 == sing[_i][0] ): #SGL_PSD_ZONE
                        #PSD类型的Index不是倒数第二位表示，需要到PSD的数据中去寻找
                        #print sing[_i][1]
                        _PSDIndex = self.getPsdVariantIndex( sing[_i][1] )
                        if  _PSDIndex in _exist_Index: #去掉重复的
                            continue
                        
                        _exist_Index.append( _PSDIndex )
                        _TmpInfo = [_PSDIndex, 'SGL_PSD_ZONE', sing[_i][1], 1]
                    if( sing[_i][0] in [2, 6, 7, 8, 9, 12] ):
                        if _VariantIni.has_key( _Index ):
                            _VariantIni[_Index] = _VariantIni[_Index] + [_TmpInfo] #添加
                        else:
                            _VariantIni[_Index] = [_TmpInfo] #创建
        
        #将获得的数据存入XML
        self.SaveVariant_inidata( _VariantIni, Ini_FilePath )
    
    #---------------------------------------------------------------------
    #@从根据PSDID到PSD区域中去找变量存放的地址Index
    # psds:[PSDID,Side,SectionID,VariantRank,ManageTypeID,SubsystemTypeID,\
    #       SubsystemID,LOGID,DoorOpeningCode,...]
    #---------------------------------------------------------------------
    def getPsdVariantIndex( self, _PSDID ):
        "从PSD数据中获取PSDIndex"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        #for _Data in self.PSDs:
        for _Data in simdata.MapData.getPsdData():
            if ( _PSDID == _Data[0] ):
                #print "----------------------------------------------------------"
                return _Data[3]
        
        return -1 #未找到返回-1


    #--------------------------------------------
    #将相关变量储存值XML
    #@将变量VariantInfo:{LineSectionID:[[variant_index,type,id,value],...],...}
    #@存储到XML中
    #-------------------------------------------    
    def SaveVariant_inidata( self, VariantIni, Ini_FilePath ):
        "保存通过分析trackmap获得的variant信息"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        _Ini_file = open( Ini_FilePath, 'w' )
        #_Ini_file.write(r'<?xml version="1.0" encoding="utf-8"?>\n') #添加头
        #创建XML根节点
        _Ini_Config = etree.Element( "Ini_Config" )
        
        for _KeyID in VariantIni:
            _Varsorted = VariantIni[_KeyID]
            _Varsorted = sorted( _Varsorted, key = lambda _Varsorted:_Varsorted[0] )
            _LineSection = etree.SubElement( _Ini_Config, "LineSection" )
            _LineSection.set( "ID", str( _KeyID ) )
            #写入每个LineSection中的数据
            for _Var in _Varsorted:
                _Variant = etree.SubElement( _LineSection, "Variant" )
                _Variant.set( "Type", _Var[1] ) #类型
                _Variant.set( "Index", str( _Var[0] ) )    #索引
                _Variant.set( "EquipmentID", str( _Var[2] ) ) #设备ID
                _Variant.set( "Value", str( _Var[3] ) )  #初始化值

        _Config_String = etree.tostring( _Ini_Config, pretty_print = True, encoding = "utf-8" )           
        _Ini_file.write( r'''<?xml version="1.0" encoding="utf-8"?>''' ) #保存数据
        _Ini_file.write( "\n" ) #保存数据
        _Ini_file.write( _Config_String ) #保存数据
        _Ini_file.close()
        
         
    #--------------------------------------------------------------------
    #根据Block信息获取LineSN_Sings
    #@_Block:trackMap的Block信息,形式如下：
    #[[id,length,sectionId,SINGindex_up,SINGindex_down,singularity_nb,\
    #  nun,nunidx,nur,nuridx,ndn,ndnidx,ndr,ndridx],...]
    #--------------------------------------------------------------------
    def getLineSN_Sings( self ):
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        #_Block = self.blockinfo
        _Block = simdata.MapData.getBlockData()
        self.LineSN_Sings = {}
        _Sing_up_Index = 0
        _Sing_NUM = 0
        for _B_Info in _Block:
            _Sing_up_Index = _B_Info[3]
            _Sing_NUM = _B_Info[5]
            if _Sing_NUM > 0:
                for _i in range( _Sing_up_Index, _Sing_up_Index + _Sing_NUM ):
                    _sectionid = simdata.MapData.getSingData()[_i][-1]
                    if -1 == _sectionid:
                        continue                                
                    if self.LineSN_Sings.has_key( _sectionid ):
                        self.LineSN_Sings[_sectionid] = self.LineSN_Sings[_sectionid] + [_i] #拼接列表
                    else:
                        self.LineSN_Sings[_sectionid] = [_i] #创建新成员

    #-------------------------------------------------------------------
    #@获取发送的ccloophour，该值将根据ResponseEND进行判断处理
    #-------------------------------------------------------------------
    def getccloophour( self, ccloophour ):
        "get cc loophour by response end"
#        if 1 == self.getDataValue( 'ResponseEND' ):
#            return ccloophour
#        elif 2 == self.getDataValue( 'ResponseEND' ):
#            return ccloophour - 1073741824 / 2  if ccloophour >= 1073741824 / 2 else ccloophour + 1073741824 / 2
#        else:
#            self.logMes( 1, 'Error Value : ResponseEND！！！' )
#            return None
        return commlib.getResponseCCLoophour( self.getDataValue( 'ResponseEND' ), ccloophour )

    def deviceEnd( self ):
        "device end"
        self.__log.fileclose()  
    
if __name__ == '__main__':
    #要先加载线路地图
    simdata.MapData.loadMapData( r'./datafile/atpCpu1Binary.txt', \
                                 r'./datafile/atpText.txt' )
    simdata.TrainRoute.loadTrainData( r'./scenario/train_route.xml' )
    
    zc = ZC( 'zc', 1 )
    zc.deviceInit( varFile = r'./setting/zc_variant.xml', \
                  msgFile = r'./setting/zc_message.xml', \
                  scenario = r'./scenario/zc_scenario.xml', \
                  variant_scenario = r'./scenario/zc_variant_scenario.xml', \
                  variniFile = r'./scenario/zc_variant_ini.xml', \
                  log = r'./log/zc.log' )
    #print 'over device init'
    #print 'data dic', zc.getDataDic()
    #print 'var dic', zc.getVarDic()
    #print 'msg dic', zc.getMsgDic()
    #print 'def scenario', zc.defScenario
    #print 'Var scenario', zc.V_Scenario

    zc.createnewIniVariantXML( r'./setting/zc_variant_ini.xml' )
    print 'create zc_variant_ini.xml!'
#    print zc.getDataValue('Variants')
#    print zc.getDataValue('Variant_Len')
#    print binascii.hexlify(zc.getEOAreport())
