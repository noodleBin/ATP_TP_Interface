#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     cuscontrol.py
# Description:   
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2012-03-25
# Company:      CASCO
# LastChange:   create 2012-03-25
# History:          
#----------------------------------------------------------------------------
#import wx.wizard
import  wx
import  wx.grid as Grid
#import sys
#from base import caseprocess
from base.caseprocess import CaseParser
from base.omapparser import OMAPParser
#import time
#import  wx.lib.filebrowsebutton as filebrowse
import images
from simplecontrol import SimpleGrid
import simplepanel
import simplewizard
try:
    from agw import customtreectrl as CT
except ImportError:
    import wx.lib.agw.customtreectrl as CT
    
    
ArtIDs = [ "None",
           "wx.ART_ADD_BOOKMARK",
           "wx.ART_DEL_BOOKMARK",
           "wx.ART_HELP_SIDE_PANEL",
           "wx.ART_HELP_SETTINGS",
           "wx.ART_HELP_BOOK",
           "wx.ART_HELP_FOLDER",
           "wx.ART_HELP_PAGE",
           "wx.ART_GO_BACK",
           "wx.ART_GO_FORWARD",
           "wx.ART_GO_UP",
           "wx.ART_GO_DOWN",
           "wx.ART_GO_TO_PARENT",
           "wx.ART_GO_HOME",
           "wx.ART_FILE_OPEN",
           "wx.ART_PRINT",
           "wx.ART_HELP",
           "wx.ART_TIP",
           "wx.ART_REPORT_VIEW",
           "wx.ART_LIST_VIEW",
           "wx.ART_NEW_DIR",
           "wx.ART_HARDDISK",
           "wx.ART_FLOPPY",
           "wx.ART_CDROM",
           "wx.ART_REMOVABLE",
           "wx.ART_FOLDER",
           "wx.ART_FOLDER_OPEN",
           "wx.ART_GO_DIR_UP",
           "wx.ART_EXECUTABLE_FILE",
           "wx.ART_NORMAL_FILE",
           "wx.ART_TICK_MARK",
           "wx.ART_CROSS_MARK",
           "wx.ART_ERROR",
           "wx.ART_QUESTION",
           "wx.ART_WARNING",
           "wx.ART_INFORMATION",
           "wx.ART_MISSING_IMAGE",
           "SmileBitmap"
           ]    

#----------------------------------------------------------------------
# -- Test Config --
class TestConfig( SimpleGrid ):
    #配置数据
    _colname = [u'被测版本标签号',
                u'测试用例编号',
                u'测试步骤编号',
                u'测试状态',
                u'备注']
    _dataType = [Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING]
#    showdata = []  #用于显示的数据[被测版本标签号,测试用例编号,测试步骤编号,测试状态,备注]
#    Usrdata = None   #用于保存操作的数据 [[secpath,Filename,usecase,type,content,createdate]]
#    curdata = None #
    curIndex = None
    Status = {0:'Waiting',
              1:'Load',
              2:'Running',
              3:'End'}
    #case config 实例
    __caseconfig = None
    def __init__( self, parent, mysize ):
        SimpleGrid.__init__( self, parent, \
                            self._colname, self._dataType, mysize )
        self.colname = self._colname
        self.dataType = self._dataType
        #载入初始化信息
#        self.__caseconfig = caseprocess.CaseProcess()
#        self.__caseconfig.importUserCase( casefile )
        
        self.rowLines = len( CaseParser.getCurSelectCaseInfo() )

        #print self.__caseconfig.getCaseDispalyInfo()
        self.setCustable( CaseParser.getCurSelectCaseInfo()\
                          if len( CaseParser.getCurSelectCaseInfo() ) > 0 \
                          else [["NoCase", "NoCase", "NoCase", "NoCase"], ] )
        self.EnableEditing( False )
        self.bindEvent()

    def RefreshPanelData( self ):
        "Refresh Data"
        self.rowLines = len( CaseParser.getCurSelectCaseInfo() )

        #print self.__caseconfig.getCaseDispalyInfo()
        self.setCustable( CaseParser.getCurSelectCaseInfo()\
                          if len( CaseParser.getCurSelectCaseInfo() ) > 0 \
                          else [["NoCase", "NoCase", "NoCase", "NoCase"], ] )        
    
    def addNewItem( self, path, attr ):
        "添加新用例"
        pass
