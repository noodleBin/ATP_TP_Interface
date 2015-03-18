#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     tsdevice.py
# Description:  轨旁仿真设备     
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      date
# Company:      CASCO
# LastChange:   
# History:      2011-08-09          
#               updata:2011-04-12
#               更新读trackMap数据
#               updata 2011-07-25
#               更新deviceInit方法
#               updata 2011-08-09
#               更新获取信标的方式，采用绝对坐标
#----------------------------------------------------------------------------
import sys
import struct
from base.loglog import LogLog
from base.basedevice import BaseDevice
#from base.databaseparse import DataTrackMap
from base.senariopreproccess import Senariopreproccess
from base import simdata
#from line import Line
from block import Block
from track import Track
from beacon import Beacon
from lxml import etree
from base import commlib
import binascii

# --------------------------------------------------------------------------
##
# @Brief 设备属性，省略name, id; 与从xml文件中读取的设备数据对应
# --------------------------------------------------------------------------
#DEVICE = {  
            #'data_type':['Lines','Depots','Mainlines','Tracks','Blocks','Beacons'],
            #'class_type':['Lines','Tracks','Blocks','Beacons'],
            #'attr':{'Lines':[],
                    #'Tracks':['type','kp_b','kp_e'],
                    #'Blocks':['t_id','sdd','p_id','kp_b','kp_e','nun','ndn','nur','ndr'],
                    #'Beacons':['t_id','kp','type','dir','cbtc','bm','tid']
            #}
        #}

# --------------------------------------------------------------------------
#tracksider中表示的列车运行方向
#direction 1-up -1-down
#距离单位毫米
# --------------------------------------------------------------------------


#Beacon的属性
# dire   0-up 1-down 2-all
# type  NONE_BEACON = 0,
#       MTIB        = 1,
#       STIB        = 2,
#       RB          = 3,
#       BMB         = 4 
# b_id  所在block的id
# kp_i 在这个abscissa中的坐标，单位厘米
DEVICE = {  
            'data_type':['Blocks', 'Beacons'],
            'class_type':['Blocks', 'Beacons'],
            'attr':{'Blocks':['id', 'length', 'sectionId', 'SINGindex_up', 'SINGindex_down', \
                              'singularity_nb', 'nun', 'nunidx', 'nunSecid', 'nur', 'nuridx', 'nurSecid', 'ndn', 'ndnidx', \
                              'ndnSecid', 'ndr', 'ndridx', 'ndrSecid'],
                    'Beacons':['id', 'type', 'b_id', 'kp_i', 'dire']
            }
        }

# --------------------------------------------------------------------------
##
# @Brief 项目数据配置
# --------------------------------------------------------------------------
PROJECT = {'BJFS':{'line':{1:'Mainlines', #线路号和线路名称的对应关系
                           2:'Depots'}
            }
    }

