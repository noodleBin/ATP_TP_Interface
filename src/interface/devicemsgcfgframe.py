#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2013-6-6

@author: Administrator
'''
import  wx
from base import devicemsgcfg
from interface.simplecontrol import ShowGrid, EditGrid

TypeList  = ['int' ,'float',  'string', 'complex']
IOList    = ['Input' ,'Log']

def SetCusFont( obj,
                PointSize = 10,
                Famliy = wx.SWISS,
                Style = wx.NORMAL,
                Weight = wx.NORMAL,
                Face = "Cambria" ):
    font = wx.Font( PointSize, Famliy, Style, Weight, face = Face )
    obj.SetFont( font )

def GetFont( PointSize = 10,
            Famliy = wx.SWISS,
            Style = wx.NORMAL,
            Weight = wx.NORMAL,
            Face = "Cambria" ):
    return wx.Font( PointSize, Famliy, Style, Weight, face = Face )

def makePageTitle( Pg, title ):
    sizer = wx.BoxSizer( wx.VERTICAL )
    Pg.SetSizer( sizer )
    title = wx.StaticText( Pg, -1, title )
    title.SetFont( wx.Font( 18, wx.SWISS, wx.NORMAL, wx.BOLD ) )
    sizer.Add( title, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
    sizer.Add( wx.StaticLine( Pg, -1 ), 0, wx.EXPAND | wx.ALL, 5 )
    return sizer
#---------------------------------------------------------------------------

class DeviceMsgCfgFrame(wx.Frame):
    #有几种类型：0：txt，1：combox，2：button
    #格式，[名字，类型，标签ref，控件ref]：button的标签ref为None    
    Var_Ctrl = [[['Index:', 0, None, None ],['Format:', 0, None, None ]],
                          [['Name:',0, None, None ]]]

    Msg_Ctrl = [[['MsgName:', 0, None, None ]], \
                          [['Msg_Id:', 0, None, None ],
                         ['PackType:', 0, None, None ]],
                         [['Add Msg', 2, None, None ], \
                          ['Del Msg', 2, None, None ],
                          ['Edit Msg', 2, None, None ]]]

    Item_Ctrl = [[['Add Item', 2, None, None ], \
                          ['Del Item', 2, None, None ],
                          ['Edit Item', 2, None, None ]]]
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE
            ):      
        wx.Frame.__init__( self, parent, ID, title, pos, size, style )
        panel = wx.Panel( self, -1 ) #frame必须有panel，否则一些事件响应会有问题        
        
        self.deviceMsg = devicemsgcfg.DeviceMsgCfg()
        #获得路径下，文件信息
        self.path = self.deviceMsg.getMsgDevicePath()        
        self.devName,self.fileName = self.deviceMsg.getMsgDeviceFile(self.path)
        self.curDevName  =  self.devName[0]
        
        #================== 开始画控件 ============================
        _Framebox = wx.BoxSizer( wx.VERTICAL )
        
        _Box = wx.BoxSizer( wx.HORIZONTAL ) 
        label = wx.StaticText( panel, -1, "Please Choose Message Device:", size = ( 100, -1 ) )
        SetCusFont( label, 12, Weight = wx.BOLD, Face = "Calibri" )
        self.DevChoiceComBoBox = wx.ComboBox( panel, -1, '', \
                                          size = ( 50, -1 ), \
                                          choices = self.devName,
                                          style = wx.CB_DROPDOWN )
        _Box.Add( label, 2, wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND, 1 )
        _Box.Add( self.DevChoiceComBoBox, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND , 1)
        
        box3 = wx.BoxSizer( wx.VERTICAL )
        self.__MsgGrid = ShowGrid( panel, [ 'MsgName', 'Id', 'Pack'], OnSelectHandle = self.OnSelectMsgNameChange )
        _box_MsgCfg = self.createMsgCtrls( panel,self.Msg_Ctrl )
        box3.Add( _Box, 0, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 20 )
        box3.Add( self.__MsgGrid, 2, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )
        box3.Add( _box_MsgCfg, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )
        
        box1 = wx.BoxSizer( wx.VERTICAL )
        label = wx.StaticText( panel, -1, 'Index List:', size = ( 50, -1 ) )
        SetCusFont( label, 14, Weight = wx.BOLD, Face = "Calibri" )
        self.__idxList = wx.ListBox( panel, -1, size = ( 50, 50 ), \
#                                     choices = self.__casenode.getDeviceList(), \
                                     choices = [], \
                                     style = wx.LB_SINGLE )
        SetCusFont( self.__idxList, 12, Weight = wx.BOLD, Face = "Calibri" )
        box1.Add( label, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )
        box1.Add( self.__idxList, 13, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1)
        
        box2 = wx.BoxSizer( wx.VERTICAL )
        _box_var = self.createCtrls( panel,self.Var_Ctrl )
        _box_cfg = self.createCtrls( panel,self.Item_Ctrl )      
        self.DevDesTxt = wx.TextCtrl( panel, -1, '', size = ( 100, 30 ), style = wx.TE_MULTILINE )
        SetCusFont( self.DevDesTxt, 14, Weight = wx.BOLD, Face = "Calibri" )
        box2.Add( _box_var, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )
        box2.Add( self.DevDesTxt, 3, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )        
        box2.Add( _box_cfg, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )
       
        _boxH = wx.BoxSizer( wx.HORIZONTAL )
        _boxH.Add( box3, 4, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _boxH.Add( box1, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )        
        _boxH.Add( box2, 3, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        line = wx.StaticLine( panel, -1, size = ( 2,-1 ), style = wx.LI_HORIZONTAL )
        _box_finish = wx.BoxSizer( wx.HORIZONTAL )
        self.okBtn = wx.Button( panel, -1, "OK", size = ( 100, -1 ) )
        self.cancelBtn = wx.Button( panel, -1, "Cancel", size = ( 100, -1 ) )
        _box_finish.Add( self.okBtn, 1, wx.ALIGN_RIGHT| wx.ALL , 5 ) 
        _box_finish.Add( self.cancelBtn, 1, wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND, 5 ) 
        
        _Framebox.Add( _boxH, 4, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( line, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP | wx.GROW | wx.EXPAND, 5 )
        #_Framebox.Add( wx.StaticLine( self, -1 ), 0, wx.EXPAND | wx.ALL, 5 )
        _Framebox.Add( _box_finish, 0,  wx.ALIGN_RIGHT | wx.ALL , 5 )
        
        panel.SetSizer( _Framebox )
        _Framebox.Fit( self )
        #================== 结束画控件 ============================
        self.iniDate()
        self.BindEvents()
    
    def EnableItemCtrl( self, enable ,Item_Ctrl):       
        "enable item ctrl"
        for _item in Item_Ctrl:
            _item[-1].Enable( enable )
    
    def iniDate( self ):       
        "ini data"
        self.__MsgGrid.setCustable( [] )
        self.__idxList.SetItems( ' ' )
        self.__idxList.SetSelection( -1 ) 
        self.EnableItemCtrl(False,self.Msg_Ctrl[2])
        self.__idxList.Enable(False)
        self.EnableItemCtrl(False,self.Item_Ctrl[0])
        self.DevDesTxt.Clear()
        
    def updataMsg(self):
        self.__MsgGrid.setCustable( self.MsgGridShow )
        self.__MsgGrid.SetSelection(self.currGridIdx)
        
        self.Msg_Ctrl[0][0][-1].SetValue( self.DevMsgName[self.currGridIdx] )
        self.Msg_Ctrl[1][0][-1].SetValue( self.DevMsgId[self.currGridIdx] )
        self.Msg_Ctrl[1][1][-1].SetValue( self.DevMsgPack[self.currGridIdx] )     
        
        self.EnableItemCtrl(True,self.Item_Ctrl[0])   
        
    #返回ItmList[idx][num][:]值
    def getItmInList(self,idx,ItmList,num):
        _rtList = []
        for _i, _c in enumerate( ItmList[idx] ):
            _rtList.append(_c[num])
        return _rtList
    
    def updataIndexItem(self):        
        self.Var_Ctrl[0][0][-1].Clear()
        self.Var_Ctrl[0][1][-1].Clear()
        self.Var_Ctrl[1][0][-1].Clear()
        self.DevDesTxt.Clear()
        _index = self.__idxList.GetSelection()
        if _index not in [None, -1]:
            self.DevDesTxt.SetValue( self.MsgItemList[self.currGridIdx][_index][3] )
            self.Var_Ctrl[0][0][-1].SetValue( self.MsgItemList[self.currGridIdx][_index][0] )
            self.Var_Ctrl[0][1][-1].SetValue( self.MsgItemList[self.currGridIdx][_index][1] )
            self.Var_Ctrl[1][0][-1].SetValue( self.MsgItemList[self.currGridIdx][_index][2] )
        self.EnableItemCtrl(True,self.Item_Ctrl[0])  
            
    def OnSelectMsgNameChange( self, event ):
        "On Select Name Value Change"
        self.__MsgGrid.OnSelect( event )      
        _value = self.__MsgGrid.GetSelectData()
        self.currGridIdx = self.__MsgGrid.GetSelection()
        IndexList = self.getItmInList(self.currGridIdx,self.MsgItemList,0)
        if None == _value:
            return
        self.EnableItemCtrl(True,self.Msg_Ctrl[2])
        self.__idxList.Enable(True)
        self.EnableItemCtrl(False,self.Item_Ctrl[0])
        self.Msg_Ctrl[0][0][-1].SetValue( _value[0] )
        self.Msg_Ctrl[1][0][-1].SetValue( _value[1] )
        self.Msg_Ctrl[1][1][-1].SetValue( _value[2] )
        self.__idxList.SetItems( IndexList )
        self.__idxList.SetSelection( len(IndexList)-1 )
        self.updataIndexItem()
        
    def BindEvents(self):
        self.Bind( wx.EVT_COMBOBOX, self.OnDevChoiceChange, self.DevChoiceComBoBox )
        self.Bind( wx.EVT_LISTBOX, self.OnChangeIdx, self.__idxList )
        
        self.Bind( wx.EVT_BUTTON, self.OnOK, self.okBtn )
        self.Bind( wx.EVT_BUTTON, self.OnCancel, self.cancelBtn )
        
        self.Bind( wx.EVT_BUTTON, self.OnAddMsg,  self.Msg_Ctrl[2][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelMsg,  self.Msg_Ctrl[2][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnEditMsg, self.Msg_Ctrl[2][2][-1] )
        
        self.Bind( wx.EVT_BUTTON, self.OnAddItem, self.Item_Ctrl[0][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelItem, self.Item_Ctrl[0][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnEditItem, self.Item_Ctrl[0][2][-1] )
        
    def OnAddMsg( self, event ):
        "click button add a value."
        _nName    = self.Msg_Ctrl[0][0][-1].GetValue() 
        _nId      = self.Msg_Ctrl[1][0][-1].GetValue()   
        _nPack    = self.Msg_Ctrl[1][1][-1].GetValue() 
        _nMsgItem = []    
        
        self.currGridIdx = len(self.DevMsgName)
        self.deviceMsg.DevAddTmpMsg(_nName,self.DevMsgName)
        self.deviceMsg.DevAddTmpMsg(_nId,self.DevMsgId)
        self.deviceMsg.DevAddTmpMsg(_nPack,self.DevMsgPack)
        self.deviceMsg.DevAddTmpMsg([_nName,_nId,_nPack],self.MsgGridShow)
        self.deviceMsg.DevAddTmpMsg(_nMsgItem,self.MsgItemList)
        
        self.updataMsg()        
        
        IndexList = self.getItmInList(self.currGridIdx,self.MsgItemList,0)
        self.__idxList.SetItems( IndexList )
        self.__idxList.SetSelection( len(IndexList)-1 )
        self.updataIndexItem()
    
    def OnDelMsg( self, event ):
        "click button delete a value."
        self.currGridIdx = self.__MsgGrid.GetSelection()
        if self.currGridIdx not in [None, -1]:
            self.deviceMsg.DevDeleteTmpMsg( self.DevMsgName,self.currGridIdx)
            self.deviceMsg.DevDeleteTmpMsg( self.DevMsgId ,self.currGridIdx)
            self.deviceMsg.DevDeleteTmpMsg( self.DevMsgPack ,self.currGridIdx)
            self.deviceMsg.DevDeleteTmpMsg( self.MsgGridShow ,self.currGridIdx)
            self.deviceMsg.DevDeleteTmpMsg( self.MsgItemList ,self.currGridIdx)
            if len(self.DevMsgName) > 0:
                self.currGridIdx = ( self.currGridIdx-1 if self.currGridIdx > 0 else 0 )
            
            self.updataMsg()            
            
            IndexList = self.getItmInList(self.currGridIdx,self.MsgItemList,0)
            self.__idxList.SetItems( IndexList )
            if len(IndexList)> 0:
                self.__idxList.SetSelection(  0 )
            self.updataIndexItem()
    
    def OnEditMsg( self, event ):#Jyno 2013/06/08
        "click button edit a value."
        self.currGridIdx = self.__MsgGrid.GetSelection()
        _index = self.__idxList.GetSelection()
        _nName    = self.Msg_Ctrl[0][0][-1].GetValue() 
        _nId      = self.Msg_Ctrl[1][0][-1].GetValue()   
        _nPack    = self.Msg_Ctrl[1][1][-1].GetValue()
        
        self.deviceMsg.DevModifyTmpMsg(_nName,self.DevMsgName,self.currGridIdx)
        self.deviceMsg.DevModifyTmpMsg(_nId,self.DevMsgId,self.currGridIdx)
        self.deviceMsg.DevModifyTmpMsg(_nPack,self.DevMsgPack,self.currGridIdx)
        self.deviceMsg.DevModifyTmpMsg([_nName,_nId,_nPack],self.MsgGridShow,self.currGridIdx)
        
        self.updataMsg()        
        
        IndexList = self.getItmInList(self.currGridIdx,self.MsgItemList,0)
        self.__idxList.SetItems( IndexList )
        self.__idxList.SetSelection( _index )
        self.updataIndexItem()
    
    def OnAddItem( self, event ):
        "click button add a value."
        _nIndex = self.Var_Ctrl[0][0][-1].GetValue()        
        _nFormat= self.Var_Ctrl[0][1][-1].GetValue()
        _nName  = self.Var_Ctrl[1][0][-1].GetValue()        
        _nDesTxt= self.DevDesTxt.GetValue()
        
        self.MsgItemList[self.currGridIdx].append([_nIndex,_nFormat,_nName,_nDesTxt])
        IndexList = self.getItmInList(self.currGridIdx,self.MsgItemList,0)
        self.__idxList.SetItems( IndexList )
        self.__idxList.SetSelection( len(IndexList)-1 )
        self.updataIndexItem()
    
    def OnDelItem( self, event ):
        "click button delete a value."        
        _index = self.__idxList.GetSelection()
        if _index not in [None, -1]:
            self.MsgItemList[self.currGridIdx].pop(_index)
            
            IndexList = self.getItmInList(self.currGridIdx,self.MsgItemList,0)
            self.__idxList.SetItems( IndexList )
            if len(IndexList)> 0:
                self.__idxList.SetSelection( _index-1 if _index > 0 else 0 )
            self.updataIndexItem()
    
    def OnEditItem( self, event ):#Jyno 2013/06/08
        "click button edit a value."
        _index = self.__idxList.GetSelection()
        _nIndex = self.Var_Ctrl[0][0][-1].GetValue()        
        _nFormat= self.Var_Ctrl[0][1][-1].GetValue()
        _nName = self.Var_Ctrl[1][0][-1].GetValue()        
        _nDesTxt= self.DevDesTxt.GetValue()
        self.MsgItemList[self.currGridIdx][_index]=[_nIndex,_nFormat,_nName,_nDesTxt]
        
        IndexList = self.getItmInList(self.currGridIdx,self.MsgItemList,0)
        self.__idxList.SetItems( IndexList )
        self.__idxList.SetSelection( _index )
        self.updataIndexItem()
    
    def OnOK( self, event ):
        "click OK."
        print "store the Variant Configuration change"
        _oneValue = []
        _tmp_DevMsg = []
        if len(self.DevMsgName) != 0:
            for _i, _c in enumerate( self.DevMsgName ):
                _oneValue.append(self.DevMsgName[_i])
                _oneValue.append(self.DevMsgId[_i])
                _oneValue.append(self.DevMsgPack[_i])
                _oneValue.append(self.MsgItemList[_i])
                _tmp_DevMsg.append(_oneValue)
                _oneValue = []        
            self.deviceMsg.saveDevMsg(self.curDevName,_tmp_DevMsg)
        self.Close(True)
    
    def OnCancel( self, event ):
        "click Cancel."
        self.Close(True)
    
    def OnChangeIdx( self, event ):
        "on change Index of Device."
        _index = self.__idxList.GetSelection()
        if _index not in [-1, None]:
            self.EnableItemCtrl(True,self.Item_Ctrl[0])
            
            self.DevDesTxt.SetValue( self.MsgItemList[self.currGridIdx][_index][3] )
            self.Var_Ctrl[0][0][-1].SetValue( self.MsgItemList[self.currGridIdx][_index][0] )
            self.Var_Ctrl[0][1][-1].SetValue( self.MsgItemList[self.currGridIdx][_index][1] )
            self.Var_Ctrl[1][0][-1].SetValue( self.MsgItemList[self.currGridIdx][_index][2] )
        
    def OnDevChoiceChange( self, event ):
        "On Device choice Change"
        self.curDevName = self.DevChoiceComBoBox.GetValue()        
        if "" == self.curDevName or None == self.curDevName:
            wx.MessageBox( "Device choice Change error!" )
            return
        #=======================================================================
        # 从XX_message.xml读入数据
        # 并存储在临时变量中
        # Jyno 2013/06/08 
        #=======================================================================
        self.DevMsgName   = []
        self.DevMsgId     = []
        self.DevMsgPack   = []
        self.MsgItemList  = []
        self.MsgGridShow  = []
        self.DevMsgData = self.deviceMsg.getDevMsg(self.curDevName)
        for _i, _c in enumerate( self.DevMsgData ):
            self.DevMsgName.append(_c[0])
            self.DevMsgId.append(_c[1])
            self.DevMsgPack.append(_c[2])
            self.MsgGridShow.append([_c[0],_c[1],_c[2]])
            self.MsgItemList.append(_c[3])
        
        if(len(self.DevMsgName)!=len(self.DevMsgId) or\
           len(self.DevMsgPack)!=len(self.DevMsgName)or\
           len(self.DevMsgName)!=len(self.MsgItemList)or\
           len(self.DevMsgName)==0):
            wx.MessageBox( "Error!!!Four items length in XX_message.xml is not same" )        
        
        self.__MsgGrid.setCustable(self.MsgGridShow)
        
    def createMsgCtrls( self, panel,list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):   #_item = ['Type', 1, None, None ]
                if 0 == _item[1]:
                    _label, _txtctl = self.createNewMsgText( panel,_item[0] )
                    _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _txtctl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][2] = _label
                    list[_i][_j][3] = _txtctl
                elif 1 == _item[1]:
                    _label, _ctrl = self.createNewMsgCombox( panel,_item[0], _item[2] )
                    _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl
                elif 2 == _item[1]: 
                    _ctrl = self.createNewMsgButton( panel,_item[0] )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl                                                           
                    
            revbox.Add( _Hbox, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
        return revbox        
    def createNewMsgText( self, panel,label ):
        "create Text."
        label = wx.StaticText( panel, -1, label, size = ( 70, -1 ) )
#        label.SetLabel()
        txtctrl = wx.TextCtrl( panel, -1, '', size = ( 150, -1 ) )
#        txtctrl.GetString()
#        txtctrl.SetEditable()                         
        return label, txtctrl

    def createNewMsgCombox( self, panel,label, list ):
        "create new comboBox"
        label = wx.StaticText( panel, -1, label, size = ( 50, -1 ) )
        _value = '' if 0 == len( list ) else list[0]
        ctrl = wx.ComboBox( panel, -1, _value, size = ( 100, -1 ), choices = list, style = wx.CB_DROPDOWN )
#        ctrl.SetItems(items)
        return label, ctrl        
        
    def createNewMsgButton( self, panel,label ):
        "create new Button"
#        label = wx.StaticText( self, -1, label, size = ( 120, -1 ) )
        _ctrl = wx.Button( panel, -1, label, size = ( 100, -1 ) )
        return _ctrl
    
    def createCtrls( self, panel,list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):   #_item = ['Type', 1, None, None ]
                if 0 == _item[1]:
                    _label, _txtctl = self.createNewText( panel,_item[0] )
                    _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _txtctl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][2] = _label
                    list[_i][_j][3] = _txtctl
                elif 1 == _item[1]:
                    _label, _ctrl = self.createNewCombox( panel,_item[0], _item[2] )
                    _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl
                elif 2 == _item[1]: 
                    _ctrl = self.createNewButton( panel,_item[0] )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl                                                           
                    
            revbox.Add( _Hbox, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
        return revbox        
    def createNewText( self, panel,label ):
        "create Text."
        label = wx.StaticText( panel, -1, label, size = ( 50, -1 ) )
#        label.SetLabel()
        txtctrl = wx.TextCtrl( panel, -1, '', size = ( 100, -1 ) )
#        txtctrl.GetString()
#        txtctrl.SetEditable()                         
        return label, txtctrl

    def createNewCombox( self, panel,label, list ):
        "create new comboBox"
        label = wx.StaticText( panel, -1, label, size = ( 50, -1 ) )
        _value = '' if 0 == len( list ) else list[0]
        ctrl = wx.ComboBox( panel, -1, _value, size = ( 100, -1 ), choices = list, style = wx.CB_DROPDOWN )
#        ctrl.SetItems(items)
        return label, ctrl        
        
    def createNewButton( self, panel,label ):
        "create new Button"
#        label = wx.StaticText( self, -1, label, size = ( 120, -1 ) )
        _ctrl = wx.Button( panel, -1, label, size = ( 100, -1 ) )
        return _ctrl
                
if __name__ == "__main__": 
    app = wx.PySimpleApp( 0 ) 
    wx.InitAllImageHandlers()
    frame_1 = DeviceMsgCfgFrame( None, -1, "Device Choose", style = wx.DEFAULT_FRAME_STYLE )
    app.SetTopWindow( frame_1 )
    frame_1.Show()
    app.MainLoop()