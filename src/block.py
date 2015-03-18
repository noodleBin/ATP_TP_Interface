#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     block.py
# Description:  block设备仿真      
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      date
# Company:      CASCO
# LastChange:   Created 2011-04-12
# History:      
#----------------------------------------------------------------------------
from base.basedevice import BaseDevice

class Block(BaseDevice):
    """
    block device class
    """


    def __init__(self, name, id):
        " block init"
        BaseDevice.__init__(self, name, id)

    #def isLocateIn(self, abscissa):
        #" if the abscissa in block then return True"
        #if self.getDataValue('kp_b') <= abscissa and abscissa <= self.getDataValue('kp_e'):
            #return True
        #elif self.getDataValue('kp_b') >= abscissa and abscissa >=self.getDataValue('kp_e'):
            #return True
        #else:
            #return False

    #def length_old(self):
        #" get block length"
        #return abs(self.getDataValue('kp_e') - self.getDataValue('kp_b'))
    
    def length(self):
        " get block length"
        return self.getDataValue('length')

    # --------------------------------------------------------------------------
    ##
    # @Brief 计算block的内部坐标到block终点的距离，up-kp_e,down-kp_b
    #
    # @Param abscissa
    # @Param dirc 1-up, 0-down
    #
    # @Returns 距离
    # --------------------------------------------------------------------------
    def calcDistance(self, abscissa ,dire):
        " calculate distance in block"
        return abs(dire*self.length() - abscissa) 

    # --------------------------------------------------------------------------
    ##
    # @Brief 将Track内的坐标转换成Block内的坐标
    #
    # @Param abscissa
    #
    # @Returns 
    # --------------------------------------------------------------------------
    #def fromTrackAbs2BlockAbs(self, abscissa):
        #" change abscissa in track to abscissa in block"
        #return abs(abscissa - self.getDataValue('kp_b'))
    
    #def inBlockDeviceAbs(self):
        #" add block abscissa for in block device"
        ##beacons
        #[_b.addDataKeyValue('kp_i' ,self.fromTrackAbs2BlockAbs(_b.getDataValue('kp'))) \
                #for _b in self.getDeviceObjList('Beacons')]
    # --------------------------------------------------------------------------
    ##
    # @Brief 获得block上，一段坐标之间的beacon object
    #
    # @Param abscissa_b 开始坐标 block相对坐标
    # @Param abscissa_e 结束坐标 block相对坐标
    # @Param dire
    #
    # @Returns beaconObjectList 
    # --------------------------------------------------------------------------
    def getBeaconBetween(self, abscissa_b, abscissa_e, curDir):
        " get beacon objects in distance"
        _b = self.getDeviceObjList('Beacons')
        return [_bb for _bb in _b \
                if (_bb.getBeaPostion() >= min(abscissa_b,abscissa_e) and \
                _bb.getBeaPostion() <= max(abscissa_b, abscissa_e) and \
                _bb.ifDireMath(curDir)\
                )]