#        self.__caseconfig.addNewCase( path, attr )
#        #更新显示
#        self.setCustable( self.__caseconfig.getCaseDispalyInfo() )
#        #更新
#        self.Resize()
        
    def deleItem( self ):
        if None == self.curIndex or \
           self.index < 0 or \
           self.curIndex >= len( CaseParser.getCurSelectCaseInfo() ):
            print 'Wrong Index!!!!!'
        else:
            CaseParser.deleteCaseFromWorkSpace( self.curIndex )
            #重新设置curIndex
            self.curIndex = None
            #更新显示
            self.setCustable( CaseParser.getCurSelectCaseInfo() )

    def bindEvent( self ):
        self.Bind( wx.EVT_SIZE, self.OnSize )
        self.Bind( Grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnSelect )
        
        self.Bind( Grid.EVT_GRID_CELL_CHANGE, self.OnCellChange )
        self.Bind( Grid.EVT_GRID_CELL_LEFT_CLICK, self.OnSelect )
    
    def OnCellChange( self, event ):
        _CellRow = event.GetRow()
        _CellCol = event.GetCol()
        value = self.GetCellValue( _CellRow, _CellCol )
        #将更新的数据加入对应的数据中
        print value, _CellRow, _CellCol
    
    def OnSelect( self, event ):
        _CellRow = event.GetRow()
        _CellCol = event.GetCol()

        if -1 == _CellRow or _CellRow >= len( CaseParser.getCurSelectCaseInfo() ):
            print "OnSelect:", "Invalid index!"
        else:
            self.changeCurIndex( _CellRow )
            #设置当前CasePaser的当前选中case编号
            CaseParser.setCurRunCaseIndex( self.curIndex )
            CaseParser.setEditCaseInfoByCurIndex()
            
        print 'On select!!!', _CellRow, _CellCol, self.curIndex
    
    
    def changeCurIndex( self, index ):
        "change current index."
        if index not in range( len( CaseParser.getCurSelectCaseInfo() ) ):
            return
        
        #高亮显示
        if None != self.curIndex:#去除高亮
            self.SetCellBackgroundColour( self.curIndex, 0, wx.WHITE )
            self.SetCellBackgroundColour( self.curIndex, 1, wx.WHITE )
            self.SetCellBackgroundColour( self.curIndex, 2, wx.WHITE )
            self.SetCellBackgroundColour( self.curIndex, 3, wx.WHITE )
            self.SetCellBackgroundColour( self.curIndex, 4, wx.WHITE )
                
        self.SetCellBackgroundColour( index, 0, wx.LIGHT_GREY )
        self.SetCellBackgroundColour( index, 1, wx.LIGHT_GREY )
        self.SetCellBackgroundColour( index, 2, wx.LIGHT_GREY )
        self.SetCellBackgroundColour( index, 3, wx.LIGHT_GREY )
        self.SetCellBackgroundColour( index, 4, wx.LIGHT_GREY )
        self.Refresh()
        #设置curIndex
        self.curIndex = index        
    
    def getCaseConfig( self ):
        return self.__caseconfig
    
    def OnSize( self, event ):
        self.Refresh()
 
    def SetCurSelectCaseIndex( self, index ):
        "set current select case index."
        CaseParser.setCurRunCaseIndex( index )
        self.changeCurIndex( index )
        return True
        
        
    def SetCaseStatus( self, status ):
        "set case status."
        CaseParser.SetCurselectCaseStatus( self.curIndex, status )
        self.RefreshData( CaseParser.getCurSelectCaseInfo()\
                          if len( CaseParser.getCurSelectCaseInfo() ) > 0 \
                          else [["NoCase", "NoCase", "NoCase", "NoCase"], ] ) 
        

#----------------------------------------------------------------------
# -- 设备变量列表 --
#----------------------------------------------------------------------
class DeviceAttrGrid( SimpleGrid ):
    #配置数据
    _colname = [u'Variable Name',
                u'Value type',
                u'IO type',
                u'Value']
    _dataType = [Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING]
    __Editing = False #用于标识是否在进行编辑
    #设备实例
    __device = None
    #数据类型字典
    __typedic = {"int":int,
                 "float":float,
                 "string":str}
    def __init__( self, parent, device ):
        SimpleGrid.__init__( self, parent, \
                            self._colname, self._dataType, ( 100, 200 ) )
        self.colname = self._colname
        self.dataType = self._dataType
        self.__device = device
        #载入初始化信息
        self.setCustable( self.getShowData() )
        self.bindEvent()
        
    def setDeviceNode( self, device ):
        "set device node."
        self.__device = device
        
    #---------------------------------------------------------------
    #@将设备内的数据转换到表格中显示
    #@_revdata:[value name,value type,value]
    #---------------------------------------------------------------
    def getShowData( self ):
        "import initial data"
        if None == self.__device:
            print "getShowData: error __device!!!"
        _revdata = []
        _var = self.__device.getVarDic()  #key(Name):[Type,IO,Value]
        
        for _key in _var:
            _tmpitem = []
            _tmpitem.append( _key )
            _tmpitem.append( _var[_key][0] )
            _tmpitem.append( _var[_key][1] )
            _tmpitem.append( repr( self.__device.getDataValue( _key ) ) )
            _revdata.append( _tmpitem )
        #print  _revdata
        #将数据按照   value name进行排序
        _revdata = sorted( _revdata, key = lambda _revdata: _revdata[0] )
        return _revdata
    
    #--------------------------------------------------------------
    #显示数据更新，建议每秒更新一次
    #--------------------------------------------------------------
    def updataGrid( self ):
        self.RefreshData( self.getShowData() )
    
    #--------------------------------------------------------------
    #@根据界面值更新设备数据
    #--------------------------------------------------------------
    def setDevData( self, index ):
        "根据界面的修改设置变量的Value"
        _valuename = self.GetCellValue( index, 0 )
        _type = self.GetCellValue( index, 1 )
        _IOtype = self.GetCellValue( index, 2 )
        _value = self.GetCellValue( index, 3 )
        if len( _valuename ) <= 0:
            return
        if "Input" != _IOtype or _type not in ["int" , "float"  , "string"]:
            print "type can't to edit！"
        else:
            self.__device.addDataKeyValue( _valuename, self.__typedic[_type]( _value ) )
        
    def bindEvent( self ):
        self.Bind( wx.EVT_SIZE, self.OnSize )
        self.Bind( Grid.EVT_GRID_CELL_CHANGE, self.OnCellChange )
    
    def OnCellChange( self, event ):
        _CellRow = event.GetRow()
        _CellCol = event.GetCol()
        #只响应_CellCol为3的修改，既value的修改
        if _CellCol != 3:
            return
        #将更新的数据加入对应的数据中
        self.setDevData( _CellRow )

    def OnSize( self, event ):
        self.Refresh()        


#----------------------------------------------------------------------
# -- 设备变量列表 --
#----------------------------------------------------------------------
class OMAPAttrGrid( SimpleGrid ):
    #OMAP配置数据
    _colname = [u'Variable Name',
                u'Value',
                u'Variable Name',
                u'Value',
                u'Variable Name',
                u'Value',
                u'Variable Name',
                u'Value']
    _dataType = [Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING,
                 Grid.GRID_VALUE_STRING]
    
    __dataLen = None
    def __init__( self, parent ):
        SimpleGrid.__init__( self, parent, \
                            self._colname, self._dataType, ( 100, 200 ) )
        self.colname = self._colname
        self.dataType = self._dataType
        #载入初始化信息
        self.EnableEditing( False )