class TrackSider( BaseDevice ):
    """
    track sider simulator device
    """
    subNodes = {
                'Platform': ( 'Track_ID', 'Platform_Type', 'Stabling_Location_ID_Not_Defined', 'PSD_ID' )
                }
    
    myPlatforms = {}
    track_id_get_psd_id = {}
    myBlockStartPosition = {}
    
    #根据路径和方向生成的信标绝对位置[[pos,id,obj]...]
    beaconPos = None   
    loophour = None
    msgHead = None
    myLogger = None
    scePrepro = None
    cogDir = None
    #两个天线间的距离
    disBeTwoAnte = None
    #激活的车头到天线的距离
    activeCoreTOantenna = None

        
    def __init__( self, name, id ):
        "track sider init"
        BaseDevice.__init__( self, name, id )
    
    def get_another_end_position( self, _abs_postion ):
        _res = 0
        _deriction = self.getDrection()
        if _deriction == 1:     # up
            _res = _abs_postion - self.len_of_train
        else:       #0:down
            _res = _abs_postion + self.len_of_train
        
    
    def generate_abs_all_block_start_position( self ):
        #print '>>> generate_abs_all_block_start_position'
        _route = self.getRoute()
        _object_list = self.getDeviceObjList( 'Blocks', _route )
        _sum = 0
        for _item in _object_list:
            self.myBlockStartPosition[_item.getDeviceId()] = _sum
            _sum += _item.length()
        #print self.myBlockStartPosition
    
    def get_abs_displacement( self, _posi ):
        _beacon_id = _posi[0]
        _abscissa = _posi[1]
        return self.myBlockStartPosition[_beacon_id] + _abscissa
        
            
    def logMes( self, level, mes ):
        " log mes"
        self.myLogger.logMes( level, mes )
    
    def load_Platforms( self, filePath ):
        #print '>>> load_Platforms'
        tree = etree.parse( filePath )
        r = tree.xpath( self.nodePath['Platform'] )
        for node in r:   
            _key = ''
            _sub_key = ''
            _list = []
            for p in self.attributes['Platform']:  
                _para = node.xpath( p )                   
                if p[1:] == 'ID':
                    _key = str( _para[0] )
                else:
                    _list.append( str( _para[0] ) )

            _sublist = []
            for sub_node_name in self.subNodes['Platform']:
                #print sub_node_name           
                    #print subnode.text
                if len( node.xpath( sub_node_name ) ) == 0:
                    _sublist.append( '' )
                else:
                    _sublist.append( node.xpath( sub_node_name )[0].text )

            _list.append( _sublist )
            self.myPlatforms[_key] = _list 
            #print _list
            if self.track_id_get_psd_id.has_key( self.myPlatforms[_key][1][0] ) == False:                
                self.track_id_get_psd_id[self.myPlatforms[_key][1][0]] = []
            self.track_id_get_psd_id[self.myPlatforms[_key][1][0]].append( self.myPlatforms[_key][1][3] )

        #print self.myPlatforms
        #print self.track_id_get_psd_id
    
    def loadData( self ):
        "load trackMap data"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )

#        _f = DataTrackMap()
#        _f.loadTrackMapFile(fileName[0], fileName[1])
        self.addDataKeyValue( 'Blocks', simdata.MapData.getBlockData() )
        self.addDataKeyValue( 'Beacons', simdata.MapData.getBeaconData() )
        self.addDataKeyValue( 'Psds', simdata.MapData.getPsdData() )
        self.addDataKeyValue( 'Sings', simdata.MapData.getSingData() )

    # --------------------------------------------------------------------------
    ##
    # @Brief 实例化设备
    #
    # @Param deviceType 设备类型，数据字典中已经添加的设备key
    #
    # @Returns 设备实例列表 
    # --------------------------------------------------------------------------
    def instanceDevice( self, deviceType ):
        "device instanceing"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name + '.' + deviceType)
        _instance = None
        _class = None
        if deviceType == 'Tracks':
            _class = Track
        elif deviceType == 'Blocks':
            _class = Block
        elif deviceType == 'Beacons':
            _class = Beacon
        else:
            self.logMes( 1, 'deviceType %s is unknow' % ( deviceType ) )
        
        if _class:
            _value = self.getDataValue( deviceType )
            if _value:
                _instance = []
                for _v in _value:
                    #name,id
                    _ins = _class( deviceType[:-1] + '_' + str( _v[0] ), _v[0] )
                    if _ins.setManyKeyValue( DEVICE['attr'][deviceType], _v ) == False:
                                    self.logMes( 1, 'device %s instance error' % ( deviceType ) )
                    _instance.append( _ins )
            else:
                self.logMes( 1, 'device value %s is unknow' % ( deviceType ) )
        return _instance


    # --------------------------------------------------------------------------
    ##
    # @Brief 创建设备实例
    #
    # @Param devices 设备类别列表
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def createDevice( self, devices ):
        " create device and set device data"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name + '. ' + repr(devices))
        for deviceType in devices:
            #instance list
            _insList = self.instanceDevice( deviceType )
            self.attachDeviceObject( deviceType, _insList )
    
    def dispDevCon( self, deviceType ):
        " log object of device connect"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name + '.' + deviceType )
        for _s in self.getDevObjDic( deviceType ):
            self.logMes( 4, _s ) 
    
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 初始化项目线路数据,项目有几条线路，关联line和track
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def linesInit( self ):
        " attach track objects to line"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )

        #该项目的trackList object
        #_pto = self.getDeviceObjList('Tracks')
        #print '_pto', _pto 
        #该项目的LinesList object
        _plo = self.getDeviceObjList( 'Lines' ) 
        #print '_plo', _plo 
        for _l in _plo:
            #该线路的trackList Id 偏移[0][3]
            _ti = self.getDataValue( PROJECT[self.getDeviceName()]['line'][_l.getDeviceId()] )[0][3]
            #绑定该线路的tracList object into line object
            _l.attachDeviceObject( 'Tracks', self.getDeviceObjList( 'Tracks', _ti ) )
    
    def deviceInit( self, *args, **kwargs ):
            " trackSider init need to do"
            #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name + '.' + repr(args) + repr(kwargs))
            self.clearDataDic()
            self.myLogger = LogLog()
            self.myLogger.orderLogger( kwargs['log'], self.getDeviceName() )
            #load varFile msgFile scenarioFile
            self.importVarint( kwargs['varFile'] )
            self.importMsg( kwargs['msgFile'] )
            self.importDefSce( kwargs['scenario'] )
            #TODO:load beacon set file
            Beacon.BeaconDicinit()
            Beacon.loadBMBeacons( kwargs['bmBeaconFile'] )
            Beacon.loadBeaconMsgSetting( kwargs['bmBeaconMesFile'] )
             
            #self.logMes(4, 'var ' + repr(self.getVarDic()))
            #self.logMes(4, 'msg ' + repr(self.getMsgDic()))
            #self.logMes(4, 'scenario ' + repr(self.defScenario))
                                  
            #load project data
            self.loadData()
            #self.logMes(4, 'trackSider after loadData ' + 'name:' + repr(self.getDeviceName()) + 'id:' + repr(self.getDeviceId()) + 'dic:' + repr(self.getDataKeys()))

            #createDevice
            self.createDevice( DEVICE['class_type'] )
            #self.logMes(4, 'trackSider after createDevice ' + repr(self.getDataKeys()))
            
