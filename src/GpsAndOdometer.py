#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2014-11-10

@author: 61504
'''
from Car import Car
import datetime
from xmldeal import XMLDeal
from LineInfoBase import LineInfoBase
class GpsAndOdometer(Car):
    
    #线路地图信息以及block id list
#     _block_map = None
    _mapList = None#所有线路地图的列表
    _blockList = None
    __ssaList = None
    
    #存储的是解析选中的若干个block模块中的Singular信息，同时删除Singular为NULL以及None的Block
#     _IdAndSingular = None #给定若干个blcok中包含Singular数据的的字典
    
    #存储的是解析选中的若干个block模块中的SSA信息，同时删除SSA为NULL以及None、255的Block
    __SSAAndId = None #给定若干个blcok中包含SSA数据的的字典
    
    #处理完返回的数据格式为block Id 和 Singular ——> _continuousSingular{_Id:_Singular}
#     _continuousSingular = None

    __i = None#singular组
    __j = None#singular组中的数据
    
    __lastSingularLength = None#最后一个singular的长度
    
    __frontGPS = None#前面的一个GPS
    __secondGPS = None#第二个GPS
    __frontGPSLength = None # 前面的一个GPSsingular实际长度
    
    _BlockLengthMap = None #  
    
    #统计一共在singular范围多少次
    _count = None
    
    #列车行驶方向
    _direction = None
    
    #第一个GPS点的偏移量为0标志位
    
    _IdAndSSA = []
    
    _continuousSSA = {}
    
    #线路列表信息
    _lineList = []
    
    
    def __init__(self, name):
        self.__i = 0
        self.__j = 0
        self._count = 0
        self.__frontGPS = []
        self.__secondGPS = []
        self.__frontGPSLength = 0
        self.__lastSingularLength = 0
        
#         self._IdAndSingular = {}
#         self._continuousSingular = {}
        Car.__init__(self, name)
#         self._direction = Car.getDirection(self)
        
    
    def deviceInit(self):
        Car.deviceInit(self)
        xmlDeal = XMLDeal()
#         mapList,cog_dir,accel,V_max,time,radio,lineId,direction,ssaList,blockList= xmlDeal.importTrainRoute( r'./scenario/train_route.xml' )
        mapList,cog_dir,accel,V_max,time,radio,lineList= xmlDeal.importTrainRoute( r'./scenario/train_route.xml' )
        print '----------------------gps device init-----------------------------'
        print cog_dir,accel,V_max,time,radio,lineList
#         print 'linemap',lineList
        lineInfo = LineInfoBase('lineInfo')
        lineInfo.deviceInit( varFile = r'./scenario/Line_Info.xml')
#         print '----------lineList-------',lineInfo.getDataValue(lineList[0])
        
        GpsAndOdometer._lineList = lineList
        print 'shit!~',GpsAndOdometer._lineList
        self._blockList = [int( _s ) for _s in lineInfo.getDataValue(GpsAndOdometer._lineList[0])[2].strip().split( ',' )]
#         print '-------block list-----',self._blockList
        self._ssaList = [int( _s ) for _s in lineInfo.getDataValue(GpsAndOdometer._lineList[0])[1].strip().split( ',' )]
        self._direction = lineInfo.getDataValue(GpsAndOdometer._lineList[0])[0]
        self._mapList = mapList
        
#         print '-----direction-------',self._direction
        self.__cog = cog_dir
        self._accel_positive = accel[0]
        self._accel_negative = accel[1]
        self._V_max = V_max
    
        self._Timer = time[0]
        self._smallTimer = time[1]
            
        self._out_radio = radio[0]
        self._in_radio = radio[1]
#         print self._blockList,self.__cog,self._accel_positive,self._accel_negative
#         print self._V_max,self._Timer,self._smallTimer,self._out_radio,self._in_radio
        
#         self._block_map = self.getBlockMap()
#         self._blockList = self.getBlockList()
#         self._mapList = self.getMapList()
        self.__ssaList = self.getSSAList()
        
#         print '------block list--------',self._blockList
        self._IdAndSingular = self.getFormatSingularBlock()
        GpsAndOdometer._IdAndSSA = self.getFormatSSA()
        GpsAndOdometer._continuousSSA = self.getContinuousSSA()
#         print '------------id and singular------------',self.getFormatSSA()
        self._continuousSingular = self.getContinuousSingular()
        self.__lastSingularLength = self.getLastSingularLength()
        self.__frontGPS = self.getFirstGPS()
        self.__secondGPS = self.getSecondGPS()
        self.__frontGPSLength = self.getFirstGPSLength()
#         print '--------------blockMap------------',self._block_map
#         print len(self._block_map)
#         print '----id and singular-----',self._IdAndSingular

    def ReInitVariant(self,_id):
        Car.deviceInit(self)
        xmlDeal = XMLDeal()
        mapList,cog_dir,accel,V_max,time,radio,lineList= xmlDeal.importTrainRoute( r'./scenario/train_route.xml' )
        print 'ReInitVariant---------------------------------------------------'
        print cog_dir,accel,V_max,time,radio,lineList
        print 'linemap',lineList
        lineInfo = LineInfoBase('lineInfo')
        lineInfo.deviceInit( varFile = r'./scenario/Line_Info.xml')
        print '----------lineList-------',lineInfo.getDataValue(lineList[_id])
        
        GpsAndOdometer._lineList = lineList
        self._blockList = [int( _s ) for _s in lineInfo.getDataValue(GpsAndOdometer._lineList[_id])[2].strip().split( ',' )]
        print '-------block list-----',self._blockList
        self._ssaList = [int( _s ) for _s in lineInfo.getDataValue(GpsAndOdometer._lineList[_id])[1].strip().split( ',' )]
        self._direction = lineInfo.getDataValue(GpsAndOdometer._lineList[_id])[0]
        self._mapList = mapList
        
        print '------direction------',self._direction
        self.__cog = cog_dir
        self._accel_positive = accel[0]
        self._accel_negative = accel[1]
        self._V_max = V_max
    
        self._Timer = time[0]
        self._smallTimer = time[1]
            
        self._out_radio = radio[0]
        self._in_radio = radio[1]
        print self._blockList,self.__cog,self._accel_positive,self._accel_negative
        print self._V_max,self._Timer,self._smallTimer,self._out_radio,self._in_radio
        
#         self._block_map = self.getBlockMap()
#         self._blockList = self.getBlockList()
#         self._mapList = self.getMapList()
        self.__ssaList = self.getSSAList()
        print '------block list--------',self._blockList
        self._IdAndSingular = self.getFormatSingularBlock()
#         print '--------id and singular------',self._IdAndSingular
        GpsAndOdometer._IdAndSSA = self.getFormatSSA()
        GpsAndOdometer._continuousSSA = self.getContinuousSSA()
#         print '------------id and sssa------------',self._IdAndSSA
        self._continuousSingular = self.getContinuousSingular()
        self.__lastSingularLength = self.getLastSingularLength()
        self.__frontGPS = self.getFirstGPS()
        self.__secondGPS = self.getSecondGPS()
        self.__frontGPSLength = self.getFirstGPSLength()
#         print '--------------blockMap------------',self._block_map
#         print len(self._block_map)
#         print '----id and singular-----',self._IdAndSingular
        pass
    
    def getDirection(self):
        return self._direction
    
    def reSetFirstGPSLength(self):
        self.__frontGPSLength = self.getFirstGPSLength()
        pass
   
    def reSetData(self):
        self.__i = 0
        self.__j = 0
        pass
    
    def getList(self):
        return self._blockList
     
    def getMap(self):
        return self._block_map
    
    def getSSAList(self):
        return self._ssaList
 
    def getSSAAndId(self):
        return self.getFormatSSA()
    
    #======================================================================
    ##[[_listId],{_ssaMap}]
    # [[44, 42, 37, 35, 31, 25, 24], {35: [['9.880000', '60.000000', '9', '255', '1', '1']], 
    # 37: [['9.880000', '60.000000', '11', '255', '1', '1']], 
    # 42: [['0.000000', '79.760000', '3', '180.000000', '4', '2']], 
    # 44: [['0.000000', '130.000000', '14', '180.000000', '4', '2']], 
    # 24: [['0.500000', '75.380000', '1', '180.000000', '1', '2']], 
    # 25: [['0.000000', '60.000000', '5', '255', '1', '1']], 
    # 31: [['9.880000', '60.000000', '7', '255', '1', '1']]}]
    #======================================================================
    #===========================================================================
    #解析选中的若干个block模块中的SSA信息，同时删除SSA为NULL以及None、255的Block
    #@return: _returnValue 给定若干个blcok中包含SSA数据的的字典
    #由选中的若干个block组成的线路地图 将数据整合成连续的数据 
    #===========================================================================   
    def getFormatSSA(self):
        _SSAMap = {}
        _idList = []
        _IdAndSSAIdmap = {}
        if self._direction == '1':#上行
            print 'gps getFormatSSA up direction'
            for x in range(len(self._mapList)):
                __tempSSA = []
                #删除block中Service_stopping_area为空的点
                if self._block_map[self._mapList[x]]['Service_stopping_area'][0][0] != '255':
#                     __tempSSA= self._block_map[self._mapList[x]]['Service_stopping_area'][0]
                    __tempSSA.append(self._block_map[self._mapList[x]]['Service_stopping_area'][0])
#                     print self._block_map[self._mapList[x]]['Service_stopping_area'][0]
                _SSAMap[self._mapList[x]] = __tempSSA
#             print '-----------SSA map-----------',_SSAMap
            _list = {}#sorted SSA and the data is not NULL and None
            _listId = []#sorted block Id the SSA is not NULL and None
            _returnValue = []#Format:[[],{}] [_listId,_list]
            for x in range(len(self._blockList)):
                if _SSAMap[self._blockList[x]] == []:
                    pass
                else:
                    _list[self._blockList[x]] = _SSAMap[self._blockList[x]]
                    _listId.append(self._blockList[x])
    #                 print (_map[self._blockList[x]])
                pass
            _returnValue.append(_listId)
            _returnValue.append(_list)
        elif self._direction == '2':#下行
            print 'gps getFormatSSA down direction'
            for x in range(len(self._mapList)):
                __tempSSA = []
                #删除block中Service_stopping_area为空的点
                if self._block_map[self._mapList[x]]['Service_stopping_area'][0][0] != '255':
#                     __tempSSA= self._block_map[self._mapList[x]]['Service_stopping_area'][0]
                    __tempSSA.append(self._block_map[self._mapList[x]]['Service_stopping_area'][0])
#                     print self._block_map[self._mapList[x]]['Service_stopping_area'][0]
                _SSAMap[self._mapList[x]] = __tempSSA
#             print '-----------SSA map-----------',_SSAMap
            _list = {}#sorted SSA and the data is not NULL and None
            _listId = []#sorted block Id the SSA is not NULL and None
            _returnValue = []#Format:[[],{}] [_listId,_list]
            for x in range(len(self._blockList)):
                if _SSAMap[self._blockList[x]] == []:
                    pass
                else:
                    _list[self._blockList[x]] = _SSAMap[self._blockList[x]]
                    _listId.append(self._blockList[x])
            _returnValue.append(_listId)
            _returnValue.append(_list)
            pass
        print '-----------ssa _returnValue-------'
        print _returnValue
        print '----------------------------------'
        return _returnValue 
  
    #===========================================================================
    #增加对含有偏移量的SSA的处理，将每一个SSA中的偏移量处理为连续的数据模块
    #处理完返回的数据格式为block Id 和 SSA ——> _continuousSingular{_Id:_SSA}
    #===========================================================================  
    def getContinuousSSA(self):
        _IdAndSSA = GpsAndOdometer._IdAndSSA
        _Id = _IdAndSSA[0]
        _SSA = _IdAndSSA[1]#取出所有的非空的SSA
        _temp = []#单个block中包含的非空所有SSA
        _continuous = []#用来临时存放转换之后的的所有Singular信息
        _continuousSingular = {}#用来存放转换好之后的Block Id 和所有的SSA信息
        if self._direction == '1':#上行
            print '-----------SSA up direction------------',_Id
            for x in range(len(_Id)):
                _fontLength = 0#用来统计每个block中的SSA的坐标值，也就是当前block前面所有的block长度之和
                if x == 0:#计算第一个block中的SSA
                    _temp = _SSA[_Id[x]]#[[ssa]]
                    _length = self._block_map[_Id[x]]['Length']
                    _temp[0][1] = float(_temp[0][1])# 将每一个SSA中的偏移量转换为float数据，起点的block数据就是坐标值，不需要转换
                    _continuous.append(_temp[0])
                    _continuousSingular[_Id[x]] = _continuous
#                     print 'test',_continuousSingular
                else:
                    _temp = _SSA[_Id[x]]#每一个非空的所有SSA
                    _length = self._block_map[_Id[x]]['Length']
                    _fontLength = self.getIncreasingFontBlockLength(self.getIndexInBlockList(_Id[x]))
                    _continuous = []
                    _temp[0][1] = _fontLength + float(_temp[0][1]) + float(_temp[0][0])
                    _continuous.append(_temp[0])
                    _continuousSingular[_Id[x]] = _continuous
#                 print _continuous
            print '-------------------处理完之后的Id:SSA----------------------'
            print _continuousSingular
            print '-----------------------------------------------------------'
            return _continuousSingular
        elif self._direction == '2':#下行
            print '-----------SSA down direction------------',_Id
            for x in range(len(_Id)):
                _fontLength = 0#用来统计每个block中的SSA的坐标值，也就是当前block前面所有的block长度之和
                if x == 0:#计算第一个block中的SSA
                    _temp = _SSA[_Id[x]]#[[ssa]]
                    _length = self._block_map[_Id[x]]['Length']
                    _temp[0][1] = float(_length) - float(_temp[0][0])
#                     _temp[0][1] = float(_temp[0][1])# 将每一个SSA中的偏移量转换为float数据，起点的block数据就是坐标值，不需要转换
                    _continuous.append(_temp[0])
                    _continuousSingular[_Id[x]] = _continuous
#                     print 'test',_continuousSingular
                else:
                    _temp = _SSA[_Id[x]]#每一个非空的所有SSA
                    _length = self._block_map[_Id[x]]['Length']
                    _fontLength = self.getDecreasingFontBlockLength(self.getIndexInBlockList(_Id[x]))
#                     print '------_fontLength----------',_fontLength
                    _continuous = []
                    _temp[0][1] = _fontLength + float(_length) - float(_temp[0][0])
#                     _temp[0][1] = _fontLength + float(_temp[0][1])
                    _continuous.append(_temp[0])
                    _continuousSingular[_Id[x]] = _continuous
#                 print _continuous
            print '-------------------处理完之后的Id:SSA----------------------'
            print _continuousSingular
            print '-----------------------------------------------------------'
            return _continuousSingular
    
    #===========================================================================
    # 获取当前值在blocklist中的下标位置
    #===========================================================================
    def getIndexInBlockList(self,_item):
        return self._blockList.index(_item)
    
    #===========================================================================
    #解析选中的若干个block模块中的Singular信息，同时删除Singular为NULL以及None的Block
    #@return: _returnValue 给定若干个blcok中包含Singular数据的的字典
    #由选中的若干个block组成的线路地图 将数据整合成连续的数据
    #===========================================================================
    def getFormatSingularBlock(self):
        _block_map = {}#临时存放给定的 {'id':[length,[singular]],...}
        _temp = []
        _blockSortMap = {}
        _temp_singular = []
        _map = {}
        if self._direction == '1':#上行
            print 'Gps getFormatSingularBlock---------up----------'
            for x in range(len(self._blockList)):
                _temp.append(self._block_map[self._blockList[x]]['Length'])
                _temp.append(self._block_map[self._blockList[x]]['Singular'])
                _block_map[self._blockList[x]] = _temp
    #             print(_block_map[self._blockList[x]])
                _temp = []
                __tempBlock = []
                #删除block中singular为空的点
                for i in range(len(self._block_map[self._blockList[x]]['Singular'])):
    
    #                 print(self._block_map[self._blockList[x]]['Singular'][i])
    #                 print(self._block_map[self._blockList[x]]['Singular'][i][0])
                    if self._block_map[self._blockList[x]]['Singular'][i][0] != 'NULL' \
                        and self._block_map[self._blockList[x]]['Singular'][i][0] != None\
                        and self._block_map[self._blockList[x]]['Singular'][i][0] != '255' :
                        __tempBlock.append(self._block_map[self._blockList[x]]['Singular'][i])
    #                     print(__tempBlock)
                    else:
    #                     print(self._blockList[x])
                        pass
                _map[self._blockList[x]] = __tempBlock
                
            _list = {}#sorted singular and the data is not NULL and None
            _listId = []#sorted block Id the singular is not NULL and None
            
            _returnValue = []#Format:[[],{}] [_listId,_list]
            for x in range(len(self._blockList)):
                if _map[self._blockList[x]] == []:
                    pass                
                else:
                    _list[self._blockList[x]] = _map[self._blockList[x]]
                    _listId.append(self._blockList[x])
    #                 print (_map[self._blockList[x]])
                pass
            _returnValue.append(_listId)
            _returnValue.append(_list)
            print 'Gps getFormatSingularBlock---------Sort Singular and Id:------------'
            print _returnValue
    #         print _list
    #         print _listId
    #         print '--------------------------------------------------------'
    #         print (_block_map)
            print 'Gps getFormatSingularBlock--------------------------------------------------------------------------------------------------------------'
            return _returnValue
        elif self._direction == '2':#下行
            print 'Gps getFormatSingularBlock-----------down direction---------'
            for x in range(len(self._blockList)):
#                 print '----block list--------',self._blockList#[21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
#                 print '---------x------------',x #0 1 2 3 4
                _temp.append(self._block_map[self._blockList[x]]['Length'])
                _temp.append(self._block_map[self._blockList[x]]['Singular'])
                _block_map[self._blockList[x]] = _temp#self._blockList[x] 5 4 3 2 1
#                 print(_block_map[self._blockList[x]])
                _temp = []
                __tempBlock = []
                #删除block中singular为空的点
                for i in range(len(self._block_map[self._blockList[x]]['Singular'])):
#                     print(self._block_map[self._blockList[x]]['Singular'][i])
#                     print(self._block_map[self._blockList[x]]['Singular'][i][0])
                    if self._block_map[self._blockList[x]]['Singular'][i][0] != 'NULL' \
                        and self._block_map[self._blockList[x]]['Singular'][i][0] != None\
                        and self._block_map[self._blockList[x]]['Singular'][i][0] != '255' :
                        __tempBlock.append(self._block_map[self._blockList[x]]['Singular'][i])
                _map[self._blockList[x]] = __tempBlock
                 
#             print '-----------_map------------',_map
            _list = {}#sorted singular and the data is not NULL and None
            _listId = []#sorted block Id the singular is not NULL and None
             
            _returnValue = []#Format:[[],{}] [_listId,_list]
            for x in range(len(self._blockList)):#0 1 2 3 4
                if _map[self._blockList[x]] == []:
                    pass                
                else:# 5 4 3 2 1 
#                     print '-----test-----',self._blockList[x]
                    _list[self._blockList[x]] = _map[self._blockList[x]]
                    _listId.append(self._blockList[x])
    #                 print (_map[self._blockList[x]])
                pass
            _returnValue.append(_listId)
            _returnValue.append(_list)
#             print '-----------------------------------------------------------------------------------'
#             print 'Sort Singular and Id: '
#             print '--------------------------------------------------------'
#             print _list
#             print _listId
#             print '--------------------5------------------------------------'
#             print (_returnValue)
#             print '--------------------------------------------------------'
            return _returnValue       
    
    #===========================================================================
    #增加对含有偏移量的Singular的处理，将每一个Singular中的偏移量处理为连续的数据模块
    #处理完返回的数据格式为block Id 和 Singular ——> _continuousSingular{_Id:_Singular}
    #===========================================================================
    def getContinuousSingular(self):
#         _IdAndSingular = self.getFormatSingularBlock()
        _IdAndSingular = self._IdAndSingular
        _Id = _IdAndSingular[0]
        _Singular = _IdAndSingular[1]#取出所有的非空的Singular
        _temp = []#单个block中包含的非空所有Singular
        _continuous = []#用来临时存放转换之后的的所有Singular信息
        _continuousSingular = {}#用来存放转换好之后的Block Id 和所有的Singular信息
#         print 'Gps getContinuousSingular----------_Id--------------',_Id
#         print 'Gps getContinuousSingular---------_Singular---------',_Singular
        if self._direction == '1':#上行
            _fontLength = 0#用来统计每个block中的Singular的坐标值，也就是当前block前面所有的block长度之和
            for x in range(len(_Id)):
                if x == 0:#计算第一个block中的Singular
                    _temp = _Singular[_Id[x]]#[[singular],[singular],[singular]]
                    _length = self._block_map[_Id[x]]['Length']
                    for i in range(len(_temp)):
                        for i1 in range(len(_temp[i])):
                            if i1 == 1:# 将每一个Singular中的偏移量转换为float数据，起点的block数据就是坐标值，不需要转换
    #                             print _temp[i][i1]
                                _temp[i][i1] = float(_temp[i][i1])
                        _continuous.append(_temp[i])
                    _continuousSingular[_Id[x]] = _continuous
    #                 print _continuousSingular
                else:
                    _temp = _Singular[_Id[x]]#每一个非空的所有Singular
                    _length = self._block_map[_Id[x]]['Length']
    #                 _fontLength = float(self._block_map[_Id[x-1]]['Length']) + _fontLength
                    _fontLength = self.getIncreasingFontBlockLength(self.getIndexInBlockList(_Id[x]))
                    _continuous = []
                    for j in range(len(_temp)):
    #                     print _temp[j][1]
                        for j1 in range(len(_temp[j])):
    #                         print _temp[j][j1]
                            if j1 == 1:# 将每一个Singular中的偏移量转换为float数据
    #                             print _fontLength
    #                             print _temp[j][j1]
                                _temp[j][j1] = _fontLength + float(_temp[j][j1])
    #                         _perTemp.append(_temp[j][j1])
                        _continuous.append(_temp[j])
                    _continuousSingular[_Id[x]] = _continuous
    #                 print _continuous
            print 'Gps getContinuousSingular-------------------处理完之后的Id:Sigular----------------------'
            print _continuousSingular
            print 'Gps _continuousSingular--------',len(_continuousSingular)
            print 'Gps getContinuousSingular-----------------------------------------------------------'
            return _continuousSingular            
        elif self._direction == '2':#下行 _Id [5, 4, 3, 2, 1]
            _fontLength = 0#用来统计每个block中的Singular的坐标值，也就是当前block前面所有的block长度之和(在下行中也就是后面几个block长度之和)
            for x in range(len(_Id)): #range(len(_Id)):0 1 2 3 4
                if x == 0:#计算第一个block中的Singular
                    _temp = _Singular[_Id[x]]#[[singular],[singular],[singular]]
                    _length = self._block_map[_Id[x]]['Length']
                    print 'Gps getContinuousSingular----------_temp-----------',_temp
                    print 'Gps getContinuousSingular----------_length-----------',_length
                    for i in range(len(_temp))[::-1]:
                        for i1 in range(len(_temp[i])):
                            if i1 == 1:# 将每一个Singular中的偏移量转换为float数据，起点的block数据就是坐标值，不需要转换
    #                             print _temp[i][i1]
                                _temp[i][i1] = float(_length) - float(_temp[i][i1])
#                                 print '------offset--------',_temp[i][i1]
                        _continuous.append(_temp[i])
                    _continuousSingular[_Id[x]] = _continuous
#                     print '------_continuousSingular-----',_continuousSingular
                else:
                    _temp = _Singular[_Id[x]]#每一个非空的所有Singular--->[[singular],[singular],[singular]]
                    _length = self._block_map[_Id[x]]['Length']
    #                 _fontLength = float(self._block_map[_Id[x-1]]['Length']) + _fontLength
                    _fontLength = self.getDecreasingFontBlockLength(self.getIndexInBlockList(_Id[x]))
                    _continuous = []
                    for j in range(len(_temp))[::-1]:
    #                     print _temp[j][1]
                        for j1 in range(len(_temp[j])):
    #                         print _temp[j][j1]
                            if j1 == 1:# 将每一个Singular中的偏移量转换为float数据
    #                             print _fontLength
    #                             print _temp[j][j1]
                                _temp[j][j1] = _fontLength + float(_length) - float(_temp[j][j1])
    #                         _perTemp.append(_temp[j][j1])
                        _continuous.append(_temp[j])
                    _continuousSingular[_Id[x]] = _continuous
    #                 print _continuous
                    pass
                pass
            print 'Gps getContinuousSingular-----处理完之后的Id:Sigular----------------------'
            print _continuousSingular
            print 'Gps getContinuousSingular-----------------------------------------------------------'
#             pass 
            return _continuousSingular            
    
    def getContinuousBlock(self):
        _temp = []
        _continuousBlock = {}#用来存放转换好之后的Block Id 和所有的Block信息
        if self._direction == '1':#上行
            _frontLength = 0
            print 'Gps getContinuousBlock-----------up direction------------'
            for x in range(len(self._blockList)):
                if x == 0:#计算第一个block中的Length
                    _continuousBlock[int(self._blockList[x])] = float(self._block_map[self._blockList[x]]['Length'])
                else:
                    _frontLength = self.getIncreasingFontBlockLength(self._blockList[x])
                    _continuousBlock[int(self._blockList[x])] = float(self._block_map[self._blockList[x]]['Length']) + _frontLength
        elif self._direction == '2':
            print 'Gps getContinuousBlock--------down direction-----------'
            for x in range(len(self._blockList)):
                if x == 0:#计算第一个block中的Length
                    _continuousBlock[int(self._blockList[x])] = float(self._block_map[self._blockList[x]]['Length'])
                else:
                    _frontLength = self.getDecreasingFontBlockLength(self._blockList[x])
                    _continuousBlock[int(self._blockList[x])] = float(self._block_map[self._blockList[x]]['Length']) + _frontLength
        print 'Gps getContinuousBlock------处理完之后的block-------'
        print _continuousBlock
   
    #===========================================================================
    #根据当前block Id获取前面若干个block的长度
    #因为当前的block Id 为非空Singular 的Id的集合
    #例如：整个线路地图取得若干个block Id为                    [1,3,6,8,10,12,14] 
    #去除NULL和None的Singular的当前block Id为[1,8,10,12,14]     
    #===========================================================================
    def getIncreasingFontBlockLength(self,_index):
        _fontLength = 0
        for x in range(len(self._blockList)):
            if x < _index:
                _fontLength = float(self._block_map[self._blockList[x]]['Length']) + _fontLength
            pass
        return _fontLength
   
    #===========================================================================
    #根据当前block Id获取前面若干个block的长度
    #因为当前的block Id 为非空Singular 的Id的集合
    #例如：整个线路地图取得若干个block Id为                    [1,3,6,8,10,12,14] 
    #去除NULL和None的Singular的当前block Id为[1,8,10,12,14]     
    #===========================================================================
    def getDecreasingFontBlockLength(self,_index):#_blockList 5 4 3 2 1
        _fontLength = 0
        for x in range(len(self._blockList)):
            if x < _index:
                _fontLength = float(self._block_map[self._blockList[x]]['Length']) + _fontLength
            pass
        return _fontLength    
    
    #根据行车里程计算出在哪一个Singular范围之内，从而以此为依据取出当前的Singular
    #===========================================================================
    # @param _cycleId:当前周期号  _error:误差范围值 单位(m)
    #===========================================================================
    def CreateGpsAccordingSingularMap(self,_mile,_error):
#         _currenMileage = self.getCurrentComprehensiveInfoPer100ms(_cycleId)[0]#当前周期只能总共的行测里程数
        _currenMileage = _mile#当前周期只能总共的行测里程数
        _IdAndSingular = self._IdAndSingular
        _Id = _IdAndSingular[0]#除去NULL和None之后的Singular Id
#         _continuousSingular = self._continuousSingular
#         print _currenMileage
#         print '--------gps---------',self.judeInWhatRangeAndCalculateGPS(_currenMileage,_error)
        return self.judeInWhatRangeAndCalculateGPS(_currenMileage,_error)
#         self._count += 1
#         return self._count
    
    #===========================================================================
    # 当前点和下一个singular的位置进行比较
    #     1.如果在当前点和下一个singular误差范围之间，这根据这两点以及当前位移算出GPS点的坐标
    #     2.如果当前点在下一个singular误差范围之内，则直接取出singular中的GPS点的坐标
    #     3.如果超出了下一个singular误差范围，则再比较下一个，以此循环递归比较，直到最后一个singular
    #===========================================================================
    def compareNextSingularLength(self,_currenMileage,_error,_GPS1):
        _IdAndSingular = self._IdAndSingular
        _Id = _IdAndSingular[0]#除去NULL和None之后的Singular Id
        _continuousSingular = self._continuousSingular
#         print '------------------------------compareNextSingularLength----------------------------------'
        _singularList = _continuousSingular[_Id[self.__i]]
        _len = len(_singularList)
        _singular = _singularList[self.__j]
        _length = _singular[1]
        _GPS2 = _singular[3]
        _GPS1 = self.__frontGPS
        _GPS1Length = self.__frontGPSLength
        _IdSize = len(_Id)
#         print '--------------------------------current singular list and singular-----------------------'
#         print _singularList
#         print _singular
#         print '-----------------------------------------------------------------------------------------'
#         print '-------------------------------------current length-------------------------------------->',_length
        if _length - _currenMileage >  _error:
            print '===========================between the two singular and Id is==========================',_Id[self.__i]
#             #点在两点之间，可以算出所需的GPS点 
#             #需要计算  近似为三角形比例
#             print '------------------front GPS singular length------------->',_GPS1Length
#             print '-------------------------------------length------------->',_length
            _shiftRatio = (_currenMileage - _GPS1Length)/(_length - _GPS1Length)
            print '--------------------------_shiftRatio------------------->',_shiftRatio
#             print '----------_gps1---------------->',self.getFormatGPS(_GPS1)
#             print '----------_gps2---------------->',self.getFormatGPS(_GPS2)
#             print '---------getBetweenGPS------------->',self.getBetweenGPS(_GPS1,_GPS2,_shiftRatio)
            print '---------original gps data front 1-------',_GPS1
            print '---------original gps data front 2-------',_GPS2
            return self.getBetweenGPS(_GPS1,_GPS2,_shiftRatio)
        elif (_length - _error <= _currenMileage) and (_currenMileage <= _length +_error):
            #当前点在Singular范围之内
            #直接取出当前的GPS坐标值
            self.__frontGPS = _GPS2
            self.__frontGPSLength = _length
            print '=============================in the range scare and Id is===============================',_Id[self.__i]
#             print _GPS2
#             print '----------_gps2---------------->',self.getFormatGPS(_GPS2)
            print '---------original gps data-------',self.getFormatGPS(_GPS2)
            return self.getFormatGPS(_GPS2)
        elif (self.__lastSingularLength + _error) < _currenMileage <= self.getTotalMileage():
            print '=============================in the last Singular range scare===========================',_Id[self.__i]
#             print  _GPS2
#             print '----------_gps2---------------->',self.getFormatGPS(_GPS2)
            return self.getFormatGPS(_GPS2)
        elif _currenMileage > self.getTotalMileage():
            print '------------current mile---------',_currenMileage
            print '--------------total mile---------',self.getTotalMileage()
            return self.getFormatGPS(_GPS2)
        else:
            if _len == 1:
#                 print '==================================================================='
#                 print '---------_len == 1------------'
#                 print '==================================================================='
                if self.__i <= max(range(len(_Id))):
                    self.__i += 1#跳转到下一组的Singular
                self.__j = 0
                return self.compareNextSingularLength(_currenMileage,_error,_GPS2)
                pass
            else:
#                 print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
#                 print '---------_len != 1------------'
#                 print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                if self.__j < max(range(len(_singularList))):
                    self.__j += 1#任然是当前组的，但是是另外一个Singular
                else:
                    self.__i += 1
                    self.__j = 0
                return self.compareNextSingularLength(_currenMileage,_error,_GPS1)
        pass
    
    #===========================================================================
    # 判断在singular的哪个范围之内，并且计算或者取出出GPS的值
    # 1.如果在起点和第一个Singular + _error的范围之内，则取出第一个Singular数据发送出去
    # 2.如果超出Singular则判断在哪一个singular范围之内：
    #     1.如果在当前点和下一个singular误差范围之间，这根据这两点以及当前位移算出GPS点的坐标
    #     2.如果当前点在下一个singular误差范围之内，则直接取出singular中的GPS点的坐标
    #     3.如果超出了下一个singular误差范围，则再比较下一个，以此循环递归比较，直到最后一个singular
    #===========================================================================
    def judeInWhatRangeAndCalculateGPS(self,_currenMileage,_error):
        _IdAndSingular = self._IdAndSingular
        _Id = _IdAndSingular[0]#除去NULL和None之后的Singular Id    //_Id[5,4,3,2,1]
        _continuousSingular = self._continuousSingular
#         print '-----------------------------------------------'
        _singularList = _continuousSingular[_Id[self.__i]]
        _len = len(_singularList)
        _singular = _singularList[self.__j]
        _length = _singular[1]
        _IdSize = len(_Id)
#         _GPS1 = _singular[3]
        if self.__i == 0 and self.__j == 0:
            if _length == 0:
                if _len == 1:
                    if self.__i <= max(range(len(_Id))):
                        self.__i += 1#跳转到下一组的Singular
                        #与下一个Singular比较范围，并且算出所在点的GPS值
                        self.__j = 0
                else:
                    if self.__j <= max(range(len(_singularList))):
                        self.__j += 1#任然是当前组的，但是是另外一个Singular
                    else:
                        self.__i += 1
                        self.__j = 0
                print '---------------first gps abs ==0----------'
                return self.getFormatGPS(self.__frontGPS)
            elif 0<_currenMileage  and _currenMileage< (_length - _error):
                print '---------------2 ----------'
                return self.getFirstToSecond(_currenMileage)
            elif (_length - _error) <= _currenMileage<= (_length + _error):
                print '---------------3 ----------'
                return self.getFormatGPS(self.__frontGPS)
            else:
                if _len == 1:
                    if self.__i <= max(range(len(_Id))):
                        self.__i += 1#跳转到下一组的Singular
                        #与下一个Singular比较范围，并且算出所在点的GPS值
                        self.__j = 0
#                         print '----------len == 1------',self.compareNextSingularLength(_currenMileage,_error,self.__frontGPS)
                        return self.compareNextSingularLength(_currenMileage,_error,self.__frontGPS)
                else:
                    if self.__j <= max(range(len(_singularList))):
                        self.__j += 1#任然是当前组的，但是是另外一个Singular
                    else:
                        self.__i += 1
                        self.__j = 0
#                     print '------self.__j = 0--------',self.compareNextSingularLength(_currenMileage,_error,self.__frontGPS)
                    return self.compareNextSingularLength(_currenMileage,_error,self.__frontGPS)
        else:
#             print '------------not------------',self.compareNextSingularLength(_currenMileage,_error,self.__frontGPS)
            return self.compareNextSingularLength(_currenMileage,_error,self.__frontGPS)
            
    def getBetweenGPS(self,_gps1,_gps2,_shiftRatio):
        _gps = []
        _gps_latitude1 = _gps1[0]
        _dd_latitude1 = int(_gps_latitude1[0:2])*100
        _mm_latitude1 = int(_gps_latitude1[2:])*0.000006
        _dd_mm_latitude1 = _dd_latitude1 + _mm_latitude1
        
        _gps_latitude2 = _gps2[0]
        _dd_latitude2 = int(_gps_latitude2[0:2])*100
        _mm_latitude2 = int(_gps_latitude2[2:])*0.000006
        _dd_mm_latitude2 = _dd_latitude2 + _mm_latitude2
        _dd_mm_latitude = _dd_mm_latitude1 + _shiftRatio*(_dd_mm_latitude2 - _dd_mm_latitude1)
        
        now = datetime.datetime.now()
        _time = now.strftime('%H%M%S.') + now.strftime('%f')[:2]
        _format_latitude =  '%9.5f' % _dd_mm_latitude
        _gps.append(_time)
        _gps.append(_format_latitude)
        if _gps1[1] == '85':
            _gps.append('N')
        else:
            _gps.append('S')
        _gps_longitude1 = _gps1[2]
        _ddd_longitude1 = int(_gps_longitude1[0:3])*100
        _mm_longitude1 = int(_gps_longitude1[3:])*0.000006
        _ddd_mm_longitude1 = _ddd_longitude1 + _mm_longitude1
        
        _gps_longitude2 = _gps2[2]
        _ddd_longitude2 = int(_gps_longitude2[0:3])*100
        _mm_longitude2 = int(_gps_longitude2[3:])*0.000006
        _ddd_mm_longitude2 = _ddd_longitude2 + _mm_longitude2
        _ddd_mm_longitude = _ddd_mm_longitude1 + _shiftRatio*(_ddd_mm_longitude2 - _ddd_mm_longitude1)
        _format_longitude = '%10.5f' % _ddd_mm_longitude
        _gps.append(_format_longitude)
        if _gps1[3] == '85':
            _gps.append('E')
        else:
            _gps.append('W')
        return _gps
    
    def getFormatGPSFirstPoint(self,_first,_second,_currentMile):
        pass
            
    def getFormatGPS(self,_init_gps):
#         print '---------calculate-------'
        _gps = []
        _gps_latitude = _init_gps[0]
        _dd_latitude = int(_gps_latitude[0:2])*100
        _mm_latitude = int(_gps_latitude[2:])*0.000006
        _dd_mm_latitude = _dd_latitude + _mm_latitude
#         print '------------_dd_mm_latitude------------',_dd_mm_latitude
        _format_latitude =  '%9.5f' % _dd_mm_latitude
#         print '---------final gps latitude------>',_format_latitude
#         print '-------------------------'
#         print type(_format_latitude)
        now = datetime.datetime.now()
        _time = now.strftime('%H%M%S.') + now.strftime('%f')[:2]
        _gps.append(_time)
        _gps.append(_format_latitude)
        
        if _init_gps[1] == '85':
            _gps.append('N')
        else:
            _gps.append('S')
        
        _gps_longitude =_init_gps[2]
        _ddd_longitude = int(_gps_longitude[0:3])*100
        _mm_longitude = int(_gps_longitude[3:])*0.000006
        _ddd_mm_longitude = _ddd_longitude + _mm_longitude
#         print '------------_ddd_mm_longitude------------',_ddd_mm_longitude
        
        _format_longitude = '%10.5f' % _ddd_mm_longitude
#         print '---------final gps longitude------>',_format_longitude
        _gps.append(_format_longitude)
        if _init_gps[3] == '85':
            _gps.append('E')
        else:
            _gps.append('W')
        return _gps
        pass
    
    #===========================================================================
    # 获取最后一个singular的长度
    # 当车行至最后一个singular和总行车里程之间，此时已经没有下一个singular
    # 所以在这一个范围之内就发送当前最后一singular中的GPS信息
    #===========================================================================
    def getLastSingularLength(self):
        _IdAndSingular = self._IdAndSingular
        _Id = _IdAndSingular[0]#除去NULL和None之后的Singular Id
        _continuousSingular = self._continuousSingular
        _i = max(range(len(_Id)))
        _singularList = _continuousSingular[_Id[_i]]
        _lenSingularList = len(_singularList)
        _lastSingular = _singularList[max(range(_lenSingularList))]
        
        _lastSingularLength = _lastSingular[1]
        return _lastSingularLength
        pass
    
    #===========================================================================
    # 获取第一个GPS的长度，当车行至下一个singular时候，同时作为存储上一个singular的GPS信息
    # 在车到达两个两个Singular之间的时候，通过这一点GPS、当前GPS坐标值以及当前行车里程 可以计算出当前GPS
    #===========================================================================
    def getFirstGPSLength(self):
        _IdAndSingular = self._IdAndSingular
        _Id = _IdAndSingular[0]#除去NULL和None之后的Singular Id
        _continuousSingular = self._continuousSingular
        print '-----------------------------------------------'
        _singularList = _continuousSingular[_Id[0]]
        _len = len(_singularList)
        _singular = _singularList[0]
        _length = _singular[1]
        return _length
    
    #===========================================================================
    # 获取第一个GPS，当车行至下一个singular时候，同时作为存储上一个singular的GPS信息
    # 在车到达两个两个Singular之间的时候，通过这一点GPS、当前GPS坐标值以及当前行车里程 可以计算出当前GPS
    #===========================================================================
    def getFirstGPS(self):
        _IdAndSingular = self._IdAndSingular
        _Id = _IdAndSingular[0]#除去NULL和None之后的Singular Id
        _continuousSingular = self._continuousSingular
        print '_continuousSingular',_continuousSingular
#         print '-----------------------------------------------'
        _singularList = _continuousSingular[_Id[0]]
        print '_singularList',_singularList
        _len = len(_singularList)
        _singular = _singularList[0]
        _length = _singular[1]
        self.__frontGPS = _singular[3]
        return self.__frontGPS
    
    def getFirstToSecond(self,_currentMile):
        _IdAndSingular = self._IdAndSingular
        _Id = _IdAndSingular[0]#除去NULL和None之后的Singular Id
        _continuousSingular = self._continuousSingular
        _singularList = _continuousSingular[_Id[0]]
#         print '_singularList',_singularList
        _firstSingular = _singularList[0]
        _firstLength = _singularList[0][1]
        _firstGps = _singularList[0][3]
#         print 'first length:',_firstLength
#         print 'first gps:',_firstGps
        _len = len(_singularList)
        if _len != 1:#第一个Singular含有两个或者多个GPS 则第二个GPS为第一个Singular的第二个GPS
#             print '------len != 1---------'
            _secondSingular = _singularList[1]
            _secondLength = _secondSingular[1]
            _secondGps = _singularList[1][3]
        else:#第一个Singular只有一个GPS 则第二个GPS为第二个Singular的第一个GPS
#             print '------len == 1---------'
            _singularList = _continuousSingular[_Id[1]]
            _secondSingular = _singularList[0]
            _secondLength = _secondSingular[1]
            _secondGps = _singularList[1][3]
#         print 'second length:',_secondLength
#         print 'second gps:',_secondGps
        _length = _secondSingular[1]
        self.__secondGPS = _secondSingular[3]
#         print 'start calculate gps' #_firstLength _secondLength _firstGps _secondGps
        #calculate first to second GPS
        return self.getFirstFormatGPS(_firstGps,_secondGps,_firstLength,_secondLength,_currentMile)
    
    def getFirstFormatGPS(self,_firstGps,_secondGps,_firstLength,_secondLength,_currentMile):
        _gps = []
        _gps_latitude1 = _firstGps[0]
        _dd_latitude1 = int(_gps_latitude1[0:2])*100
        _mm_latitude1 = int(_gps_latitude1[2:])*0.000006
        _dd_mm_latitude1 = _dd_latitude1 + _mm_latitude1
        
        _gps_latitude2 = _secondGps[0]
        _dd_latitude2 = int(_gps_latitude2[0:2])*100
        _mm_latitude2 = int(_gps_latitude2[2:])*0.000006
        _dd_mm_latitude2 = _dd_latitude2 + _mm_latitude2
        
        _dd_mm_latitude = (_secondLength * _dd_mm_latitude1 - _firstLength * _dd_mm_latitude2 + (_dd_mm_latitude2 - _dd_mm_latitude1) *_currentMile)/(_secondLength - _firstLength)
#         print '---------',_dd_mm_latitude
        now = datetime.datetime.now()
        _time = now.strftime('%H%M%S.') + now.strftime('%f')[:2]
        _format_latitude =  '%9.5f' % _dd_mm_latitude
        _gps.append(_time)
        _gps.append(_format_latitude)
        
        if _firstGps[1] == '85':
            _gps.append('N')
        else:
            _gps.append('S')
            
        _gps_longitude1 = _firstGps[2]
        _ddd_longitude1 = int(_gps_longitude1[0:3])*100
        _mm_longitude1 = int(_gps_longitude1[3:])*0.000006
        _ddd_mm_longitude1 = _ddd_longitude1 + _mm_longitude1
        
        _gps_longitude2 = _secondGps[2]
        _ddd_longitude2 = int(_gps_longitude2[0:3])*100
        _mm_longitude2 = int(_gps_longitude2[3:])*0.000006
        _ddd_mm_longitude2 = _ddd_longitude2 + _mm_longitude2
        
        _ddd_mm_longitude = (_secondLength * _ddd_mm_longitude1 - _firstLength * _ddd_mm_longitude2 + (_ddd_mm_longitude2 - _ddd_mm_longitude1) *_currentMile)/(_secondLength - _firstLength)
        _format_longitude = '%10.5f' % _ddd_mm_longitude
        _gps.append(_format_longitude)
        if _firstGps[3] == '85':
            _gps.append('E')
        else:
            _gps.append('W')
            
        print '----gps:',_gps
        return _gps
    
    def getSecondGPS(self):
        _IdAndSingular = self._IdAndSingular
        _Id = _IdAndSingular[0]#除去NULL和None之后的Singular Id
        _continuousSingular = self._continuousSingular
        _singularList = _continuousSingular[_Id[0]]
        _len = len(_singularList)
        if _len != 1:#第一个Singular含有两个或者多个GPS 则第二个GPS为第一个Singular的第二个GPS
            _singular = _singularList[1]
        else:#第一个Singular只有一个GPS 则第二个GPS为第二个Singular的第一个GPS
            _singularList = _continuousSingular[_Id[1]]
            _singular = _singularList[0]
        _length = _singular[1]
        self.__secondGPS = _singular[3]
        return self.__secondGPS


if __name__ == '__main__':
    gpsAndOdometer = GpsAndOdometer('gpsAndOdometer')
#     gpsAndOdometer.deviceInit()
#     print 'get first gps',gpsAndOdometer.getFirstGPS()
#     print 'get second gps',gpsAndOdometer.getSecondGPS()
#     gpsAndOdometer.getFirstToSecond()
    
#     gpsAndOdometer.getFormatSingularBlock()
#     gpsAndOdometer.getFormatSSA()
#     print '--------1-------------',gpsAndOdometer.getSSAAndId()
#     gpsAndOdometer.getContinuousSSA()
#     print GpsAndOdometer._continuousSSA
#     print '----------ssa and id-----',gpsAndOdometer.getSSAAndId()[0][0]
#     print gpsAndOdometer.getSSAList()
#     print 'ssa anf id',gpsAndOdometer.getSSAAndId()
#     gpsAndOdometer.getContinuousBlock()
#     print '---------ReInitial data------------'
    gpsAndOdometer.ReInitVariant(1)
#     print '--------2-------------',gpsAndOdometer.getSSAAndId()
#     print gpsAndOdometer.getContinuousSSA()
#     gpsAndOdometer.CreateGpsAccordingSingularMap(200, 3)
