#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     line.py
# Description:  线路设备仿真      
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      date
# Company:      CASCO
# LastChange:   Created 2011-04-12
# History:      
#----------------------------------------------------------------------------
from base.basedevice import BaseDevice

class Line(BaseDevice):
    """
    line device class
    """


    def __init__(self, name, id):
        "block init"
        BaseDevice.__init__(self, name, id)

if __name__ == '__main__':
    l = Line('line', 1)
    print type(l)
    print l
    print l.getDeviceName(),l.getDeviceId(), l.getDataDic()