#            for _b in self.getDeviceObjList('Blocks'):
#                print 'block ',_b.getDataDic()
#                
#            for _b in self.getDeviceObjList('Beacons'):
#                print 'beacon ',_b.getDataDic() 
            
            self.onePassBeacon = []
            #线路初始化
            self.trackInit()
            
            for _b in self.getDeviceObjList( 'Beacons' ):
                _b.createBeaconMsg()
            
            #loophour,除车辆外其它设备的loophour从2开始
            self.loophour = 1            
            self.msgHead = self.getDataValue( 'msgHead' )
            
            self.disBeTwoAnte = self.getDataValue( 'disBeTwoAnte' )
            #_trainRoute = commlib.loadTrainRout(kwargs['trainRouteFile'])
            #self.activeCoreTOantenna = _trainRoute[3]
            self.activeCoreTOantenna = simdata.TrainRoute.getTrainLength()
            #_drec = _trainRoute[2]
            #self.cogDir = _trainRoute[4]
            self.cogDir = simdata.TrainRoute.getCogDirection()
            self.setDrection( simdata.TrainRoute.getRouteDirection() )
            #self.setRoute(_trainRoute[0])
            self.setRoute( simdata.TrainRoute.getRoute() )
            
            #按照绝对坐标构造线路
            self.beaconPos = []
            self.scePrepro = Senariopreproccess()
#            self.scePrepro.getblockinfolist( kwargs['trackMap'], kwargs['trackMaptxt'] )
            #获取psd的消息
            self.getPsdInfo()
            
            for _b in self.getDeviceObjList( 'Blocks', self.getRoute() ):
                for _bb in _b.getDeviceObjList( 'Beacons' ):
                    self.beaconPos.append( [self.scePrepro.getabsolutedistance( _b.getDeviceId(),
                                                                                _bb.getDataValue( 'kp_i' ) ) + \
                                                                                _bb.getDataValue( 'deta_beacon_distance' ),
                                          _bb.getDeviceId(), _bb] )
            #print 'beaconPos', self.beaconPos
            return True    


    # --------------------------------------------------------------------------
    ##
    # @Brief 关联设备—1到设备—2 例如关联blcoks 到 tracks
    #
    # @Param deviceType_1
    # @Param deviceType_2
    # @Param id_name deviceType_1 通过id_name属性对应的值确定绑定到具体的deviceType_2 
    # @Param sort_key 根据设备-1的sort_key属性的值排序
    # @Returns 
    # --------------------------------------------------------------------------
    def attachTwoDevice( self, deviceType_1, deviceType_2, id_name, sort_key ):
        " attach deviceType_1 into deviceType_2"
