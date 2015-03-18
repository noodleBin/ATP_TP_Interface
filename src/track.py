#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     track.py
# Description:  区段设备仿真      
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      date
# Company:      CASCO
# LastChange:   Created 2011-04-12
# History:      
#----------------------------------------------------------------------------
import sys
from base.loglog import LogLog
from base.basedevice import BaseDevice

class Track(BaseDevice):
    """
    track device class
    """

    def __init__(self, name, id):
        BaseDevice.__init__(self, name, id)
               
    
    def logMes(self, level, mes):
        LogLog.orderLogger('Track')
        LogLog.logMes(level, mes)

    # --------------------------------------------------------------------------
    ##
    # @Brief 通过坐标定位block
    #
    # @Param abscissa 坐标，track上的坐标
    #
    # @Returns detal = 0 ,返回block_id list detal = 1,返回[(block_id,block_in_abscissa)]
    # block_in_abscissa block内部坐标,相对kp_b,单位cm
    # --------------------------------------------------------------------------
    def locateBlock(self, abscissa, detal=0):
        " locate block by abscissa"
        self.logMes(4, type(self).__name__+'.'+sys._getframe().f_code.co_name+'.'+repr(abscissa))
        if detal == 0:
            return [_b.getDeviceId() for _b in self.getDeviceObjList('Blocks') if _b.isLocateIn(abscissa) == True]
        elif detal == 1:
            return [(_b.getDeviceId(),abs(abscissa - _b.getDataValue('kp_b'))) for _b in self.getDeviceObjList('Blocks') if _b.isLocateIn(abscissa) == True]
        else:
            return []
    # --------------------------------------------------------------------------
    ##
    # @Brief 给beacon 对象添加b_id属性
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def beaconBlockId(self):
        " set b_id attribute for beacons object"
        self.logMes(4, type(self).__name__+'.'+sys._getframe().f_code.co_name)
        for _b in self.getDeviceObjList('Beacons'):
            _bl = self.locateBlock(_b.getDataValue('kp')) 
            if len(_bl) == 0:
                self.logMes(1, type(self).__name__ + '.' + sys._getframe().f_code.co_name+'.' + \
                        'beacon %d is not belong any block'%(_b.getDeviceId()))
            elif len(_bl) > 1:
                self.logMes(1, type(self).__name__ + '.' + sys._getframe().f_code.co_name+'.' + \
                        'beacon %d is belong more than one block'%(_b.getDeviceId()) + repr(_bl))
            else:
                _b.addDataKeyValue('b_id',_bl[0])