#        print self.getShowData()
        self.__dataLen = 0
        self.setCustable( self.getShowData() )
    
        
    #---------------------------------------------------------------
    #@将设备内的数据转换到表格中显示
    #@_revdata:[value name,value type,value]
    #---------------------------------------------------------------
    def getShowData( self ):
        "import initial data"
        _revdata = []
        for _FrameLabel in OMAPParser.OMAPShow:
            _revdata.append( ['', '', _FrameLabel, 'OMAP', 'SHOW', 'Variants:', '', ''] )
            _temp = []
            
            for _content in OMAPParser.OMAPShow[_FrameLabel]:
                _temp.append( [_content, OMAPParser.OMAPShow[_FrameLabel][_content]] )
            #将显示数据按照字母序列排列
            _temp = sorted( _temp, key = lambda _temp: _temp[0] )
            
            _len = len( _temp )
            for _i in range( ( _len / 4 ) + 1 ):
                if ( 4 * _i + 3 ) < _len:
                    _revdata.append( _temp[3 * _i] + _temp[3 * _i + 1] + _temp[3 * _i + 2] + _temp[3 * _i + 3] )
                elif ( 4 * _i + 3 ) == _len:
                    _revdata.append( _temp[3 * _i] + _temp[3 * _i + 1] + _temp[3 * _i + 2] + ['', ''] )
                elif ( 4 * _i + 2 ) == _len:
                    _revdata.append( _temp[3 * _i] + _temp[3 * _i + 1] + ['', ''] + ['', ''] )
                elif ( 3 * _i + 1 ) == _len:
                    _revdata.append( _temp[3 * _i] + ['' + ''] + ['', ''] + ['', ''] )
                else:
                    continue
        if len( _revdata ) == 0:
            _revdata = [['', '', '', '', '', '', '', '']]
        
        return _revdata
    
    #--------------------------------------------------------------
    #显示数据更新，建议每秒更新一次
    #--------------------------------------------------------------
    def updataGrid( self ):
        __data = self.getShowData()
        if self.__dataLen == len( __data ):
            self.RefreshData( __data )
        else:
            self.setCustable( __data )
            self.__dataLen = len( __data )
    
    def OnSize( self, event ):
        self.Refresh()            


#---------------------------------------------------------------------------
# CustomTreeCtrl Demo Implementation
#---------------------------------------------------------------------------
class CustomTreeCtrl( CT.CustomTreeCtrl ):
    
    __NumOfOMAPFrame = 0
    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition,
                 size = wx.DefaultSize,
                 style = wx.SUNKEN_BORDER | CT.TR_HAS_BUTTONS | CT.TR_HAS_VARIABLE_ROW_HEIGHT | wx.WANTS_CHARS,
                 log = None ):

        CT.CustomTreeCtrl.__init__( self, parent, id, pos, size, style )

        alldata = dir( CT )
        
        treestyles = []
        events = []
        for data in alldata:
            if data.startswith( "TR_" ):
                treestyles.append( data )
            elif data.startswith( "EVT_" ):
                events.append( data )

        self.events = events
        self.styles = treestyles
        self.item = None
        
        il = wx.ImageList( 16, 16 )

        for items in ArtIDs[1:-1]:
            bmp = wx.ArtProvider_GetBitmap( eval( items ), wx.ART_TOOLBAR, ( 16, 16 ) )
            il.Add( bmp )

        smileidx = il.Add( images.Smiles.GetBitmap() )
        numicons = il.GetImageCount()

        self.AssignImageList( il )
        self.count = 0
        self.log = log
    
    def GetTreeStyle( self ):
        "Return the CustomTree Style"
        return self.GetWindowStyle()
    
    def getSelectCaseItemInfo( self ):
        "get select case item info."
        _pathinfo = CaseParser.getPathInfo()
        _reVal = []
        _root = self.GetRootItem()
        _roottext = self.GetItemText( _root )
        
        _caseNum, _case_cookie = self.GetFirstChild( _root )        
        while _caseNum:
            _caseNumtxt = self.GetItemText( _caseNum )
            if True == self.IsItemChecked( _caseNum ): #用例Num被选中
                #将所有step都加入其中
                for _steptxt in _pathinfo[1][_caseNumtxt]:
                    _reVal.append( [_roottext, _caseNumtxt, _steptxt] )
            else:#查看下面是否有选中的
                _caseStep, _case_step_cookie = self.GetFirstChild( _caseNum )
                while _caseStep:
                    _case_steptxt = self.GetItemText( _caseStep )
                    if True == self.IsItemChecked( _caseStep ): #用例Step被选中 
                        _reVal.append( [_roottext, _caseNumtxt, _case_steptxt] )
                    _caseStep, _case_step_cookie = self.GetNextChild( _caseNum, _case_step_cookie )
            _caseNum, _case_cookie = self.GetNextChild( _root, _case_cookie )
        
        return _reVal
    
    #------------------------------------------------------------------------
    #_caselist:[被测版本标签号,{测试用例编号1:{测试步骤编号1:[LogPath,ScriptPath,UpLogPath],...},...}]
    #------------------------------------------------------------------------
    def CreateTreeFromCaseNode( self ):
        "create Tree From Case node."
        #_caselist:[被测版本标签号,{测试用例编号1:{测试步骤编号1:[LogPath,ScriptPath,UpLogPath],...},...}]
        _caselist = CaseParser.getPathInfo()
        #先删除，再创建
        self.DeleteAllItems()
        
        self.root = self.AddRoot( _caselist[0] )

        if not( self.GetTreeStyle() & CT.TR_HIDE_ROOT ):
            self.SetPyData( self.root, None )
            self.SetItemImage( self.root, 24, CT.TreeItemIcon_Normal )
            self.SetItemImage( self.root, 13, CT.TreeItemIcon_Expanded )
        
        #将用例先按照顺序排序
        _caseNumlist = []
        for _case in _caselist[1]:
            _caseNumlist.append( _case )
        _caseNumlist.sort()
         
        for _case in _caseNumlist:
            child = self.AppendItem( self.root, _case, ct_type = 1 )