#        self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name + \
#                '.' + deviceType_1 + '.' + deviceType_2)
        
        #该项目的deviceType_1
        _bo = self.getDeviceObjList( deviceType_1 )

        #该项目中的deviceType_2
        _to = self.getDeviceObjList( deviceType_2 )
        #该项目中的 deviceType_2 和列表缓存 [(id,[]),(id,[])]
        _ti = [( _t.getDeviceId(), [] ) for _t in _to]

        for _b in _bo:
            _has = 0
            #print '_b' , id_name,_b.getDeviceName(),_b.getDeviceId(),_b.getDataValue(id_name)
            for _t in _ti:
                #print '_t', _t[0]
                if _t[0] == _b.getDataValue( id_name ):
                    _t[1].append( _b )
                    _has = 1
            if _has == 0:
                self.logMes( 1, type( self ).__name__ + '.' + sys._getframe().f_code.co_name + ' %s %s %d can not match' % ( deviceType_1, deviceType_2, _b.getDeviceId() ) )
        
        for _i, _tto in enumerate( _to ):
            #排序
            if len( _ti[_i][1] ) > 1:
                _ii = sorted( _ti[_i][1], key = lambda d: d.getDataValue( sort_key ) )
            else:
                _ii = _ti[_i][1]
            _tto.attachDeviceObject( deviceType_1, _ii )
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 关联beacon到block
    # @Returns 
    # --------------------------------------------------------------------------
    def trackInit( self ):
        " attach Beacons to Blocks"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        
        #绑定beacons to blocks
        self.attachTwoDevice( 'Beacons', 'Blocks', 'b_id', 'kp_i' )



    # --------------------------------------------------------------------------
    ##
    # @Brief 设置列车运行路径
    #
    # @Param blockLis block路径列表
    #
    # @Returns
    # --------------------------------------------------------------------------
    def setRoute( self, blockList ):
        " set train run route"
        self.addDataKeyValue( 'route', blockList )   
        #self.generate_beacon_list_route_based(blockList)
        #self.generate_abs_all_block_start_position()

    def getRoute( self ):
        " get route"
        return self.getDataValue( 'route' )
  
    # --------------------------------------------------------------------------
    ##
    # @Brief 设置列车运行方向
    #
    # @Param direction 1-up 0-down
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def setDrection( self, direction ):
        " set train move direction"
        self.addDataKeyValue( 'dire', direction )
    
    def getDrection( self ):
        " get train move direction"
        return self.getDataValue( 'dire' )


    # --------------------------------------------------------------------------
    ##
    # @Brief 从车辆仿真获取车辆一个周期的位移，单位毫米
    #
    # @Param abscissa_1 列车本周期开始位置
    # @Param abscissa_2 列车本周期结束位置
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def getTrainMove( self, abscissa_1, abscissa_2 ):
        " get one cycle train movement"
        self.trainMove = ( abscissa_1, abscissa_2, abscissa_1 - abscissa_2 )
    
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 判断一段位置内是否有信标
    #
    # @Param start 列车本周期开始位置
    # @Param end 列车本周期结束位置
    # @Param beaPos 信标位置
    # @Param rsdir 车辆运行的方向
    # @Param bdir 信标的方向
    #
    # @Returns True or None
    # --------------------------------------------------------------------------    
    def ifPassBeacon( self , start, end, beaPos, rsdir, bdir ):
        "if pass beacon"
        if ( beaPos >= start and beaPos <= end ) or ( beaPos <= start and beaPos >= end ):
            #print 'bdir', bdir, 'rsdir', rsdir
            #if bdir == 2 or (rsdir + bdir) in (0, 1):
            return True

        return False
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 根据列车的位置获得本周期进过的信标
    #
    # @Param abscissa_1 列车本周期开始位置
    # @Param abscissa_2 列车本周期结束位置
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def getOneCyclePass( self, start, end ):
        " get pass device one cycle"
        self.onePassBeacon = []
        self.onePassBeaconEnd = []
        
        _curRouteDir = self.getDrection()
        
        # 停车
        _curRsDir = 0
        if start < end:
            #前进 
            _curRsDir = _curRouteDir
        elif start > end:
            #后退
            _curRsDir = -1 * _curRouteDir
        
        _startTail = start - self.disBeTwoAnte * self.cogDir
        _endTail = end - self.disBeTwoAnte * self.cogDir
        #速度大于0.5米/秒时，才发信标
        if abs( start - end ) >= 50:    
            for _b in self.beaconPos:
                if 1 == _b[2].getDataValue( 'Disable' ):#不发送beacon消息
                    continue
                #车头
                if self.ifPassBeacon( start, end, _b[0], _curRsDir, _b[2].getDataValue( 'dire' ) ):
                    self.onePassBeacon.append( ( 0.001 * _b[0], \
                                                     _b[1], _b[2].getBeaMes() ) )
                #车尾巴
                if self.ifPassBeacon( _startTail, _endTail, _b[0], _curRsDir, _b[2].getDataValue( 'dire' ) ):
                    self.onePassBeaconEnd.append( ( 0.001 * _b[0], \
                                                     _b[1], _b[2].getBeaMes() ) )
    
    def deviceRun( self, *args, **kwargs ):
        " device runing "
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name + '.' + repr( args ) + repr( kwargs ) )
#        print 'ts running...'
        _msgDic = self.getMsgDic()
        
        #队列消息头offset
        _loopIndex = 0
        _msgIdIndex = 1
        _headLen = 2

        #RS位置消息
        _trainPosMsgId = self.getDataValue( 'train_pos_id' )
        _trainPosSubType = self.getDataValue( 'train_pos_type' )
        _trainSubIndex = _msgDic[_trainPosMsgId]['Subtype']
        _trainPosSIndex = _msgDic[_trainPosMsgId]['Coordinates_S']
        _trainPosEIndex = _msgDic[_trainPosMsgId]['Coordinates_E']

        #Beacon消息
        _beaconMsgId = self.getDataValue( 'beacon_mes_id' )
        _beaconSubType = self.getDataValue( 'beacon_mes_type' )
        _beaconSubIndex = _msgDic[_beaconMsgId]['subType']
        _beaconCoodIndex = _msgDic[_beaconMsgId]['Coordinates_offset']
        _beaconMesIndex = _msgDic[_beaconMsgId]['Message']
        
        while True:
            try:
                _msg = self.unpackAppMsgHasHead( self.inQ.get() )
                #self.logMes(4, 'recv mes:' + repr(_msg))
            except struct.error, e:
                self.logMes( 1, 'unpack message error:' + e )
            
            #rs位置消息
