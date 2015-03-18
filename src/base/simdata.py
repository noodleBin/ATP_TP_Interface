#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     simdata.py
# Description:  用于读取平台的静态变量，以用于各个设备的读取      
# Author:       KunPeng Xiong
# Version:      0.0.1
# Created:      2011-12-09
# Company:      CASCO
# LastChange:   
# History:      create 2011-12-09
#               create 2012-06-01
#               修改支持Edit和Running同时进行的形式，两个之间不应该相互影响，此问题需要认真修改
#----------------------------------------------------------------------------
#from databaseparse import DataCCNVTrackMap
from xmldatabaseparse import CCDataBaseXmlParser
from xmldeal import XMLDeal
import os

class MapData():
    """
    Read TrackMap Data and Deal it to create some data for device
    """
    __blocks = {"Running":None, "Edit":None}
    __Zcs = {"Running":None, "Edit":None}
    __beacons = {"Running":None, "Edit":None}
    __BMbeacons = {"Running":None, "Edit":None}
    __Sings = {"Running":None, "Edit":None}
    __MTIBs = {"Running":None, "Edit":None}
    __Psds = {"Running":None, "Edit":None}
    __map = {"Running":None, "Edit":None}
    __Psd_Side_Dic = {"Running":None, "Edit":None}
    __VIOM_Port_Dic = {"Running":None, "Edit":None}
    __CIToZC_Dic = {"Running":None, "Edit":None}
    __ZCToCI_Dic = {"Running":None, "Edit":None}

    __binpath = {"Running":None, "Edit":None}
    __txtpath = {"Running":None, "Edit":None}
    
    __Block_CBI_Dic = {"Running":None, "Edit":None}
    def __init__( self ):
        pass
    
    @classmethod
    def loadMapData( cls, binpath, txtpath, Type = "Running" ):
        """
        binpath: binary trackmap path
        txtpath: text trackmap path
        """
        if None == cls.__map[Type] or\
           binpath != cls.__binpath[Type] or\
           txtpath != cls.__txtpath[Type]:  #只进行一次读取,路径改变也要重新读取
#            cls.__map[Type] = DataTrackMap() #改为读CCNV地图
#            cls.__map[Type] = DataCCNVTrackMap()
            cls.__map[Type] = CCDataBaseXmlParser() #改为读取xml文件
#            _folder, _tmp = os.path.split( binpath )
#            print "loadMapData", binpath
            cls.__map[Type].loadXMLFile( os.path.split( binpath )[0] )
#            cls.__map[Type].loadTrackMapFile( binpath, txtpath )
            
            #读取数据放入变量中
            cls.__blocks[Type] = cls.__map[Type].getBlocks()
            cls.__Zcs[Type] = cls.__map[Type].getZCs()
            cls.__beacons[Type] = cls.__map[Type].getBeacons()
            cls.__BMbeacons[Type] = cls.__map[Type].getBMBeacons()
            cls.__Sings[Type] = cls.__map[Type].getSings()
            cls.__MTIBs[Type] = cls.__map[Type].getMTIBs()
            cls.__Psds[Type] = cls.__map[Type].getPsds()
            cls.__VIOM_Port_Dic[Type] = cls.__map[Type].getVIOMPorts()
            cls.__ZCToCI_Dic[Type] = cls.__map[Type].getZCToCBIDic()
            cls.__CIToZC_Dic[Type] = cls.__map[Type].getCBIToZCDic()
            cls.__Psd_Side_Dic[Type] = cls.getPSD_Side_Dic( Type )
            cls.__Block_CBI_Dic[Type] = cls.__map[Type].getBlockCBIs()
            
            #关闭文件
#            cls.__map[Type].closeTrackMapFile()
            cls.__binpath[Type] = binpath
            cls.__txtpath[Type] = txtpath
    
    @classmethod
    def getPSD_Side_Dic( cls, Type = "Running" ):
        "get PSD id and side dic."
        _psd_side_dic = {} 
        for _psd in cls.getPsdData( Type ):
            if _psd[0] > 0: #有效的psdid
                _psd_side_dic[_psd[0]] = _psd[1]                
        return _psd_side_dic

    @classmethod
    def getPSDSide( cls, PSDid, Type = "Running" ):
        "get psd side from psdid." 
        try:
            return cls.__Psd_Side_Dic[Type][PSDid]
        except KeyError, e:
            print "getPSDSide Error", e
            return 0
        
    @classmethod
    def getBlockData( cls, Type = "Running" ):
        return cls.__blocks[Type] 
    
    @classmethod
    def getVIOMPortDic( cls, Type = "Running" ):
        return cls.__VIOM_Port_Dic[Type]
    
    @classmethod
    def getZcData( cls, Type = "Running" ): 
        return cls.__Zcs[Type]      
    
    @classmethod
    def getBeaconData( cls, Type = "Running" ): 
        return cls.__beacons[Type]

    @classmethod
    def getBMBeaconData( cls, Type = "Running" ): 
        return cls.__BMbeacons[Type]
        
    @classmethod
    def getSingData( cls, Type = "Running" ): 
        return cls.__Sings[Type] 
    
    @classmethod
    def getMTIBData( cls, Type = "Running" ): 
        return cls.__MTIBs[Type]  
    
    @classmethod
    def getPsdData( cls, Type = "Running" ): 
        return cls.__Psds[Type]  
    
    @classmethod
    def getBlockCBIDic( cls, Type = "Running" ):
        return cls.__Block_CBI_Dic[Type]
    
    @classmethod
    def getZCToCIDic( cls, Type = "Running" ):
        return cls.__ZCToCI_Dic[Type]

    @classmethod
    def getCIToZCDic( cls, Type = "Running" ):
        return cls.__CIToZC_Dic[Type]
    
    @classmethod
    def ClearData( cls, Type = "Running" ): 
        cls.__blocks[Type] = None
        cls.__Zcs[Type] = None
        cls.__beacons[Type] = None
        cls.__BMbeacons[Type] = None
        cls.__Sings[Type] = None
        cls.__MTIBs[Type] = None
        cls.__Psds[Type] = None 
        cls.__VIOM_Port_Dic[Type] = None 
        cls.__map[Type] = None               
        cls.__Block_CBI_Dic[Type] = None
        cls.__ZCToCI_Dic[Type] = None
        cls.__CIToZC_Dic[Type] = None     