#            self.SetItemBold( child, True )
            
            self.SetPyData( child, None )
            self.SetItemImage( child, 24, CT.TreeItemIcon_Normal )
            self.SetItemImage( child, 13, CT.TreeItemIcon_Expanded )
            
            #将步骤先按照顺序排序
            _caseSteplist = []
            for _case_child in _caselist[1][_case]:
                _caseSteplist.append( _case_child )
            _caseSteplist.sort()
            
            for _case_child in _caseSteplist:
                case_child = self.AppendItem( child, _case_child, ct_type = 1 )
                self.SetPyData( child, None )
                self.SetItemImage( case_child, 28, CT.TreeItemIcon_Normal )
                self.SetItemImage( case_child, 28, CT.TreeItemIcon_Selected )             


        self.Bind( wx.EVT_LEFT_DCLICK, self.OnLeftDClick )
        self.Bind( wx.EVT_IDLE, self.OnIdle )

        self.eventdict = {'EVT_TREE_BEGIN_DRAG': self.OnBeginDrag, 'EVT_TREE_BEGIN_LABEL_EDIT': self.OnBeginEdit,
                          'EVT_TREE_BEGIN_RDRAG': self.OnBeginRDrag, 'EVT_TREE_DELETE_ITEM': self.OnDeleteItem,
                          'EVT_TREE_ITEM_ACTIVATED': self.OnActivate, 'EVT_TREE_ITEM_CHECKED': self.OnItemCheck,
                          'EVT_TREE_ITEM_CHECKING': self.OnItemChecking, 'EVT_TREE_ITEM_COLLAPSED': self.OnItemCollapsed,
                          'EVT_TREE_ITEM_COLLAPSING': self.OnItemCollapsing, 'EVT_TREE_ITEM_EXPANDED': self.OnItemExpanded,
                          'EVT_TREE_ITEM_EXPANDING': self.OnItemExpanding, 'EVT_TREE_ITEM_GETTOOLTIP': self.OnToolTip,
                          'EVT_TREE_ITEM_MENU': self.OnItemMenu, 'EVT_TREE_ITEM_RIGHT_CLICK': self.OnRightDown,
                          'EVT_TREE_SEL_CHANGED': self.OnSelChanged, 'EVT_TREE_SEL_CHANGING': self.OnSelChanging, "EVT_TREE_ITEM_HYPERLINK": self.OnHyperLink}

        mainframe = wx.GetTopLevelParent( self )
        
        if not hasattr( mainframe, "leftpanel" ):
            self.Bind( CT.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded )
            self.Bind( CT.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed )
            self.Bind( CT.EVT_TREE_SEL_CHANGED, self.OnSelChanged )
            self.Bind( CT.EVT_TREE_SEL_CHANGING, self.OnSelChanging )
            self.Bind( wx.EVT_RIGHT_DOWN, self.OnRightDown )
            self.Bind( wx.EVT_RIGHT_UP, self.OnRightUp )
        else:
            for combos in mainframe.treeevents:
                self.BindEvents( combos )

        if hasattr( mainframe, "leftpanel" ):
            self.ChangeStyle( mainframe.treestyles )

        if not( self.GetTreeStyle() & CT.TR_HIDE_ROOT ):
            self.SelectItem( self.root )
            self.Expand( self.root )


    def BindEvents( self, choice, recreate = False ):

        value = choice.GetValue()
        text = choice.GetLabel()
        
        evt = "CT." + text
        binder = self.eventdict[text]

        if value == 1:
            if evt == "CT.EVT_TREE_BEGIN_RDRAG":
                self.Bind( wx.EVT_RIGHT_DOWN, None )
                self.Bind( wx.EVT_RIGHT_UP, None )
            self.Bind( eval( evt ), binder )
        else:
            self.Bind( eval( evt ), None )
            if evt == "CT.EVT_TREE_BEGIN_RDRAG":
                self.Bind( wx.EVT_RIGHT_DOWN, self.OnRightDown )
                self.Bind( wx.EVT_RIGHT_UP, self.OnRightUp )


    def ChangeStyle( self, combos ):

        style = 0
        for combo in combos:
            if combo.GetValue() == 1:
                style = style | eval( "CT." + combo.GetLabel() )

        if self.GetTreeStyle() != style:
            self.SetTreeStyle( style )
            

    def OnCompareItems( self, item1, item2 ):
        
        t1 = self.GetItemText( item1 )
        t2 = self.GetItemText( item2 )
        
        print 'compare: ' + t1 + ' <> ' + t2 

        if t1 < t2:
            return -1
        if t1 == t2:
            return 0

        return 1

    
    def OnIdle( self, event ):

        event.Skip()


    def OnRightDown( self, event ):
        
        pt = event.GetPosition()
        item, flags = self.HitTest( pt )

        if item:
            self.item = item
                    
            if len( self.item.GetChildren() ) > 0: #只处理底层的用例
                event.Skip()
                return
            
            _CaseStepTxt = self.GetItemText( self.item )
            _CaseNumTxt = self.GetItemText( self.item.GetParent() )
            
            CaseParser.setEditCaseInfo( _CaseNumTxt, _CaseStepTxt, '0' )