#            if _msg[_msgIdIndex] == _trainPosMsgId:
#                if _msg[_headLen:][_trainSubIndex] == _trainPosSubType:
#                    self.logMes( 4, 'Train head:' + repr( _msg[_headLen:][_trainPosSIndex] ) + ':' + repr( _msg[_headLen:][_trainPosEIndex] ) )
#                    self.logMes( 4, 'Train head:' + \
#                                 repr( self.scePrepro.getBlockandAbs( _msg[_headLen:][_trainPosSIndex] ) ) + ':' \
#                                 + repr( self.scePrepro.getBlockandAbs( _msg[_headLen:][_trainPosEIndex] ) ) )
#                                       
#                    self.getOneCyclePass( _msg[_headLen:][_trainPosSIndex], \
#                                         _msg[_headLen:][_trainPosEIndex] )
#                    
#                    if len( self.onePassBeacon ):
#                        #print 'beacon:', self.onePassBeacon
#                        for _beacon in self.onePassBeacon:
#                            self.logMes( 4, 'beacon dis:' + str( _beacon[0] ) + '-id-' + str( _beacon[1] ) )
#                            self.logMes( 4, 'beacon mes' + commlib.str2hexlify( _beacon[2] ) )
#                    
#                    if len( self.onePassBeaconEnd ):
#                        #print 'beacon_end:', self.onePassBeaconEnd
#                        for _beacon in self.onePassBeaconEnd:
#                            self.logMes( 4, 'beacon end dis:' + str( _beacon[0] ) + '-id-' + str( _beacon[1] ) )
##                            self.logMes(4, 'beacon end mes' + commlib.str2hexlify(_beacon[2]))                            
#                            if 'datp' in self.getDataValue( 'devDic' ).keys():
#                                self.getDataValue( 'devDic' )['datp'].inQ.put( self.packAppMsgHasHead( self.loophour, 514, 1, _beacon[1] ) )                  

                    
            if _msg[_msgIdIndex] == 99:
                if _msg[2] == 92:
                    self.loophour += 1
                    self.logMes( 4, '--loophour--' + str( self.loophour ) )
                    self.addDataKeyValue( 'loophour', self.loophour )