class TrainRoute():
    """
    Read Train Route and save some data for device such as "rs"
    """
    __routeV = {"Running":None, "Edit":None}
    __startV = {"Running":None, "Edit":None}
    __direV = {"Running":None, "Edit":None}
    __trainLen = {"Running":None, "Edit":None}
    __Cog_dir = {"Running":None, "Edit":None}
    __blockinfolist = {"Running":None, "Edit":None}  #[[id,length,direction],...]
    __startdistance = {"Running":None, "Edit":None}
    
    def __init__( self ):
        pass

    
    #-------------------------------------------------------------------
    #根据连续两个block的id判断，从begin到endblock的beginblock上的坐标朝向
    #blockInfo为数据源
    #up:1
    #down:-1
    #-------------------------------------------------------------------
    @classmethod
    def getUpDownDirectionByBlockID( cls, beginBlockID, EndBlockID, blockInfo ):
        "get up down direction by block id"
        _rev = None
        
        for _blockitem in blockInfo: #查找ID
            if beginBlockID == _blockitem[0]: #找到
                if EndBlockID in [_blockitem[-12], _blockitem[-9]]:
                    _rev = 1
                elif EndBlockID in [_blockitem[-6], _blockitem[-3]]:
                    _rev = -1
                else:
                    print "getUpDownDirectionByBlockID Error!", beginBlockID, EndBlockID
                break #找到跳出循环        
        
        return _rev

    #-------------------------------------------------------------------
    #@根据trackmap中的block信息以及运行路径的blockIDlist获取bolckInfolist
    #@_blocklist:[blockID,...]
    #@_path:trackmap的file文件路径
    #@返回:[[blockid,length(mm),direction(1:up,-1:down)],...]
    #-------------------------------------------------------------------    
    @classmethod
    def CalBlockInfolist( cls, _blocklist, Type = "Running" ):
        _block = MapData.getBlockData( Type )
        if None == _block:
            print "未读取地图信息！"
        _blockinfolist = [] #初始化返回变量
        
        #计算self.blockinfolist
        for _B_ID in _blocklist:
            _tmpinfo = [] #临时变量，存储单个blockinfo
            _find = 0
            for _blockitem in _block: #查找ID
                if _B_ID == _blockitem[0]: #找到
                    _tmpinfo.append( _blockitem[0] )
                    _tmpinfo.append( _blockitem[1] )
                    _find = 1
                    break #找到跳出循环
            #对虚拟block的特殊处理
            if -1 == _B_ID: #为虚拟block
                _tmpinfo.append( -1 )
                _tmpinfo.append( 200000 ) #虚拟block的长度固定为200m
                _find = 1
                
            if 1 == _find:
                _blockinfolist.append( _tmpinfo )
            else:#添加代码，对应blockid=-1的情况
                _blockinfolist = None
                break #出错跳出循环
        
        #对每个block信息加入direct
        if 1 == len( _blockinfolist ):#只有一个block的时候采用设置的值
            _blockinfolist[0].append( cls.getRouteDirection( Type ) )
        elif len( _blockinfolist ) > 1:
            for _i, _info in enumerate( _blockinfolist ):
                if _i < len( _blockinfolist ) - 1:
                    _blockinfolist[_i].append( cls.getUpDownDirectionByBlockID( _blockinfolist[_i][0], _blockinfolist[_i + 1][0], _block ) )
                else:
                    _dir = 1 if -1 == cls.getUpDownDirectionByBlockID( _blockinfolist[_i][0], _blockinfolist[_i - 1][0], _block ) else -1
                    _blockinfolist[_i].append( _dir )
        #返回结果
        return _blockinfolist
    
    @classmethod
    def getBlockLength_05( cls, blockID, Type = "Running" ):
        "get block length."
        _length = None
        for _b in cls.getBlockinfolist( Type ):
            if blockID == _b[0]:
                _length = _b[1] / 500.0   #转换为0.5m为单位
            
        return _length

    #---------------------------------------------------------------------------
    #校验当前block朝当前方向走，的下一个block是否是灯泡的极点
    #输入：
    #startBlockID：当前block起点id
    #dir：搜索方向，方向有4个：1:up normal,2:up reverse,3:down normal,4:down reverse
    #blockInfo：block的数据信息
    #---------------------------------------------------------------------------
    @classmethod
    def checkIfBulbPole( cls, startBlockID, dir, blockInfo ):
        "check If Bulb Pole"
        _rev = False
        
        for _startblockitem in blockInfo: #查找ID
            if startBlockID == _startblockitem[0]: #找到
                _nextBlockId = None
                if 1 == dir:
                    _nextBlockId = _startblockitem[-12]
                elif 2 == dir:
                    _nextBlockId = _startblockitem[-9] 
                elif 3 == dir:
                    _nextBlockId = _startblockitem[-6]
                elif 4 == dir:
                    _nextBlockId = _startblockitem[-3]   
                            
                for _endblockitem in blockInfo: #查找ID
                    if _nextBlockId == _endblockitem[0]: #找到
                        _beginBlockId = None
                        if 1 == dir:
                            _beginBlockId = _endblockitem[-12]
                        elif 2 == dir:
                            _beginBlockId = _endblockitem[-9] 
                        elif 3 == dir:
                            _beginBlockId = _endblockitem[-6]
                        elif 4 == dir:
                            _beginBlockId = _endblockitem[-3]                          
                
                        if _beginBlockId == startBlockID:
                            _rev = True
                        break #找到跳出循环  

                break #找到跳出循环        
        
        return _rev        
    
    #---------------------------------------------------------------------------
    #根据起终点的blockID，获取一组blocklist,且blocklist的朝向必须是一个方向的
    #比如搜索一直朝UP方向或则down方向
    #这里要注意灯泡线的问题，在经过灯泡线的时候要转变方向
    #dir:-1:down,1:up
    #---------------------------------------------------------------------------
    @classmethod
    def getBlockListInfoByblockID( cls, startBlockId, endBlockId, dir, TurnFlag, Type = "Running" ):
        "get block list information by block ID"
        _rev = []
        if startBlockId == endBlockId: #已经搜索到终点
            return [[startBlockId]]
        _blocks = MapData.getBlockData( Type )
        #在block中搜索startBlockId
        for _bInfo in _blocks:
