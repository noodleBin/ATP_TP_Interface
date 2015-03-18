#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     auotAnalysisHMI.py
# Description:  自动分析界面    
# Author:       Sonnie Chen
# Version:      0.0.1
# Created:      2012-12-10
# Company:      CASCO
# LastChange:   
# History:      
#----------------------------------------------------------------------------

import wx
import wx.lib.filebrowsebutton as filebrowse
from base import commlib
import math
import os
from inputHandle import UsrDefInput

#------------------------------------------------------------------------------------------
#用于编辑查看UsrDefined.xml 的Frame
#------------------------------------------------------------------------------------------

class EditUsrDefXML( wx.Frame ):
    '''
    Edit user defined data xml
    '''
    RunStatus = True
    SaveStatus = True
    
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
                  style = wx.DEFAULT_DIALOG_STYLE
                  ):
        
        # initialized MapInput, for the copy of ConstDict
        self.usrDefDat = UsrDefInput()
        self.usrDefDat.loadUsrDefDat( r'config/usrData.xml' )
              
        wx.Frame.__init__( self, parent, ID, title, pos, size, style )
        panel = wx.Panel( self, -1 ) #frame必须有panel，否则一些事件响应会有问题
        self.RunStatus = False
        self.SaveStatus = False
        

        # outside Frame box
        _Frame = wx.BoxSizer( wx.VERTICAL )
        
        # frame for static box (left and right)
        _Framebox = wx.BoxSizer( wx.HORIZONTAL )
        #_Box = wx.BoxSizer(wx.HORIZONTAL)
        
        # left Frame box
#        _FrameboxLeft = wx.BoxSizer( wx.VERTICAL )
#        _Box1 = wx.BoxSizer( wx.VERTICAL )
        _BoxLeft = wx.StaticBox( panel, -1, "Select Panel" )
        _BoxLeftSizer = wx.StaticBoxSizer( _BoxLeft, wx.VERTICAL )
        
#        _labelSta1 = wx.StaticText( panel, -1, "Source:", size = ( 100, -1 ) )
        _labelContentSta1 = ['Const', 'UsrDef']
        self.FrameComBoBox1 = wx.ComboBox( panel, -1, _labelContentSta1[0], \
                                          size = ( 380, -1 ), \
                                          choices = _labelContentSta1,
                                          style = wx.CB_DROPDOWN )
