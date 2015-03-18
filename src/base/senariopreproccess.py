#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     senariopreprocess.py
# Description:  处理用于处理改值脚本，这里需要引进改值的列表     
# Author:       Kunpeng Xiong
# Version:      0.0.1
# Created:      2011-07-19
# Company:      CASCO
# LastChange:   update 2011-07-21
# History:      2011-07-21 :add getNormalChangeItem
#----------------------------------------------------------------------------
import simdata
from simdata import TrainRoute
#import commlib
class Senariopreproccess():
    """
         脚本预处理，在使用该示例之前请确认已经进行了线路地图的读取
    """
    """
    2011.12.10 重构删除
    #@路径的信息列表[[blockID,length]]
    #blockinfolist = []
    """
    #@存储由于延时而尚未更改的变量
    #{_index:[name,value],...}#_index 表示该值在脚本列表中的位置
    __ChangeValuelist = {}
    
    #保存已经进行过更改的脚本的Index值
    __haschangedIndex = []
    
    #设备节点
    __deviceNode = None
    """
    2011.12.10 重构删除
    #列车开始运行的绝对位置
    #__startdistance = None 
    
    #路径的方向和list，以及列车起始位置
    __blocklist = None
    __direct = None
    __startV = None
    __trainLen = None
    __cog_dir = None
    """
    var_type = {'int':int, 'string':str, 'float':float}
    
    def __init__(self, devnode = None):
        "init method"
        
        self.__ChangeValuelist = {}
        self.__haschangedIndex = []
        self.__deviceNode = devnode

        #2011.12.10 重构删除
        #读取train_route
        #self.blockinfolist = []
        #self.__startdistance = 0
        #self.__blocklist, self.__startV, self.__direct, self.__trainLen , self.__cog_dir = commlib.loadTrainRout(path)

    #---------------------------------------------------------
    #@根据trackmap中的block信息以及运行路径的blockIDlist获取bolckInfolist
    #@_blocklist:[blockID,...]
    #@_path:trackmap的file文件路径
    #@结果存入bolckInfolist中
    def getblockinfolist(self, _path, _pathfile):
        #获取trackmap中的block信息
        #代码已经移入TrainRoute类中,本函数以无效
        pass
        #TrainRoute.getBlockinfolist()
        
            
    #---------------------------------------------------------
    #@根据当前_blockID，横坐标_absicssa，以及运行方向，获得绝对路径
    #@注：在调用本函数前，必须先计算出了_blockinfolist，也即要先调用函数：getblockinfolist
    #@返回绝对路径（相对于blocklist路径的起点）
    #---------------------------------------------------------
    def getabsolutedistancefromBlock(self, _blockID, _absicssa):
        "获取相对于block原点的绝对对路径函数"
        #代码已经移入TrainRoute类中
        return TrainRoute.getabsolutedistancefromBlock(_blockID, _absicssa)
    
    #---------------------------------------------------------
    #@根据当前_blockID，横坐标_absicssa，以及运行方向，获得绝对路径
    #@注：在调用本函数前，必须先计算出了_blockinfolist，也即要先调用函数：getblockinfolist
    #@_direct:运行方向：由小坐标到大坐标为1，反之为-1
    #@返回绝对路径（相对于列车的起始位置路径的起点）
    #---------------------------------------------------------
    def getabsolutedistance(self, _blockID, _absicssa):
        "获取相对于列车起始位置的绝对对路径函数"
        #代码已经移入TrainRoute类中
        return TrainRoute.getabsolutedistance(_blockID, _absicssa)
        
    
    #---------------------------------------------------------------------------
    #@根据脚本_defscenario_sorted:[[absolutedistance, delay_cycle,[[var_key, value]...]]...]
    #@注：脚本必须是根据绝对距离（由小到大排好了顺序的）,且本函数每周期只能调用一次
    #@当前的位置信息_position:[start,end]
    #@返回需要修改的值的列表：ChangeItem:[[var_key,value],...]
    #---------------------------------------------------------------------------
    def getNormalChangeItem(self, _position, _defscenario_sorted):
        "通过当前位置获取当前需要修改的变量列表"
        #位置无用则直接返回
        if None == _position or None == _position[0] or None == _position[1]:
            return []
        
        _changeItem = [] #初始改变的变量列表