#            print _bInfo
            if startBlockId == _bInfo[0]:  #找到开始的blockID
                if 1 == dir: #up方向搜索
                    if -1 != _bInfo[-12]:#定位
#                        print _bInfo[-12]
                        dir = ( -1 ) * dir if TurnFlag else dir
                        _NormalBlockList = cls.getBlockListInfoByblockID( _bInfo[-12],
                                                                          endBlockId,
                                                                          dir,
                                                                          cls.checkIfBulbPole( _bInfo[-12], 1, _blocks ),
                                                                          Type )
                        for _tmpList in _NormalBlockList:
                            _rev.append( [startBlockId] + _tmpList )
                    if -1 != _bInfo[-9]:#反位
                        dir = ( -1 ) * dir if TurnFlag else dir
                        _ReverseBlockList = cls.getBlockListInfoByblockID( _bInfo[-9],
                                                                           endBlockId,
                                                                           dir,
                                                                           cls.checkIfBulbPole( _bInfo[-9], 2, _blocks ),
                                                                           Type )
                        for _tmpList in _ReverseBlockList:
                            _rev.append( [startBlockId] + _tmpList )
                elif -1 == dir: #down方向搜索           
                    if -1 != _bInfo[-6]:#定位
                        dir = ( -1 ) * dir if TurnFlag else dir
                        _NormalBlockList = cls.getBlockListInfoByblockID( _bInfo[-6],
                                                                          endBlockId,
                                                                          dir,
                                                                          cls.checkIfBulbPole( _bInfo[-6], 3, _blocks ),
                                                                          Type )
                        for _tmpList in _NormalBlockList:
                            _rev.append( [startBlockId] + _tmpList )
                    if -1 != _bInfo[-3]:#反位
                        dir = ( -1 ) * dir if TurnFlag else dir
                        _ReverseBlockList = cls.getBlockListInfoByblockID( _bInfo[-3],
                                                                           endBlockId,
                                                                           dir,
                                                                           cls.checkIfBulbPole( _bInfo[-3], 4, _blocks ),
                                                                           Type )
                        for _tmpList in _ReverseBlockList:
                            _rev.append( [startBlockId] + _tmpList )
                break
        
        return _rev
    
    #------------------------------------------------------------------------------
    #根据线路的blocklist获取与Block相关Variant的设置，也即输入类似[247,91,92,93,94,95]的设置
    #计算该条线路的定反位的变量的设置，具体返回如下：
    #返回格式[[linesectionID,Index,value],...]]
    #注：这里的blocklist一定要是存在的
    #根据发现的问题修改这部分：blocklist的正反向都要保证是这段线路
    #------------------------------------------------------------------------------
    @classmethod
    def getZCVariantAccordBlockInfoByBlockList( cls, blocklist, Type = "Running" ):
        "get ZC Variant According to Block Infomation By Block List"
        _rev = []
        _blocks = MapData.getBlockData( Type )
        #正向检查
        for _i in range( len( blocklist ) - 1 ):
            _startBlockId = blocklist[_i]
            _nextBlockId = blocklist[_i + 1]
            #在block中搜索BlockId
            for _bInfo in _blocks:
                if _startBlockId == _bInfo[0]:  #找到开始的blockID
                    if _nextBlockId == _bInfo[-12]:#up定位
                        if -1 != _bInfo[-11]:
                            _rev.append( [_bInfo[-10], _bInfo[-11], 1] )
                    else:
                        if -1 != _bInfo[-11]:
                            _rev.append( [_bInfo[-10], _bInfo[-11], 0] )                        
                            
                    if _nextBlockId == _bInfo[-9]:#up反位
                        if -1 != _bInfo[-8]:
                            _rev.append( [_bInfo[-7], _bInfo[-8], 1] )
                    else:
                        if -1 != _bInfo[-11]:
                            _rev.append( [_bInfo[-7], _bInfo[-8], 0] )   
                    if _nextBlockId == _bInfo[-6]:#down定位
                        if -1 != _bInfo[-5]:
                            _rev.append( [_bInfo[-4], _bInfo[-5], 1] )
                    else:
                        if -1 != _bInfo[-5]:
                            _rev.append( [_bInfo[-4], _bInfo[-5], 0] )
                    if _nextBlockId == _bInfo[-3]:#down反位
                        if -1 != _bInfo[-2]:
                            _rev.append( [_bInfo[-1], _bInfo[-2], 1] )
                    else:
                        if -1 != _bInfo[-2]:
                            _rev.append( [_bInfo[-1], _bInfo[-2], 0] )
                    break

        #反向检查
        _blocklist_reverse = [blocklist[len( blocklist ) - _i - 1] for _i in range( len( blocklist ) ) ]
