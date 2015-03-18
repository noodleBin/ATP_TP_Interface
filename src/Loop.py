#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2014-11-11

@author: 61504

'''

from Car import Car
from GpsAndOdometer import GpsAndOdometer
from xmldeal import XMLDeal
from LineInfoBase import LineInfoBase
class Loop(Car):
    
    #线路地图信息以及block id list
    _block_map = None
    __blockList = None
    _loopId = None
    #存储的是解析选中的若干个block模块中的LoopInfo信息，同时删除LoopInfo为NULL以及None的Block
#     _IdAndLoopInfo = None #给定若干个blcok中包含LoopInfo数据的的字典
    
    #处理完返回的数据格式为block Id 和 LoopInfo ——> _continuousLoopInfo{_Id:_LoopInfo}
#     __continuousLoopInfo = None
    
    def __init__(self, name):
#         self._IdAndLoopInfo = {}
#         self.__continuousLoopInfo = {}
        self._loopId = 0
        Car.__init__(self, name)
#         self.gps.deviceInit()
        print '---------------loop initial complete-----------------------------'
    
    def deviceInit(self):
        Car.deviceInit(self)
        xmlDeal = XMLDeal()
        mapList,cog_dir,accel,V_max,time,radio,lineList= xmlDeal.importTrainRoute( r'./scenario/train_route.xml' )
        
        lineInfo = LineInfoBase('lineInfo')
        lineInfo.deviceInit( varFile = r'./scenario/Line_Info.xml')
#         print '----------lineList-------',lineInfo.getDataValue(lineList[0])
        self.__blockList = [int( _s ) for _s in lineInfo.getDataValue(lineList[0])[2].strip().split( ',' )]
        
        
        self._direction = lineInfo.getDataValue(lineList[0])[0]
        
#         print '------direction------',self._direction
#         self.__blockList = self.gps.getList()
#         print 'loop blocklist',self.__blockList
        self._IdAndLoopInfo = self.getFormatLoopInfo()
        self._continuousLoopInfo = self.getContinusLoopInfo()
        print 'device _continuousLoopInfo',self._continuousLoopInfo
        print '------------------------------- loop device init--------------------------------'

    def ReInitVariant(self,_id):
        Car.deviceInit(self)
        xmlDeal = XMLDeal()
        mapList,cog_dir,accel,V_max,time,radio,lineList= xmlDeal.importTrainRoute( r'./scenario/train_route.xml' )
        lineInfo = LineInfoBase('lineInfo')
        lineInfo.deviceInit( varFile = r'./scenario/Line_Info.xml')
#         print '----------lineList-------',lineInfo.getDataValue(lineList[_id])
        self.__blockList = [int( _s ) for _s in lineInfo.getDataValue(lineList[_id])[2].strip().split( ',' )]
        
        self._direction = lineInfo.getDataValue(lineList[_id])[0]
        
#         print '------direction------',self._direction
#         print 'loop blocklist',self.__blockList
        self._IdAndLoopInfo = self.getFormatLoopInfo()
        self._continuousLoopInfo = self.getContinusLoopInfo()
        print '------------------------------- loop device ReInitVariant--------------------------------'
    #===========================================================================
    #解析选中的若干个block模块中的LoopInfo信息，同时删除LoopInfo为NULL以及None的Block
    #@return: _returnValue 给定若干个blcok中包含LoopInfo数据的的字典
    #由选中的若干个block组成的线路地图 将数据整合成连续的数据
    #===========================================================================
    def getFormatLoopInfo(self):
        _blockMap = {}#临时存放给定的
        _temp = []
        _blockSortMap = {}
        _temp_singular = []
        _map = {} 
        for x in range(len(self.__blockList)):
            _temp.append(self._block_map[self.__blockList[x]]['Loop_info'])
            _blockMap[self.__blockList[x]] = _temp
#             print(_blockMap[self.__blockList[x]])
            _temp = []
            __tempBlock = []
            #删除block中singular为空的点
            for i in range(len(self._block_map[self.__blockList[x]]['Loop_info'])):
                if self._block_map[self.__blockList[x]]['Loop_info'][i][0] != 'NULL' \
                and self._block_map[self.__blockList[x]]['Loop_info'][i][0] != None \
                and self._block_map[self.__blockList[x]]['Loop_info'][i][0] != '255':
                    __tempBlock.append(self._block_map[self.__blockList[x]]['Loop_info'][i])
                else:
                    pass
            _map[self.__blockList[x]] = __tempBlock
            
        _list = {}#sorted singular and the data is not NULL and None
        _listId = []#sorted block Id the singular is not NULL and None
        
        _returnValue = []#Format:[[],{}] [_listId,_list]
        for x in range(len(self.__blockList)):
            if _map[self.__blockList[x]] == []:
                pass                
            else:
                _list[self.__blockList[x]] = _map[self.__blockList[x]]
                _listId.append(self.__blockList[x])
#                 print (_map[self.__blockList[x]])
        _returnValue.append(_listId)
        _returnValue.append(_list)
#         print '---return value----',_returnValue
        return _returnValue
    
    #===========================================================================
    #增加对含有偏移量的LoopInfo的处理，将每一个LoopInfo中的偏移量处理为连续的数据模块
    #处理完返回的数据格式为block Id 和 LoopInfo ——> _continuousLoopInfo{_Id:_LoopInfo}
    #===========================================================================
    def getContinusLoopInfo(self):
        _IdAndLoopInfo = self._IdAndLoopInfo
        _Id = _IdAndLoopInfo[0]
        _LoopInfo = _IdAndLoopInfo[1]#取出所有的非空的LoopInfo
        _temp = []#单个block中包含的非空所有LoopInfo
        _continuous = []#用来临时存放转换之后的的所有LoopInfo信息
        _continuousLoopInfo = {}#用来存放转换好之后的Block Id 和所有的LoopInfo信息
#         print '---direction-------------',self.gps.getDirection()
        if self._direction == '1':
            for x in range(len(_Id)):
                _fontLength = 0#用来统计每个block中的LoopInfo的坐标值，也就是当前block前面所有的block长度之和
                _temp = _LoopInfo[_Id[x]]#每一个非空的所有Singular
    #             _length = self._block_map[_Id[x]]['Length']
    #                 _fontLength = float(self._block_map[_Id[x-1]]['Length']) + _fontLength
                _fontLength = self.getFontBlockLength(self.getIndexInBlockList(_Id[x]))
                _continuous = []
                if x == 0:
                    _temp[0][1] = float(_temp[0][1])
                    _continuous.append(_temp[0])
                    _continuousLoopInfo[_Id[x]] = _continuous
                else:
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
                _continuousLoopInfo[_Id[x]] = _continuous
#             print '---------------------1  continuous loop info---------------------'
#             print _continuousLoopInfo
#             print '--------------------------------------------------------------'
#             return _continuousLoopInfo
        elif self._direction == '2':
            for x in range(len(_Id)):
                _fontLength = 0#用来统计每个block中的LoopInfo的坐标值，也就是当前block前面所有的block长度之和
                _temp = _LoopInfo[_Id[x]]#每一个非空的所有Singular
                _length = self._block_map[_Id[x]]['Length']
    #                 _fontLength = float(self._block_map[_Id[x-1]]['Length']) + _fontLength
                _fontLength = self.getFontBlockLength(self.getIndexInBlockList(_Id[x]))
                _continuous = []
#                 if x == 0:
#                     _temp[0][1] = float(_temp[0][1])
#                     _continuous.append(_temp[0])
#                     _continuousLoopInfo[_Id[x]] = _continuous
#                     pass
#                 else:
                for j in range(len(_temp)):
    #                     print _temp[j][1]
                    for j1 in range(len(_temp[j])):
    #                         print _temp[j][j1]
                        if j1 == 1:# 将每一个Singular中的偏移量转换为float数据
    #                             print _fontLength
    #                             print _temp[j][j1]
                            _temp[j][j1] = _fontLength + float(_length) - float(_temp[j][j1])
    #                         _perTemp.append(_temp[j][j1])
                    _continuous.append(_temp[j])
                _continuousLoopInfo[_Id[x]] = _continuous
#             print '---------------------2  continuous loop info---------------------'
#             print _continuousLoopInfo
#             print '--------------------------------------------------------------'
        return _continuousLoopInfo

    #===========================================================================
    #根据当前block Id获取前面若干个block的长度
    #因为当前的block Id 为非空Singular 的Id的集合
    #例如：整个线路地图取得若干个block Id为                    [1,3,6,8,10,12,14]
    #去除NULL和None的Singular的当前block Id为[1,8,10,12,14] 
    #===========================================================================
    def getFontBlockLength(self,_index):
        _fontLength = 0
        for x in range(len(self.__blockList)):
            if x < _index:
                _fontLength = float(self._block_map[self.__blockList[x]]['Length']) + _fontLength
            pass
        return _fontLength
    
    def getIndexInBlockList(self,_item):
        return self.__blockList.index(_item)
    
    #根据行车里程计算出在哪一个Loop范围之内!
    #===========================================================================
    # @param _cycleId:当前周期号  _error:误差范围值 单位(m)
    #===========================================================================
    def judgeLoopInWhatRange(self,_mile,_error):
#         _currenMileage = self.getCurrentComprehensiveInfoPer100ms(_cycleId)[0]#当前周期只能总共的行测里程数
        _currenMileage = _mile#当前周期只能总共的行测里程数
#         _currenMileage = _mile
#         print '------current mileage-----',_currenMileage
        _IdAndLoopInfo = self._IdAndLoopInfo
        _Id = _IdAndLoopInfo[0]#除去NULL和None之后的Singular Id
        _continuousLoopInfo = self._continuousLoopInfo
#         print '--------_continuousLoopInfo----------',_continuousLoopInfo
#         print '----------loop id--------------------',int(_continuousLoopInfo[25][0][0])
        _inRangeFlag = 0
        _flagAndId = [0,0]
#         print _currenMileage
        #开始遍历continuousLoopInfo 查看当前周期是否在Loop范围之内
#         print _continuousLoopInfo
#         print _Id
        for i in range(len(_Id)):
            _length = _continuousLoopInfo[_Id[i]][0][1]#当前LoopInfo中的长度
            try:
#             if (_length - _error <= _currenMileage) and (_currenMileage <= _length +_error):
                if abs(_currenMileage - _length) <= _error:
                    print '--------------------current cycle in the loop range------------------'
                    _inRangeFlag = 1
                    self._loopId = int(_continuousLoopInfo[_Id[i]][0][0])
                    print '-------------id---------',self._loopId
                    pass
            
                else:
#                 print '--------------------not in the loop range----------------------------'
#                 print '-------------id---------',_Id[i]
                    pass
            except Exception:
                pass
#             print _length
            pass
#         print _inRangeFlag
        _flagAndId[0] = _inRangeFlag
        _flagAndId[1] = self._loopId
        print '--------flag and id---------',_flagAndId
        return _flagAndId

if __name__ == '__main__':
    loop = Loop('loop')
    loop.deviceInit()
#     loop.ReInitVariant(1)
#     loop.getContinusLoopInfo()
    loop.judgeLoopInWhatRange(165, 3)
    pass