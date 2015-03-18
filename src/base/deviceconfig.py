#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2013-6-3

@author: Administrator
'''
from xmlparser import XmlParser
import lxml
from lxml import etree
import os
import commlib
from base.xmldeal import XMLDeal
from base.simdata import MapData
import copy
import filehandle
from base.caseprocess import CaseParser

class DeviceVarCfg( object ):
    """
    Device variant config Process class
    """
    __data = None 
    __dataotherinfo = None

    def __init__( self ):
        pass

    #===========================================================================
    # 获得路径下面的所有Device variant的XML文件
    # Device_Path为绝对路径
    # 要求所有Device variant的XML文件命名格式：XX_variant.xml
    #===========================================================================
    def getDeviceFile(self,Device_Path):
        "get Device variant dir"        
        self.__CurWorkPath = Device_Path #记录当前路径
        self.varFileName = []   
        self.deviceName = []  
        root, dirs, files = self.getFolderlist( Device_Path ) 
        for file in files:            
            tmpFile = file.split(".")
            if tmpFile[-1] in [u"xml"]:
                tmpFileName = tmpFile[-2].split("_")
                if tmpFileName[-1] in [u"variant"] and len(tmpFileName) > 1:                    
                    self.deviceName.append(tmpFileName[-2])
                    self.varFileName.append(tmpFileName[-2] + '_variant.xml')
        
        #print self.deviceName,self.varFileName 
        return self.deviceName,self.varFileName
    
    #-------------------------------------------------------
    #@获取文件夹下的所有文件夹
    #-------------------------------------------------------
    @classmethod
    def getFolderlist( self, path ):
        "get folder list."
        for root, dirs, files in os.walk( path ):            
            return root, dirs, files 
    
    #获得Device variant的XML文件路径
    def getDevicePath( self ): 
        #tmpPath = commlib.getCurFileDir().strip().split( "\\" )
        #self.rootPath = '\\'.join(tmpPath[:-1])
        self.rootPath = commlib.getCurFileDir()
        self.DevicePath = commlib.joinPath( self.rootPath, "\TPConfig\setting" )
        return self.DevicePath     
       
    def DevUpdateTmpData(self, tmpdata, tmpList):   
        tmpList.append(tmpdata)
        
    def DevDeleteTmpVariant(self, tmpList, delIndex):   
        try:
            tmpList.pop( delIndex )            
        except IndexError, e:
            print "Delete error!!", delIndex, e
            
    def DevModifyTmpData(self, tmpdata, tmpList, modIndex):   
        try:
            tmpList[modIndex] = tmpdata            
        except IndexError, e:
            print "Modify Error!!", modIndex, e  
            
    def saveTheConfig( self, tmp_Var, path ):
        "save the configuration."
        XMLDeal.ExportVariant(path,tmp_Var) 
          
        
            
if __name__ == '__main__':
    case = DeviceVarCfg()
    path = case.getDevicePath()
    print "path:",path
    case.getDeviceFile(path)