#        print _blocklist_reverse
        for _i in range( len( _blocklist_reverse ) - 1 ):
            _startBlockId = _blocklist_reverse[_i]
            _nextBlockId = _blocklist_reverse[_i + 1]
            #在block中搜索BlockId
            for _bInfo in _blocks:
                if _startBlockId == _bInfo[0]:  #找到开始的blockID
                    if _nextBlockId == _bInfo[-12]:#up定位
                        if -1 != _bInfo[-11]:
                            _rev.append( [_bInfo[-10], _bInfo[-11], 1] )
                    else:
                        if -1 != _bInfo[-11]:
                            _rev.append( [_bInfo[-10], _bInfo[-11], 0] )                        
                            
                    if _nextBlockId == _bInfo[-9]:#up反位
                        if -1 != _bInfo[-8]:
                            _rev.append( [_bInfo[-7], _bInfo[-8], 1] )
                    else:
                        if -1 != _bInfo[-11]:
                            _rev.append( [_bInfo[-7], _bInfo[-8], 0] )   
                    if _nextBlockId == _bInfo[-6]:#down定位
                        if -1 != _bInfo[-5]:
                            _rev.append( [_bInfo[-4], _bInfo[-5], 1] )
                    else:
                        if -1 != _bInfo[-5]:
                            _rev.append( [_bInfo[-4], _bInfo[-5], 0] )
                    if _nextBlockId == _bInfo[-3]:#down反位
                        if -1 != _bInfo[-2]:
                            _rev.append( [_bInfo[-1], _bInfo[-2], 1] )
                    else:
                        if -1 != _bInfo[-2]:
                            _rev.append( [_bInfo[-1], _bInfo[-2], 0] )
                    break
        
        #将重复的合并，采用有赋值为1的则赋值为1
#        print _rev
        _revfinal = []
        _indexContentList = [] #存储已经有的[linesectionID,index]
        for _r in _rev:
            try:
                _indexfind = _indexContentList.index( _r[0:2] )
                #存在则看是否需要修改
#                print _r
                if 1 == _r[2]: #为的时候才覆盖
                    _revfinal[_indexfind][2] = 1
            except ValueError, e:
                #不存在则直接添加
                _indexContentList.append( _r[0:2] )
                _revfinal.append( _r )
            
        return _revfinal        
    
    
    #-----------------------------------------------------------------------
    #获取跑车情况下的各条SSA的相关信息
    #返回：[[SSAList,SSAinfoList],...]
    #-----------------------------------------------------------------------
    @classmethod
    def getAllSSAInfoInRunningMode( cls ):
        "get All SSA information in running mode"
        _rev = []
        for _info in cls.__RouteList["Running"]:
