#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2013-6-6

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

class DeviceMsgCfg( object ):
    """
    Device message config Process class
    """
    __data = None 
    __dataotherinfo = None

    def __init__( self ):
        pass

    #===========================================================================
    # 获得路径下面的所有Device message的XML文件
    # Device_Path为绝对路径
    # 要求所有Device message的XML文件命名格式：XX_message.xml
    #===========================================================================
    def getMsgDeviceFile(self,Device_Path):
        "get Device message dir"        
        __CurWorkPath = Device_Path #记录当前路径
        self.msgFileName = []   
        self.deviceName = []  
        root, dirs, files = self.getFolderlist( Device_Path ) 
        for file in files:            
            tmpFile = file.split(".")
            if tmpFile[-1] in [u"xml"]:
                tmpFileName = tmpFile[-2].split("_")
                if tmpFileName[-1] in [u"message"] and len(tmpFileName) > 1:                    
                    self.deviceName.append(tmpFileName[-2])
                    self.msgFileName.append(tmpFileName[-2] + '_message.xml')
        
        #print self.deviceName,self.msgFileName 
        return self.deviceName,self.msgFileName
    
    #-------------------------------------------------------
    #@获取文件夹下的所有文件夹
    #-------------------------------------------------------
    @classmethod
    def getFolderlist( self, path ):
        "get folder list."
        for root, dirs, files in os.walk( path ):            
            return root, dirs, files 
    
    #获得Device message的XML文件路径
    def getMsgDevicePath( self ): 
        #tmpPath = commlib.getCurFileDir().strip().split( "\\" )
        #self.rootPath = '\\'.join(tmpPath[:-1])
        self.rootPath = commlib.getCurFileDir()
        self.msgDevicePath = commlib.joinPath( self.rootPath, "\TPConfig\setting" )
        return self.msgDevicePath    
    
    #从“XX_message.xml”中获得数据
    def getDevMsg( self,devName ): 
        DevMsgFile = self.msgFileName[self.deviceName.index(devName)]
        DevMsgPath = self.msgDevicePath
        DevMsgPathF = os.path.join(DevMsgPath,DevMsgFile )
        self.DevMsg = XMLDeal.importDevMsg(DevMsgPathF)
        return self.DevMsg  
       
    #保存“XX_message.xml”数据
    def saveDevMsg( self,devName,msgData ): 
        DevMsgFile = self.msgFileName[self.deviceName.index(devName)]
        DevMsgPath = self.msgDevicePath
        DevMsgPathF = os.path.join(DevMsgPath,DevMsgFile )
        self.DevMsg = XMLDeal.ExportDevMsg(DevMsgPathF,msgData)
       
    def DevAddTmpMsg(self, tmpdata, tmpList):   
        tmpList.append(tmpdata)
        
    def DevDeleteTmpMsg(self, tmpList, delIndex):   
        try:
            tmpList.pop( delIndex )            
        except IndexError, e:
            print "Delete error!!", delIndex, e
            
    def DevModifyTmpMsg(self, tmpdata, tmpList, modIndex):   
        try:
            tmpList[modIndex] = tmpdata            
        except IndexError, e:
            print "Modify Error!!", modIndex, e  
            
    def saveTheConfig( self, tmp_Var, path ):
        "save the configuration."
        XMLDeal.ExportVariant(path,tmp_Var) 
          
        
            
if __name__ == '__main__':
    case = DeviceMsgCfg()
    case.getMsgDeviceFile(case.getMsgDevicePath())
    a = [['CC2CIVariantRequest', '2314', '!', [['0', 'B', 'Message_Identifier', 'Message Identifier'], ['1', 'I', 'CCLoopHour', 'CC Loop Hour'], ['2', '3B', 'CheckSum_S1', 'checksum 1'], ['5', '3B', 'CheckSum_S2', 'checksum 2']]], ['CI2CCVariantRequest', '15364', '!', [['0', 'B', 'Message_Identifier', 'Message Identifier'], ['1', 'I', 'CILoopHour', 'CC Loop Hour'], ['2', '3B', 'CheckSum_S1', 'checksum 1'], ['5', '3B', 'CheckSum_S2', 'checksum 2']]]]
    case.saveDevMsg('ci',a)