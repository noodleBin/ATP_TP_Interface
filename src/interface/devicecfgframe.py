#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2013-6-3

@author: Administrator
'''
import  wx
import os
from base import deviceconfig
from base.xmldeal import XMLDeal

TypeList = ['int' , 'float', 'string', 'complex']
IOList = ['Input' , 'Log']
NameList = ['Please insert name']
ValueList = ['Please insert Value']

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

class DeviceCfgFrame( wx.Frame ):
    #有几种类型：0：txt，1：combox，2：button
    #格式，[名字，类型，标签ref，控件ref]：button的标签ref为None    
    Var_Ctrl = [[['Name:', 0, None, None ], \
                          ['Type:', 1, [], None ]],
                          [['Value:', 0, None, None ],
                           ['IO:', 1, [], None ]]]

    Item_Ctrl = [[['Add Item', 2, None, None ], \
                          ['Del Item', 2, None, None ],
                          ['Edit Item', 2, None, None ]]]
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE
            ):      
        wx.Frame.__init__( self, parent, ID, title, pos, size, style )
        panel = wx.Panel( self, -1 ) #frame必须有panel，否则一些事件响应会有问题
        
        self.deviceVar = deviceconfig.DeviceVarCfg()
        #获得路径下，文件信息
        #并将文件名读入
        self.path = self.deviceVar.getDevicePath()        
        self.devName, self.fileName = self.deviceVar.getDeviceFile( self.path )
        self.curDevName = self.devName[0] 
        
        #================== 开始画控件 ============================
        # Jyno 2013/06/08
        _Framebox = wx.BoxSizer( wx.VERTICAL )
        
        _Box = wx.BoxSizer( wx.HORIZONTAL ) 
        label = wx.StaticText( panel, -1, "Choose Device:", size = ( 100, -1 ) )
        SetCusFont( label, 12, Weight = wx.BOLD, Face = "Calibri" )
        self.DevChoiceComBoBox = wx.ComboBox( panel, -1, '', \
                                          size = ( 50, -1 ), \
                                          choices = self.devName,
                                          style = wx.CB_DROPDOWN )
        _Box.Add( label, 2, wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND, 1 )
        _Box.Add( self.DevChoiceComBoBox, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND , 1 )
        
        box1 = wx.BoxSizer( wx.VERTICAL )
        label = wx.StaticText( panel, -1, 'Name List:', size = ( 50, -1 ) )
        SetCusFont( label, 14, Weight = wx.BOLD, Face = "Calibri" )
        self.__devList = wx.ListBox( panel, -1, size = ( 50, 50 ), \
#                                     choices = self.__casenode.getDeviceList(), \
                                     choices = [], \
                                     style = wx.LB_SINGLE )
        SetCusFont( self.__devList, 12, Weight = wx.BOLD, Face = "Calibri" )
        box1.Add( _Box, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )
        box1.Add( label, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )
        box1.Add( self.__devList, 13, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )
        
        box2 = wx.BoxSizer( wx.VERTICAL )
        _box_var = self.createCtrls( panel, self.Var_Ctrl )
        _box_cfg = self.createCtrls( panel, self.Item_Ctrl )      
        self.DevDesTxt = wx.TextCtrl( panel, -1, '', size = ( 100, 30 ), style = wx.TE_MULTILINE )
        SetCusFont( self.DevDesTxt, 14, Weight = wx.BOLD, Face = "Calibri" )
        box2.Add( _box_var, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )
        box2.Add( self.DevDesTxt, 3, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )        
        box2.Add( _box_cfg, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 1 )
       
        _boxH = wx.BoxSizer( wx.HORIZONTAL )
        _boxH.Add( box1, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )        
        _boxH.Add( box2, 2, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        line = wx.StaticLine( panel, -1, size = ( 2, -1 ), style = wx.LI_HORIZONTAL )
        _box_finish = wx.BoxSizer( wx.HORIZONTAL )
        self.okBtn = wx.Button( panel, -1, "OK", size = ( 100, -1 ) )
        self.cancelBtn = wx.Button( panel, -1, "Cancel", size = ( 100, -1 ) )
        _box_finish.Add( self.okBtn, 1, wx.ALIGN_RIGHT | wx.ALL , 5 ) 
        _box_finish.Add( self.cancelBtn, 1, wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND, 5 ) 
        
        _Framebox.Add( _boxH, 4, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( line, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP | wx.GROW | wx.EXPAND, 5 )
        #_Framebox.Add( wx.StaticLine( self, -1 ), 0, wx.EXPAND | wx.ALL, 5 )
        _Framebox.Add( _box_finish, 0, wx.ALIGN_RIGHT | wx.ALL , 5 )
        
        panel.SetSizer( _Framebox )
        _Framebox.Fit( self )
        #================== 结束画控件 ============================
        
        self.EnableItemCtrl( False ) 
        self.iniDate()
        self.BindEvents()
        
    def iniDate( self ):
        self.__devList.SetItems( ' ' )
        self.__devList.SetSelection( -1 )
        
        self.Var_Ctrl[0][1][-1].SetItems( TypeList )
        self.Var_Ctrl[0][1][-1].SetSelection( 0 )
        self.Var_Ctrl[1][1][-1].SetItems( IOList )
        self.Var_Ctrl[1][1][-1].SetSelection( 0 )
        
    def updataPage( self ):
        _index = self.__devList.GetSelection()
        if _index < 0 :
            _index = 0
        self.__devList.SetItems( self.tmp_DevName )
        self.__devList.SetSelection( _index )
        
        self.DevDesTxt.SetValue( self.tmp_DevDescription[_index] )
        self.Var_Ctrl[0][0][-1].SetValue( self.tmp_DevName[_index] )
        self.Var_Ctrl[0][1][-1].SetValue( self.tmp_DevType[_index] )
        self.Var_Ctrl[1][0][-1].SetValue( self.tmp_DevValue[_index] )
        self.Var_Ctrl[1][1][-1].SetValue( self.tmp_DevIO[_index] )
        self.EnableItemCtrl( True )
       
    def EnableItemCtrl( self, enable ):       
        "enable item ctrl"
        self.DevDesTxt.Enable( enable )
        for _row in self.Item_Ctrl:
            for _item in _row:
                if ( True == enable ) and ( _item == self.Item_Ctrl[0][2] ):#不用这个函数设置edit的true
                    pass
                else:
                    _item[-1].Enable( enable )
      
        
    def BindEvents( self ):
        self.Bind( wx.EVT_COMBOBOX, self.OnDevChoiceChange, self.DevChoiceComBoBox )
        self.Bind( wx.EVT_LISTBOX, self.OnChangeDev, self.__devList )
        
        self.Bind( wx.EVT_BUTTON, self.OnOK, self.okBtn )
        self.Bind( wx.EVT_BUTTON, self.OnCancel, self.cancelBtn )
        
        self.Bind( wx.EVT_BUTTON, self.OnAddItem, self.Item_Ctrl[0][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelItem, self.Item_Ctrl[0][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnEditItem, self.Item_Ctrl[0][2][-1] )
  
        
    def OnDevChoiceChange( self, event ):
        "On Device choice Change"
        self.curDevName = self.DevChoiceComBoBox.GetValue()
        if "" == self.curDevName or None == self.curDevName:
            wx.MessageBox( "Device choice Change error!" )
            return
        #=======================================================================
        # 从xx_variant.xml读入数据
        # 并存储在临时变量中
        # Jyno 2013/06/08 
        #=======================================================================
        self.tmp_DevName = []
        self.tmp_DevType = []
        self.tmp_DevIO = []
        self.tmp_DevValue = []
        self.tmp_DevDescription = []
        _deviceFile = self.fileName[self.devName.index( self.curDevName )]
        self.DevPathFile = os.path.join( self.path, _deviceFile )       
        self.DevVar = XMLDeal.importVariant( self.DevPathFile )
        #print self.DevVar
        for _i, _c in enumerate( self.DevVar ):
            self.tmp_DevName.append( _c[0] )
            self.tmp_DevType.append( _c[1] )
            self.tmp_DevIO.append( _c[2] )
            self.tmp_DevValue.append( _c[3] )
            self.tmp_DevDescription.append( _c[4] )
        if( len( self.tmp_DevName ) != len( self.tmp_DevType ) or\
           len( self.tmp_DevIO ) != len( self.tmp_DevValue )or\
           len( self.tmp_DevIO ) != len( self.tmp_DevDescription )or\
           len( self.tmp_DevType ) != len( self.tmp_DevDescription ) ):
            wx.MessageBox( "Error!!!Four items length in Dev_variant.xml is not same" )        
        
        self.updataPage()
        
    def OnAddItem( self, event ):
        "click button add a value."
        self.EnableItemCtrl( False )
        self.Item_Ctrl[0][2][-1].Enable( False )
        _nName = self.Var_Ctrl[0][0][-1].GetValue()        
        _nType = self.Var_Ctrl[0][1][-1].GetValue()
        _nValue = self.Var_Ctrl[1][0][-1].GetValue()
        _nIO = self.Var_Ctrl[1][1][-1].GetValue()
        _nDesTxt = self.DevDesTxt.GetValue()
        self.deviceVar.DevUpdateTmpData( _nName, self.tmp_DevName )
        self.deviceVar.DevUpdateTmpData( _nType, self.tmp_DevType )
        self.deviceVar.DevUpdateTmpData( _nValue, self.tmp_DevValue )
        self.deviceVar.DevUpdateTmpData( _nIO, self.tmp_DevIO )
        self.deviceVar.DevUpdateTmpData( _nDesTxt, self.tmp_DevDescription )
        self.__devList.SetItems( self.tmp_DevName )
        self.__devList.SetSelection( len( self.tmp_DevName ) - 1 )
        self.DevDesTxt.Clear()
        self.updataPage()
    
    def OnDelItem( self, event ):
        "click button delete a value."
        self.EnableItemCtrl( False )
        self.Item_Ctrl[0][2][-1].Enable( False )
        _index = self.__devList.GetSelection()
        if _index not in [None, -1]:
            self.deviceVar.DevDeleteTmpVariant( self.tmp_DevName, _index )
            self.deviceVar.DevDeleteTmpVariant( self.tmp_DevType, _index )
            self.deviceVar.DevDeleteTmpVariant( self.tmp_DevValue, _index )
            self.deviceVar.DevDeleteTmpVariant( self.tmp_DevIO, _index )
            self.deviceVar.DevDeleteTmpVariant( self.tmp_DevDescription, _index )
            self.__devList.SetItems( self.tmp_DevName )
            self.__devList.SetSelection( _index - 1 if _index > 0 else 0 )
            self.DevDesTxt.Clear()
            self.updataPage()
    
    def OnEditItem( self, event ):
        "click button edit a value."
        _index = self.__devList.GetSelection()
        _nName = self.Var_Ctrl[0][0][-1].GetValue()        
        _nType = self.Var_Ctrl[0][1][-1].GetValue()
        _nValue = self.Var_Ctrl[1][0][-1].GetValue()
        _nIO = self.Var_Ctrl[1][1][-1].GetValue()
        _nDesTxt = self.DevDesTxt.GetValue()
        self.deviceVar.DevModifyTmpData( _nName, self.tmp_DevName, _index )
        self.deviceVar.DevModifyTmpData( _nType, self.tmp_DevType, _index )
        self.deviceVar.DevModifyTmpData( _nValue, self.tmp_DevValue, _index )
        self.deviceVar.DevModifyTmpData( _nIO, self.tmp_DevIO, _index )
        self.deviceVar.DevModifyTmpData( _nDesTxt, self.tmp_DevDescription, _index )
        self.updataPage()
    
    def OnOK( self, event ):
        "click OK."
        print "store the Variant Configuration change"
        _oneValue = []
        _tmp_DevVar = []
        for _i, _c in enumerate( self.tmp_DevName ):
            _oneValue.append( self.tmp_DevName[_i] )
            _oneValue.append( self.tmp_DevType[_i] )
            _oneValue.append( self.tmp_DevIO[_i] )
            _oneValue.append( self.tmp_DevValue[_i] )
            _oneValue.append( self.tmp_DevDescription[_i] )
            _tmp_DevVar.append( _oneValue )
            _oneValue = []
            
        #print self.tmp_DevVar
        self.deviceVar.saveTheConfig( _tmp_DevVar, self.DevPathFile )
        self.Close( True )
    
    def OnCancel( self, event ):
        "click Cancel."
        self.Close( True )    
    
    def OnChangeDev( self, event ):
        "on change Name of Device."
        self.EnableItemCtrl( True )
        _index = self.__devList.GetSelection()
        if _index not in [-1, None]:   
                    
            self.DevDesTxt.SetValue( self.tmp_DevDescription[_index] )            
            self.Item_Ctrl[0][2][-1].Enable( True )
            self.Var_Ctrl[0][0][-1].SetValue( self.tmp_DevName[_index] )
            self.Var_Ctrl[0][1][-1].SetValue( self.tmp_DevType[_index] )
            self.Var_Ctrl[1][0][-1].SetValue( self.tmp_DevValue[_index] )
            self.Var_Ctrl[1][1][-1].SetValue( self.tmp_DevIO[_index] )
    
    
    def createCtrls( self, panel, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):   #_item = ['Type', 1, None, None ]
                if 0 == _item[1]:
                    _label, _txtctl = self.createNewText( panel, _item[0] )
                    _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _txtctl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][2] = _label
                    list[_i][_j][3] = _txtctl
                elif 1 == _item[1]:
                    _label, _ctrl = self.createNewCombox( panel, _item[0], _item[2] )
                    _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl
                elif 2 == _item[1]: 
                    _ctrl = self.createNewButton( panel, _item[0] )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl                                                           
                    
            revbox.Add( _Hbox, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
        return revbox        
    def createNewText( self, panel, label ):
        "create Text."
        label = wx.StaticText( panel, -1, label, size = ( 50, -1 ) )
#        label.SetLabel()
        txtctrl = wx.TextCtrl( panel, -1, '', size = ( 100, -1 ) )
#        txtctrl.GetString()
#        txtctrl.SetEditable()
        return label, txtctrl

    def createNewCombox( self, panel, label, list ):
        "create new comboBox"
        label = wx.StaticText( panel, -1, label, size = ( 50, -1 ) )
        _value = '' if 0 == len( list ) else list[0]
        ctrl = wx.ComboBox( panel, -1, _value, size = ( 100, -1 ), choices = list, style = wx.CB_DROPDOWN )
#        ctrl.SetItems(items)
        return label, ctrl        
        
    def createNewButton( self, panel, label ):
        "create new Button"
#        label = wx.StaticText( self, -1, label, size = ( 120, -1 ) )
        _ctrl = wx.Button( panel, -1, label, size = ( 100, -1 ) )
        return _ctrl  

class VersionFrame( wx.Frame ):
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE
            ):      
        wx.Frame.__init__( self, parent, ID, title, pos, size, style )
        panel = wx.Panel( self, -1 ) #frame必须有panel，否则一些事件响应会有问题
        
        
        _label = wx.StaticText( panel, -1, "Version: Bcode_iTC_TP_V2.1.1_Build_20141023", size = ( 380, -1 ) )
        SetCusFont( _label, 14, Weight = wx.BOLD, Face = "Calibri" )
        #================== 开始画控件 ============================
        # Jyno 2013/06/08
        _Framebox = wx.BoxSizer( wx.VERTICAL )
        _Framebox.Add( _label, 1, wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND, 5 )
        
        panel.SetSizer( _Framebox )
        _Framebox.Fit( self )

        
if __name__ == "__main__": 
    app = wx.PySimpleApp( 0 ) 
    wx.InitAllImageHandlers()
    frame_1 = DeviceCfgFrame( None, -1, "OMAP Demo", style = wx.DEFAULT_FRAME_STYLE )
    app.SetTopWindow( frame_1 )
    frame_1.Show()
    app.MainLoop()