#            print cls.__RouteList["Running"]
#            print _info
            _rev.append( cls.getSSAInfoInBlockList( _info[0], _info[2], Type = "Running" ) )
             
        return _rev
    
    #-----------------------------------------------------------------------
    #通过地图获取，blocklist中的SSA区段，按照block的顺序排列
    #返回两个list，一个是SSAList,一个是SSA对应的属性：
    #[[[upStartblockId, upStartAbs], [upEndblockId, upEndAbs]], ...]
    #dir表示现在是up：1，还是down:-1方向
    #-----------------------------------------------------------------------
    @classmethod
    def getSSAInfoInBlockList( cls, blocklist, dir, Type = "Running" ):
        "get SSA information in block list"
        _Blocks = MapData.getBlockData( Type )
        _Sings = MapData.getSingData( Type )
        #先获取blocklist中所有的SSA相关的奇点
        _blockSSADic = {} #{blockid:[[SSAID,Abs,orientation]],...}
        for _blockId in blocklist:
            for _bInfo in _Blocks:
                if _blockId == _bInfo[0]:
                    _Sing_up_Index = _bInfo[3]
                    _Sing_NUM = _bInfo[5]                    
                    #搜奇点类型为16的
                    for _index in range( _Sing_up_Index, _Sing_up_Index + _Sing_NUM ):
                        if 16 == _Sings[_index][0]:
                            if _blockSSADic.has_key( _bInfo[0] ):
                                _blockSSADic[_bInfo[0]].append( [_Sings[_index][1], _Sings[_index][2], _Sings[_index][6] ] )
                            else:
                                _blockSSADic[_bInfo[0]] = [[_Sings[_index][1], _Sings[_index][2], _Sings[_index][6] ]] 
        
#        print _blockSSADic
        
        _tmpSSAdic = {} #{SSAID:[[upStartblockId,upStartAbs],[upEndblockId,upEndAbs]],...}
        for _blockid in _blockSSADic:
            for _ssaInfo in _blockSSADic[_blockid]:
                if _ssaInfo[-1] in [0, 1]: #是起始和终止奇点
                    if not _tmpSSAdic.has_key( _ssaInfo[0] ):
                        _tmpSSAdic[_ssaInfo[0]] = [None, None]
                    _tmpSSAdic[_ssaInfo[0]][_ssaInfo[-1]] = [_blockid, _ssaInfo[1]]    
                        
#        print _tmpSSAdic
        
        _revSSAList = []
        _revSSAInfoList = []
        #对SSA按照blocklist进行排序
        for _blockId in blocklist:
            if 1 == dir: #up
                for _ssa in _tmpSSAdic:
                    if _blockId == _tmpSSAdic[_ssa][0][0]:
                        #先查看是否已经有SSAID在这个block上面
                        if len( _revSSAList ) > 0 and _tmpSSAdic[_revSSAList[-1]][0][0] == _blockId:
                            #已经有则需要比较大小并插入当前的SSA
                            _Abs = _tmpSSAdic[_ssa][0][1]
                            _index = None
                            for _i, _info in  enumerate( _revSSAInfoList ):
                                if _blockId == _info[0][0]:
                                    if _Abs < _info[0][1]:
                                        _index = _i
                                        break
                            if  None == _index:
                                _revSSAList.append( _ssa )
                                _revSSAInfoList.append( _tmpSSAdic[_ssa] )
                            else:
                                _revSSAList.insert( _index, _ssa )
                                _revSSAInfoList.insert( _index, _tmpSSAdic[_ssa] )                               
                        else:
                            _revSSAList.append( _ssa )
                            _revSSAInfoList.append( _tmpSSAdic[_ssa] )
            elif -1 == dir:#down
                for _ssa in _tmpSSAdic:
                    if _blockId == _tmpSSAdic[_ssa][1][0]:
                        #先查看是否已经有SSAID在这个block上面
                        if len( _revSSAList ) > 0 and _tmpSSAdic[_revSSAList[-1]][1][0] == _blockId:
                            #已经有则需要比较大小并插入当前的SSA
                            _Abs = _tmpSSAdic[_ssa][1][1]
                            _index = None
                            for _i, _info in  enumerate( _revSSAInfoList ):
                                if _blockId == _info[1][0]:
                                    if _Abs < _info[1][1]:
                                        _index = _i
                                        break
                            if  None == _index:
                                _revSSAList.append( _ssa )
                                _revSSAInfoList.append( _tmpSSAdic[_ssa] )
                            else:
                                _revSSAList.insert( _index, _ssa )
                                _revSSAInfoList.insert( _index, _tmpSSAdic[_ssa] )                               
                        else:
                            _revSSAList.append( _ssa )
                            _revSSAInfoList.append( _tmpSSAdic[_ssa] )                
        return [_revSSAList, _revSSAInfoList]
		
    #------------------------------------------------------------------------------
    #根据线路的blocklist获取与跑车相关的所有Variant的设置，也即输入类似[247,91,92,93,94,95]的设置
    #计算该条线路的定反位的变量的设置，具体返回如下：
    #返回格式[[linesectionID,Index,value],...]]，这里除了Block外，其他
    #注：这里的blocklist一定要是存在的
    #------------------------------------------------------------------------------
    @classmethod
    def getAllCIVariantInfoInBlockList( cls, blocklist, Type = "Running" ):
        "get All CI Variant Infomation In the Block List"
        
        #[[linesectionID,Index,value],...]]
        _tmpZCVariantInfo = cls.getAllZCVariantInfoInBlockList( blocklist, Type = Type )
        _tmpZCToCIDic = MapData.getZCToCIDic( Type = Type )
        
        _tmpCIInfo = []
        for _variantInfo in _tmpZCVariantInfo:
            _tmpKey = ( _variantInfo[1], _variantInfo[0] )
            if _tmpZCToCIDic.has_key( _tmpKey ):
                _tmpCIInfo.append( [ _tmpZCToCIDic[_tmpKey][1], _tmpZCToCIDic[_tmpKey][0], _variantInfo[-1]] )
            else:
                print "getAllCIVariantInfoInBlockList Error:", _tmpKey
