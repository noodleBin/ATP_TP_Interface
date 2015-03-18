#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     varCombine.py
# Description:  本模块 ,并将之进行返回
# Author:       Sonnie Chen
# Version:      0.0.1
# Created:      2012-12-12
# Company:      CASCO
# LastChange:   
# History:      Created --- 2012-12-12
#               
#----------------------------------------------------------------------------
from inputHandle import OMAPInput
from inputHandle import UsrDefInput
from base.xmldeal import XMLDeal
from base import commlib
class VarComb():
    
    def __init__( self, formatpath = None, usrdefpath = None ):
        "init"
#        OMAPInput.importEnuDic(r'config/Enumerate.xml')
        OMAPInput.importFormat( formatpath if None != formatpath else r'../TPConfig/OMAPFormat.xml' )
#        OMAPInput.LoadZipOMAPData(r'config')
        self.OMAPInput = OMAPInput()
        
        self.usrDefInput = UsrDefInput()
        self.usrDefInput.loadUsrDefDat( usrdefpath if None != usrdefpath else r'config/OMAPFormat.xml' )
        
        # total variable including: 0. OMAP FORAMT, 1. CONST, 2. MAP DATA 3. USR DEFINED 
        self.totlDict = {}
        
        # dictionary of variable which picked up by user
        self.varDict = {}
#        print self.usrDefInput.ConstDict
        
    def bldTotlDict( self ):
        ""
        
        self.totlDict['OMAPFMT'] = OMAPInput.OMAPFormat['iTC_ATP_UP'].keys()
        self.totlDict['OMAPFMT'].sort()
        self.totlDict['CONST'] = self.usrDefInput.getDictKW()
        self.totlDict['CONST'].sort()
        self.totlDict['USRDEF'] = self.usrDefInput.getUsrDefDictKW()
        self.totlDict['USRDEF'].sort()
        self.totlDict['MAP'] = []
    
    def getTotlDict( self ):
        return self.totlDict
        
    def getOMAPFmtLst( self ):
        "get the list of variable name on OMAP Format"
        return OMAPInput.OMAPFormat['iTC_ATP_UP'].keys()
    
    def getConstLst( self ):
        "get the list of constant name"
        return self.usrDefInput.getDictKW()
    
    def getUsrDefLst( self ):
        "get the list of name of user defined expression"
        return self.usrDefInput.getUsrDefDictKW()
    
    #----------------------------------------------------------------------------
    #Type = 0: format过来的数据,存储格式: VarName:["0",Name,Attr,Des]
    #Type = 1: const数据，存储格式:VarName:["1",Name,Attr,Des]
    #Type = 2: Map数据，存储格式:VarName:["2",Name,Attr,Des],其中Attr是一个按照格式书写的string，是需要解析的
    #Type = 3: 用户自定义数据，存储格式:VarName:["3", Name, RuleDic,Des]     
    #-----------------------------------------------------------------------------
    def tp2num( self, type ):
        if type == 'OMAPFMT':
            _tp = '0'
        if type == 'CONST':
            _tp = '1'
        if type == 'MAP':
            _tp = '2'
        if type == 'USRDEF':
            _tp = '3'
        return _tp
            
    def addOneVar( self, name, type, attr, des ):
        ""
        _tp = self.tp2num( type )
        
        if not self.varDict.has_key( name ):
            self.varDict[name] = [_tp, name, attr, des]

        
    def delOneVar( self, name ):
        ""
        if self.varDict.has_key( name ):
            self.varDict.pop( name )
        
    def modOneVar( self, name, type, attr, des ):
        ""
        _tp = self.tp2num( type )
        if self.varDict.has_key( name ):
            self.varDict[name] = [_tp, name, attr, des]
        
        
if __name__ == '__main__':
    
    test = VarComb()
    test.bldTotlDict()
#    print test.getTotlDict()
    print test.totlDict['OMAPFMT']
#    print test.getOMAPFmtLst()
#    print test.getConstLst()
#    print test.getUsrDefLst()