#            print _CaseStepTxt, _CaseNumTxt, CaseParser.getEditCaseInfo()


    def OnRightUp( self, event ):

        item = self.item
        
        if not item:
            event.Skip()
            return

        if not self.IsItemEnabled( item ):
            event.Skip()
            return
        
        if self.item == self.GetRootItem(): #不响应根节点
            event.Skip()
            return
        
        if len( self.item.GetChildren() ) == 0: 
            _type = 1  #处理用例编号层
        else:
            _type = 2  #处理用例标签层
        
        # Item Text Appearance
        ishtml = self.IsItemHyperText( item )
        back = self.GetItemBackgroundColour( item )
        fore = self.GetItemTextColour( item )
        isbold = self.IsBold( item )
        font = self.GetItemFont( item )

        # Icons On Item
        normal = self.GetItemImage( item, CT.TreeItemIcon_Normal )
        selected = self.GetItemImage( item, CT.TreeItemIcon_Selected )
        expanded = self.GetItemImage( item, CT.TreeItemIcon_Expanded )
        selexp = self.GetItemImage( item, CT.TreeItemIcon_SelectedExpanded )

        # Enabling/Disabling Windows Associated To An Item
        haswin = self.GetItemWindow( item )

        # Enabling/Disabling Items
        enabled = self.IsItemEnabled( item )

        # Generic Item's Info
        children = self.GetChildrenCount( item )
        itemtype = self.GetItemType( item )
        text = self.GetItemText( item )
        pydata = self.GetPyData( item )
        
        self.current = item
        self.itemdict = {"ishtml": ishtml, "back": back, "fore": fore, "isbold": isbold,
                         "font": font, "normal": normal, "selected": selected, "expanded": expanded,
                         "selexp": selexp, "haswin": haswin, "children": children,
                         "itemtype": itemtype, "text": text, "pydata": pydata, "enabled": enabled}
        
        if 1 == _type: #处理用例步骤层
            menu = wx.Menu()
            item1 = menu.Append( wx.ID_ANY, "Edit Case Configuration" )
            item2 = menu.Append( wx.ID_ANY, "Show Case Log" )
            item3 = menu.Append( wx.ID_ANY, "Delete This Case" )
            item4 = menu.Append( wx.ID_ANY, "ReName..." )
            item5 = menu.Append( wx.ID_ANY, "Edit Analysis Configuration " )
        
            self.Bind( wx.EVT_MENU, self.OnEditCaseConfig, item1 )
            self.Bind( wx.EVT_MENU, self.OnShowLog, item2 )
            self.Bind( wx.EVT_MENU, self.OnDelCaseStep, item3 )
            self.Bind( wx.EVT_MENU, self.OnReNameCaseStep, item4 )
            self.Bind( wx.EVT_MENU, self.OnEditAnalysisConfig, item5 )
            
            self.PopupMenu( menu )
            menu.Destroy()        
        elif 2 == _type:
            menu = wx.Menu()
            item1 = menu.Append( wx.ID_ANY, "ReName..." )

            self.Bind( wx.EVT_MENU, self.OnReNameCaseNum, item1 )
        
            self.PopupMenu( menu )
            menu.Destroy()  
    
    def OnReNameCaseNum( self, event ):
        "On ReName Case"
        dlg = wx.TextEntryDialog( self,
                                 'New name:',
                                 'Rename Resourse',
                                 self.GetItemText( self.current ) )

        if dlg.ShowModal() == wx.ID_OK:
            _value = dlg.GetValue()
            #检查是否有重名，没有才替换否则要提醒用户
            #在caseparser中需要修改的类变量有__pathinfo，__CurSelectCases，__EditCaseInfo
            _EditFlag = CaseParser.RenameEditCaseNum( self.GetItemText( self.current ), _value )  #记录是否修改了记录在test_config_panel中包含的用例
            if False == _EditFlag:
                wx.MessageBox( u"Can't Rename Case name!" )
            elif _EditFlag in [1, 2]: 
                self.SetItemText( self.current, _value )
                if 2 == _EditFlag:#需要更新test_config_panel
                    self.GetParent().GetParent().\
                    test_config_panel.RefreshData( CaseParser.getCurSelectCaseInfo()\
                                                  if len( CaseParser.getCurSelectCaseInfo() ) > 0 \
                                                  else [["NoCase", "NoCase", "NoCase", "NoCase"]] )                    

        dlg.Destroy()
    
    def OnReNameCaseStep( self, event ):
        "On rename case Step"
#        print "OnReNameCase", self.current, self.GetItemText(self.current)#, self.SetItemText(self.current, "haha")
#        print CaseParser.getEditCaseInfo()[0], CaseParser.getEditCaseInfo()[1], CaseParser.getEditCaseInfo()[2]
        dlg = wx.TextEntryDialog( self,
                                 'New name:',
                                 'Rename Resourse',
                                 self.GetItemText( self.current ) )

        if dlg.ShowModal() == wx.ID_OK:
            _value = dlg.GetValue()
            #检查是否有重名，没有才替换否则要提醒用户
            #在caseparser中需要修改的类变量有__pathinfo，__CurSelectCases，__EditCaseInfo
            _EditFlag = CaseParser.RenameEditCaseStep( _value )  #记录是否修改了记录在test_config_panel中包含的用例
            if False == _EditFlag:
                wx.MessageBox( u"Can't Rename Case name!" )
            elif _EditFlag in [1, 2]: 
                self.SetItemText( self.current, _value )
                if 2 == _EditFlag:#需要更新test_config_panel
                    self.GetParent().GetParent().\
                    test_config_panel.RefreshData( CaseParser.getCurSelectCaseInfo()\
                                                  if len( CaseParser.getCurSelectCaseInfo() ) > 0 \
                                                  else [["NoCase", "NoCase", "NoCase", "NoCase"]] )                    

        dlg.Destroy()

    
    def OnDelCaseStep( self, event ):
        "On delete case"
        dlg = wx.MessageDialog( self, "Do you want to delete this step?",
                               "Warnning For Delete",
                               wx.OK | wx.CANCEL | wx.ICON_WARNING )
        
        if wx.ID_OK == dlg.ShowModal():
#            print "OK"
            _hasFlag = CaseParser.delEditCaseStep() #记录是否在test_config_panel中包含此用例
            self.GetParent().trees['CaseTree'].CreateTreeFromCaseNode()
            if True == _hasFlag:
                #需要进行test_config_panel中此用例的删除
                self.GetParent().GetParent().test_config_panel.RefreshPanelData()        
        dlg.Destroy()

    def OnEditAnalysisConfig( self, event ):
        "edit analysis configuration"
        _wizard = simplewizard.AnalysisWizard( self, NewFlag = False )

        if _wizard.StartWizard():
            wx.MessageBox( "Wizard completed successfully", "That's all folks!" )
        else:
            wx.MessageBox( "Wizard was cancelled", "That's all folks!" )
        
        _wizard.Destroy()          
        
    def OnEditCaseConfig( self , event ):
        "edit case configuration."