#        print "getAllCIVariantInfoInBlockList", _tmpCIInfo
        
        return _tmpCIInfo
                        
    #------------------------------------------------------------------------------
    #根据线路的blocklist获取与跑车相关的所有Variant的设置，也即输入类似[247,91,92,93,94,95]的设置
    #计算该条线路的定反位的变量的设置，具体返回如下：
    #返回格式[[linesectionID,Index,value],...]]，这里除了Block外，其他
    #注：这里的blocklist一定要是存在的
    #------------------------------------------------------------------------------
    @classmethod
    def getAllZCVariantInfoInBlockList( cls, blocklist, Type = "Running" ):
        "get All ZC Variant Infomation In the Block List"
        _rev = []
        #先获取与block相关的varaint
        _rev = cls.getZCVariantAccordBlockInfoByBlockList( blocklist, Type )
        
        #获取其他的
        #先找到在blocklist上的所有的几点的Index List
        _SingsIndexList = []
        _Blocks = MapData.getBlockData( Type )
        _Sings = MapData.getSingData( Type )
        for _B_Info in _Blocks:
            if _B_Info[0] in blocklist:
                _Sing_up_Index = _B_Info[3]
                _Sing_NUM = _B_Info[5]
                if _Sing_NUM > 0:
                    _SingsIndexList += range( _Sing_up_Index, _Sing_up_Index + _Sing_NUM )
#        print _SingsIndexList
        #寻找其中type在 
        #2:'SGL_PROTECTION_ZONE',
        #6:'SGL_SIGNAL',
        #7:'SGL_SIGNAL_BM_INIT',
        #8:'SGL_SIGNAL_OVERLAP',
        #9:'SGL_SIGNAL_OVERLAP_BM',
        #10:'SGL_OVERLAP_END'
        #12:'SGL_PSD_ZONE'
        #中的
        for _index in _SingsIndexList: #(type,id,abscissa,PERcomputedEnergy_up,PERcomputedEnergy_downAttribute,Attribute,Orientation,Section id)
            _sInfo = _Sings[_index]
            if _sInfo[0] in [2, 6, 7]:
#                print _sInfo
                if [_sInfo[-1], _sInfo[-3] , 1 ] not in _rev:
                    _rev.append( [_sInfo[-1], _sInfo[-3] , 1 ] )
            elif _sInfo[0] in [ 8, 9]:#带overlap的信号机
                _rev.append( [_sInfo[-1], _sInfo[-3] , 1 ] )
#            line_section = g_TrackMap.sings[signal_sid].section_id;
#            signal_var_idx = g_TrackMap.sings[signal_sid].Attribute;
#            overlap_var_idx = signal_var_idx + 1;
                #放入overlap
                _rev.append( [_sInfo[-1], _sInfo[-3] + 1 , 1 ] )
                
            elif 12 == _sInfo[0]:
#                print _sInfo
                _index = cls.getPsdVariantIndex( _sInfo[1], Type )
                if [_sInfo[-1], _index , 1 ] not in _rev: 
                    _rev.append( [_sInfo[-1], _index , 1 ] )
        
        return _rev    

    #---------------------------------------------------------------------
    #@从根据PSDID到PSD区域中去找变量存放的地址Index
    # psds:[PSDID,Side,SectionID,VariantRank,ManageTypeID,SubsystemTypeID,\
    #       SubsystemID,LOGID,DoorOpeningCode,...]
    #---------------------------------------------------------------------
    @classmethod
    def getPsdVariantIndex( cls, PSDID, Type = "Running" ):
        "从PSD数据中获取PSDIndex"
        for _Data in MapData.getPsdData( Type ):
            if ( PSDID == _Data[0] ):
                return _Data[3]
        
        return -1 #未找到返回-1
    
    #----------------------------------------------------------------
    #根据要设置的ZCVariant消息计算BM信标的相关位的状态
    #返回{BMBeaconId:[[index,value],...],...}
    #ZCVariantList:[[linesectionID,Index,value],...]]
    #blockList:运行线路
    #----------------------------------------------------------------
    @classmethod
    def getBMVariantInfoByZCVariantInfo( cls, blockList, ZCVariantList, Type = "Running" ):
        "get BM Variant Information By ZCVariant Infomation"
        _revDic = {}
        #先获取线路上的BM信标数
        _beaconList = MapData.getBeaconData( Type )
        _BMBeaconInfo = MapData.getBMBeaconData( Type )
        _BMBeacon_List = []
        for _bInfo in _beaconList: #(id,type,b_id,abscissa,dir)