#                    #有beacon经过
#                    if len( self.onePassBeacon ):
#                        _beaconMes = ''
#                        for _beacon in self.onePassBeacon:
#                            _beaconMes += self.packAppMsg( _beaconMsgId,
#                                                          _beaconSubType, \
#                                                         _beacon[0], \
#                                                         _beacon[2] )  
#                                                    
#                        _head = struct.pack( '!IH', self.loophour, _beaconMsgId )                        
#                        self.outQ.put( _head + _beaconMes )
#                    else:
#                        self.outQ.put( "No Beacon" )
                elif _msg[2] == 94:
                    self.loophour = 1
                    self.addDataKeyValue( 'loophour', self.loophour )
                
                elif _msg[2] == 93:
                    self.outQ.put( "END Case" ) #发送结束用例消息
                    break
        print 'end ts running...'

    #-----------------------------------------------------------------------
    #为保证RS发出来的位置和TS发出来的信标位置准确对应，将信标的计算移入到RS中计算
    #这里通过调用该函数实现
    #startPos,endPos:开始和结束位置
    #-----------------------------------------------------------------------
    def getOneBeaconPassInTS( self, startPos, endPos ):
        "get one Beacon pass in tracksider"
        #计算在[startPos,endPos]是否经过信标，这个两边都取闭集合，在下位机取[startPos,endPos)
        self.getOneCyclePass( startPos, endPos )
                    
        if len( self.onePassBeacon ):
            #print 'beacon:', self.onePassBeacon
            for _beacon in self.onePassBeacon:
                self.logMes( 4, 'beacon dis:' + str( _beacon[0] ) + '-id-' + str( _beacon[1] ) )
                self.logMes( 4, 'beacon mes' + commlib.str2hexlify( _beacon[2] ) )
                    
        if len( self.onePassBeaconEnd ):
            #print 'beacon_end:', self.onePassBeaconEnd
            for _beacon in self.onePassBeaconEnd:
                self.logMes( 4, 'beacon end dis:' + str( _beacon[0] ) + '-id-' + str( _beacon[1] ) )
#               self.logMes(4, 'beacon end mes' + commlib.str2hexlify(_beacon[2]))                            
                if 'datp' in self.getDataValue( 'devDic' ).keys():
                    self.getDataValue( 'devDic' )['datp'].inQ.put( self.packAppMsgHasHead( self.loophour, 514, 1, _beacon[1] ) )                  

        #组包要发送的beacon消息
        #有beacon经过
        _beaconMes = ''
        if len( self.onePassBeacon ):
            for _beacon in self.onePassBeacon:
                _beaconMes += self.packAppMsg( self.getDataValue( 'beacon_mes_id' ),
                                               self.getDataValue( 'beacon_mes_type' ), \
                                               _beacon[0], \
                                               _beacon[2] )  
                                                    
                _head = struct.pack( '!IH', self.loophour, self.getDataValue( 'beacon_mes_id' ) )                        
                self.outQ.put( _head + _beaconMes )
        return _beaconMes  
        
        
    def deviceEnd( self, *args, **kwargs ):
        " device run end"