#        dlg = simplepanel.CaseConfigPanel( self, -1, "Case Config Dialog", size = ( 800, 600 ),
#                         #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
#                         style = wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
#                         )
#        if dlg.ShowModal() == wx.ID_OK:
#            CaseParser.SaveEditCaseConfig()
#        dlg.Destroy() 
        _wizard = simplewizard.CaseWizard( self, NewFlag = False )

        if _wizard.StartWizard():
            wx.MessageBox( "Wizard completed successfully", "That's all folks!" )
        else:
            wx.MessageBox( "Wizard was cancelled", "That's all folks!" )
        
        _wizard.Destroy()  

    def OnShowLog( self , event ):
        "Show Log."
#        dlg = simplepanel.ShowOMAPLogDlg( self, -1, "OMAP Show Dialog", size = ( 800, 600 ),
#                         #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
#                         style = wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
#                         )
#        dlg.ShowModal()
#        dlg.ClearData()
#        dlg.Destroy() 
        try: 
            if False == self.AddNumOfOMAPFrame():
                return
            _CaseNum = CaseParser.getEditCaseInfo()[1] + " - " + CaseParser.getEditCaseInfo()[2]
            FRM = simplepanel.ShowOMAPLogFRM( self, -1, "OMAP Show Frame: " + _CaseNum , size = ( 800, 600 ),
                         	#style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
                         	style = wx.DEFAULT_FRAME_STYLE, # & ~wx.CLOSE_BOX,
                         	)
            FRM.SetBackgroundColour( wx.WHITE )
            FRM.Show( True )
            
        except:
            wx.MessageBox( u"ERROR in open Case:" + _CaseNum + ", please check the log exist first!!!", "Error" )

    def DelNumOfOMAPFrame( self ):
        if self.__NumOfOMAPFrame <= 0:
            print 'DelNumOfOMAPFrame error!!!'
        else:
            self.__NumOfOMAPFrame -= 1

    def AddNumOfOMAPFrame( self ):
        if self.__NumOfOMAPFrame >= 3:
            print 'AddNumOfOMAPFrame error!!!'
            wx.MessageBox( u"最多只能打开3个OMAP窗口!!!" )
            return False
        else:
            self.__NumOfOMAPFrame += 1
            return True

    def OnItemBackground( self, event ):

        colourdata = wx.ColourData()
        colourdata.SetColour( self.itemdict["back"] )
        dlg = wx.ColourDialog( self, colourdata )
        
        dlg.GetColourData().SetChooseFull( True )

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            col1 = data.GetColour().Get()
            self.SetItemBackgroundColour( self.current, col1 )
        dlg.Destroy()


    def OnItemForeground( self, event ):

        colourdata = wx.ColourData()
        colourdata.SetColour( self.itemdict["fore"] )
        dlg = wx.ColourDialog( self, colourdata )
        
        dlg.GetColourData().SetChooseFull( True )

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            col1 = data.GetColour().Get()
            self.SetItemTextColour( self.current, col1 )
        dlg.Destroy()


    def OnItemBold( self, event ):

        self.SetItemBold( self.current, not self.itemdict["isbold"] )


    def OnItemFont( self, event ):

        data = wx.FontData()
        font = self.itemdict["font"]
        
        if font is None:
            font = wx.SystemSettings_GetFont( wx.SYS_DEFAULT_GUI_FONT )
            
        data.SetInitialFont( font )

        dlg = wx.FontDialog( self, data )
        
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            self.SetItemFont( self.current, font )

        dlg.Destroy()
        

    def OnItemHyperText( self, event ):

        self.SetItemHyperText( self.current, not self.itemdict["ishtml"] )


    def OnEnableWindow( self, event ):

        enable = self.GetItemWindowEnabled( self.current )
        self.SetItemWindowEnabled( self.current, not enable )


    def OnDisableItem( self, event ):

        self.EnableItem( self.current, False )
        


    def SetNewIcons( self, bitmaps ):

        self.SetItemImage( self.current, bitmaps[0], CT.TreeItemIcon_Normal )
        self.SetItemImage( self.current, bitmaps[1], CT.TreeItemIcon_Selected )
        self.SetItemImage( self.current, bitmaps[2], CT.TreeItemIcon_Expanded )
        self.SetItemImage( self.current, bitmaps[3], CT.TreeItemIcon_SelectedExpanded )


    def OnItemInfo( self, event ):

        itemtext = self.itemdict["text"]
        numchildren = str( self.itemdict["children"] )
        itemtype = self.itemdict["itemtype"]
        pydata = repr( type( self.itemdict["pydata"] ) )

        if itemtype == 0:
            itemtype = "Normal"
        elif itemtype == 1:
            itemtype = "CheckBox"
        else:
            itemtype = "RadioButton"

        strs = "Information On Selected Item:\n\n" + "Text: " + itemtext + "\n" \
               "Number Of Children: " + numchildren + "\n" \
               "Item Type: " + itemtype + "\n" \
               "Item Data Type: " + pydata + "\n"

        dlg = wx.MessageDialog( self, strs, "CustomTreeCtrlDemo Info", wx.OK | wx.ICON_INFORMATION )
        dlg.ShowModal()
        dlg.Destroy()
                
        

    def OnItemDelete( self, event ):

        strs = "Are You Sure You Want To Delete Item " + self.GetItemText( self.current ) + "?"
        dlg = wx.MessageDialog( None, strs, 'Deleting Item', wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_QUESTION )

        if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
            dlg.Destroy()
            return

        dlg.Destroy()

        self.DeleteChildren( self.current )
        self.Delete( self.current )
        self.current = None
        


    def OnItemPrepend( self, event ):

        dlg = wx.TextEntryDialog( self, "Please Enter The New Item Name", 'Item Naming', 'Python' )

        if dlg.ShowModal() == wx.ID_OK:
            newname = dlg.GetValue()
            newitem = self.PrependItem( self.current, newname )
            self.EnsureVisible( newitem )

        dlg.Destroy()


    def OnItemAppend( self, event ):

        dlg = wx.TextEntryDialog( self, "Please Enter The New Item Name", 'Item Naming', 'Python' )

        if dlg.ShowModal() == wx.ID_OK:
            newname = dlg.GetValue()
            newitem = self.AppendItem( self.current, newname )
            self.EnsureVisible( newitem )

        dlg.Destroy()
        

    def OnBeginEdit( self, event ):
        
        print "OnBeginEdit"
        # show how to prevent edit...
        item = event.GetItem()
        if item and self.GetItemText( item ) == "The Root Item":
            wx.Bell()
            print "You can't edit this one..."

            # Lets just see what's visible of its children
            cookie = 0
            root = event.GetItem()
            ( child, cookie ) = self.GetFirstChild( root )

            while child:
                print "Child [%s] visible = %d" % ( self.GetItemText( child ), self.IsVisible( child ) )
                ( child, cookie ) = self.GetNextChild( root, cookie )

            event.Veto()


        


    def OnLeftDClick( self, event ):
        
        pt = event.GetPosition()
        item, flags = self.HitTest( pt )
        if item and ( flags & CT.TREE_HITTEST_ONITEMLABEL ):
            if self.GetTreeStyle() & CT.TR_EDIT_LABELS:
                print "OnLeftDClick: %s (manually starting label edit)" % self.GetItemText( item )
                self.EditLabel( item )
            else:
                print "OnLeftDClick: Cannot Start Manual Editing, Missing Style TR_EDIT_LABELS\n"

        event.Skip()                
        

    def OnItemExpanded( self, event ):
        
        item = event.GetItem()
        if item:
            print "OnItemExpanded: %s" % self.GetItemText( item )