#            print _bInfo[2], _bInfo[1], blockList
            if _bInfo[2] in blockList and 4 == _bInfo[1]: #在线路上的BM信标
                _BMBeacon_List.append( _bInfo[0] )
        
        
        _tmpZCVariantListInfo = [_Variant[0:2] for _Variant in ZCVariantList]
#        print _tmpZCVariantListInfo
#        print _BMBeacon_List
        #遍历BM信标，查看是否有需要修改的Index
        for _BmInfo in _BMBeaconInfo:
#            print _BmInfo
            if _BmInfo[0] in _BMBeacon_List:#在线路中
#                print _BmInfo
                for _index in range( _BmInfo[2] ): #变量个数
                    try:
#                        print _BmInfo[3 + _index * 3:5 + _index * 3]
                        _tmpindex = _tmpZCVariantListInfo.index( _BmInfo[3 + _index * 3:5 + _index * 3] )
                        if _revDic.has_key( _BmInfo[0] ):
                            _revDic[_BmInfo[0]].append( [_index, ZCVariantList[_tmpindex][-1]] )
                        else:
                            _revDic[_BmInfo[0]] = [[_index, ZCVariantList[_tmpindex][-1]]]
                    except ValueError, e:
#                        print "getBMVariantInfoByZCVariantInfo", e
                        pass
            
        return _revDic
        
    #---------------------------------------------------------
    #@根据当前_blockID，横坐标_absicssa(mm)，以及运行方向，获得绝对路径
    #@注：在调用本函数前，必须先计算出了__blockinfolist
    #@_direct:运行方向：由小坐标到大坐标为1，反之为-1
    #@返回绝对距离（相对于blocklist路径的起点的长度）
    #---------------------------------------------------------
    @classmethod
    def getabsolutedistancefromBlock( cls, _blockID, _absicssa, Type = "Running" ):
        "获取相对于block原点的绝对对路径函数"
        _distance = 0
        _find = 0
        for _info in cls.getBlockinfolist( Type ):
            if _blockID == _info[0]:
                if 1 == _info[-1]:#cls.getRouteDirection( Type ):
                    _distance = _distance + _absicssa
                elif -1 == _info[-1]: #cls.getRouteDirection( Type ):
                    _distance = _distance + ( _info[1] - _absicssa )
                else:
                    _distance = None #_direct错误
                _find = 1
                break
            else:
                if 1 == _info[-1]:#cls.getRouteDirection( Type ):
                    _distance = _distance + _info[1]
                elif -1 == _info[-1]:#cls.getRouteDirection( Type ):
                    _distance = _distance + _info[1]
                else:
                    _distance = None #_direct错误
                    break 
        #没找到则数据有误
        if _find == 0:
            _distance = None
        
        return _distance  #mm
    
    #---------------------------------------------------------
    #@根据当前_blockID，横坐标_absicssa，以及运行方向，计算相对于列车起始位置的距离
    #计算前__startdistance必须已经完成
    #@返回相对距离（相对于列车的起始位置路径的起点）
    #---------------------------------------------------------
    @classmethod
    def getabsolutedistance( cls, _blockID, _absicssa, Type = "Running" ):
        "获取相对于列车起始位置的绝对对路径函数"
        __distance = cls.getabsolutedistancefromBlock( _blockID, _absicssa, Type )
        
        if None == __distance:
            return None
        else:
            return __distance - cls.getStartDistance( Type ) - cls.getTrainLength( Type )


    #----------------------------------------------------------------------------
    #@根据相对于列车起始位置的距离，单位毫米，获取该位置的block ID以及abscissa(单位毫米)
    #----------------------------------------------------------------------------    
    @classmethod
    def getBlockandAbs( cls, absdistance, Type = "Running" ):
        "get block ID and Abscissa from absolute accordding to train start Position"
        _start = absdistance + cls.getStartDistance( Type ) + cls.getTrainLength( Type ) #转换为相对于blocklist的位置
        _Route_blocklist = cls.getBlockinfolist( Type ) #[[blockID,length,direction],...]
        _BlockID = None
        _Absicssa = None
        _Wholedistance = 0
        _Find = False
        for _B_info in _Route_blocklist:
            if ( _start < _Wholedistance + _B_info[1] ):#找到该block
                _Find = True
                _BlockID = _B_info[0]
                if 1 == _B_info[-1]:#cls.getRouteDirection( Type ):
                    _Absicssa = _start - _Wholedistance
                elif -1 == _B_info[-1]:#cls.getRouteDirection( Type ):
                    _Absicssa = _B_info[1] - ( _start - _Wholedistance )
                else:
                    print 'direct error!!！'
                _Find = True    
                break    
            _Wholedistance = _Wholedistance + _B_info[1]     
        
        if _Find:
            return _BlockID, _Absicssa  
        else:
            print 'Can not find the block ID and absicssa!!!'
            return None, None

    @classmethod
    def loadTrainData( cls, xmlpath, Type = "Running" ):
        """
        xmlpath: xml trackmap path
        """
        _rout = XMLDeal.importTrainRoute( xmlpath )
        #读取数据放入变量中
        cls.__routeV[Type] = _rout[0]
        cls.__startV[Type] = _rout[1]
        cls.__direV[Type] = _rout[2]
        cls.__trainLen[Type] = _rout[3]
        cls.__Cog_dir[Type] = _rout[4]
        cls.__blockinfolist[Type] = cls.CalBlockInfolist( cls.__routeV[Type], Type )
        #print cls.__blockinfolist[Type]
        cls.__startdistance[Type] = cls.getabsolutedistancefromBlock( cls.getStartBlockAbs( Type )[0], \
                                                                      cls.getStartBlockAbs( Type )[1],
                                                                      Type )
        
    @classmethod
    def getRoute( cls, Type = "Running" ):
        """
        [biockid,....]
        """
        return cls.__routeV[Type] 
    
    @classmethod
    def getStartBlockAbs( cls, Type = "Running" ):
        """
        [blockid,Absicass]
        """
        return cls.__startV[Type]    

    @classmethod
    def getRouteDirection( cls, Type = "Running" ):
        """
        1:up,-1:down
        """
        return cls.__direV[Type] 

    @classmethod
    def getTrainLength( cls, Type = "Running" ):
        """
        Train Length from end to antenna
        """
        return cls.__trainLen[Type]    

    @classmethod
    def getCogDirection( cls, Type = "Running" ):
        """
        cog direction,1>,-1<
        """
        return cls.__Cog_dir[Type]   

    @classmethod
    def getBlockinfolist( cls, Type = "Running" ):
        return cls.__blockinfolist[Type]
    
    @classmethod
    def getStartDistance( cls, Type = "Running" ):
        return cls.__startdistance[Type]    
    
    @classmethod
    def clearData( cls, Type = "Running" ):
        cls.__routeV[Type] = None
        cls.__startV[Type] = None
        cls.__direV[Type] = None
        cls.__trainLen[Type] = None
        cls.__Cog_dir[Type] = None
        cls.__blockinfolist[Type] = None   
        cls.__startdistance[Type] = None

    #----------------------------------------------------------------------------
    #@根据相对于列车起始位置的距离，单位毫米，获取当前与列车通信的CBI ID
    #----------------------------------------------------------------------------    
    @classmethod
    def getCBIInfo( cls, absdistance, Type = "Running" ):
        "get CBI Information"
        try:
            _BlockCbiListZCID = MapData.getBlockCBIDic( Type )
            _BlkCBIInfo = {}       #{blkID:CBIID,...}
            for _ZC in _BlockCbiListZCID:
                for _block in _BlockCbiListZCID[_ZC]:
                    _BlkCBIInfo[_block] = _BlockCbiListZCID[_ZC][_block]
            _BlockList = []
            _CBIList = []
            _trainLen = cls.getTrainLength( Type )        
            _start = absdistance + cls.getStartDistance( Type ) + _trainLen #转换为相对于blocklist的位置
            _endpostion = _start - _trainLen
            _Route_blocklist = cls.getBlockinfolist( Type ) #[[blockID,length,direction],...]
            _Wholedistance = 0
            _Find = False
            for _B_info in _Route_blocklist:
                if ( _start < _Wholedistance + _B_info[1] ):#找到start处block的索引
                    _startindex = _Route_blocklist.index( _B_info )                                
                    break    
                _Wholedistance = _Wholedistance + _B_info[1] 
            _Wholedistance = 0
            _Find = False
            for _B_info in _Route_blocklist:
                if ( _endpostion < _Wholedistance + _B_info[1] ):#找到end处block的索引
                    _endindex = _Route_blocklist.index( _B_info )
                    break    
                _Wholedistance = _Wholedistance + _B_info[1]            
            for _index in range( _endindex, _startindex + 1 ):    #获取列车所在的blocklist
                _BlockList.append( _Route_blocklist[_index][0] )   
            for _tmpBlk in _BlockList:
                _tmpCBI = _BlkCBIInfo[_tmpBlk]
                if _tmpCBI not in _CBIList:
                    _CBIList.append( _tmpCBI )
        except:
            _CBIList = []
        
        return _CBIList
#        print _BlkCBIInfo
#        print _BlockList
#        print _CBIList
   
if __name__ == '__main__':
    Data = MapData()
    Data.loadMapData( '../Bcode_CC_OFFLINE_VN_Build20111223/12/ccnvBinary.txt', '../Bcode_CC_OFFLINE_VN_Build20111223/12/ccnvText.txt' )
    Trainroute = TrainRoute()
    Trainroute.loadTrainData( '../default case/scenario/train_route.xml' )
    print Trainroute.getBlockinfolist()
    print Trainroute.getCBIInfo( 211160 )