#        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name + '.' + repr( args ) + repr( kwargs ) ) 
        self.myLogger.fileclose()
    
    def deviceExcept( self, *args, **kwargs ):
        " device except"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name + '.' + repr( args ) + repr( kwargs ) )
    
    def packAppMsgHasHead( self, loophour, msgId, *args ):
        "packing message and add head"
        _head = struct.pack( self.msgHead, loophour, msgId )
        return _head + self.packAppMsg( msgId, *args )
    
    def unpackAppMsgHasHead( self, msg ):
        "unpacking message has head"
        _head = struct.unpack( self.msgHead, msg[0:struct.calcsize( self.msgHead )] )
        return _head + self.unpackAppMsg( _head[1], msg[struct.calcsize( self.msgHead ):] )    


    def generateBeaconXML( self, *args, **kwargs ):
        
#        trackmap = DataTrackMap()
#        trackmap.loadTrackMapFile(kwargs['trackMap'], kwargs['trackMaptxt'])
        _Bm_beacon_file = open( kwargs['bmBeaconFile'], 'w' )
        #创建XML根节点
        _BM_Beacon = etree.Element( "BM_Beacon" )    
        #_BM_beacons = trackmap.getBMBeacons()
        _BM_beacons = simdata.MapData.getBMBeaconData()
        #对BM Beacon按照Id进行排序
        _BM_beaconsorted = sorted( _BM_beacons , key = lambda _BM_beacons:_BM_beacons[0] )
    
        for _beacon in _BM_beaconsorted:
            #print _beacon
            _Beacon = etree.SubElement( _BM_Beacon, "Beacon" )
            _Beacon.set( "ID", str( _beacon[0] ) )
            if _beacon[1] == 0:
                _Beacon.set( "direction", "up" )
            elif _beacon[1] == 1:
                _Beacon.set( "direction", "down" )
            elif _beacon[1] == 2:
                _Beacon.set( "direction", "all" )
            else:
                _Beacon.set( "direction", "error direction" )
            _Beacon.set( "VARnumber", str( _beacon[2] ) )
            for _count in range( 0, 16 ):
                _Variant = etree.SubElement( _Beacon, "Variant" )
                _Variant.set( "Index", str( _count ) ) #变量ID
                if _count < _beacon[2]:
                    _Variant.set( "Value", '0' ) #变量Rank
                else:
                    _Variant.set( "Value", '-1' ) #变量Rank
        
        _Config_String = etree.tostring( _BM_Beacon, pretty_print = True )           
        
        _Bm_beacon_file.write( _Config_String ) #保存数据
        _Bm_beacon_file.close()  
        
    def displayBlockInfo( self ):
        #查看block,Beacons
        for _b in self.getDeviceObjList( 'Blocks' ):
            _strBlockDic = commlib.str2hexlify( str( _b.getDataDic() ) )
            #print _strId,_strDic
            self.logMes( 4, 'blocks ' + repr( _b.getDeviceId() ) + repr( _b.getDataDic() ) )
            for _bb in _b.getDeviceObjList( 'Beacons' ):
                _beaconMsg = commlib.str2hexlify( _bb.getDataDic()['msg'] )
                #print _beaconMsg
                self.logMes( 4, 'Beacons ' + repr( _bb.getDeviceId() ) + repr( _bb.getDataDic() ) )
                self.logMes( 4, 'BeaconMsg:' + _beaconMsg )
    #------------------------------------------------------------------
    #@根据trackmap信息获取中获取psd的相关信息，并存入全局列表中
    #__psdInfo = [[PsdId,start,end，side],...]
    #------------------------------------------------------------------
    def getPsdInfo( self ):
        "get psd info"
        self.__psdInfo = []
        #(id,length,sectionId,SINGindex_up,SINGindex_down,singularity_nb,\
        # nun,nunidx,nur,nuridx,ndn,ndnidx,ndr,ndridx)