#            self.log.write("OnItemExpanded: %s" % self.GetItemText(item) + "\n")


    def OnItemExpanding( self, event ):
        
        item = event.GetItem()
        if item:
            print "OnItemExpanding: %s" % self.GetItemText( item )
            
        event.Skip()

        
    def OnItemCollapsed( self, event ):

        item = event.GetItem()
        if item:
            print "OnItemCollapsed: %s" % self.GetItemText( item )
            

    def OnItemCollapsing( self, event ):

        item = event.GetItem()
        if item:
            print "OnItemCollapsing: %s" % self.GetItemText( item )
    
        event.Skip()

        
    def OnSelChanged( self, event ):

        self.item = event.GetItem()
        if self.item:
            pass
        else:
            event.Skip()
            return
        
        if len( self.item.GetChildren() ) > 0: #只处理底层的用例
            event.Skip()
            return
        
        _CaseStepTxt = self.GetItemText( self.item )
        _CaseNumTxt = self.GetItemText( self.item.GetParent() )
        
        CaseParser.setEditCaseInfo( _CaseNumTxt, _CaseStepTxt, '0' )
        
        event.Skip()


    def OnSelChanging( self, event ):

        item = event.GetItem()
        olditem = event.GetOldItem()
        
        if item:
            if not olditem:
                olditemtext = "None"
            else:
                olditemtext = self.GetItemText( olditem )
            print "OnSelChanging: From %s" % olditemtext + " To %s" % self.GetItemText( item )
                
        event.Skip()


    def OnBeginDrag( self, event ):

        self.item = event.GetItem()
        if self.item:
            print "Beginning Drag..."

            event.Allow()


    def OnBeginRDrag( self, event ):

        self.item = event.GetItem()
        if self.item:
            print "Beginning Right Drag..."

            event.Allow()
        

    def OnEndDrag( self, event ):

        self.item = event.GetItem()
        if self.item:
            print "Ending Drag!"

        event.Skip()            


    def OnDeleteItem( self, event ):

        item = event.GetItem()

        if not item:
            return

        print "Deleting Item: %s" % self.GetItemText( item )
        event.Skip()
        

    def OnItemCheck( self, event ):

        item = event.GetItem()
        print "Item " + self.GetItemText( item ) + " Has Been Checked!\n"
        event.Skip()


    def OnItemChecking( self, event ):

        item = event.GetItem()
        print "Item " + self.GetItemText( item ) + " Is Being Checked...\n"
        event.Skip()
        

    def OnToolTip( self, event ):

        item = event.GetItem()
        if item:
            event.SetToolTip( wx.ToolTip( self.GetItemText( item ) ) )


    def OnItemMenu( self, event ):

        item = event.GetItem()
        if item:
            print "OnItemMenu: %s" % self.GetItemText( item ) 
    
        event.Skip()

        
        
    def OnActivate( self, event ):
        
        if self.item:
            print "OnActivate: %s" % self.GetItemText( self.item )

        event.Skip()

        
    def OnHyperLink( self, event ):

        item = event.GetItem()
        if item:
            print "OnHyperLink: %s" % self.GetItemText( self.item )
            

    def OnTextCtrl( self, event ):

        char = chr( event.GetKeyCode() )
        print "EDITING THE TEXTCTRL: You Wrote '" + char + \
                       "' (KeyCode = " + str( event.GetKeyCode() ) 
        event.Skip()