#        _Box1Sizer.Add( _labelSta1, 1, wx.ALIGN_TOP | wx.ALL | wx.EXPAND, 5 )
        _BoxLeftSizer.Add( self.FrameComBoBox1, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        _labelSrh = wx.StaticText( panel, -1, "Search Variant:", size = ( 380, -1 ) )
        self.SearchCtrl = wx.SearchCtrl( panel, size = ( 380, -1 ), style = wx.TE_PROCESS_ENTER )
        self._listBox = wx.ListBox( panel, -1, size = ( 380, 200 ), \
                                     choices = [], \
                                     style = wx.LB_SINGLE )
        
        _BoxLeftSizer.Add( _labelSrh, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _BoxLeftSizer.Add( self.SearchCtrl, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _BoxLeftSizer.Add( self._listBox, 13, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )

        

        
#         right Frame box
#        _FrameboxRight = wx.BoxSizer( wx.VERTICAL )
        _BoxRight = wx.StaticBox( panel, -1, "Edit Panel" )
        _BoxRightSizer = wx.StaticBoxSizer( _BoxRight, wx.VERTICAL )
        
        _labelID = wx.StaticText( panel, -1, "ID:", size = ( 280, -1 ) )
        self._TxtCrtlID = wx.TextCtrl( panel, -1, "", size = ( 280, -1 ) )
        
        _labelVal = wx.StaticText( panel, -1, "Val:", size = ( 280, -1 ) )
        self._TxtCrtlVal = wx.TextCtrl( panel, -1, "", size = ( 280, -1 ) )
        
        _labelAttr = wx.StaticText( panel, -1, "Attr:", size = ( 280, -1 ) )
        self._TxtCrtlAttr = wx.TextCtrl( panel, -1, "", size = ( 280, -1 ) )
        
        _labelUsr = wx.StaticText( panel, -1, "Usr Def:", size = ( 280, -1 ) )
        self._TxtCrtlUsr = wx.TextCtrl( panel, -1, "", size = ( 280, -1 ) )
        
        _labelDes = wx.StaticText( panel, -1, "Description:", size = ( 280, -1 ) )
        self._TxtCrtlDes = wx.TextCtrl( panel, -1, "", size = ( 280, -1 ) )

        _BoxRightSizer.Add( _labelID, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND , 5 )
        _BoxRightSizer.Add( self._TxtCrtlID, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND , 5 )
        _BoxRightSizer.Add( _labelVal, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND , 5 )
        _BoxRightSizer.Add( self._TxtCrtlVal, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND , 5 )
        _BoxRightSizer.Add( _labelAttr, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND , 5 )
        _BoxRightSizer.Add( self._TxtCrtlAttr, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _BoxRightSizer.Add( _labelUsr, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _BoxRightSizer.Add( self._TxtCrtlUsr, 2, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _BoxRightSizer.Add( _labelDes, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _BoxRightSizer.Add( self._TxtCrtlDes, 4, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
#        _FrameboxRight.Add(_BoxSizer, 1, wx.ALL, 1)
        
        _Framebox.Add( _BoxLeftSizer, 1, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( _BoxRightSizer, 2, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5 )
        
        
        self.line = wx.StaticLine( panel )
          
        # Frame for buttons
        _FrameboxBtn = wx.BoxSizer( wx.HORIZONTAL )
        
        self.btnSav = wx.Button( panel, -1, "Save", size = ( 80, -1 ) )
        self.btnMod = wx.Button( panel, -1, "Mod", size = ( 80, -1 ) )
        self.btnAdd = wx.Button( panel, -1, "Add", size = ( 80, -1 ) )
        self.btnDel = wx.Button( panel, -1, "Del", size = ( 80, -1 ) )
        
        
        _FrameboxBtn.Add( self.btnMod, 1, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5 )
        _FrameboxBtn.Add( self.btnAdd, 1, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5 )
        _FrameboxBtn.Add( self.btnDel, 1, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5 )
        _FrameboxBtn.Add( self.btnSav, 1, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5 )
        
        _Frame.Add( _Framebox, 24, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5 )
        _Frame.Add( self.line , 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 3 )
        _Frame.Add( _FrameboxBtn, 2, wx.ALIGN_RIGHT | wx.ALL, 5 )
        
        
        panel.SetSizer( _Frame )
        
        self.BindEvents()
        
        self.initFrame()
        
    def initFrame( self ):
        self._listBox.SetItems( self.usrDefDat.getDictKW() )
        self._TxtCrtlID.Disable()
        self._TxtCrtlVal.Disable()
        self._TxtCrtlAttr.Disable()
        self._TxtCrtlUsr.Disable()
        self._TxtCrtlDes.Disable()
        
    def BindEvents( self ):
        self.Bind( wx.EVT_COMBOBOX, self.OnSelSrc, self.FrameComBoBox1 )
        self.Bind( wx.EVT_LISTBOX, self.OnSelLst, self._listBox )
        self.Bind( wx.EVT_BUTTON, self.OnBtnSavClk, self.btnSav )
        self.Bind( wx.EVT_BUTTON, self.OnBtnModClk, self.btnMod )
        self.Bind( wx.EVT_BUTTON, self.OnBtnAddClk, self.btnAdd )
        self.Bind( wx.EVT_BUTTON, self.OnBtnDelClk, self.btnDel )
    
    
    def OnSelSrc( self, event ):
        "on select source: constant or user defined data"
        _content = self.FrameComBoBox1.GetValue()
        print _content
        
        if _content == "Const":
            self._listBox.SetItems( self.usrDefDat.getDictKW() )
            self._TxtCrtlUsr.Disable()
        if _content == "UsrDef":
            self._TxtCrtlID.Disable()
            self._TxtCrtlVal.Disable()
            self._TxtCrtlAttr.Disable()
            self._TxtCrtlUsr.Enable()
            self._TxtCrtlDes.Enable()
            self._listBox.SetItems( self.usrDefDat.getUsrDefDictKW() )
            
        
    def OnSelLst( self, event ):
        "on select list"
        _id = self._listBox.GetSelection()
        print _id
        
        _content = self.FrameComBoBox1.GetValue()
        print _content
        if _content == "Const":
            self._TxtCrtlID.Enable()
            self._TxtCrtlVal.Enable()
            self._TxtCrtlAttr.Enable()
            self._TxtCrtlDes.Enable()
            
            self._TxtCrtlID.SetValue( self._listBox.GetItems()[_id] ) 
            self._TxtCrtlVal.SetValue( str( self.usrDefDat.ifMapConst( self._listBox.GetItems()[_id] ) ) )
            self._TxtCrtlAttr.SetValue( self.usrDefDat.ifMapConstType( self._listBox.GetItems()[_id] ) )
            self._TxtCrtlDes.SetValue( self.usrDefDat.ifMapConstDes( self._listBox.GetItems()[_id] ) )
            
        if _content == "UsrDef":
            self._TxtCrtlID.SetValue( self._listBox.GetItems()[_id] )
            self._TxtCrtlID.Enable()
            self._TxtCrtlUsr.SetValue( self.usrDefDat.ifMapUsrDef( self._listBox.GetItems()[_id] ) )
            self._TxtCrtlDes.SetValue( self.usrDefDat.ifMapUsrDefDes( self._listBox.GetItems()[_id] ) ) 
        
        
    def OnBtnSavClk( self, event ):
        "on click button save"
        self.usrDefDat.savUsrDefDat( self.usrDefDat.ConstDict, self.usrDefDat.UsrDefDict )
        
    def OnBtnModClk( self, event ):
        "on click button modify"
        _content = self.FrameComBoBox1.GetValue()
        if _content == "Const":
            name = self._TxtCrtlID.GetValue()
            type = self._TxtCrtlAttr.GetValue()
            des = self._TxtCrtlDes.GetValue()
                
            if type == 'int':
                value = int( self._TxtCrtlVal.GetValue() )
            elif type == 'float':
                value = float( self._TxtCrtlVal.GetValue() )
            else:
                value = self._TxtCrtlVal.GetValue()  
            rt = self.usrDefDat.modOneEle( name, value, type, des )
            if rt == -1:
                wx.MessageBox( "Modify Error, ID changed!!!" )
         
        if _content == "UsrDef":
            name = self._TxtCrtlID.GetValue()
            des = self._TxtCrtlDes.GetValue()
            ruleDict = self.usrDefDat.ifMapUsrDefDict( self._TxtCrtlUsr.GetValue() )
            
            rt = self.usrDefDat.modOneUsrDef( name, ruleDict, des )
            if rt == -1:
                wx.MessageBox( "Modify Error, ID changed!!!" )
                  
        
    def OnBtnAddClk( self, event ):
        "on click button add"
        _content = self.FrameComBoBox1.GetValue()
        if _content == "Const":
            name = self._TxtCrtlID.GetValue()
        
            type = self._TxtCrtlAttr.GetValue()
            
            des = self._TxtCrtlDes.GetValue()
        
            if type == 'int':
                value = int( self._TxtCrtlVal.GetValue() )
            elif type == 'float':
                value = float( self._TxtCrtlVal.GetValue() )
            else:
                value = self._TxtCrtlVal.GetValue()        
        
            self.usrDefDat.addOneEle( name, value, type, des )
            #refresh list box
            self._listBox.SetItems( self.usrDefDat.getDictKW() )
   
        if _content == "UsrDef":
            name = self._TxtCrtlID.GetValue()
            
            ruleDict = self.usrDefDat.ifMapUsrDefDict( self._TxtCrtlUsr.GetValue() )
            
            des = self._TxtCrtlDes.GetValue()
            
            self.usrDefDat.addOneUsrDef( name, ruleDict, des )
            
            #refresh list box
            self._listBox.SetItems( self.usrDefDat.getUsrDefDictKW() )
                
        
    def OnBtnDelClk( self, event ):
        "on click button delete"
        _content = self.FrameComBoBox1.GetValue()
        if _content == "Const":
            name = self._TxtCrtlID.GetValue()
            print "del", name
            self.usrDefDat.delOneEle( name )
        
            # refresh list box
            self._listBox.SetItems( self.usrDefDat.getDictKW() )
            
        if _content == "UsrDef":
            name = self._TxtCrtlID.GetValue()
            self.usrDefDat.delOneUsrDef( name )
            
            # refresh list box
            self._listBox.SetItems( self.usrDefDat.getUsrDefDictKW() )
        
#    def UpdLstVal(self):
#        "refresh listbox value after combobox selected"
        
        
    
if __name__ == "__main__": 
    app = wx.PySimpleApp( 0 )
    wx.InitAllImageHandlers()
    frame_1 = EditUsrDefXML( None, -1, "Edit UsrDefXML", size = ( 800, 600 ), style = wx.DEFAULT_FRAME_STYLE )
    app.SetTopWindow( frame_1 )
    frame_1.Show()
    app.MainLoop()
    