#        _blocksInfo = self.getDataValue('Blocks')
#        _singsInfo = self.getDataValue('Sings')
#        _psdsInfo = self.getDataValue('Psds')
#        _blocklist = self.getRoute()
#        _direct = self.getDrection()
        _blocksInfo = simdata.MapData.getBlockData()
        _singsInfo = simdata.MapData.getSingData()
        _psdsInfo = simdata.MapData.getPsdData()
        _blocklist = self.getRoute()
        _direct = self.getDrection()
        
        _block2Psdsingindex = {} #找到所有的blocklist中的PSDSingsindex，blockid：[Index,...]
        for _b_id in _blocklist:
            for _block in _blocksInfo:
                if _b_id == _block[0]:
                    for _i in range( _block[3], _block[5] + _block[3] ):
                        if _singsInfo[_i][0] == 12: #屏蔽门
                            if _block2Psdsingindex.has_key( _b_id ):
                                _block2Psdsingindex[_b_id].append( _i )
                            else:
                                _block2Psdsingindex[_b_id] = [_i]
                    break #找到该ID跳出循环
                
        _psdtmpinfo = []  #[[psdID, coord], ...]
        #计算每个psd起始和终点的相对位置
        for _bid in _block2Psdsingindex:
            _psdlist = _block2Psdsingindex[_bid]
            for _index in _psdlist:
                #计算每个psd的位置
                _coord = self.scePrepro.getabsolutedistance( _bid, _singsInfo[_index][2] )
                _psdtmpinfo.append( [_singsInfo[_index][1], _coord] )
              
        #计算每个psd起始和终点的相对位置
        _psdInfo = []
        for _pinfotmp in _psdtmpinfo:
            _find = False
            for _i, _pinfo in  enumerate( _psdInfo ):
                if _pinfotmp[0] == _pinfo[0]:
                    _find = True
                    if _pinfotmp[1] > _pinfo[1]:
                        _pinfo.append( _pinfotmp[1] )
                    else:
                        _pinfo.append( _pinfo[1] )
                        _pinfo[1] = _pinfotmp[1]
            
            if _find == False:
                _psdInfo.append( _pinfotmp )  
          
        #添加是左侧还是右侧门信息
        for _pinfo in _psdInfo:
            for _p in _psdsInfo:
                if _pinfo[0] == _p[0]:
                    _tmp = _pinfo + [_p[1]]
                    self.__psdInfo.append( _tmp )
                    
        #print self.__psdInfo                        
            
        
        

if __name__ == '__main__':
    simdata.MapData.loadMapData( r'./datafile/atpCpu1Binary.txt', \
                                 r'./datafile/atpText.txt' )
    simdata.TrainRoute.loadTrainData( r'./scenario/train_route.xml' )
    t = TrackSider( 'ts', 1 )
    #t.deviceInit(xml_1='/home/bzhu/program/python/iTC/background_simu/datafile/BJFSL_SyDB_Chain1.xml', xml_2='/home/bzhu/program/python/iTC/background_simu/datafile/BJFS_All_lines_Beacon_Layout_File_v1.0.5.xml') 
    t.deviceInit( varFile = r'./setting/ts_variant.xml', \
                 msgFile = r'./setting/ts_message.xml', \
                 scenario = r'./scenario/ts_scenario.xml', \
                 bmBeaconFile = r'./scenario/bm_beacons.xml', \
                 bmBeaconMesFile = r'./scenario/beacon_msg_setting.xml', \
                 log = r'./log/ts.log', \
                 )
    
    



    #测试从RS收到的车辆位置消息
    
    #_locationMsg = [15, 0, 200000]
    #_packlocationMsg = t.packAppMsgHasHead( t.loophour, 258, *_locationMsg )
    #print 'pack Location message', len( _packlocationMsg ), binascii.hexlify( _packlocationMsg ) 
    #t.inQ.put( _packlocationMsg )
    #_locationMsg = [15, 200000, 500000]
#    _packlocationMsg = t.packAppMsgHasHead(t.loophour, 115, *_locationMsg)
#    print 'pack Location message', len(_packlocationMsg), binascii.hexlify(_packlocationMsg) 
#    t.inQ.put(_packlocationMsg)
#    t.deviceRun()
    
    #测试生成BM Beacon 的XML
    t.generateBeaconXML( trackMap = r'./datafile/atpCpu1Binary.txt', \
            bmBeaconFile = r'./setting/bm_beacons.xml',
            trackMaptxt = r'./datafile/atpText.txt' )
    t.displayBlockInfo()
    