#-------------------------------------------------------------------
#@自定义tree-notebook类，用于生成界面右端的显示
#@界面1:tree:General:基本显示tree，包括主显示界面等信息
#@界面2:tree:TPConfig:脚本控制界面tree，主要是脚本的运行界面
#@界面3:tree:testconfig:用例设置界面tree，用于显示设备
#-------------------------------------------------------------------
class TreeNotebook( wx.Notebook ):
    __treeinfo = [( CustomTreeCtrl, 'CaseTree' ),
                  ( wx.TreeCtrl, 'General' ),
                  ( wx.TreeCtrl, 'TPConfig' ),
                  ( wx.TreeCtrl, 'testconfig' )]
    
    def __init__( self, parent, _size ):
        wx.Notebook.__init__( self, parent, -1, style = wx.BK_DEFAULT )
        self.trees = {}
        for class_, title in self.__treeinfo:
            if title == 'CaseTree':
                tree = class_( self, -1, style = wx.SUNKEN_BORDER | CT.TR_HAS_BUTTONS | CT.TR_HAS_VARIABLE_ROW_HEIGHT | wx.WANTS_CHARS )
            else:
                tree = class_( self, -1, style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TR_FULL_ROW_HIGHLIGHT )
                
            self.trees[title] = tree
            self.AddPage( tree, title )
        self.createGeneralTree()
        self.createTPConfigTree( [] )
        self.createTestConfigTree()
        self.createCaseTree()
        self.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged )

    #----------------------------------------------------------------
    #生成基本树
    #----------------------------------------------------------------
    def createGeneralTree( self ):
        "创建基本树"
        _imglist = wx.ImageList( 16, 16, True, 2 )
        _imglist.Add( wx.Bitmap( r"./interface/ico/General View.ico", wx.BITMAP_TYPE_ANY ) )
        _imglist.Add( wx.Bitmap( r"./interface/ico/Status.ico", wx.BITMAP_TYPE_ANY ) )
        self.trees['General'].AssignImageList( _imglist )
        _root = self.trees['General'].AddRoot( 'General Information', 0 )
        #self.General_items = {}
        self.trees['General'].AppendItem( _root, "Train status", 1 )
        self.trees['General'].AppendItem( _root, "OMAP status", 1 )
#        self.trees['General'].AppendItem( _root, "VIOM status", 1 )
        
        self.trees['General'].Expand( _root )
    
    #----------------------------------------------------------------
    #生成平台配置树,平台配置树，用于对平台中的每个用例进行配置
    #数据为当前平台中的当前testconfig中的用例的data:{casepath:[Filename,casename,type],...}
    #----------------------------------------------------------------
    def createTPConfigTree( self, data ):
        "生成平台配置树"
        _imglist = wx.ImageList( 16, 16, True, 2 )
        _imglist.Add( wx.Bitmap( r"./interface/ico/panel.ico", wx.BITMAP_TYPE_ANY ) )
        _imglist.Add( wx.Bitmap( r"./interface/ico/select case panel.ico", wx.BITMAP_TYPE_ANY ) )
        _imglist.Add( wx.Bitmap( r"./interface/ico/case.ico", wx.BITMAP_TYPE_ANY ) )
        self.trees['TPConfig'].AssignImageList( _imglist )
        _root = self.trees['TPConfig'].AddRoot( 'Test platform Config', 0 )
        #self.General_items = {}
        self.trees['TPConfig'].AppendItem( _root, "Select Case Panel", 1 )
        
        for _key in data:
            self.trees['TPConfig'].AppendItem( _root, data[_key][1], 2 )
        
        self.trees['TPConfig'].Expand( _root )
        
    #----------------------------------------------------------------
    #生成测试用例配置树,主要是设备
    #----------------------------------------------------------------
    def createTestConfigTree( self, _devicelist = [] ):
        "生成测试用例配置树"
        _imglist = wx.ImageList( 16, 16, True, 2 )
        _imglist.Add( wx.Bitmap( r"./interface/ico/devices.ico", wx.BITMAP_TYPE_ANY ) )
        _imglist.Add( wx.Bitmap( r"./interface/ico/device.ico", wx.BITMAP_TYPE_ANY ) )
        self.trees['testconfig'].AssignImageList( _imglist )

        #_devicelist = ["ts", "rs", "viom", "datp", "dccnv", "zc", "lc", "ats", "ci"]
        _root = self.trees['testconfig'].AddRoot( 'Device List', 0 )
        #self.General_items = {}
        for _d in _devicelist:
            self.trees['testconfig'].AppendItem( _root, _d, 1 )
        
        self.trees['testconfig'].Expand( _root )    
    
    #-------------------------------------------------------
    #@更新ConfigTreeList
    #-------------------------------------------------------
    def updataTestConfigTree( self, _devicelist ):
        "updata test config tree."
        self.trees['testconfig'].DeleteAllItems()
        _root = self.trees['testconfig'].AddRoot( 'Device List', 0 )
        #self.General_items = {}
        for _d in _devicelist:
            self.trees['testconfig'].AppendItem( _root, _d, 1 )
        
        self.trees['testconfig'].Expand( _root ) 
        
    #-----------------------------------------------------
    #创建case树
    #-----------------------------------------------------
    def createCaseTree( self ):
        "create Case Tree"
        self.trees['CaseTree'].CreateTreeFromCaseNode()
    
    #------------------------------------------------------
    #@获取当前在casetree中选中的所有用例标签[[被测版本标签号,测试用例编号,测试步骤编号],...]
    #------------------------------------------------------
    def getSelectCaseItem( self ):
        "get Select Case Item"
        return self.trees['CaseTree'].getSelectCaseItemInfo()
        
    #----------------------------------------------------------------
    #根据该控件的操作，反映出相关的指令
    #----------------------------------------------------------------
    def createControlOrder( self ):
        pass

    def OnPageChanged( self, event ):
        #oldTree = self.GetPage(event.OldSelection)
        newTree = self.GetPage( event.Selection )
        newTree.Refresh()
        
        #newTree.SetExpansionState(oldTree.GetExpansionState())
        event.Skip()

    def GetIndicesOfSelectedItems( self ):
        tree = self.trees[self.GetSelection()]
        if tree.GetSelections():
            return [tree.GetIndexOfItem( item ) for item in tree.GetSelections()]
        else:
            return [()]

    def RefreshItems( self ):
        tree = self.trees[self.GetSelection()]
        #tree.RefreshItems()
        #tree.UnselectAll()

    def EnableCaseTree( self, enable ):
        "enable Case Tree"
        self.trees['CaseTree'].Enable( enable )

                            
if __name__ == '__main__':
    pass