#        if _position[0] > _position[1]:#对倒车情况不进行值的改变
#            return []
        #print '__haschangedIndex',self.__haschangedIndex
        #print '__ChangeValuelist',self.__ChangeValuelist
        #print '_defscenario_sorted',_defscenario_sorted
        for _i, _sce in enumerate(_defscenario_sorted):#遍历脚本，获得需要改变值的脚本
            #先处理静止的情况
            if _i in self.__haschangedIndex:
                continue   #已经改变的Index不再处理,进入下一个                 
            
            #找到要触发该值的位置
            if (_sce[0] >= _position[0]) and (_sce[0] <= _position[1]):
                if 0 == _sce[1]: #无延时的变量,对于需要延时的变量下个周期再进行判断处理
                    _changeItem = _changeItem + _sce[2]
                    self.__haschangedIndex.append(_i)
                else:#需要延时将其放入__ChangeValuelist中
                    if self.__ChangeValuelist.has_key(_i):
                        pass
                    else:#没有才添加
                        self.__ChangeValuelist[_i] = _sce + []
        
        #检查延时列表中的变量            
        for _key in self.__ChangeValuelist:
            _tmp = self.__ChangeValuelist[_key]
            #print _tmp
            if 0 == _tmp[1]:
                _changeItem = _changeItem + _tmp[2]
                self.__haschangedIndex.append(_key)

            else:
                _tmp[1] = _tmp[1] - 1
                self.__ChangeValuelist[_key] = _tmp
                
        for _index in self.__haschangedIndex: #将已改变的值从self.__ChangeValuelist去除
            if self.__ChangeValuelist.has_key(_index):
                self.__ChangeValuelist.pop(_index)
        #print self.__haschangedIndex
        #返回变量列表
        return _changeItem
    
    #------------------------------------------------------------------------
    #@排序和坐标转换函数：
    #@输入：_defscenario:[[block,absicssa, delay_cycle,[[var_key, value]...]]...]
    #@输入：_direct：方向，由小到大为1，由大到小为-1
    #@返回：按照绝对距离由小到大排好了顺序的列表：
    #@_defscenario_sorted:[[absolutedistance, delay_cycle,[[var_key, value]...]]...]
    #------------------------------------------------------------------------
    def getsortedscenario(self, _defscenario, _direct):
        _defscenario_sorted = []#初始化
        _tmpItem = []
        #距离转换
        for _sec in _defscenario:
            _distance = self.getabsolutedistance(int(_sec[0]), float(_sec[1]))
            _tmpItem = [_distance, int(_sec[2]), _sec[3]]
            _defscenario_sorted.append(_tmpItem)
        #排序
        _defscenario_sorted = sorted(_defscenario_sorted, \
                                     key = lambda _defscenario_sorted: _defscenario_sorted[0])
        #返回结果
        return _defscenario_sorted     

    #---------------------------------------------------------------------------
    #@根据脚本TimeScenario:[[loophour,[[var_key, value]...]]...]
    #@当前的位置信息loophour:周期
    #@返回需要修改的值的列表：ChangeItem:[[var_key,value],...]
    #---------------------------------------------------------------------------
    def getTimeChangeItem(self, loophour, TimeScenario):
        "根据当前的时间获取修改的值"
        _changeItem = [] #初始改变的变量列表
        for _sce in TimeScenario:#遍历脚本，获得需要改变值的脚本
            if loophour == _sce[0]:
                _changeItem = _changeItem + _sce[1]
        return _changeItem            
    #----------------------------------------------------------------------------
    #@根据相对于列车起始位置的距离，单位毫米，获取该位置的block ID以及abscissa(单位毫米)
    #----------------------------------------------------------------------------    
    def getBlockandAbs(self, absdistance):
        "get block ID and Abscissa from absolute accordding to train start Position"
        #代码已经移入TrainRoute类中
        return TrainRoute.getBlockandAbs(absdistance)


    #---------------------------------------------------------------
    #@默认的修改函数
    #根据位置
    #@devicenode：设备节点
    #@pos：位置信息：[start,end]
    #---------------------------------------------------------------
    def senarioCheck(self,pos,devicenode = None):
        "检查校本并修改值"
        if None == devicenode:
            devicenode = self.__deviceNode
        if None == devicenode:
            return "error senarioCheck: Unknow device node!"
        _change_Item = self.getNormalChangeItem(pos, devicenode.defScenario)
        #根据changeItem去改变相关的值
        for _item in _change_Item:
            _typename = devicenode.getVarDic()[_item[0]][0]
            devicenode.addDataKeyValue(_item[0], self.var_type[_typename](_item[1]))
        
        #获取根据loophour修改的值：
        _Time_change_Item = self.getTimeChangeItem(devicenode.loophour, devicenode.TimeScenario)
        for _item in _Time_change_Item:
            _typename = devicenode.getVarDic()[_item[0]][0]
            devicenode.addDataKeyValue(_item[0], self.var_type[_typename](_item[1]))
                

        
if __name__ == '__main__':    
    """
    simdata.MapData.loadMapData(binpath, txtpath)
    simdata.TrainRoute.loadTrainData(xmlpath)    
    _defscenario = [[1, 0, [["nama1", "1"], ["dasf", "fads"]]], [100, 7, [["nama2", "2"]]], [200, 0, [["nama3", "3"]]], \
                    [500, 1, [["nama4", "4"]]]]
    a = Senariopreproccess()
    print a.getNormalChangeItem([0, 50], _defscenario)
    print a.getNormalChangeItem([50, 100], _defscenario)
    print a.getNormalChangeItem([100, 95], _defscenario)
    print a.getNormalChangeItem([95, 80], _defscenario)
    print a.getNormalChangeItem([90, 95], _defscenario)
    print a.getNormalChangeItem([95, 150], _defscenario)
    print a.getNormalChangeItem([150, 250], _defscenario)
    print a.getNormalChangeItem([250, 400], _defscenario)
    print a.getNormalChangeItem([400, 550], _defscenario)
    print a.getNormalChangeItem([550, 650], _defscenario)
    """
