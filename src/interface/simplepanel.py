#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     simplepanel.py
# Description:  本文件用于画各种需要使用的    
# Author:       Xiong KunPeng
# Version:      0.0.1
# Created:      2011-11-23
# Company:      CASCO
# LastChange:   create 2011-11-23
# History:      create 2011-11-23 By XiongKunpeng
#----------------------------------------------------------------------------
import  wx
import  wx.lib.filebrowsebutton as filebrowse
from simpleplot import DataPlot
from base.caseprocess import CaseParser
from base import commlib
import math
from base.omapparser import OMAPParser, OMAPFigureDataHandle, OMAPFigureConfigHandle
from base.simdata import TrainRoute
from interface.simplecontrol import ShowGrid, EditGrid
import  wx.wizard as wiz
from base import simdata
import  wx.grid as Grid
import os
from base import filehandle
from wx.lib import masked
import time
from autoAnalysis.expressionparser import ExpressionParser
# import matplotlib
#from matplotlib.figure import Figure
# from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas                            
# import numpy as np
try:
    from agw import speedmeter as SM
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.speedmeter as SM

try:
    from agw import floatspin as FS
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.floatspin as FS


def makePageTitle( wizPg, title ):
    sizer = wx.BoxSizer( wx.VERTICAL )
    wizPg.SetSizer( sizer )
    title = wx.StaticText( wizPg, -1, title )
    title.SetFont( wx.Font( 18, wx.SWISS, wx.NORMAL, wx.BOLD ) )
    sizer.Add( title, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
    sizer.Add( wx.StaticLine( wizPg, -1 ), 0, wx.EXPAND | wx.ALL, 5 )
    return sizer

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


#--------------------------------------------------------------------
#Wizard: panel1,选择脚本路径，用例名字，以及用例的类型
#--------------------------------------------------------------------
class WizardPathConfig( wx.Panel ):
    def __init__( self, parent, size = wx.DefaultSize, pos = wx.DefaultPosition ):
        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        self.__path = None
        self.__casename = None
        self.__caseType = None
        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer( wx.VERTICAL )
        
        self.SelPath = filebrowse.DirBrowseButton( 
            self, -1, size = ( 600, -1 ), changeCallback = self.SelPathCallback
            )
        self.SelPath.SetLabel( "Case Path:" )
        self.SelPath.SetHelpText( "Select a case path!" )
        sizer.Add( self.SelPath, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )

        box = wx.BoxSizer( wx.HORIZONTAL )

        label = wx.StaticText( self, -1, "Case name:" )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )

        self.caseText = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        self.caseText.SetHelpText( "Write case name here!" )
        box.Add( self.caseText, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnCaseText, self.caseText )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        box = wx.BoxSizer( wx.HORIZONTAL )

        label = wx.StaticText( self, -1, "Platform Type:" )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )

        self.typeText = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        #self.typeText.SetHelpText("Write platform type here!")
        box.Add( self.typeText, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnTypeText, self.typeText )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        self.SetSizer( sizer )
        sizer.Fit( self )
        
    def SelPathCallback( self, event ):
        "获取路径"
        self.__path = event.GetString() 

    def OnCaseText( self, event ):
        "获取路径"
        self.__casename = event.GetString()

    def OnTypeText( self, event ):
        "获取路径"
        self.__caseType = event.GetString()
    
    def getConfigData( self ):
        "get config data from config panel"
        return [self.__path, self.__casename, self.__caseType]

#--------------------------------------------------------------------
#Wizard: panel2,配置路径trainroute专用界面工具
#--------------------------------------------------------------------
class WizardRouteConfig( wx.Panel ):
    dir = {"up":1, "down":-1}
    def __init__( self, parent, size = wx.DefaultSize, pos = wx.DefaultPosition ):
        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        self.__blockList = None
        self.__blockId = None
        self.__absicssa = None
        self.__trainLen = None
        self.__direction = None
        self.__cog_direction = None

        sizer = wx.BoxSizer( wx.VERTICAL )

        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "Block list:" )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.blocklist = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        box.Add( self.blocklist, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnblocklistText, self.blocklist )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "block id:" )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.blockid = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        box.Add( self.blockid, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnblockidText, self.blockid )
        label = wx.StaticText( self, -1, "abscissa(mm):" )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.abscissa = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        box.Add( self.abscissa, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnabscissaText, self.abscissa )        
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )        

        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "train length:" )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.trainLength = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        box.Add( self.trainLength, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OntrainlengthText, self.trainLength )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 ) 
        
        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "direction:" )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.direction = wx.ComboBox( self, -1, "up", ( 80, -1 ), ( 160, -1 ), ["up", "down"], wx.CB_DROPDOWN )
        box.Add( self.direction, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_COMBOBOX, self.OndirectionText, self.direction )
        label = wx.StaticText( self, -1, "cog direction:" )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.cog_dir = wx.ComboBox( self, -1, "up", ( 80, -1 ), ( 160, -1 ), ["up", "down"], wx.CB_DROPDOWN )
        wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        box.Add( self.cog_dir, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_COMBOBOX, self.OncogdirText, self.cog_dir )        
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )                

        self.SetSizer( sizer )
        sizer.Fit( self )
        
    def OnblocklistText( self, event ):
        "获取跑车路径"
        try:
            self.__blockList = [int( str ) for str in event.GetString().strip().splite( "," )]
        except:
            print "OnblocklistText: wrong block list!"
    def OnblockidText( self, event ):
        "get block id"
        self.__blockId = int( event.GetString() )

    def OnabscissaText( self, event ):
        "get abscissa"
        self.__absicssa = int( event.GetString() )
    
    def OntrainlengthText( self, event ):
        "get train length"
        self.__trainLen = int( event.GetString() )
        
    def OndirectionText( self, event ):
        "get direction"
        self.__direction = self.dir( event.GetString() )
        
    def OncogdirText( self, event ):
        "get cog direction"
        self.__cog_direction = self.dir( event.GetString() )    

    def getConfigData( self, event ):
        "get config data"
        return {"blocklist":self.__blockList,
                "blockid":self.__blockId,
                "abscissa":self.__absicssa,
                "trainlen":self.__trainLen,
                "direction":self.__direction,
                "cog_direction":self.__cog_direction
                }                 

#--------------------------------------------------------------------
#Wizard: panel3,配置跑车加速度的专用界面工具
#--------------------------------------------------------------------
class WizardRSSpeedConfig( wx.Panel ):
    def __init__( self, parent, size = wx.DefaultSize, pos = wx.DefaultPosition ):
        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        self.__startcoord = None
        self.__endcoord = None
        self.__expspeed = None
        self.__dewelltime = None
        self.__direction = None
        self.__cog_direction = None

        sizer = wx.BoxSizer( wx.VERTICAL )
        
        #图形控件
        self.plotpanel = DataPlot( self , ( 400, 240 ) )
        sizer.Add( self.plotpanel, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        box = wx.BoxSizer( wx.HORIZONTAL )
        box1 = wx.BoxSizer( wx.VERTICAL )
        box2 = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "Start Coordination:" )
        box2.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.start_coord = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        box2.Add( self.start_coord, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnstartcoordText, self.start_coord )
        box1.Add( box2, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        box2 = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "End Coordination:" )
        box2.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.end_coord = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        box2.Add( self.end_coord, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnendcoordText, self.end_coord )        
        box1.Add( box2, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )        

        self.add_button = wx.Button( self, -1, "Add", size = ( 80, -1 ) )
        self.Bind( wx.EVT_BUTTON, self.OnaddText, self.add_button )        
        box1.Add( self.add_button, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 ) 

        box.Add( box1, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )
        
        box1 = wx.BoxSizer( wx.VERTICAL )
        box2 = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "Expect Speed:" )
        box2.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.exp_speed = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        box2.Add( self.exp_speed, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnexpspeedText, self.exp_speed )
        box1.Add( box2, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        box2 = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "Dewell Time:" )
        box2.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.dewell_time = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        box2.Add( self.dewell_time, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OndewelltimeText, self.dewell_time )        
        box1.Add( box2, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )        

        self.delete_button = wx.Button( self, -1, "Delete", size = ( 80, -1 ) )
        self.Bind( wx.EVT_BUTTON, self.OndeleText, self.delete_button )        
        box1.Add( self.delete_button, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 ) 

        box.Add( box1, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )                

        self.route_list = wx.ListBox( self, -1, ( 200, -1 ), self.RouteList, wx.LB_SINGLE )
        box.Add( self.route_list, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )                
        self.Bind( wx.EVT_LISTBOX, self.OnSelList, self.route_list )        
        
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )
        
        self.SetSizer( sizer )
        sizer.Fit( self )
        
    def OnblocklistText( self, event ):
        "获取跑车路径"
        try:
            self.__blockList = [int( str ) for str in event.GetString().strip().splite( "," )]
        except:
            print "OnblocklistText: wrong block list!"
    def OnblockidText( self, event ):
        "get block id"
        self.__blockId = int( event.GetString() )

    def OnabscissaText( self, event ):
        "get abscissa"
        self.__absicssa = int( event.GetString() )
    
    def OntrainlengthText( self, event ):
        "get train length"
        self.__trainLen = int( event.GetString() )
        
    def OndirectionText( self, event ):
        "get direction"
        self.__direction = self.dir( event.GetString() )
        
    def OncogdirText( self, event ):
        "get cog direction"
        self.__cog_direction = self.dir( event.GetString() )    

    def getConfigData( self, event ):
        "get config data"
        return {"blocklist":self.__blockList,
                "blockid":self.__blockId,
                "abscissa":self.__absicssa,
                "trainlen":self.__trainLen,
                "direction":self.__direction,
                "cog_direction":self.__cog_direction
                }  


#------------------------------------------------------------------
#@用于添加用例的界面
#------------------------------------------------------------------
class AddCasePanel( wx.Dialog ):
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE,
            useMetal = False,
            ):
        self.__path = None
        self.__casename = None
        self.__caseType = None
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle( wx.DIALOG_EX_CONTEXTHELP )
        pre.Create( parent, ID, title, pos, size, style )

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate( pre )

        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle( wx.DIALOG_EX_METAL )


        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer( wx.VERTICAL )
        
        self.SelPath = filebrowse.DirBrowseButton( 
            self, -1, size = ( 600, -1 ), changeCallback = self.SelPathCallback
            )
        self.SelPath.SetLabel( "Case Path:" )
        self.SelPath.SetHelpText( "Select a case path!" )
        sizer.Add( self.SelPath, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )

        box = wx.BoxSizer( wx.HORIZONTAL )

        label = wx.StaticText( self, -1, "Case name:" )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )

        self.caseText = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        self.caseText.SetHelpText( "Write case name here!" )
        box.Add( self.caseText, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnCaseText, self.caseText )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        box = wx.BoxSizer( wx.HORIZONTAL )

        label = wx.StaticText( self, -1, "Platform Type:" )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )

        self.typeText = wx.TextCtrl( self, -1, "", size = ( 80, -1 ) )
        self.typeText.SetHelpText( "Write platform type here!" )
        box.Add( self.typeText, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnTypeText, self.typeText )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        line = wx.StaticLine( self, -1, size = ( 20, -1 ), style = wx.LI_HORIZONTAL )
        sizer.Add( line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5 )

        btnsizer = wx.StdDialogButtonSizer()
        
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton( self )
            btnsizer.AddButton( btn )
        
        btn = wx.Button( self, wx.ID_OK )
        btn.SetHelpText( "The OK button completes the dialog" )
        btn.SetDefault()
        btnsizer.AddButton( btn )

        btn = wx.Button( self, wx.ID_CANCEL )
        btn.SetHelpText( "The Cancel button cancels the dialog. (Cool, huh?)" )
        btnsizer.AddButton( btn )
        btnsizer.Realize()

        sizer.Add( btnsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )

        self.SetSizer( sizer )
        sizer.Fit( self )
        
    def SelPathCallback( self, event ):
        "获取路径"
        self.__path = event.GetString() 

    def OnCaseText( self, event ):
        "获取路径"
        self.__casename = event.GetString()

    def OnTypeText( self, event ):
        "获取路径"
        self.__caseType = event.GetString()
    
    def getDialogData( self ):
        _casename = self.__casename
        _caseType = self.__caseType
        _path = self.__path
        if "" in [_casename, _caseType, _path] or None in [_casename, _caseType, _path]:            
            return None
        else:
            return [_path, _casename, _caseType]


#------------------------------------------------------------------------------------------
#用于配置用例选用的地图库和配置文件（主要是选是end1，还是end2），最后还会显示用例的description
#------------------------------------------------------------------------------------------
class CaseConfigWizard( wiz.WizardPageSimple ):
    '''
    Case configuration Wizard
    '''

    Case_Config_Ctrl = [[['Case Version', 0, None, None ],
                         ['Case Number', 0, None, None ],
                         ['Case Step', 0, None, None ]],
                        [['Map Version', 0, None, None ],
                         ['Map Number', 1, [], None ],
                         ['Map Description', 0, None, None ]],
                        [['CC Core ID', 0, None, None ],
                         ['DataPlug Path', 0, None, None ],
                         ['Train Description', 0, None, None ]],
                        [['End Case Type', 1, ['1'], None ],
                         ['End Parmeter', 0, None, None ],
                         ['End Case Description', 0, None, None ]],
                        [['', 0, None, None ],
                         ['Description', 0, None, None ],
                         ['Add History', 2, None, None ]]]

    
    def __init__( self, parent, title = '', Create = True, size = wx.DefaultSize, pos = wx.DefaultPosition , CaseEditNode = None ):
#        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        wiz.WizardPageSimple.__init__( self, parent )
        self.sizer = makePageTitle( self, title )
        self.__casenode = CaseEditNode
        
        self.createFlag = Create
        
        if False == Create: #不是创建的时候，直接从记录中获取信息
            #获取选中的用例的相关信息
            _info = CaseParser.getEditCaseInfo()
            self.__CaseVersion = _info[0]
            self.__CaseNum = _info[1]
            self.__CaseStep = _info[2]
            self.__CaseStatus = _info[3]
        else: #创建的时候需要进行相关的数据处理
            self.__CaseVersion = CaseParser.getCurCaseVersion()
            self.__CaseNum = ""
            self.__CaseStep = ""
            self.__CaseStatus = ""
            
        _ConfigInfo = CaseParser.importEditCaseConfig()
            
        self.__MapVersion = _ConfigInfo['map'][0]
        self.__MapNum = _ConfigInfo['map'][1]
        self.__MapDes = _ConfigInfo['map'][2]
            
        self.__FileEnd = _ConfigInfo['fileconfig'][0]
        self.__DataPlugPath = _ConfigInfo['fileconfig'][1]
        self.__FileDes = _ConfigInfo['fileconfig'][2]
    
        self.__EndType = _ConfigInfo['endconfig'][0]
        self.__EndPara = _ConfigInfo['endconfig'][1]
        self.__EndDes = _ConfigInfo['endconfig'][2]
        
        # Now continue with the normal construction of the dialog
        # 开始画控件
        sizer = wx.BoxSizer( wx.VERTICAL )
        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "Case Version:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.CVTxT = wx.TextCtrl( self, -1, self.__CaseVersion, size = ( 160, -1 ) )
        self.CVTxT.SetEditable( False )
        box.Add( self.CVTxT, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )        
        label = wx.StaticText( self, -1, "Case Number:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 ) 
        self.CNTxt = wx.TextCtrl( self, -1, self.__CaseNum, size = ( 160, -1 ) )
        self.CNTxt.SetEditable( Create )
        box.Add( self.CNTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )        
        label = wx.StaticText( self, -1, "Case Step:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.CSTxt = wx.TextCtrl( self, -1, self.__CaseStep, size = ( 240, -1 ) )
        self.CSTxt.SetEditable( Create )
        box.Add( self.CSTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        sizer.Add( box, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        
        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "Map Version:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.MVTxt = wx.TextCtrl( self, -1, self.__MapVersion, size = ( 160, -1 ) )
        self.MVTxt.SetEditable( False )
        box.Add( self.MVTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )        
        label = wx.StaticText( self, -1, "Map Number:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 ) 
        self.MNCB = wx.ComboBox( self, -1, self.__MapNum, size = ( 160, -1 ) , choices = CaseParser.getMaplist(), style = wx.CB_DROPDOWN )
        self.Bind( wx.EVT_COMBOBOX, self.ONMapNumComboBox, self.MNCB )
        box.Add( self.MNCB, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )        
        label = wx.StaticText( self, -1, "Map Description:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.MDTxt = wx.TextCtrl( self, -1, self.__MapDes, size = ( 240, -1 ) )
        self.Bind( wx.EVT_TEXT, self.OnMapDescription, self.MDTxt )
        box.Add( self.MDTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        sizer.Add( box, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        
        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "CC Core ID:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.EndTxt = wx.ComboBox( self, -1, self.__FileEnd, size = ( 160, -1 ) , choices = ['End1', 'End2'], style = wx.CB_DROPDOWN )
        self.Bind( wx.EVT_COMBOBOX, self.OnEndType, self.EndTxt )
        box.Add( self.EndTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )        
        label = wx.StaticText( self, -1, "DataPlug Path:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 ) 
        self.DPTxt = wx.TextCtrl( self, -1, self.__DataPlugPath, size = ( 160, -1 ) )
        self.Bind( wx.EVT_TEXT, self.OnDataplugFile, self.DPTxt )
        box.Add( self.DPTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )        
        label = wx.StaticText( self, -1, "Train Description:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.FDTxt = wx.TextCtrl( self, -1, self.__FileDes, size = ( 240, -1 ) )
        self.Bind( wx.EVT_TEXT, self.OnFileDescription, self.FDTxt )
        box.Add( self.FDTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        sizer.Add( box, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )

        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "End Case Type:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.EndCB = wx.ComboBox( self, -1, self.__EndType, size = ( 160, -1 ) , choices = ['1'], style = wx.CB_DROPDOWN )
        self.Bind( wx.EVT_COMBOBOX, self.OnEndCombobox, self.EndCB )
        box.Add( self.EndCB, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )        
        label = wx.StaticText( self, -1, "End Parmeter:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 ) 
        self.ParaTxt = wx.TextCtrl( self, -1, str( self.__EndPara ), size = ( 160, -1 ) )
        self.Bind( wx.EVT_TEXT, self.OnParaEdit, self.ParaTxt )
        box.Add( self.ParaTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )        
        label = wx.StaticText( self, -1, "End Description:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.EDSTxt = wx.TextCtrl( self, -1, self.__EndDes, size = ( 240, -1 ) )
        box.Add( self.EDSTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_TEXT, self.OnEndDescription, self.EDSTxt )
        sizer.Add( box, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        
        #描述
        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText( self, -1, "Step Status:", size = ( 100, -1 ) )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 ) 
        self.CaseStatusCB = wx.ComboBox( self, -1, "Not Run", size = ( 160, -1 ) , choices = ['Not Run', "PASS", "FAIL"], style = wx.CB_DROPDOWN )                        
        box.Add( self.CaseStatusCB, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.DesTxt = wx.TextCtrl( self, -1, "Write Description Here!", size = ( 410, -1 ) )
        box.Add( self.DesTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.AddDesB = wx.Button( self, -1, 'Add', size = ( 64, -1 ) )
        box.Add( self.AddDesB, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_BUTTON, self.OnAddHistroy, self.AddDesB )
        self.EditDesB = wx.Button( self, -1, 'Edit', size = ( 64, -1 ) )
        box.Add( self.EditDesB, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.EditDesB.Enable( False )        
        self.Bind( wx.EVT_BUTTON, self.OnEditHistroy, self.EditDesB )
        self.DelDesB = wx.Button( self, -1, 'Delete', size = ( 64, -1 ) )
        box.Add( self.DelDesB, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )        
        sizer.Add( box, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        self.Bind( wx.EVT_BUTTON, self.OnDelHistroy, self.DelDesB )

        
        self.DescriptionShow = ShowGrid( self,
                                         ["Time", "Status", "Description"],
                                         size = ( 910, 200 ),
                                         OnSelectHandle = self.OnGridSelect )
        self.DescriptionShow.setCustable( _ConfigInfo['history'] )
        
        sizer.Add( self.DescriptionShow, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        
        self.sizer.Add( sizer, 8, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.SetSizer( self.sizer )
        self.sizer.Fit( self ) 
   
    def OnGridSelect( self, event ):
        "On Grid Select"
        self.DescriptionShow.OnSelect( event )
        _value = self.DescriptionShow.GetSelectData()
        if None == _value:
            return
        self.CaseStatusCB.SetValue( _value[1] )
        self.DesTxt.SetValue( _value[2] )
        self.EditDesB.Enable( True )
         
    def OnDelHistroy( self, event ):
        "delete history."
        _index = self.DescriptionShow.GetSelection()
        if None != _index:
            CaseParser.delHistory( _index )
            self.DescriptionShow.setCustable( CaseParser.getEditCaseConfig()['history'] )
            self.EditDesB.Enable( False ) 
            
    def OnEditHistroy( self, event ):
        "edit history"
        _content = self.DesTxt.GetValue()
        _data = commlib.curTime()
        _his = [_data, self.CaseStatusCB.GetValue(), _content]
        _index = self.DescriptionShow.GetSelection()
        if None != _index:
            CaseParser.editHistory( _data, self.CaseStatusCB.GetValue(), _content, _index )
#            self.DescriptionShow.setCustable( CaseParser.getEditCaseConfig()['history'] )
            self.DescriptionShow.EditOneData( _his )
                
    def OnAddHistroy( self , event ):
        "add history."
        _content = self.DesTxt.GetValue()
        _data = commlib.curTime()
        _his = [_data, self.CaseStatusCB.GetValue(), _content]
        CaseParser.addHistory( _data, self.CaseStatusCB.GetValue(), _content )
        self.DescriptionShow.setCustable( CaseParser.getEditCaseConfig()['history'] )

    def OnEndDescription( self , event ):
        "end type description."
        _content = self.EDSTxt.GetValue()
        CaseParser.setendTypeConfig_Des( _content )
    
    def OnParaEdit( self , event ):
        "end type Para"
        _content = self.ParaTxt.GetValue()
        CaseParser.setendTypeConfig_Para( _content )
        
    def OnEndCombobox( self , event ):
        "end type Para"
        _content = self.EndCB.GetValue()
        CaseParser.setendTypeConfig_Type( _content )
    
    def OnFileDescription( self , event ):
        "file description."
        _content = self.FDTxt.GetValue()
        CaseParser.setfileConfig_des( _content )
        
    def OnDataplugFile( self , event ):
        "dataplug path"
        _content = self.DPTxt.GetValue()
        CaseParser.setfileConfig_path( _content )
    
    def OnEndType( self , event ):
        "end type end1, end2."
        _content = self.EndTxt.GetValue()
#        print _content
        CaseParser.setfileConfig_end( _content )
    
    def OnMapDescription( self , event ):
        "Map Description."
        _content = self.MDTxt.GetValue()
        CaseParser.setMapConfig_Des( _content )
    
    def ONMapNumComboBox( self , event ):
        "Map Number."
        _content = self.MNCB.GetValue()
        CaseParser.setMapConfig_Num( _content )

    #---------------------------------------------------------
    #有几种返回值，0：修改配置成功。 1：新建成功，2：CaseNum, CaseStep中有不对的文件名，3.存在该用例不能创建
    #---------------------------------------------------------
    def EndThisPanel( self ):
        "end this panel"           
        if True == self.createFlag:
            _CaseNum = self.CNTxt.GetValue()
            _CaseStep = self.CSTxt.GetValue()
            if "" in [_CaseNum, _CaseStep]:
                wx.MessageBox( "Please right Case Number and Case Step!!!", "Sorry" )
                return 2
            if False == CaseParser.CreateNewCaseStep( _CaseNum, _CaseStep ):
                wx.MessageBox( "Please right Case Number and Case Step!!!", "Sorry" )
                return 3
            else:#用例创建成功，后续将会更新用例表
                #保存root_case_setting.xml
#                CaseParser.SaveEditCaseConfig()
                _scepath = CaseParser.getEditCaseInfo()[-1] + '/Script/scenario'
                _setpath = commlib.joinPath( commlib.getCurFileDir(), "/TPConfig/setting" )
                _mappath = CaseParser.getMapPathByMapName( self.MNCB.GetValue() )
                #重新设置path位置
                self.__casenode.SetPath( _scepath, _setpath, _mappath[2], _mappath[-1] )
                self.CNTxt.SetEditable( False )
                self.CSTxt.SetEditable( False )
                #创建完成将该码位置去
                self.createFlag = False
                return 1
        else:
#            CaseParser.SaveEditCaseConfig()
            _scepath = CaseParser.getEditCaseInfo()[-1] + '/Script/scenario'
            _setpath = commlib.joinPath( commlib.getCurFileDir(), "/TPConfig/setting" )
            _mappath = CaseParser.getMapPathByMapName( self.MNCB.GetValue() )
            #重新设置path位置
            self.__casenode.SetPath( _scepath, _setpath, _mappath[2], _mappath[-1] )

            return 0            
            

class RouteConfigWizard( wiz.WizardPageSimple ):
    '''
    Route Configuration Wizard
    '''
    Train_Route_Txt = [[['Block List', None], ['Start Block Id', None], [ 'Start Abscissa', None]],
                       [['Direction', None], ['Train Length', None], ['Cog Direction', None]] ]
    
    #有几种类型：0：txt，1：combox，2：button
    #格式，[名字，类型，标签ref，控件ref]：button的标签ref为None
    ExpectSpeed_Ctl = [[['Type', 1, ['1', '0'], None ], \
                        ['Coordinate', 0, None, None ], \
                        ['ExpectCoor', 0, None, None ], \
                        ['ExpectSpeed', 0, None, None ]],
                       [['End Position', 0, None, None ], \
                        ['Dwelltime', 0, None, None ], \
                        ['Add One Item', 2, None, None ], \
                        ['Del One Item', 2, None, None ], \
                        ['Edit One Item', 2, None, None ]]]

    __casenode = None
    
    __HasLoadDataFlag = False #记录是否已经载入数据的标志
    def __init__( self, parent, title = '', size = wx.DefaultSize, pos = wx.DefaultPosition , CaseEditNode = None ):
#        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        wiz.WizardPageSimple.__init__( self, parent )
        self.sizer = makePageTitle( self, title )
        
        self.__casenode = CaseEditNode 
        #创建Train_Route相关界面
        _route_box = self.createTexts( self.Train_Route_Txt )
        _Expect_box = self.createCtrls( self.ExpectSpeed_Ctl )
        
        _Framebox = wx.BoxSizer( wx.VERTICAL )
        _Framebox.Add( _route_box, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        line = wx.StaticLine( self, -1, size = ( 20, -1 ), style = wx.LI_HORIZONTAL )
        _Framebox.Add( line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5 )         
        _Framebox.Add( _Expect_box, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        #装载数据
#        self.__casenode.getTrainRouteList()
#        self.__casenode.getExpectSpeedList()
#        
#        #获取Train_Route值
#        self.Train_Route_Txt[0][0][-1].SetValue( self.__casenode.getTRBlockList() )
#        self.Train_Route_Txt[0][1][-1].SetValue( self.__casenode.getTRStartBlockID() )
#        self.Train_Route_Txt[0][2][-1].SetValue( self.__casenode.getTRStartAbs() )
#        
#        self.Train_Route_Txt[1][0][-1].SetValue( self.__casenode.getTRDirect() )
#        self.Train_Route_Txt[1][1][-1].SetValue( self.__casenode.getTRTrainLen() )
#        self.Train_Route_Txt[1][2][-1].SetValue( self.__casenode.getTRCogDir() )
        
        #创建list
#        self.__list = wx.ListBox( self, -1, size = ( 100, 200 ), \
#                                  choices = [], \
##                                 choices = self.__casenode.getExpectSpeedShowList(), \
#                                 style = wx.LB_SINGLE )
        box = wx.BoxSizer( wx.HORIZONTAL )
        self.__Grid = ShowGrid( self, ["Type",
                                       "Coordinate",
                                       "ExpectCoor/Accelerate",
                                       "ExpectSpeed",
                                       "Dwelltime"],
                               size = ( 100, 200 ),
                               OnSelectHandle = self.OnSelectGrid )
        
        self.SpeedDesTxt = wx.TextCtrl( self, -1, '', size = ( 100, 200 ), style = wx.TE_MULTILINE )
        SetCusFont( self.SpeedDesTxt, 14, Weight = wx.BOLD, Face = "Calibri" )
        box.Add( self.__Grid, 5, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box.Add( self.SpeedDesTxt, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
#        self.__list.SetSelection( 0 )
        _Framebox.Add( box, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.BindEvents()
        
        self.sizer.Add( _Framebox, 8, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.SetSizer( self.sizer )
        self.sizer.Fit( self )          
    
    def UpLoadData( self ):
        "upload data according to config"
        #载入选择好的地图
        self.__casenode.loadMap()
        #装载数据
        if False == self.__HasLoadDataFlag:
            print "load data route!"
            self.__casenode.getTrainRouteList()
            self.__casenode.getExpectSpeedList()
            self.__HasLoadDataFlag = True
        
        #获取Train_Route值
        self.Train_Route_Txt[0][0][-1].SetValue( self.__casenode.getTRBlockList() )
        self.Train_Route_Txt[0][1][-1].SetValue( self.__casenode.getTRStartBlockID() )
        self.Train_Route_Txt[0][2][-1].SetValue( self.__casenode.getTRStartAbs() )
        
        self.Train_Route_Txt[1][0][-1].SetValue( self.__casenode.getTRDirect() )
        self.Train_Route_Txt[1][1][-1].SetValue( self.__casenode.getTRTrainLen() )
        self.Train_Route_Txt[1][2][-1].SetValue( self.__casenode.getTRCogDir() )
        
        self.ExpectSpeed_Ctl[1][0][-1].SetValue( self.__casenode.getExpectSpeedEndPos() )
        
        #初始的时候设置Edit按钮为不可用
        self.ExpectSpeed_Ctl[1][4][3].Enable( False )
        #创建list
        self.__Grid.setCustable( self.__casenode.getExpectSpeedShowList() ) 
#        self.__Grid.SetSelection( None )
        self.SpeedDesTxt.Enable( False )
        
    def BindEvents( self ):
        "bind events"
        #先绑定修改TrainRoute的相关事件
        for _col in self.Train_Route_Txt:
            for _txt in _col:
#                print _txt
                self.Bind( wx.EVT_TEXT, self.ModifyTrainRoute, _txt[-1] )
                
        #绑定添加expectspeed事件
        self.Bind( wx.EVT_BUTTON, self.AddOneSpeed, self.ExpectSpeed_Ctl[1][2][3] )
        #绑定删除expectspeed事件
        self.Bind( wx.EVT_BUTTON, self.DelOneSpeed, self.ExpectSpeed_Ctl[1][3][3] )
        #绑定编辑expectspeed事件
        self.Bind( wx.EVT_BUTTON, self.EditOneSpeed, self.ExpectSpeed_Ctl[1][4][3] )
        #绑定类型的转换
        self.Bind( wx.EVT_COMBOBOX, self.OnSpeedTypeChange, self.ExpectSpeed_Ctl[0][0][3] )
        #绑定修改EndPos
        self.Bind( wx.EVT_TEXT, self.OnEditEndPos, self.ExpectSpeed_Ctl[1][0][3] )
        #绑定修改Des
        self.Bind( wx.EVT_TEXT, self.OnEditSpeedDes, self.SpeedDesTxt )
    
    def OnEditSpeedDes( self, event ):
        "On Edit Speed Description"
        _index = self.__Grid.GetSelection()
        if _index not in [-1, None]:
            self.__casenode.ModifyExpectSpeedOneDes( _index, self.SpeedDesTxt.GetValue() )
        else:
            print "OnEditSpeedDes error:", _index     

    def EditOneSpeed( self, event ):
        "edit one speed"
        _index = self.__Grid.GetSelection()
        
        if _index in [None, -1]:
            wx.MessageBox( "Please select a item to edit!" )
        else:
            try:
                _value = []
                _type = int( self.ExpectSpeed_Ctl[0][0][-1].GetValue() )
                _value.append( _type )
                _value.append( float( self.ExpectSpeed_Ctl[0][1][-1].GetValue() ) )
                _value.append( float( self.ExpectSpeed_Ctl[0][2][-1].GetValue() ) )
                _value.append( float( self.ExpectSpeed_Ctl[0][3][-1].GetValue() ) )
                if 1 == _type:
                    _value.append( int( float( self.ExpectSpeed_Ctl[1][1][-1].GetValue() ) ) )
                if True == self.__casenode.ModifyExpectSpeedOneContent( _index, _value ):
                    #更新Grid
                    self.__Grid.setCustable( self.__casenode.getExpectSpeedShowList() ) 
                    self.SpeedDesTxt.Enable( False )
        #            self.__list.Append( repr( _value ) )
                else:
                    print "EditOneSpeed Error!!!"
                    if 0 != _index:
                        wx.MessageBox( "Please write correct Speed Parameter To Edit!!!", "Warnning For EditOneSpeed!" )
                    else:
                        wx.MessageBox( "First Speed Sceanrio Can't be Edited!!!", "Warnning For EditOneSpeed!" )
            except ValueError, e:
                print 'EditOneSpeed error:', e            
    
    def OnSelectGrid( self, event ):
        "On SelectGrid"
        self.__Grid.OnSelect( event )
        _index = self.__Grid.GetSelection()
        
        if _index not in [None, -1]:
            #有选中的列的时候设置edit的Enable为true
            self.ExpectSpeed_Ctl[1][4][3].Enable( True )
            self.SpeedDesTxt.Enable( True )
            self.SpeedDesTxt.SetValue( self.__casenode.getExpectSpeedOneDes( _index ) )
            _content = self.__Grid.GetData()[_index]
            if "1" == _content[0]:
                self.ExpectSpeed_Ctl[0][0][-1].SetValue( "1" )
                self.ExpectSpeed_Ctl[1][1][3].Enable( True )
                self.ExpectSpeed_Ctl[0][2][2].SetLabel( 'expectCoor' )
                self.ExpectSpeed_Ctl[1][1][-1].SetValue( _content[4] )                 
            elif "0" == _content[0]:
                self.ExpectSpeed_Ctl[0][0][-1].SetValue( "0" )
                self.ExpectSpeed_Ctl[1][1][3].Enable( False )
                self.ExpectSpeed_Ctl[0][2][2].SetLabel( 'accelerate' )               
            
            self.ExpectSpeed_Ctl[0][1][-1].SetValue( _content[1] )
            self.ExpectSpeed_Ctl[0][2][-1].SetValue( _content[2] )
            self.ExpectSpeed_Ctl[0][3][-1].SetValue( _content[3] )
    
    def OnEditEndPos( self, evnet ):
        "on edit end pos"
        try:
            self.__casenode.setExpectSpeedEndPos( self.ExpectSpeed_Ctl[1][0][3].GetValue() )
        except ValueError, e:
            print "OnEditEndPos:", e
            
    def ModifyTrainRoute( self, event ):
        "modify Train Route"
        _lb = event.GetEventObject()
        _txt = _lb.GetValue()
        _label = None
        for _col in self.Train_Route_Txt:
            for _t in _col:
                if _t[1] == _lb:
                    _label = _t[0]
                    break
#        print 'ModifyTrainRoute', _txt, _label
        if _label == 'Block List':
            self.__casenode.setTRBlockList( _txt )
        elif _label == 'Start Block Id':
            self.__casenode.setTRStartBlockID( _txt )
        elif _label == 'Start Abscissa':
            self.__casenode.setTRStartAbs( _txt )
        elif _label == 'Direction':
            self.__casenode.setTRDirect( _txt )
        elif _label == 'Train Length':
            self.__casenode.setTRTrainLen( _txt )
        elif _label == 'Cog Direction':
            self.__casenode.setTRCogDir( _txt )
        else:
            print "ModifyTrainRoute error.", _label
    
    def AddOneSpeed( self, event ):
        "add One Speed."    
        _value = []
        try:
            _type = int( self.ExpectSpeed_Ctl[0][0][-1].GetValue() )
            _value.append( _type )
            _value.append( float( self.ExpectSpeed_Ctl[0][1][-1].GetValue() ) )
            _value.append( float( self.ExpectSpeed_Ctl[0][2][-1].GetValue() ) )
            _value.append( float( self.ExpectSpeed_Ctl[0][3][-1].GetValue() ) )
            if 1 == _type:
                _value.append( int( float( self.ExpectSpeed_Ctl[1][1][-1].GetValue() ) ) )
            if True == self.__casenode.AddExpectSpeedOneContent( _value ):
                #更新Grid
                self.__Grid.setCustable( self.__casenode.getExpectSpeedShowList() )
                self.SpeedDesTxt.Enable( False ) 
#            self.__list.Append( repr( _value ) )
            else:
                print "AddOneSpeed Error!!"
                wx.MessageBox( "Please write correct Speed Parameter To Add!!!", "Warnning For AddOneSpeed!" )
        except ValueError, e:
            print 'AddOneSpeed error:', e

    def DelOneSpeed( self, event ):
        "delete One speed"
        _index = self.__Grid.GetSelection()
        if 0 == _index:#第一个不能修改
            wx.MessageBox( "First Speed Sceanrio Can't be Deleted!!!", "Warnning For DelOneSpeed!" )
            return None
        if _index not in [wx.NOT_FOUND, -1, None]:
            self.__casenode.DeleteExpectSpeedOneContent( _index )
            self.__Grid.setCustable( self.__casenode.getExpectSpeedShowList() ) 
            self.SpeedDesTxt.Enable( False )
        else:
            print "DelOneSpeed: no item sellected!"
            
     
    def OnSpeedTypeChange( self, event ):
        "on speed type change."
        _ComboBox = event.GetEventObject()
        _type = int( _ComboBox.GetValue() )
        
        if 0 == _type:
#            print "OnSpeedTypeChange", _type
            self.ExpectSpeed_Ctl[1][1][3].Enable( False )
            self.ExpectSpeed_Ctl[0][2][2].SetLabel( 'accelerate' )
        elif 1 == _type:
#            print "OnSpeedTypeChange", _type
            self.ExpectSpeed_Ctl[1][1][3].Enable( True )
            self.ExpectSpeed_Ctl[0][2][2].SetLabel( 'expectCoor' )            
            
    def createNewText( self, label ):
        "create Text."
        label = wx.StaticText( self, -1, label, size = ( 100, -1 ) )
#        label.SetLabel()
        txtctrl = wx.TextCtrl( self, -1, '', size = ( 100, -1 ) )
#        txtctrl.Enable()
#        txtctrl.GetString()
#        txtctrl.SetEditable()
        return label, txtctrl
    
    def createLargeText( self, label ):
        "create Large Text."
        label = wx.StaticText( self, -1, label, size = ( 80, -1 ) )
#        label.SetLabel()
        txtctrl = wx.TextCtrl( self, -1, '', size = ( 200, -1 ) )
#        txtctrl.Enable()
#        txtctrl.GetString()
#        txtctrl.SetEditable()
        return label, txtctrl

    def createNewCombox( self, label, list ):
        "create new comboBox"
        label = wx.StaticText( self, -1, label, size = ( 100, -1 ) )
        _value = '' if 0 == len( list ) else list[0]
        ctrl = wx.ComboBox( self, -1, _value, size = ( 100, -1 ), choices = list, style = wx.CB_DROPDOWN )
#        ctrl.SetValue()
#        ctrl = wx.ComboBox( self, -1, list[0], size = ( 100, -1 ), choices = list, style = wx.CB_DROPDOWN )
#        ctrl.GetValue()
        return label, ctrl        
        
    def createNewButton( self, label ):
        "create new comboBox"
#        label = wx.StaticText( self, -1, label, size = ( 120, -1 ) )
        _ctrl = wx.Button( self, -1, label, size = ( 100, -1 ) )
#        _ctrl.Enable()
        return _ctrl  
        
    def createCtrls( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):   #_item = ['Type', 1, None, None ]
                if 0 == _item[1]:
                    _label, _txtctl = self.createNewText( _item[0] )
                    _Hbox.Add( _label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                    _Hbox.Add( _txtctl, 3, wx.ALIGN_CENTRE | wx.ALL, 5 )
                    list[_i][_j][2] = _label
                    list[_i][_j][3] = _txtctl
                elif 1 == _item[1]:
                    _label, _ctrl = self.createNewCombox( _item[0], _item[2] )
                    _Hbox.Add( _label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                    _Hbox.Add( _ctrl, 3, wx.ALIGN_CENTRE | wx.ALL, 5 )
                    list[_i][_j][3] = _ctrl
                elif 2 == _item[1]: 
                    _ctrl = self.createNewButton( _item[0] )
                    _Hbox.Add( _ctrl, 4, wx.ALIGN_CENTRE | wx.ALL, 5 )
                    list[_i][_j][3] = _ctrl                                                           
                    
            revbox.Add( _Hbox, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        return revbox        
    
    
    def createTexts( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):
                _label, _txtctl = self.createLargeText( _item[0] )
                _Hbox.Add( _label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                _Hbox.Add( _txtctl, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                list[_i][_j][1] = _txtctl
            revbox.Add( _Hbox, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        return revbox

    def EndThisPanel( self ):
        "end this panel"        

class SceConfigWizard( wiz.WizardPageSimple ):
    '''
    scenario config Wizard
    '''
    
    #有几种类型：0：txt，1：combox，2：button
    #格式，[名字，类型，标签ref，控件ref]：button的标签ref为None
    AddSce_Ctrl = [[['Type', 1, ['Position', 'Time'], None ], \
                    ['Block ID', 0, None, None ], \
                    ['Add One Sce', 2, None, None ]],
                   [['Abscissa', 0, None, None ], \
                    ['Delay', 0, None, None ], \
                    ['Del One Sce', 2, None, None ]],
                   [['Show Trans-Frm', 2, None, None ], \
                    ['Edit One Sce', 2, None, None ]]]
    
    AddNameValue_Ctrl = [[['Name', 1, [], None ], \
                          ['Add One Value', 2, None, None ]],
                         [['Value', 0, None, None ], \
                          ['Del One Value', 2, None, None ]],
                         [['Edit One Value', 2, None, None ]]]
    
    __HasLoadDataFlag = False #记录是否已经载入数据的标志
    __TransFromFrame = None   #存储transform界面
    def __init__( self, parent, title = None, size = wx.DefaultSize, pos = wx.DefaultPosition, CaseEditNode = None ):
#        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        wiz.WizardPageSimple.__init__( self, parent )
        self.sizer = makePageTitle( self, title )

    
        self.__casenode = CaseEditNode
#        #导入数据
#        self.__casenode.getScenarioDic()
#        self.__casenode.getDevVarListDic()
        
        #创建Devicelist
        box3 = wx.BoxSizer( wx.VERTICAL )
        label = wx.StaticText( self, -1, 'Device List:', size = ( 80, -1 ) )
        self.__devList = wx.ListBox( self, -1, size = ( 100, 300 ), \
#                                     choices = self.__casenode.getDeviceList(), \
                                     choices = [], \
                                     style = wx.LB_SINGLE )
        SetCusFont( self.__devList, 12, Weight = wx.BOLD, Face = "Calibri" )
        box3.Add( label, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box3.Add( self.__devList, 13, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
#        self.__devList.SetSelection( -1 )
        
        box = wx.BoxSizer( wx.VERTICAL )
        #创建AddSce
        _box_Sce = self.createCtrls( self.AddSce_Ctrl )
        
        box.Add( _box_Sce, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        #PosList
        self.__PosList = wx.ListBox( self, -1, size = ( 100, 100 ), \
                                    choices = [], \
                                    style = wx.LB_SINGLE )
        self.__PosList.SetSelection( -1 )
        
        SetCusFont( self.__PosList, 12, Weight = wx.BOLD, Face = "Calibri" )
#        box.Add( self.__PosList, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        #TimeList
        self.__TimeList = wx.ListBox( self, -1, size = ( 100, 100 ), \
                                     choices = [], \
                                     style = wx.LB_SINGLE )
        self.__TimeList.SetSelection( -1 )
        self.__TimeList.Enable( False ) #默认值
        SetCusFont( self.__TimeList, 11, Weight = wx.BOLD, Face = "Calibri" )
#        box.Add( self.__TimeList, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        box_3 = wx.BoxSizer( wx.VERTICAL )
        box_3.Add( self.__PosList, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box_3.Add( self.__TimeList, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.SCEDesTxt = wx.TextCtrl( self, -1, '', size = ( 100, 200 ), style = wx.TE_MULTILINE )
        SetCusFont( self.SCEDesTxt, 12, Weight = wx.BOLD, Face = "Calibri" )
        box_2 = wx.BoxSizer( wx.HORIZONTAL )
        box_2.Add( box_3, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box_2.Add( self.SCEDesTxt, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )        
        
        box.Add( box_2, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        box1 = wx.BoxSizer( wx.VERTICAL )
        
        #创建AddNameValue
        _box_Name_Value = self.createCtrls( self.AddNameValue_Ctrl )
        self.__VarDesTxt = wx.TextCtrl( self, -1, '', size = ( 100, 80 ), style = wx.TE_MULTILINE )
        self.__VarDesTxt.SetEditable( False )
        SetCusFont( self.__VarDesTxt, 11, Weight = wx.BOLD, Face = "Calibri" )
#        self.__VarDesTxt.Enable( False )
        self.__NameValueGrid = ShowGrid( self,
                                         ['Name', 'Value'],
                                         size = ( 100, 180 ),
                                         OnSelectHandle = self.OnSelectNameValueGrid )
        box1.Add( _box_Name_Value, 6, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box1.Add( self.__VarDesTxt, 4, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box1.Add( self.__NameValueGrid, 9, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        _Framebox = wx.BoxSizer( wx.HORIZONTAL )
        _Framebox.Add( box3, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box, 8, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box1, 5, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.BindEvents()


        self.sizer.Add( _Framebox, 8, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.SetSizer( self.sizer )
        self.sizer.Fit( self )

    def UpLoadData( self ):
        "upload data according to config"
        #导入数据
        if False == self.__HasLoadDataFlag:
            print "load data scenario!"
            self.__casenode.getScenarioDic()
            self.__casenode.getDevVarListDic()
            self.__HasLoadDataFlag = True
            
        self.__devList.SetItems( self.__casenode.getDeviceList() )        
        self.__devList.SetSelection( -1 )
    
        #设置__PosList为空
        self.__PosList.SetItems( [] )
        self.__PosList.SetSelection( -1 )
        
        #设置__TimeList为空
        self.__TimeList.SetItems( [] )
        self.__TimeList.SetSelection( -1 )
        
        #设置 AddSce_Ctrl为disable
        self.EnableAddSceCtrl( False )
        
        #设置 __NameValueGrid为disable
        self.EnableNameValueCtrl( False )
        self.SCEDesTxt.Enable( False )
        
    def EnableAddSceCtrl( self, enable ):       
        "enable name value ctrl"
        for _row in self.AddSce_Ctrl:
            for _item in _row:
                if ( True == enable ) and ( _item == self.AddSce_Ctrl[2][1] ):#edit的Enable方式不同
                    pass
                else:
                    _item[-1].Enable( enable )
        
        #对于type='Time'的要将下面两个控件改为disable
        _type = self.AddSce_Ctrl[0][0][-1].GetValue()
        if "Time" == _type:
            self.AddSce_Ctrl[1][0][-1].Enable( False )
            self.AddSce_Ctrl[1][1][-1].Enable( False )
        
    def EnableNameValueCtrl( self, enable ):       
        "enable name value ctrl"
        self.__NameValueGrid.Enable( enable )
        for _row in self.AddNameValue_Ctrl:
            for _item in _row:
                if ( True == enable ) and ( _item == self.AddNameValue_Ctrl[2][0] ):#edit的Enable方式不同
                    _item[-1].Enable( False ) #edit value只有一种情况可以为enable！！！
                else:
                    _item[-1].Enable( enable )
               
    def BindEvents( self ):
        "bind events"
        self.Bind( wx.EVT_LISTBOX, self.OnChangeDevice, self.__devList )
        
        self.Bind( wx.EVT_LISTBOX, self.OnChangePosList, self.__PosList )
        self.Bind( wx.EVT_LISTBOX, self.OnChangeTimeList, self.__TimeList )
        self.Bind( wx.EVT_COMBOBOX, self.OnTypeChange, self.AddSce_Ctrl[0][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnAddSce, self.AddSce_Ctrl[0][2][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelSce, self.AddSce_Ctrl[1][2][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnEditSce, self.AddSce_Ctrl[2][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnShowTransformFrame, self.AddSce_Ctrl[2][0][-1] )
        
        self.Bind( wx.EVT_BUTTON, self.OnAddValue, self.AddNameValue_Ctrl[0][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelValue, self.AddNameValue_Ctrl[1][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnEditValue, self.AddNameValue_Ctrl[2][0][-1] )
        self.Bind( wx.EVT_COMBOBOX, self.OnNameChange, self.AddNameValue_Ctrl[0][0][-1] )
        
        self.Bind( wx.EVT_TEXT, self.OnEditSceDes, self.SCEDesTxt )
    
    
    def OnEditSceDes( self, event ):
        "On Edit Scenario Description"
        _type = self.AddSce_Ctrl[0][0][-1].GetValue()
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()] 
        if "Position" == _type:
            _index = self.__PosList.GetSelection()
            if _index not in [-1, None]:
                self.__casenode.EditOneSceDes( _deviceName,
                                               0,
                                               _index,
                                               self.SCEDesTxt.GetValue() )

        elif "Time" == _type:
            _index = self.__TimeList.GetSelection()
            if _index not in [-1, None]:
                self.__casenode.EditOneSceDes( _deviceName,
                                               1,
                                               _index,
                                               self.SCEDesTxt.GetValue() )
        else:
            print "OnEditSce: error", _type, _deviceName          
        
    
    def OnShowTransformFrame( self, event ):
        "On Show Transform Frame"
        if not self.__TransFromFrame:
            self.__TransFromFrame = DistanceTransFromFrm( self, -1, "Transform Frame", CaseEditNode = self.__casenode )
            self.__TransFromFrame.Show()
        else:
            self.__TransFromFrame.Show()            

    def CloseTransformFrame( self ):
        "On Show Transform Frame"
        if self.__TransFromFrame:
            self.__TransFromFrame.Destroy()
            self.__TransFromFrame = None
    
    def OnNameChange( self, event ):
        "On Name change"
        #refresh Variant Description
        _Value = self.AddNameValue_Ctrl[0][0][-1].GetValue()
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()]
        self.__VarDesTxt.SetValue( self.__casenode.getDevVarDes( _deviceName, _Value ) )
        
    def OnEditSce( self, event ):
        "on edit scenario"
        _type = self.AddSce_Ctrl[0][0][-1].GetValue()
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()] 
        if "Position" == _type:
            _block_id = self.AddSce_Ctrl[0][1][-1].GetValue()
            _Abs = self.AddSce_Ctrl[1][0][-1].GetValue()
            _Delay = self.AddSce_Ctrl[1][1][-1].GetValue()
            _index = self.__PosList.GetSelection()
            self.__casenode.EditOneSce( _deviceName, 0, _index, [_block_id, _Abs, _Delay, []] )
            self.__PosList.SetItems( self.__casenode.getSceContentShowList( _deviceName ) )
            self.__PosList.SetSelection( _index )
        elif "Time" == _type:
            _Time = self.AddSce_Ctrl[0][1][-1].GetValue()
            _index = self.__TimeList.GetSelection()
            self.__casenode.EditOneSce( _deviceName, 1, _index, [_Time, []] )
            self.__TimeList.SetItems( self.__casenode.getTimeContentShowList( _deviceName ) )
            self.__TimeList.SetSelection( _index )
        else:
            print "OnEditSce: error", _type, _deviceName        
        
    def OnEditValue( self, event ):
        "on edit value"
        if self.__PosList.GetSelection() < 0 and self.__TimeList.GetSelection() < 0:
            print "OnEditValue: please select a sec to add!!"
            return
        _Name = self.AddNameValue_Ctrl[0][0][-1].GetValue()
        _Value = self.AddNameValue_Ctrl[1][0][-1].GetValue()
        
        self.__NameValueGrid.EditOneData( [_Name, _Value] )
        
        _type = self.AddSce_Ctrl[0][0][-1].GetValue()
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()] 

        if "Position" == _type:
            self.__casenode.ModifyOneSce( _deviceName, \
                                          0, \
                                          self.__PosList.GetSelection(), \
                                          self.__NameValueGrid.GetData() )
        elif "Time" == _type:
            self.__casenode.ModifyOneSce( _deviceName, \
                                          1, \
                                          self.__TimeList.GetSelection(), \
                                          self.__NameValueGrid.GetData() )              
    
    
    def OnAddValue( self, event ):
        "On Add Value"
        if self.__PosList.GetSelection() < 0 and self.__TimeList.GetSelection() < 0:
            print "OnAddValue: please select a sec to add!!"
            return
        _Name = self.AddNameValue_Ctrl[0][0][-1].GetValue()
        _Value = self.AddNameValue_Ctrl[1][0][-1].GetValue()
        
        self.__NameValueGrid.AddOneData( [_Name, _Value] )
        
        _type = self.AddSce_Ctrl[0][0][-1].GetValue()
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()] 

        if "Position" == _type:
            self.__casenode.ModifyOneSce( _deviceName, \
                                          0, \
                                          self.__PosList.GetSelection(), \
                                          self.__NameValueGrid.GetData() )
        elif "Time" == _type:
            self.__casenode.ModifyOneSce( _deviceName, \
                                          1, \
                                          self.__TimeList.GetSelection(), \
                                          self.__NameValueGrid.GetData() )      
    
    def OnDelValue( self, event ):
        "On delete Value"
        _index = self.__NameValueGrid.GetSelection()
        if None != _index:
            self.__NameValueGrid.DelOneData( _index )

        _type = self.AddSce_Ctrl[0][0][-1].GetValue()
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()]
        if "Position" == _type:
            self.__casenode.ModifyOneSce( _deviceName, \
                                          0, \
                                          self.__PosList.GetSelection(), \
                                          self.__NameValueGrid.GetData() )
        elif "Time" == _type:
            self.__casenode.ModifyOneSce( _deviceName, \
                                          1, \
                                          self.__TimeList.GetSelection(), \
                                          self.__NameValueGrid.GetData() ) 
    
    def OnAddSce( self, event ):
        "on add scenario."
        _type = self.AddSce_Ctrl[0][0][-1].GetValue()
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()] 
        if "Position" == _type:
            _block_id = self.AddSce_Ctrl[0][1][-1].GetValue()
            _Abs = self.AddSce_Ctrl[1][0][-1].GetValue()
            _Delay = self.AddSce_Ctrl[1][1][-1].GetValue()
            self.__casenode.AddOneSce( _deviceName, 0, [_block_id, _Abs, _Delay, []] )
            self.__PosList.SetItems( self.__casenode.getSceContentShowList( _deviceName ) )
            self.__PosList.SetSelection( -1 )
            self.SCEDesTxt.Enable( False )
        elif "Time" == _type:
            _Time = self.AddSce_Ctrl[0][1][-1].GetValue()
            self.__casenode.AddOneSce( _deviceName, 1, [_Time, []] )
            self.__TimeList.SetItems( self.__casenode.getTimeContentShowList( _deviceName ) )
            self.__TimeList.SetSelection( -1 )
            self.SCEDesTxt.Enable( False )            
        else:
            print "OnAddSce: error", _type, _deviceName
    
    def OnDelSce( self, event ):
        "on delete scenario."
        _type = self.AddSce_Ctrl[0][0][-1].GetValue()
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()] 
        #设置 __NameValueGrid为disable
        self.EnableNameValueCtrl( False )
        
        if "Position" == _type:
            _index = self.__PosList.GetSelection()
            self.__casenode.DeleteOneSce( _deviceName, 0, _index )
            self.__PosList.SetItems( self.__casenode.getSceContentShowList( _deviceName ) )
            self.__PosList.SetSelection( -1 ) 
            self.SCEDesTxt.Enable( False )           
        elif "Time" == _type:
            _index = self.__TimeList.GetSelection()
            self.__casenode.DeleteOneSce( _deviceName, 1, _index )
            self.__TimeList.SetItems( self.__casenode.getTimeContentShowList( _deviceName ) )
            self.__TimeList.SetSelection( -1 )               
            self.SCEDesTxt.Enable( False )
    
    def OnChangePosList( self, event ):
        "On change Pos list"
        _index = self.__PosList.GetSelection()
#        self.__NameValueGrid.Enable( True )
        self.EnableNameValueCtrl( True )
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()]
        
        if -1 != _index:
            _showData = self.__casenode.getOneSceContentPos( _deviceName, _index )
            self.__NameValueGrid.setCustable( _showData )
            self.__NameValueGrid.SetSelection( None )
            
            _Poscontent = self.__casenode.getOneScePosContent( _deviceName, _index )
            self.AddSce_Ctrl[2][1][-1].Enable( True )
            self.AddSce_Ctrl[0][0][-1].SetValue( "Position" )
            self.AddSce_Ctrl[0][1][-1].SetValue( str( _Poscontent[0] ) )
            self.AddSce_Ctrl[1][0][-1].SetValue( str( _Poscontent[1] ) )
            self.AddSce_Ctrl[1][1][-1].SetValue( str( _Poscontent[2] ) )
            self.SCEDesTxt.Enable( True )
            self.SCEDesTxt.SetValue( self.__casenode.getOneSceDes( _deviceName, 0, _index ) )
            
            
    def OnChangeTimeList( self, event ):
        "On change Time list"
        _index = self.__TimeList.GetSelection()
#        self.__NameValueGrid.Enable( True )
        self.EnableNameValueCtrl( True )
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()]
        
        if -1 != _index:
            _showData = self.__casenode.getOneSceContentTime( _deviceName, _index )
            self.__NameValueGrid.setCustable( _showData )
            self.__NameValueGrid.SetSelection( None )        

            Time = self.__casenode.getOneSceTimeContent( _deviceName, _index )
            self.AddSce_Ctrl[2][1][-1].Enable( True )
            self.AddSce_Ctrl[0][0][-1].SetValue( "Time" )
            self.AddSce_Ctrl[0][1][-1].SetValue( str( Time ) )
            self.SCEDesTxt.Enable( True )
            self.SCEDesTxt.SetValue( self.__casenode.getOneSceDes( _deviceName, 1, _index ) )
            
    def OnSelectNameValueGrid( self, event ):
        "On Select Name Value Grid"
        self.__NameValueGrid.OnSelect( event )
        _value = self.__NameValueGrid.GetSelectData()
        if None == _value:
            return
        self.AddNameValue_Ctrl[0][0][-1].SetValue( _value[0] )
        self.AddNameValue_Ctrl[1][0][-1].SetValue( _value[1] )
        self.AddNameValue_Ctrl[2][0][-1].Enable( True )
        #refresh Variant Description
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()]
        self.__VarDesTxt.SetValue( self.__casenode.getDevVarDes( _deviceName, _value[0] ) )
    
    def OnChangeDevice( self, event ):
        "on change device"
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()]
        #设置 AddSce_Ctrl为Enable
        self.EnableAddSceCtrl( True )
        self.AddSce_Ctrl[2][1][-1].Enable( False )
        #将name控件的list进行修改
        _Namelist = self.__casenode.getDevVarList( _deviceName )
        self.AddNameValue_Ctrl[0][0][-1].SetItems( _Namelist )
        self.AddNameValue_Ctrl[0][0][-1].SetSelection( 0 )
        #更新描述
        _Value = self.AddNameValue_Ctrl[0][0][-1].GetValue()
        _deviceName = self.__casenode.getDeviceList()[self.__devList.GetSelection()]
        self.__VarDesTxt.SetValue( self.__casenode.getDevVarDes( _deviceName, _Value ) )

        
        #在list上显示脚本
        self.__PosList.SetItems( self.__casenode.getSceContentShowList( _deviceName ) )
        self.__PosList.SetSelection( -1 )
        self.__TimeList.SetItems( self.__casenode.getTimeContentShowList( _deviceName ) )
        self.__TimeList.SetSelection( -1 )
        
        #设置 __NameValueGrid为disable
        self.EnableNameValueCtrl( False )
        
        self.SCEDesTxt.Enable( False )
        
    def OnTypeChange( self, event ):
        "On Type Change"
        _ComboBox = event.GetEventObject()
        _Value = _ComboBox.GetValue() 
        if 'Position' == _Value:
            self.__PosList.Enable( True )
            self.__PosList.SetSelection( -1 )
            self.__TimeList.Enable( False )
            self.__TimeList.SetSelection( -1 )
            self.AddSce_Ctrl[0][1][2].SetLabel( 'Block ID' )
            self.AddSce_Ctrl[1][0][-1].Enable( True ) 
            self.AddSce_Ctrl[1][1][-1].Enable( True ) 
            self.__NameValueGrid.setCustable( [['None', 'None']] )
            self.SCEDesTxt.Enable( False )
            
        elif 'Time' == _Value:
            self.__PosList.Enable( False )
            self.__PosList.SetSelection( -1 )
            self.__TimeList.Enable( True )
            self.__TimeList.SetSelection( -1 )
            self.AddSce_Ctrl[0][1][2].SetLabel( 'Time' )
            self.AddSce_Ctrl[1][0][-1].Enable( False ) 
            self.AddSce_Ctrl[1][1][-1].Enable( False )        
            self.__NameValueGrid.setCustable( [['None', 'None']] )
            self.SCEDesTxt.Enable( False )
    
    
    def createNewText( self, label ):
        "create Text."
        label = wx.StaticText( self, -1, label, size = ( 50, -1 ) )
#        label.SetLabel()
        txtctrl = wx.TextCtrl( self, -1, '', size = ( 100, -1 ) )
#        txtctrl.GetString()
#        txtctrl.SetEditable()
        return label, txtctrl

    def createNewCombox( self, label, list ):
        "create new comboBox"
        label = wx.StaticText( self, -1, label, size = ( 50, -1 ) )
        _value = '' if 0 == len( list ) else list[0]
        ctrl = wx.ComboBox( self, -1, _value, size = ( 100, -1 ), choices = list, style = wx.CB_DROPDOWN )
        
#        ctrl = wx.ComboBox( self, -1, list[0], size = ( 100, -1 ), choices = list, style = wx.CB_DROPDOWN )
#        ctrl.SetItems(items)
#        ctrl.SetSelection()
        return label, ctrl        
        
    def createNewButton( self, label ):
        "create new comboBox"
#        label = wx.StaticText( self, -1, label, size = ( 120, -1 ) )
        _ctrl = wx.Button( self, -1, label, size = ( 100, -1 ) )
        return _ctrl  
        
    def createCtrls( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):   #_item = ['Type', 1, None, None ]
                if 0 == _item[1]:
                    _label, _txtctl = self.createNewText( _item[0] )
                    _Hbox.Add( _label, 0, wx.ALIGN_RIGHT | wx.ALL, 4 )
                    _Hbox.Add( _txtctl, 0, wx.ALIGN_RIGHT | wx.ALL, 4 )
                    list[_i][_j][2] = _label
                    list[_i][_j][3] = _txtctl
                elif 1 == _item[1]:
                    _label, _ctrl = self.createNewCombox( _item[0], _item[2] )
                    _Hbox.Add( _label, 0, wx.ALIGN_RIGHT | wx.ALL, 4 )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_RIGHT | wx.ALL, 4 )
                    list[_i][_j][3] = _ctrl
                elif 2 == _item[1]: 
                    _ctrl = self.createNewButton( _item[0] )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_RIGHT | wx.ALL, 4 )
                    list[_i][_j][3] = _ctrl                                                           
                    
            revbox.Add( _Hbox, 0, wx.ALIGN_RIGHT | wx.ALL, 4 )
        return revbox        
    
    
    def createTexts( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):
                _label, _txtctl = self.createNewText( _item[0] )
                _Hbox.Add( _label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                _Hbox.Add( _txtctl, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                list[_i][_j][1] = _txtctl
            revbox.Add( _Hbox, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        return revbox

    def EndThisPanel( self ):
        "end this panel"        
        return True        

#===============================================================================
# 
# 主要对CI数据进行配置
# 来自文件：ci_variant_scenario.xml
#===============================================================================
class CISceConfigWizard( wiz.WizardPageSimple ):
    '''
    CI scenario config Wizard
    '''
    
    #有几种类型：0：txt，1：combox，2：button
    #格式，[名字，类型，标签ref，控件ref]：button的标签ref为None
    CISce_Ctrl = [[['Block ID', 0, None, None ], \
                    ['Abscissa', 0, None, None ]],
                   [['Delay', 0, None, None ]],
                   [['Add Sce', 2, None, None ], \
                    ['Del Sce', 2, None, None ],
                    ['Edit Sce', 2, None, None ]]]    

    CISceItem_Ctrl = [[['CBI_ID', 1, [], None ], \
                          ['Index', 0, None, None ]],
                         [['Value', 0, None, None ]],
                         [['Add Item', 2, None, None ], \
                          ['Del Item', 2, None, None ],
                          ['Edit Item', 2, None, None ],
                          ['Default', 2, None, None ]]]
    
    __HasLoadDataFlag = False #记录是否已经载入数据的标志
    def __init__( self, parent, title = None, size = wx.DefaultSize, pos = wx.DefaultPosition, CaseEditNode = None ):
#        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        wiz.WizardPageSimple.__init__( self, parent )
        self.sizer = makePageTitle( self, title ) 
           
        self.__casenode = CaseEditNode
        #self.CIVarP = CaseEditNode

        #============================ 绘制控件-开始 ===============================        
        box1 = wx.BoxSizer( wx.VERTICAL )
        _box_sce = self.createCtrls( self.CISce_Ctrl )
#        print 'getCIVariantSceShowData', self.__casenode.getCIVariantSceShowData()
        self.__SceList = wx.ListBox( self, -1, size = ( 100, 100 ), \
#                                    choices = self.__casenode.getCIVariantSceShowData(), \
                                    choices = [], \
                                    style = wx.LB_SINGLE )
        
        SetCusFont( self.__SceList, 12, Weight = wx.BOLD, Face = "Calibri" )
#        self.__SceList.SetSelection( -1 )
        
        box1.Add( _box_sce, 3, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        box1.Add( self.__SceList, 5, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        self.CISCEDesTxt = wx.TextCtrl( self, -1, '', size = ( 100, -1 ), style = wx.TE_MULTILINE )
        SetCusFont( self.CISCEDesTxt, 14, Weight = wx.BOLD, Face = "Calibri" )
        box1.Add( self.CISCEDesTxt, 2, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        box2 = wx.BoxSizer( wx.VERTICAL )
        _box_item = self.createCtrls( self.CISceItem_Ctrl )
#        self.CISceItem_Ctrl[0][0][-1].SetItems( self.__casenode.getLineSecList() )
#        self.CISceItem_Ctrl[0][0][-1].SetSelection( 0 )        
        self.__ItemGrid = ShowGrid( self, [ 'CBI_ID', 'Index', 'Value'], OnSelectHandle = self.OnSelectNameValueChange )
#        self.__ItemGrid.setCustable( self.__casenode.getCIVariantSceShowData() )
        box2.Add( _box_item, 3, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        box2.Add( self.__ItemGrid, 7, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 ) 
        
        line = wx.StaticLine( self, -1, size = ( 2, -1 ), style = wx.LI_VERTICAL )
       
        _Framebox = wx.BoxSizer( wx.HORIZONTAL )
        _Framebox.Add( box1, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( line, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP | wx.GROW, 5 )       
        _Framebox.Add( box2, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        self.BindEvents()

        self.sizer.Add( _Framebox, 8, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.SetSizer( self.sizer )
        self.sizer.Fit( self )   
        #============================ 绘制控件-结束 ===============================
      
    def UpLoadData( self ):
        "upload data according to config"
        #导入数据
        if False == self.__HasLoadDataFlag:
            print "load data zc scenario!"
            #self.__casenode.getZCVariantIni()
            self.__casenode.getCIVariantSce()
            self.__HasLoadDataFlag = True

        
        self.__SceList.SetItems( self.__casenode.getCIVariantSceShowData() )
        self.__SceList.SetSelection( -1 )

        self.CISceItem_Ctrl[0][0][-1].SetItems( self.__casenode.getCBIIDList() )
        self.CISceItem_Ctrl[0][0][-1].SetSelection( 0 )    
        
        #初始化显示
        self.__ItemGrid.setCustable( [] )
        
        self.EnableItemCtrl( False )
        #self.EnableItemCtrl( True )
        
        self.CISce_Ctrl[2][2][-1].Enable( False )
        
        self.CISCEDesTxt.Enable( False )

        
    def EnableItemCtrl( self, enable ):       
        "enable item ctrl"
        self.__ItemGrid.Enable( enable )
        for _row in self.CISceItem_Ctrl:
            for _item in _row:
                if ( True == enable ) and ( _item == self.CISceItem_Ctrl[2][2] ):#不用这个函数设置edit的true
                    pass
                else:
                    _item[-1].Enable( enable )
    
    def BindEvents( self ):
        "bind events"
        
        self.Bind( wx.EVT_BUTTON, self.OnAddScePosition, self.CISce_Ctrl[2][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelScePosition, self.CISce_Ctrl[2][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnEditScePosition, self.CISce_Ctrl[2][2][-1] )      
 
        self.Bind( wx.EVT_BUTTON, self.OnAddSceItem, self.CISceItem_Ctrl[2][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelSceItem, self.CISceItem_Ctrl[2][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnEditSceItem, self.CISceItem_Ctrl[2][2][-1] ) 
        self.Bind( wx.EVT_BUTTON, self.OnDefaultVarName, self.CISceItem_Ctrl[2][3][-1] )
        
        self.Bind( wx.EVT_LISTBOX, self.OnChangeSce, self.__SceList )
        
        self.Bind( wx.EVT_TEXT, self.OnEditCISceDes, self.CISCEDesTxt )
            
    def OnAddScePosition( self, event ):
        "on add Position to scenario"
        self.EnableItemCtrl( False )
        self.CISce_Ctrl[2][2][-1].Enable( False )
        _block_id = self.CISce_Ctrl[0][0][-1].GetValue()
        _abs = self.CISce_Ctrl[0][1][-1].GetValue()
        _delay = self.CISce_Ctrl[1][0][-1].GetValue()
        self.__casenode.AddOneCIVariantSce( [_block_id, _abs, _delay, []] )
        self.__SceList.SetItems( self.__casenode.getCIVariantSceShowData() )
        self.CISCEDesTxt.Enable( False )
        
    def OnDelScePosition( self, event ):
        "on delete Position in scenario."
        self.EnableItemCtrl( False )
        self.CISce_Ctrl[2][2][-1].Enable( False )
        _index = self.__SceList.GetSelection()
        if _index in [None, -1]:
            return
        self.__casenode.DeleteOneCIVariantSce( _index )
        self.__SceList.SetItems( self.__casenode.getCIVariantSceShowData() )
        self.__ItemGrid.setCustable( [] )
        self.CISCEDesTxt.Enable( False )
    
    def OnEditScePosition( self, event ):
        "On Edit Position in scanario"
        _index = self.__SceList.GetSelection()
        _block_id = self.CISce_Ctrl[0][0][-1].GetValue()
        _abs = self.CISce_Ctrl[0][1][-1].GetValue()
        _delay = self.CISce_Ctrl[1][0][-1].GetValue()        
        self.__casenode.ModifyOneCIVariantScePos( _index, [_block_id, _abs, _delay] )
        self.__SceList.SetItems( self.__casenode.getCIVariantSceShowData() )
        self.__SceList.SetSelection( _index )
        
    def OnAddSceItem( self, event ):
        "on add item to the Position of scanario"
        self.CISceItem_Ctrl[2][2][-1].Enable( False )
        _line = self.CISceItem_Ctrl[0][0][-1].GetValue()
        _index = self.CISceItem_Ctrl[0][1][-1].GetValue()
        _value = self.CISceItem_Ctrl[1][0][-1].GetValue()
        self.__ItemGrid.AddOneData( [_line, _index, _value] )
        
        self.__casenode.ModifyOneCIVariantSce( self.__SceList.GetSelection(), \
                                              self.__ItemGrid.GetData() )
    
    def OnDelSceItem( self, event ):
        "on delete item in the Position of scanario"
        self.CISceItem_Ctrl[2][2][-1].Enable( False )
        _Index = self.__ItemGrid.GetSelection()
        if None != _Index:
            self.__ItemGrid.DelOneData( _Index )
        
        self.__casenode.ModifyOneCIVariantSce( self.__SceList.GetSelection(), \
                                              self.__ItemGrid.GetData() )
    
    def OnEditSceItem( self, event ):
        "On Edit item in the Position of scanario."
        _line = self.CISceItem_Ctrl[0][0][-1].GetValue()
        _index = self.CISceItem_Ctrl[0][1][-1].GetValue()
        _value = self.CISceItem_Ctrl[1][0][-1].GetValue()
        self.__ItemGrid.EditOneData( [_line, _index, _value] )
        
        self.__casenode.ModifyOneCIVariantSce( self.__SceList.GetSelection(), \
                                              self.__ItemGrid.GetData() )

    def OnDefaultVarName( self, event ):
        "on default variant scenario"
        _index = self.__SceList.GetSelection()
        if _index not in [-1, None]:
            self.__casenode.SetOneCIVariantSceToDefault( _index )
    
            self.__ItemGrid.setCustable( self.__casenode.getOneCIVariantSceContent( _index ) )
        else:
            print "OnDefaultVarName CI", _index
    
    def OnChangeSce( self, event ):
        "on change Position of scenario."
        self.EnableItemCtrl( True )
        _index = self.__SceList.GetSelection()
        if _index not in [-1, None]:
            self.CISCEDesTxt.Enable( True )
            self.CISCEDesTxt.SetValue( self.__casenode.getOneCIVariantSceDes( _index ) )
            
            self.__ItemGrid.setCustable( self.__casenode.getOneCIVariantSceContent( _index ) )
            
            _posinfo = self.__casenode.getOneCIVariantScePos( _index )
            self.CISce_Ctrl[2][2][-1].Enable( True )
            self.CISce_Ctrl[0][0][-1].SetValue( str( _posinfo[0] ) )
            self.CISce_Ctrl[0][1][-1].SetValue( str( _posinfo[1] ) )
            self.CISce_Ctrl[1][0][-1].SetValue( str( _posinfo[2] ) )
            
    def OnEditCISceDes( self, event ):
        "On Edit CI Position of Scenario Description"
        _index = self.__SceList.GetSelection()
        if _index not in [-1, None]:
            self.__casenode.ModifyOneCIVariantSceDes( _index,
                                                      self.CISCEDesTxt.GetValue() )
        else:
            print "OnEditCISceDes error!"
    
        
    def createCtrls( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):   #_item = ['Type', 1, None, None ]
                if 0 == _item[1]:
                    _label, _txtctl = self.createNewText( _item[0] )
                    _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _txtctl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][2] = _label
                    list[_i][_j][3] = _txtctl
                elif 1 == _item[1]:
                    _label, _ctrl = self.createNewCombox( _item[0], _item[2] )
                    _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl
                elif 2 == _item[1]: 
                    _ctrl = self.createNewButton( _item[0] )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl                                                           
                    
            revbox.Add( _Hbox, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
        return revbox        
    def createNewText( self, label ):
        "create Text."
        label = wx.StaticText( self, -1, label, size = ( 50, -1 ) )
#        label.SetLabel()
        txtctrl = wx.TextCtrl( self, -1, '', size = ( 170, -1 ) )
#        txtctrl.GetString()
#        txtctrl.SetEditable()
        return label, txtctrl

    def createNewCombox( self, label, list ):
        "create new comboBox"
        label = wx.StaticText( self, -1, label, size = ( 50, -1 ) )
        _value = '' if 0 == len( list ) else list[0]
        ctrl = wx.ComboBox( self, -1, _value, size = ( 170, -1 ), choices = list, style = wx.CB_DROPDOWN )
#        ctrl.SetItems(items)
        return label, ctrl        
        
    def createNewButton( self, label ):
        "create new Button"
#        label = wx.StaticText( self, -1, label, size = ( 120, -1 ) )
        _ctrl = wx.Button( self, -1, label, size = ( 110, -1 ) )
        return _ctrl  
    
    def OnSelectNameValueChange( self, event ):
        "On Select Name Value Change"
        self.__ItemGrid.OnSelect( event )
        _value = self.__ItemGrid.GetSelectData()
        if None == _value:
            return
        self.CISceItem_Ctrl[0][0][-1].SetValue( _value[0] )
        self.CISceItem_Ctrl[0][1][-1].SetValue( _value[1] )
        self.CISceItem_Ctrl[1][0][-1].SetValue( _value[2] )
        self.CISceItem_Ctrl[2][2][-1].Enable( True )


class ZCSceConfigWizard( wiz.WizardPageSimple ):
    '''
    ZC scenario config Wizard
    '''
    
    #有几种类型：0：txt，1：combox，2：button
    #格式，[名字，类型，标签ref，控件ref]：button的标签ref为None
    AddSce_Ctrl = [[['Block ID', 0, None, None ], \
                    ['Abscissa', 0, None, None ]],
                   [['Delay', 0, None, None ]],
                   [['Add Sce', 2, None, None ], \
                    ['Del Sce', 2, None, None ],
                    ['Edit Sce', 2, None, None ]]]    

    AddNameValue_Ctrl = [[['LineSec', 1, [], None ], \
                          ['Index', 0, None, None ]],
                         [['Value', 0, None, None ]],
                         [['Add...', 2, None, None ], \
                          ['Del...', 2, None, None ],
                          ['Edit...', 2, None, None ],
                          ['Def...', 2, None, None ]]]   

    AddVariant_Ctrl = [[['LineSec', 1, [], None ], \
                        ['Index', 0, None, None ]], \
                       [['Type', 1, ['Block', 'SGL_PROTECTION_ZONE', \
                                     'SGL_SIGNAL', 'SGL_SIGNAL_BM_INIT', \
                                     'SGL_SIGNAL_OVERLAP', 'SGL_SIGNAL_OVERLAP_BM', \
                                     'SGL_PSD_ZONE'], None ],
                        ['Value', 0, None, None ]],
                       [['EQ_ID', 0, None, None ]],
                       [['Add Var', 2, None, None ], \
                        ['Del Var', 2, None, None ]]]       
    
    __HasLoadDataFlag = False #记录是否已经载入数据的标志
    def __init__( self, parent, title = None, size = wx.DefaultSize, pos = wx.DefaultPosition, CaseEditNode = None ):
#        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        wiz.WizardPageSimple.__init__( self, parent )
        self.sizer = makePageTitle( self, title ) 
           
        self.__casenode = CaseEditNode
#        #导入数据
#        self.__casenode.getZCVariantIni()
#        self.__casenode.getZCVariantSce()
        
        box = wx.BoxSizer( wx.VERTICAL )
        _box_variant = self.createCtrls( self.AddVariant_Ctrl )
        self.__VariantGrid = ShowGrid( self, [ 'Index', 'Value', 'Type', 'Equipment ID' ] )
        #更新linsec
#        self.AddVariant_Ctrl[0][0][-1].SetItems( self.__casenode.getLineSecList() )
##        print self.__casenode.getLineSecList()
#        self.AddVariant_Ctrl[0][0][-1].SetSelection( -1 )
        #更新变量
#        self.__VariantGrid.setCustable( self.__casenode.getZCVariantShowData( self.AddVariant_Ctrl[0][0][-1].GetValue() ) )
        box.Add( _box_variant, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        box.Add( self.__VariantGrid, 2, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        box1 = wx.BoxSizer( wx.VERTICAL )
        _box_sce = self.createCtrls( self.AddSce_Ctrl )
#        print 'getZCVariantSceShowData', self.__casenode.getZCVariantSceShowData()
        self.__SceList = wx.ListBox( self, -1, size = ( 100, 100 ), \
#                                    choices = self.__casenode.getZCVariantSceShowData(), \
                                    choices = [], \
                                    style = wx.LB_SINGLE )
        
        SetCusFont( self.__SceList, 12, Weight = wx.BOLD, Face = "Calibri" )
#        self.__SceList.SetSelection( -1 )
        
        box1.Add( _box_sce, 3, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        box1.Add( self.__SceList, 5, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        self.ZCSCEDesTxt = wx.TextCtrl( self, -1, '', size = ( 100, -1 ), style = wx.TE_MULTILINE )
        SetCusFont( self.ZCSCEDesTxt, 14, Weight = wx.BOLD, Face = "Calibri" )
        box1.Add( self.ZCSCEDesTxt, 2, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        box2 = wx.BoxSizer( wx.VERTICAL )
        _box_namevalue = self.createCtrls( self.AddNameValue_Ctrl )
#        self.AddNameValue_Ctrl[0][0][-1].SetItems( self.__casenode.getLineSecList() )
#        self.AddNameValue_Ctrl[0][0][-1].SetSelection( 0 )        
        self.__NameValueGrid = ShowGrid( self, [ 'Linsection', 'Index', 'Value'], OnSelectHandle = self.OnSelectNameValueChange )
#        self.__NameValueGrid.setCustable( self.__casenode.getZCVariantSceShowData() )
        box2.Add( _box_namevalue, 3, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        box2.Add( self.__NameValueGrid, 7, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )        
        
        _Framebox = wx.BoxSizer( wx.HORIZONTAL )
        _Framebox.Add( box, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box1, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box2, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        self.BindEvents()

        self.sizer.Add( _Framebox, 8, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.SetSizer( self.sizer )
        self.sizer.Fit( self )   

    def UpLoadData( self ):
        "upload data according to config"
        #导入数据
        if False == self.__HasLoadDataFlag:
            print "load data zc scenario!"
            self.__casenode.getZCVariantIni()
            self.__casenode.getZCVariantSce()
            self.__HasLoadDataFlag = True

        self.AddVariant_Ctrl[0][0][-1].SetItems( self.__casenode.getLineSecList() )
#        print self.__casenode.getLineSecList()
        self.AddVariant_Ctrl[0][0][-1].SetSelection( -1 )
        
        self.__SceList.SetItems( self.__casenode.getZCVariantSceShowData() )
        self.__SceList.SetSelection( -1 )

        self.AddNameValue_Ctrl[0][0][-1].SetItems( self.__casenode.getLineSecList() )
        self.AddNameValue_Ctrl[0][0][-1].SetSelection( 0 )    
        
        #初始化显示
        self.__VariantGrid.setCustable( [] )
        self.__NameValueGrid.setCustable( [] )
        
        #disable NameValueCtrl
        self.EnableNameValueCtrl( False )
        
        self.AddSce_Ctrl[2][2][-1].Enable( False )
        
        self.ZCSCEDesTxt.Enable( False )

        
    def EnableNameValueCtrl( self, enable ):       
        "enable name value ctrl"
        self.__NameValueGrid.Enable( enable )
        for _row in self.AddNameValue_Ctrl:
            for _item in _row:
                if ( True == enable ) and ( _item == self.AddNameValue_Ctrl[2][2] ):
                    pass
                else:
                    _item[-1].Enable( enable )
    
    def BindEvents( self ):
        "bind events"
        self.Bind( wx.EVT_COMBOBOX, self.OnLineSec1Change, self.AddVariant_Ctrl[0][0][-1] )
#        self.Bind( wx.EVT_COMBOBOX, self.OnLineSec2Change, self.AddNameValue_Ctrl[0][0][-1] )
        
        self.Bind( wx.EVT_BUTTON, self.OnAddVariant, self.AddVariant_Ctrl[3][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelVariant, self.AddVariant_Ctrl[3][1][-1] )
        
        self.Bind( wx.EVT_BUTTON, self.OnAddVarSce, self.AddSce_Ctrl[2][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelVarSce, self.AddSce_Ctrl[2][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnEditVarSce, self.AddSce_Ctrl[2][2][-1] )
            

        self.Bind( wx.EVT_BUTTON, self.OnAddVarName, self.AddNameValue_Ctrl[2][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelVarName, self.AddNameValue_Ctrl[2][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnEditVarName, self.AddNameValue_Ctrl[2][2][-1] ) 
        self.Bind( wx.EVT_BUTTON, self.OnDefaultVarName, self.AddNameValue_Ctrl[2][3][-1] )
        
        self.Bind( wx.EVT_LISTBOX, self.OnChangeSce, self.__SceList )
        
        self.Bind( wx.EVT_TEXT, self.OnEditZCSceDes, self.ZCSCEDesTxt )
        
    def OnEditZCSceDes( self, event ):
        "On Edit ZC Scenario Description"
        _index = self.__SceList.GetSelection()
        if _index not in [-1, None]:
            self.__casenode.ModifyOneZCVariantSceDes( _index,
                                                      self.ZCSCEDesTxt.GetValue() )
        else:
            print "OnEditZCSceDes error!"

    def OnLineSec1Change( self, event ):
        "on line Section1 change"
        _line = self.AddVariant_Ctrl[0][0][-1].GetValue()
        
        _list = self.__casenode.getZCVariantShowData( _line )
        
        self.__VariantGrid.setCustable( _list )
        
    def OnAddVariant( self, event ):
        "on add variant."
        _line = self.AddVariant_Ctrl[0][0][-1].GetValue()
        _index = self.AddVariant_Ctrl[0][1][-1].GetValue()
        _type = self.AddVariant_Ctrl[1][0][-1].GetValue()
        _Value = self.AddVariant_Ctrl[1][1][-1].GetValue()
        _EqId = self.AddVariant_Ctrl[2][0][-1].GetValue()
        
        self.__casenode.AddOneZCVariant( _line, [_index, _Value , _type, _EqId] )
        self.__VariantGrid.setCustable( self.__casenode.getZCVariantShowData( self.AddVariant_Ctrl[0][0][-1].GetValue() ) )
    
    def OnDelVariant( self, event ):
        "on delete variant"
        _line = self.AddVariant_Ctrl[0][0][-1].GetValue()
        if None == self.__VariantGrid.GetSelection():
            return
        self.__casenode.DeleteOneZCVariant( _line, self.__VariantGrid.GetData()[self.__VariantGrid.GetSelection()] )
        self.__VariantGrid.setCustable( self.__casenode.getZCVariantShowData( self.AddVariant_Ctrl[0][0][-1].GetValue() ) )
        self.__VariantGrid.SetSelection( None ) #只能删除一次
        
    def OnAddVarSce( self, event ):
        "on add variant scenario"
        self.EnableNameValueCtrl( False )
        self.AddSce_Ctrl[2][2][-1].Enable( False )
        _block_id = self.AddSce_Ctrl[0][0][-1].GetValue()
        _abs = self.AddSce_Ctrl[0][1][-1].GetValue()
        _delay = self.AddSce_Ctrl[1][0][-1].GetValue()
        self.__casenode.AddOneZCVariantSce( [_block_id, _abs, _delay, []] )
        self.__SceList.SetItems( self.__casenode.getZCVariantSceShowData() )
        self.ZCSCEDesTxt.Enable( False )
        
    def OnDelVarSce( self, event ):
        "on delete variant scenario."
        self.EnableNameValueCtrl( False )
        self.AddSce_Ctrl[2][2][-1].Enable( False )
        _index = self.__SceList.GetSelection()
        if _index in [None, -1]:
            return
        self.__casenode.DeleteOneZCVariantSce( _index )
        self.__SceList.SetItems( self.__casenode.getZCVariantSceShowData() )
        self.__NameValueGrid.setCustable( [] )
        self.ZCSCEDesTxt.Enable( False )

    def OnEditVarSce( self, event ):
        "On Edit Variant scanario"
        _index = self.__SceList.GetSelection()
        _block_id = self.AddSce_Ctrl[0][0][-1].GetValue()
        _abs = self.AddSce_Ctrl[0][1][-1].GetValue()
        _delay = self.AddSce_Ctrl[1][0][-1].GetValue()        
        self.__casenode.ModifyOneZCVariantScePos( _index, [_block_id, _abs, _delay] )
        self.__SceList.SetItems( self.__casenode.getZCVariantSceShowData() )
        self.__SceList.SetSelection( _index )
        
    def OnAddVarName( self, event ):
        "on add var name"
        self.AddNameValue_Ctrl[2][2][-1].Enable( False )
        _line = self.AddNameValue_Ctrl[0][0][-1].GetValue()
        _index = self.AddNameValue_Ctrl[0][1][-1].GetValue()
        _value = self.AddNameValue_Ctrl[1][0][-1].GetValue()
        self.__NameValueGrid.AddOneData( [_line, _index, _value] )
        
        self.__casenode.ModifyOneZCVariantSce( self.__SceList.GetSelection(), \
                                              self.__NameValueGrid.GetData() )
    
    def OnDelVarName( self, event ):
        "on delete var name."
        self.AddNameValue_Ctrl[2][2][-1].Enable( False )
        _Index = self.__NameValueGrid.GetSelection()
        if None != _Index:
            self.__NameValueGrid.DelOneData( _Index )
        
        self.__casenode.ModifyOneZCVariantSce( self.__SceList.GetSelection(), \
                                              self.__NameValueGrid.GetData() )
    
    def OnEditVarName( self, event ):
        "On Edit var name."
        _line = self.AddNameValue_Ctrl[0][0][-1].GetValue()
        _index = self.AddNameValue_Ctrl[0][1][-1].GetValue()
        _value = self.AddNameValue_Ctrl[1][0][-1].GetValue()
        self.__NameValueGrid.EditOneData( [_line, _index, _value] )
        
        self.__casenode.ModifyOneZCVariantSce( self.__SceList.GetSelection(), \
                                              self.__NameValueGrid.GetData() )
    
    
    def OnDefaultVarName( self, event ):
        "on default variant scenario"
        _index = self.__SceList.GetSelection()
        if _index not in [-1, None]:
            self.__casenode.SetOneZCVariantSceToDefault( _index )
    
            self.__NameValueGrid.setCustable( self.__casenode.getOneZCVariantSceContent( _index ) )
        else:
            print "OnDefaultVarName", _index
    
    def OnSelectNameValueChange( self, event ):
        "On Select Name Value Change"
        self.__NameValueGrid.OnSelect( event )
        _value = self.__NameValueGrid.GetSelectData()
        if None == _value:
            return
        self.AddNameValue_Ctrl[0][0][-1].SetValue( _value[0] )
        self.AddNameValue_Ctrl[0][1][-1].SetValue( _value[1] )
        self.AddNameValue_Ctrl[1][0][-1].SetValue( _value[2] )
        self.AddNameValue_Ctrl[2][2][-1].Enable( True )
    
    def OnChangeSce( self, event ):
        "on change scenario."
        self.EnableNameValueCtrl( True )
        _index = self.__SceList.GetSelection()
        if _index not in [-1, None]:
            self.ZCSCEDesTxt.Enable( True )
            self.ZCSCEDesTxt.SetValue( self.__casenode.getOneZCVariantSceDes( _index ) )
            
            self.__NameValueGrid.setCustable( self.__casenode.getOneZCVariantSceContent( _index ) )
            
            _posinfo = self.__casenode.getOneZCVariantScePos( _index )
            self.AddSce_Ctrl[2][2][-1].Enable( True )
            self.AddSce_Ctrl[0][0][-1].SetValue( str( _posinfo[0] ) )
            self.AddSce_Ctrl[0][1][-1].SetValue( str( _posinfo[1] ) )
            self.AddSce_Ctrl[1][0][-1].SetValue( str( _posinfo[2] ) )
        
    
    def createNewText( self, label ):
        "create Text."
        label = wx.StaticText( self, -1, label, size = ( 50, -1 ) )
#        label.SetLabel()
        txtctrl = wx.TextCtrl( self, -1, '', size = ( 70, -1 ) )
#        txtctrl.GetString()
#        txtctrl.SetEditable()
        return label, txtctrl

    def createNewCombox( self, label, list ):
        "create new comboBox"
        label = wx.StaticText( self, -1, label, size = ( 50, -1 ) )
        _value = '' if 0 == len( list ) else list[0]
        ctrl = wx.ComboBox( self, -1, _value, size = ( 70, -1 ), choices = list, style = wx.CB_DROPDOWN )
#        ctrl.SetItems(items)
        return label, ctrl        
        
    def createNewButton( self, label ):
        "create new comboBox"
#        label = wx.StaticText( self, -1, label, size = ( 120, -1 ) )
        _ctrl = wx.Button( self, -1, label, size = ( 60, -1 ) )
        return _ctrl  
        
    def createCtrls( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):   #_item = ['Type', 1, None, None ]
                if 0 == _item[1]:
                    _label, _txtctl = self.createNewText( _item[0] )
                    _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _txtctl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][2] = _label
                    list[_i][_j][3] = _txtctl
                elif 1 == _item[1]:
                    _label, _ctrl = self.createNewCombox( _item[0], _item[2] )
                    _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl
                elif 2 == _item[1]: 
                    _ctrl = self.createNewButton( _item[0] )
                    _Hbox.Add( _ctrl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl                                                           
                    
            revbox.Add( _Hbox, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
        return revbox        
    
    
    def createTexts( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):
                _label, _txtctl = self.createNewText( _item[0] )
                _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
                _Hbox.Add( _txtctl, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
                list[_i][_j][1] = _txtctl
            revbox.Add( _Hbox, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        return revbox
    
    def EndThisPanel( self ):
        "end this panel"


class BeaconConfigWizard( wiz.WizardPageSimple ):
    '''
    Beacon config Wizard
    '''
    
    Value_dic = {'False':'0', 'True':'1', 'Right':'', 'Wrong':'0'}
    
    #有几种类型：0：txt，1：combox，2：button
    #格式，[名字，类型，标签ref，控件ref]：button的标签ref为None
    Add_BeaconSce_Ctrl = [[['Beacon ID', 0, None, None ],
                           ['Beacon Name', 0, None, None ],
                           ['Disable', 1, ['False', 'True'], None ]],
                          [['Msg Beacon ID', 0, None, None ],
                           ['Use Default Msg', 1, ['False', 'True'], None ],
                           ['Available', 1, ['False', 'True'], None ]],
                          [['Cal CheckSum', 1, ['Right', 'Wrong'], None ],
                           ['Deta Distance', 0, None, None ]],
                          [['Add One Sce', 2, None, None ], \
                           ['Del One Sce', 2, None, None ],
                           ['Edit One Sce', 2, None, None ]]]    

    __HasLoadDataFlag = False #记录是否已经载入数据的标志
    __MapPath = None #记录地图的路径，有修改则要重新加载
    def __init__( self, parent, title = None, size = wx.DefaultSize, pos = wx.DefaultPosition, CaseEditNode = None ):
#        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        wiz.WizardPageSimple.__init__( self, parent )
        self.sizer = makePageTitle( self, title )
            
        self.__casenode = CaseEditNode
#        #导入数据
#        self.__casenode.getBMBeaconDic()
#        self.__casenode.getBeaconMsgSetting()
        
        #创建BmBeaconlist
#        _beaconlist, _clientdata = self.__casenode.getBMBeaconShowData()
        label = wx.StaticText( self, -1, "Beacon List:", size = ( 120, -1 ) )
        self.__BeaconsList = wx.ListBox( self, -1, size = ( 100, 100 ), \
#                                        choices = _beaconlist,
                                        choices = [],
                                        style = wx.LB_SINGLE )
        self.__BMVarDefaultBtn = wx.Button( self, -1, "Default Variant", size = ( 120, -1 ) )
        SetCusFont( self.__BeaconsList, 10, Weight = wx.BOLD, Face = "Calibri" )
#        for _i, _c in enumerate( _clientdata ):
#            self.__BeaconsList.SetClientData( _i, _c )
##            print self.__BeaconsList.GetClientData( _i )
#        self.__BeaconsList.SetSelection( -1 )
        
        box1 = wx.BoxSizer( wx.VERTICAL )
        box1.Add( label, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        box1.Add( self.__BeaconsList, 10, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        box1.Add( self.__BMVarDefaultBtn, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        label = wx.StaticText( self, -1, "Beacon Variants:", size = ( 120, -1 ) )
        self.__BMVariants = EditGrid( self,
                                      ['Index', 'Value', 'Description'],
                                      [False, True, True],
                                      self.BMVariantsChange )
        
        box2 = wx.BoxSizer( wx.VERTICAL )
        box2.Add( label, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        box2.Add( self.__BMVariants, 10, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        _box_Sce = self.createCtrls( self.Add_BeaconSce_Ctrl )
        
        
        self.__BeaconSecGrid = ShowGrid( self, ['ID', 'Name',
                                                'Disable', 'W_ID',
                                                'Default', 'Avail',
                                                'Check1', 'Check2',
                                                'D_Dis'],
                                        OnSelectHandle = self.OnBeaconGridSelectChange )
#        self.__BeaconSecGrid.setCustable( self.__casenode.getBeaconMsgSettingShowData() )

        box3 = wx.BoxSizer( wx.VERTICAL )
        box3.Add( _box_Sce, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        box3.Add( self.__BeaconSecGrid, 2, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        
        _Framebox = wx.BoxSizer( wx.HORIZONTAL )
        _Framebox.Add( box1, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box2, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box3, 3, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        self.BindEvents()
             
        self.sizer.Add( _Framebox, 8, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5 )
        
        self.SetSizer( self.sizer )
        self.sizer.Fit( self )          

    def UpLoadData( self ):
        "upload data according to config"
        #导入数据
        if self.__MapPath != self.__casenode.getMapPath():
            print "load new map!"
            self.__casenode.getBMBeaconDic()
            self.__MapPath = self.__casenode.getMapPath()

        if False == self.__HasLoadDataFlag:
            print "load beacon data!"
            self.__casenode.getBeaconMsgSetting()
            self.__HasLoadDataFlag = True

            
        _beaconlist, _clientdata = self.__casenode.getBMBeaconShowData()
        self.__BeaconsList.SetItems( _beaconlist )

        for _i, _c in enumerate( _clientdata ):
            self.__BeaconsList.SetClientData( _i, _c )
#            print self.__BeaconsList.GetClientData( _i )
        self.__BeaconsList.SetSelection( -1 )

        self.__BeaconSecGrid.setCustable( self.__casenode.getBeaconMsgSettingShowData() )
        #初始化beacon variant
        self.__BMVariants.setCustable( [] )
        self.__BMVariants.Enable( False )
        
        #Edit button disable
        self.Add_BeaconSce_Ctrl[3][2][-1].Enable( False )
    
    def OnBeaconGridSelectChange( self, event ):
        "On Beacon Grid Select Change"
        self.__BeaconSecGrid.OnSelect( event )
        _value = self.__BeaconSecGrid.GetSelectData()
        if None == _value:
            return
        self.Add_BeaconSce_Ctrl[3][2][-1].Enable( True )
        self.Add_BeaconSce_Ctrl[0][0][-1].SetValue( _value[0] )
        self.Add_BeaconSce_Ctrl[0][1][-1].SetValue( _value[1] )
        self.Add_BeaconSce_Ctrl[0][2][-1].SetValue( "False" if "1" != _value[2] else "True" )
        self.Add_BeaconSce_Ctrl[1][0][-1].SetValue( _value[3] )
        self.Add_BeaconSce_Ctrl[1][1][-1].SetValue( "False" if "1" != _value[4] else "True" )
        self.Add_BeaconSce_Ctrl[1][2][-1].SetValue( "False" if "1" != _value[5] else "True" )
        self.Add_BeaconSce_Ctrl[2][0][-1].SetValue( "Right" if "0" != _value[6] else "Wrong" )
        self.Add_BeaconSce_Ctrl[2][1][-1].SetValue( _value[8] )
    
    def BindEvents( self ):
        "bind events"
        self.Bind( wx.EVT_LISTBOX, self.OnBMSelectChange, self.__BeaconsList )
#        self.Bind( wx.EVT_COMBOBOX, self.OnLineSec2Change, self.AddNameValue_Ctrl[0][0][-1] )
        
        self.Bind( wx.EVT_BUTTON, self.OnAddSce, self.Add_BeaconSce_Ctrl[3][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelSce, self.Add_BeaconSce_Ctrl[3][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnEditSce, self.Add_BeaconSce_Ctrl[3][2][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDefaultBeacon, self.__BMVarDefaultBtn )
        
    def OnDefaultBeacon( self, event ):
        "on default beacon"
        self.__casenode.SetBMBeaconSetVarToDefault()
        
        _Index = self.__BeaconsList.GetSelection()
        if _Index in [wx.NOT_FOUND, None]:
            print "BMVariantsChange error:", _Index
            return
        
        _beaconId = self.__BeaconsList.GetClientData( _Index ) 
        self.__BMVariants.RefreshData( self.__casenode.getBMBeaconVariants( _beaconId ) )
    
    def BMVariantsChange( self, event ):
        "on BM Variants change"
#        print "on BM Variants change"
        _Index = self.__BeaconsList.GetSelection()
        if _Index in [wx.NOT_FOUND, None]:
            print "BMVariantsChange error:", _Index
            return
        
        _beaconId = self.__BeaconsList.GetClientData( _Index )    
        if False == self.__BMVariants.OnCellChange( event ):
#            print "on BM Variants change1212121"
            #不修改时维持原始值
            self.__BMVariants.RefreshData( self.__casenode.getBMBeaconVariants( _beaconId ) )
        else:
#            print '_Index', _Index
#            _beaconId = self.__BeaconsList.GetClientData( _Index )
#            print _beaconId
            #修改时则将数据传出
            _data = self.__BMVariants.GetData()
            self.__casenode.ModifyBMBeaconVariants( _beaconId, _data )
        
    def OnAddSce( self, event ):
        "on add scenario"
        _beacon_Id = self.Add_BeaconSce_Ctrl[0][0][-1].GetValue()
        _beacon_Name = self.Add_BeaconSce_Ctrl[0][1][-1].GetValue() 
        _Disable = self.Value_dic[self.Add_BeaconSce_Ctrl[0][2][-1].GetValue()] 
        _Msg_Beacon_ID = self.Add_BeaconSce_Ctrl[1][0][-1].GetValue()
        _Use_Default_Msg = self.Value_dic[self.Add_BeaconSce_Ctrl[1][1][-1].GetValue()]
        _Available = self.Value_dic[self.Add_BeaconSce_Ctrl[1][2][-1].GetValue()]
        
        _CheckSum1 = self.Value_dic[self.Add_BeaconSce_Ctrl[2][0][-1].GetValue()]
        _CheckSum2 = self.Value_dic[self.Add_BeaconSce_Ctrl[2][0][-1].GetValue()]
        _Deta_Distance = self.Add_BeaconSce_Ctrl[2][1][-1].GetValue()
        
        self.__casenode.AddOneBeaconMsgSetting( [_beacon_Id, _beacon_Name,
                                                _Disable, _Msg_Beacon_ID,
                                                _Use_Default_Msg, _Available,
                                                _CheckSum1, _CheckSum2,
                                                _Deta_Distance] )
        self.__BeaconSecGrid.setCustable( self.__casenode.getBeaconMsgSettingShowData() )
        
        self.Add_BeaconSce_Ctrl[3][2][-1].Enable( False )
    
    def OnEditSce( self, event ):
        "On Edit Scenario"
        if self.__BeaconSecGrid.GetSelection() not in [None, -1]: #要有选中才能开始编辑
            _beacon_Id = self.Add_BeaconSce_Ctrl[0][0][-1].GetValue()
            _beacon_Name = self.Add_BeaconSce_Ctrl[0][1][-1].GetValue() 
            _Disable = self.Value_dic[self.Add_BeaconSce_Ctrl[0][2][-1].GetValue()] 
            _Msg_Beacon_ID = self.Add_BeaconSce_Ctrl[1][0][-1].GetValue()
            _Use_Default_Msg = self.Value_dic[self.Add_BeaconSce_Ctrl[1][1][-1].GetValue()]
            _Available = self.Value_dic[self.Add_BeaconSce_Ctrl[1][2][-1].GetValue()]
            
            _CheckSum1 = self.Value_dic[self.Add_BeaconSce_Ctrl[2][0][-1].GetValue()]
            _CheckSum2 = self.Value_dic[self.Add_BeaconSce_Ctrl[2][0][-1].GetValue()]
            _Deta_Distance = self.Add_BeaconSce_Ctrl[2][1][-1].GetValue()
            
            _last_beacon_Id = self.__BeaconSecGrid.GetSelectData()[0]
            
            self.__BeaconSecGrid.EditOneData( [_beacon_Id, _beacon_Name,
                                              _Disable, _Msg_Beacon_ID,
                                              _Use_Default_Msg, _Available,
                                              _CheckSum1, _CheckSum2,
                                              _Deta_Distance] )
            
            if _last_beacon_Id != _beacon_Id:#不相等的时候要删除这个
                self.__casenode.DeleteOneBeaconMsgSetting( [_last_beacon_Id, _beacon_Name,
                                                           _Disable, _Msg_Beacon_ID,
                                                           _Use_Default_Msg, _Available,
                                                           _CheckSum1, _CheckSum2,
                                                           _Deta_Distance] )
            #添加新的
            self.__casenode.AddOneBeaconMsgSetting( [_beacon_Id, _beacon_Name,
                                                    _Disable, _Msg_Beacon_ID,
                                                    _Use_Default_Msg, _Available,
                                                    _CheckSum1, _CheckSum2,
                                                    _Deta_Distance] )        
        
    def OnDelSce( self, event ):
        "on delete scenario"
        _Index = self.__BeaconSecGrid.GetSelection()
        if _Index not in [-1, None]:
            _content = self.__BeaconSecGrid.GetData()[_Index]
            self.__casenode.DeleteOneBeaconMsgSetting( _content )
            self.__BeaconSecGrid.setCustable( self.__casenode.getBeaconMsgSettingShowData() )
            self.Add_BeaconSce_Ctrl[3][2][-1].Enable( False )
        
    def OnBMSelectChange( self, event ):
        "on bm select change"
#        _oldIndex = event.GetOldSelection()
#        _newIndex = event.GetSelection()
#        if _oldIndex != -1:
#            _beaconId = self.__BeaconsList.GetClientData(_oldIndex)
#            _data = self.__BMVariants.GetData()
#            self.__casenode.ModifyBMBeaconVariants(_beaconId, _data)
        _newIndex = self.__BeaconsList.GetSelection()
        if _newIndex != wx.NOT_FOUND:
#            print _newIndex
            _beaconId = self.__BeaconsList.GetClientData( _newIndex )
            _data = self.__casenode.getBMBeaconVariants( _beaconId )
            self.__BMVariants.setCustable( _data )
            self.__BMVariants.AutoSizeColumns()
            self.__BMVariants.Enable( True )

    def EndThisPanel( self ):
        "end this panel"
        #用于处理本panel结束时的相关操作包括保存数据等
        _selectIndex = self.__BeaconsList.GetSelection()
        if _selectIndex != -1:
            _beaconId = self.__BeaconsList.GetClientData( _selectIndex )
            _data = self.__BMVariants.GetData()
            self.__casenode.ModifyBMBeaconVariants( _beaconId, _data )        
    
    
    
    def createNewText( self, label ):
        "create Text."
        label = wx.StaticText( self, -1, label, size = ( 60, -1 ) )
#        label.SetLabel()
        txtctrl = wx.TextCtrl( self, -1, '', size = ( 80, -1 ) )
#        txtctrl.GetString()
#        txtctrl.SetEditable()
        return label, txtctrl

    def createNewCombox( self, label, list ):
        "create new comboBox"
        label = wx.StaticText( self, -1, label, size = ( 60, -1 ) )
        _value = '' if 0 == len( list ) else list[0]
        ctrl = wx.ComboBox( self, -1, _value, size = ( 80, -1 ), choices = list, style = wx.CB_DROPDOWN )
        
#        ctrl = wx.ComboBox( self, -1, list[0], size = ( 100, -1 ), choices = list, style = wx.CB_DROPDOWN )
#        ctrl.SetItems(items)
        return label, ctrl        
        
    def createNewButton( self, label ):
        "create new comboBox"
#        label = wx.StaticText( self, -1, label, size = ( 120, -1 ) )
        _ctrl = wx.Button( self, -1, label, size = ( 120, -1 ) )
        return _ctrl  
        
    def createCtrls( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):   #_item = ['Type', 1, None, None ]
                if 0 == _item[1]:
                    _label, _txtctl = self.createNewText( _item[0] )
                    _Hbox.Add( _label, 1, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _txtctl, 1, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][2] = _label
                    list[_i][_j][3] = _txtctl
                elif 1 == _item[1]:
                    _label, _ctrl = self.createNewCombox( _item[0], _item[2] )
                    _Hbox.Add( _label, 1, wx.ALIGN_LEFT | wx.ALL, 2 )
                    _Hbox.Add( _ctrl, 1, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl
                elif 2 == _item[1]: 
                    _ctrl = self.createNewButton( _item[0] )
                    _Hbox.Add( _ctrl, 1, wx.ALIGN_LEFT | wx.ALL, 2 )
                    list[_i][_j][3] = _ctrl                                                           
                    
            revbox.Add( _Hbox, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
        return revbox        
    
    
    def createTexts( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):
                _label, _txtctl = self.createNewText( _item[0] )
                _Hbox.Add( _label, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
                _Hbox.Add( _txtctl, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
                list[_i][_j][1] = _txtctl
            revbox.Add( _Hbox, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        return revbox



class ViomTSRConfigWizard( wiz.WizardPageSimple ):
    '''
    VIOM and TSR Config Wizard
    '''
    
    #有几种类型：0：txt，1：combox，2：button
    #格式，[名字，类型，标签ref，控件ref]：button的标签ref为None
    Add_TSR_Ctrl = [[['TSR_Speed', 0, None, None ]],
                    [['First_Block_ID', 0, None, None ]],
                    [['Start_Abscissa_On_First_Block', 0, None, None ]],
                    [['Number_Of_Intermediate_Blocks', 0, None, None ]],
                    [['Intermediate_Block_ID', 0, None, None ]],
                    [['Last_Block_ID', 0, None, None ]],
                    [['End_Abscissa_On_Last_Block', 0, None, None ]],
                    [['Edit TSR', 2, None, None ], ['Add TSR', 2, None, None ], ['Del TSR', 2, None, None ]]]    

    __HasLoadDataFlag = False #记录是否已经载入数据的标志
    def __init__( self, parent, title = None, size = wx.DefaultSize, pos = wx.DefaultPosition, CaseEditNode = None ):
#        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        wiz.WizardPageSimple.__init__( self, parent )
        self.sizer = makePageTitle( self, title )
            
        self.__casenode = CaseEditNode
#        #导入数据
#        self.__casenode.getVIOMSetting()
#        self.__casenode.getTSRSetting()
        
        #创建viom comboBox
        self.__viom_combo = wx.ComboBox( self, -1, 'viom_vital_in', \
                                        size = ( 150, -1 ), \
                                        choices = ['viom_vital_in', 'viom_vital_out'],
                                        style = wx.CB_DROPDOWN )
        self.__viom_combo.SetSelection( -1 )
        self.__viom_Grid = EditGrid( self, ['VIOMType', 'Name' , 'Index'],
                                    [False, False, True], self.VIOMIndexChange )
#        self.__viom_Grid.setCustable( self.__casenode.getVIOMSettingShowData( 0 ) )
        
        box1 = wx.BoxSizer( wx.VERTICAL )
        box1.Add( self.__viom_combo, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box1.Add( self.__viom_Grid, 10, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        label = wx.StaticText( self, -1, "TSR List:", size = ( 50, -1 ) )
        self.__TSR_List = wx.ListBox( self, -1, size = ( 50, 100 ), \
#                                     choices = self.__casenode.getTSRSettingIndex(),
                                      choices = [],
                                      style = wx.LB_SINGLE )
        SetCusFont( self.__TSR_List, 12, Weight = wx.BOLD, Face = "Calibri" )
#        self.__TSR_List.SetSelection( -1 )
        box2 = wx.BoxSizer( wx.VERTICAL )
        box2.Add( label, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box2.Add( self.__TSR_List, 10, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        box3 = wx.BoxSizer( wx.VERTICAL )        
        _box_TSR = self.createCtrls( self.Add_TSR_Ctrl )
        self.TSRDesTxt = wx.TextCtrl( self, -1, '', size = ( 100, -1 ), style = wx.TE_MULTILINE )
        SetCusFont( self.TSRDesTxt, 14, Weight = wx.BOLD, Face = "Calibri" )
        box3.Add( _box_TSR, 5, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box3.Add( self.TSRDesTxt , 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        _Framebox = wx.BoxSizer( wx.HORIZONTAL )
        _Framebox.Add( box1, 5, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box2, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box3, 6, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.BindEvents()
        
        self.sizer.Add( _Framebox, 8, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.SetSizer( self.sizer )
        self.sizer.Fit( self )          

    def UpLoadData( self ):
        "upload data according to config"
        #导入数据
        if False == self.__HasLoadDataFlag:
            print "load viom tsr data!"
            self.__casenode.getVIOMSetting()
            self.__casenode.getTSRSetting()
            self.__HasLoadDataFlag = True
        
        self.__TSR_List.SetItems( self.__casenode.getTSRSettingIndex() )                
        self.__TSR_List.SetSelection( -1 )
        self.TSRDesTxt.Enable( False )
        
    def BindEvents( self ):
        "bind events"
        self.Bind( wx.EVT_COMBOBOX, self.OnViomComboChange, self.__viom_combo )
        self.Bind( wx.EVT_LISTBOX, self.OnTSRListChange, self.__TSR_List )
        
        self.Bind( wx.EVT_BUTTON, self.OnEditTSR, self.Add_TSR_Ctrl[7][0][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnAddTSR, self.Add_TSR_Ctrl[7][1][-1] )
        self.Bind( wx.EVT_BUTTON, self.OnDelTSR, self.Add_TSR_Ctrl[7][2][-1] )
        self.Bind( wx.EVT_TEXT, self.OnEditTSRDes, self.TSRDesTxt )
    
    def OnEditTSRDes( self, event ):
        "On Edit TSR description"
        _index = self.__TSR_List.GetSelection()
        if _index not in [-1, None]:
            self.__casenode.ModifyTSRSettingDes( self.__TSR_List.GetString( _index ),
                                                 self.TSRDesTxt.GetValue() )
        else:
            print "OnEditTSDes error!"
    
    def OnDelTSR( self, event ):
        "on delete TSR"
        _index = self.__TSR_List.GetString( self.__TSR_List.GetSelection() )
        self.__casenode.deleteTSRSetting( _index )
        
        self.__TSR_List.SetItems( self.__casenode.getTSRSettingIndex() ) 
        self.TSRDesTxt.Enable( False )
        
    
    def OnEditTSR( self, event ):
        "on edit tsr"
        _index = self.__TSR_List.GetString( self.__TSR_List.GetSelection() )
        
        _Tsr_Speed = int( self.Add_TSR_Ctrl[0][0][-1].GetValue() )
        _first_block_id_of_tsr = int( self.Add_TSR_Ctrl[1][0][-1].GetValue() ) 
        _start_abs_on_first_block_of_tsr = int( self.Add_TSR_Ctrl[2][0][-1].GetValue() )
        _Number_Of_Intermediate_Blocks_Of_TSR = int( self.Add_TSR_Ctrl[3][0][-1].GetValue() )
        try:
            _Intermediate_Block_ID_Of_TSR = [int( _i ) for _i in self.Add_TSR_Ctrl[4][0][-1].GetValue().strip().split( ',' )]
        except ValueError, e:
            _Intermediate_Block_ID_Of_TSR = [] 
        _Last_Block_ID_Of_TSR = int( self.Add_TSR_Ctrl[5][0][-1].GetValue() )
        _End_Abscissa_On_Last_Block_Of_TSR = int( self.Add_TSR_Ctrl[6][0][-1].GetValue() )
        
        self.__casenode.ModifyTSRSetting( _index,
                                         [_Tsr_Speed,
                                          _first_block_id_of_tsr,
                                          _start_abs_on_first_block_of_tsr,
                                          _Number_Of_Intermediate_Blocks_Of_TSR,
                                          _Intermediate_Block_ID_Of_TSR,
                                          _Last_Block_ID_Of_TSR,
                                          _End_Abscissa_On_Last_Block_Of_TSR] )
    
    def OnAddTSR( self, event ): 
        "On add TSR"
        _Tsr_Speed = int( self.Add_TSR_Ctrl[0][0][-1].GetValue() )
        _first_block_id_of_tsr = int( self.Add_TSR_Ctrl[1][0][-1].GetValue() ) 
        _start_abs_on_first_block_of_tsr = int( self.Add_TSR_Ctrl[2][0][-1].GetValue() )
        _Number_Of_Intermediate_Blocks_Of_TSR = int( self.Add_TSR_Ctrl[3][0][-1].GetValue() )
        try:
            _Intermediate_Block_ID_Of_TSR = [int( _i ) for _i in self.Add_TSR_Ctrl[4][0][-1].GetValue().strip().split( ',' )]
        except ValueError, e:
            _Intermediate_Block_ID_Of_TSR = []
        _Last_Block_ID_Of_TSR = int( self.Add_TSR_Ctrl[5][0][-1].GetValue() )
        _End_Abscissa_On_Last_Block_Of_TSR = int( self.Add_TSR_Ctrl[6][0][-1].GetValue() )
        
        self.__casenode.AddTSRSetting( [_Tsr_Speed,
                                        _first_block_id_of_tsr,
                                        _start_abs_on_first_block_of_tsr,
                                        _Number_Of_Intermediate_Blocks_Of_TSR,
                                        _Intermediate_Block_ID_Of_TSR,
                                        _Last_Block_ID_Of_TSR,
                                        _End_Abscissa_On_Last_Block_Of_TSR] )   
        
        self.__TSR_List.Append( str( len( self.__casenode.getTSRSettingIndex() ) ) )       
        self.__TSR_List.SetSelection( len( self.__casenode.getTSRSettingIndex() ) - 1 )
        self.TSRDesTxt.Enable( True )
        _index = self.__TSR_List.GetString( self.__TSR_List.GetSelection() )
        self.TSRDesTxt.SetValue( self.__casenode.getOneTSRSettingDes( _index ) )
        
    def VIOMIndexChange( self, event ):
        "viom index change"
        _type = self.__viom_combo.GetValue()
        if False == self.__viom_Grid.OnCellChange( event ):
            if _type == 'viom_vital_in':
                self.__viom_Grid.RefreshData( self.__casenode.getVIOMSettingShowData( 0 ) )
            elif _type == 'viom_vital_out':
                self.__viom_Grid.RefreshData( self.__casenode.getVIOMSettingShowData( 1 ) )     
        else:
            _data = self.__viom_Grid.GetData()
            if _type == 'viom_vital_in':
                for _d in _data:  #_d:['VIOMType', 'Name' , 'Index']
                    self.__casenode.ModifyVIOMSetting( 0, _d[1], int( _d[2] ) )
            elif _type == 'viom_vital_out':
                for _d in _data:
                    self.__casenode.ModifyVIOMSetting( 1, _d[1], int( _d[2] ) )
        
                
    def OnViomComboChange( self, event ):
        "on add scenario"
        _type = self.__viom_combo.GetValue()
#        print 'OnViomComboChange', _type
        if 'viom_vital_in' == _type:
            self.__viom_Grid.setCustable( self.__casenode.getVIOMSettingShowData( 0 ) )
        elif 'viom_vital_out' == _type:
            self.__viom_Grid.setCustable( self.__casenode.getVIOMSettingShowData( 1 ) )
            
    def OnTSRListChange( self, event ):
        "on tsr list change"
        try:
            _index = self.__TSR_List.GetString( self.__TSR_List.GetSelection() )
            
            _datalist = self.__casenode.getOneTSRSetting( _index )
            
            self.Add_TSR_Ctrl[0][0][-1].SetValue( str( _datalist[0] ) )
            self.Add_TSR_Ctrl[1][0][-1].SetValue( str( _datalist[1] ) )
            self.Add_TSR_Ctrl[2][0][-1].SetValue( str( _datalist[2] ) )
            self.Add_TSR_Ctrl[3][0][-1].SetValue( str( _datalist[3] ) )
            self.Add_TSR_Ctrl[4][0][-1].SetValue( repr( _datalist[4] )[1:-1] )
            self.Add_TSR_Ctrl[5][0][-1].SetValue( str( _datalist[5] ) )
            self.Add_TSR_Ctrl[6][0][-1].SetValue( str( _datalist[6] ) )
            self.TSRDesTxt.Enable( True )
            self.TSRDesTxt.SetValue( self.__casenode.getOneTSRSettingDes( _index ) )
                
        except wx._core.PyAssertionError, e:
            print 'OnTSRListChange', e, self.__TSR_List.GetSelection()
    
    def EndThisPanel( self ):
        "end this panel"
        #用于处理本panel结束时的相关操作包括保存数据等
        return True
    
    
    def createNewText( self, label ):
        "create Text."
        label = wx.StaticText( self, -1, label, size = ( 180, -1 ) )
#        label.SetLabel()
        txtctrl = wx.TextCtrl( self, -1, '', size = ( 140, -1 ) )
#        txtctrl.SetValue()
#        txtctrl.GetString()
#        txtctrl.SetEditable()
        return label, txtctrl

    def createNewCombox( self, label, list ):
        "create new comboBox"
        label = wx.StaticText( self, -1, label, size = ( 200, -1 ) )
        _value = '' if 0 == len( list ) else list[0]
        ctrl = wx.ComboBox( self, -1, _value, size = ( 100, -1 ), choices = list, style = wx.CB_DROPDOWN )
        
#        ctrl = wx.ComboBox( self, -1, list[0], size = ( 100, -1 ), choices = list, style = wx.CB_DROPDOWN )
#        ctrl.SetItems(items)
        return label, ctrl        
        
    def createNewButton( self, label ):
        "create new comboBox"
#        label = wx.StaticText( self, -1, label, size = ( 120, -1 ) )
        _ctrl = wx.Button( self, -1, label, size = ( 120, -1 ) )
        return _ctrl  
        
    def createCtrls( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):   #_item = ['Type', 1, None, None ]
                if 0 == _item[1]:
                    _label, _txtctl = self.createNewText( _item[0] )
                    _Hbox.Add( _label, 1, wx.ALIGN_BOTTOM | wx.ALL, 5 )
                    _Hbox.Add( _txtctl, 1, wx.ALIGN_BOTTOM | wx.ALL, 5 )
                    list[_i][_j][2] = _label
                    list[_i][_j][3] = _txtctl
                elif 1 == _item[1]:
                    _label, _ctrl = self.createNewCombox( _item[0], _item[2] )
                    _Hbox.Add( _label, 1, wx.ALIGN_BOTTOM | wx.ALL, 5 )
                    _Hbox.Add( _ctrl, 1, wx.ALIGN_BOTTOM | wx.ALL, 5 )
                    list[_i][_j][3] = _ctrl
                elif 2 == _item[1]: 
                    _ctrl = self.createNewButton( _item[0] )
                    _Hbox.Add( _ctrl, 1, wx.ALIGN_BOTTOM | wx.ALL, 5 )
                    list[_i][_j][3] = _ctrl                                                           
                    
            revbox.Add( _Hbox, 0, wx.ALIGN_BOTTOM | wx.ALL, 5 )
        return revbox        
    
    
    def createTexts( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):
                _label, _txtctl = self.createNewText( _item[0] )
                _Hbox.Add( _label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                _Hbox.Add( _txtctl, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                list[_i][_j][1] = _txtctl
            revbox.Add( _Hbox, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        return revbox


class ShowStatusPanel( wx.Panel ):
    '''
    show status panel
    '''
    showData_Left = [[['Case Version', None], ['Case label', None], [ 'Case  Step', None]],
                     [['ATPLoophour', None], ['InhibitEmergencyBrake', None], ['EmergencyBrakeCause', None]],
                     [['LocalizationState', None], [ 'LocFaultType', None], ['TrainFrontEnd', None]],
                     [['TrainLocationEnd1.ExtBlock', None], ['TrainLocationEnd2.ExtBlock', None], ['RealLocation.ExtBlock', None]],
                     [['TrainLocationEnd1.ExtAbscissa', None], ['TrainLocationEnd2.ExtAbscissa', None], ['RealLocation.ExtAbscissa', None]] ]
    
    showData_Down = [[['ExistOtherCCsynchroReport', None], ['ExistNonVitalRequest', None], ['ExistEOAreport', None], ['ExistVariantReport', None]],
                     [['ExistVersionAuthReport', None], ['ExistDateSynchroReport', None], ['ExistTSRdownloadContent', None], ['ExistLCmessage', None]],
                     [['ExistCImessage[0]', None], ['ExistCImessage[1]', None]]]
    
    def __init__( self, parent, size = wx.DefaultSize, pos = wx.DefaultPosition ):
        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )

        #创建速度窗口
#        panel1 = wx.Panel( self, -1, style = wx.SUNKEN_BORDER, size = ( 350, 350 ) )
        self.SpeedWindow = self.createSpeedWindow( self )
        box1 = wx.BoxSizer( wx.HORIZONTAL )
        box1.Add( self.SpeedWindow, 1, wx.EXPAND | wx.CENTRE, 5 )
        
        #创建Text，用于显示车的位置和定位状态
        box_left = self.createShowTexts( self.showData_Left )
        box_Down = self.createShowTexts( self.showData_Down )
        
        box1.Add( box_left, 3, wx.ALIGN_CENTRE | wx.ALL, 5 )
        
        _Framebox = wx.BoxSizer( wx.VERTICAL )
        _Framebox.Add( box1, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        line = wx.StaticLine( self, -1, size = ( 20, -1 ), style = wx.LI_HORIZONTAL )
        _Framebox.Add( line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5 )        
        _Framebox.Add( box_Down, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                           
        self.SetSizer( _Framebox )
        _Framebox.Fit( self )        

    
    def createNewText( self, label ):
        "create Text."
        label = wx.StaticText( self, -1, label, size = ( 160, -1 ) )
        txtctrl = wx.TextCtrl( self, -1, '', size = ( 100, -1 ) )
        txtctrl.SetEditable( False )
        return label, txtctrl
    
    def createShowTexts( self, list ):
        "create Texts"
        revbox = wx.BoxSizer( wx.VERTICAL )
        for _i, _col in enumerate( list ):
            _Hbox = wx.BoxSizer( wx.HORIZONTAL )
            for _j, _item in enumerate( _col ):
                _label, _txtctl = self.createNewText( _item[0] )
                _Hbox.Add( _label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                _Hbox.Add( _txtctl, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
                list[_i][_j][1] = _txtctl
            revbox.Add( _Hbox, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        return revbox
        
        
    def createSpeedWindow( self, panel ):
        "create speed window"

        _SpeedWindow = SM.SpeedMeter( panel,
                                      agwStyle = SM.SM_DRAW_HAND | 
                                      SM.SM_DRAW_SECTORS | 
                                      SM.SM_DRAW_MIDDLE_TEXT | 
                                      SM.SM_DRAW_SECONDARY_TICKS )

        # Set The Region Of Existence Of SpeedMeter (Always In Radians!!!!)
        _SpeedWindow.SetAngleRange( -math.pi / 6, 7 * math.pi / 6 )

        # Create The Intervals That Will Divide Our SpeedMeter In Sectors        
        intervals = range( 0, 201, 20 )
        _SpeedWindow.SetIntervals( intervals )

        # Assign The Same Colours To All Sectors (We Simulate A Car Control For Speed)
        # Usually This Is Black
        colours = [wx.BLACK] * 10
        _SpeedWindow.SetIntervalColours( colours )

        # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
        ticks = [str( interval ) for interval in intervals]
        _SpeedWindow.SetTicks( ticks )
        # Set The Ticks/Tick Markers Colour
        _SpeedWindow.SetTicksColour( wx.WHITE )
        # We Want To Draw 5 Secondary Ticks Between The Principal Ticks
        _SpeedWindow.SetNumberOfSecondaryTicks( 5 )

        # Set The Font For The Ticks Markers
        _SpeedWindow.SetTicksFont( wx.Font( 7, wx.SWISS, wx.NORMAL, wx.NORMAL ) )
                                       
        # Set The Text In The Center Of SpeedMeter
        _SpeedWindow.SetMiddleText( "0 Km/h" )
        # Assign The Colour To The Center Text
        _SpeedWindow.SetMiddleTextColour( wx.Colour( 255, 255, 0 ) )
        # Assign A Font To The Center Text
        _SpeedWindow.SetMiddleTextFont( wx.Font( 8, wx.SWISS, wx.NORMAL, wx.BOLD ) )

        # Set The Colour For The Hand Indicator
        _SpeedWindow.SetHandColour( wx.Colour( 255, 50, 0 ) )

        # Do Not Draw The External (Container) Arc. Drawing The External Arc May
        # Sometimes Create Uglier Controls. Try To Comment This Line And See It
        # For Yourself!
        _SpeedWindow.DrawExternalArc( False )        

        # Set The Current Value For The SpeedMeter
        _SpeedWindow.SetSpeedValue( 0 )
        
        return _SpeedWindow
    
        
    #--------------------------------------------------------
    #distance为100ms运行的距离，单位为mm
    #--------------------------------------------------------
    def setSpeedValue( self, distance ):
        "set speed value"
        #计算速度，单位为km/h
        _speed = abs( distance ) * 3.6 / 100
        self.SpeedWindow.SetSpeedValue( _speed )
        self.SpeedWindow.SetMiddleText( str( _speed ) + " Km/h" )
        
    #---------------------------------------------------------
    #@更新OMAP显示数据
    #---------------------------------------------------------
    def upDataOMAPInfo( self ):
        "updata OMAP information"
        _data = OMAPParser.getShowData( 'iTC_ATP_UP' ) #值采用iTC_ATP_UP的数据
        
        for _col in self.showData_Left:
            for _item in _col:
                if _item[0] not in ['Case Version', 'Case label', 'Case  Step', 'RealLocation.ExtBlock', 'RealLocation.ExtAbscissa']:
                    try:
                        _item[1].SetValue( _data[_item[0]] )
                    except:        
                        _item[1].SetValue( 'No data' )
                        
        for _col in self.showData_Down:
            for _item in _col:
                try:
                    _item[1].SetValue( _data[_item[0]] )
                except:        
                    _item[1].SetValue( 'No data' )    
   
    #--------------------------------------------------------
    #@更新用例相关数据
    #--------------------------------------------------------
    def upDataCaseInfo( self ):
        "updata case information."
        _info = None
        try:
            _info = CaseParser.getCurCaseInfo()
        except:
            _info = ( '', '', '' )
        for _col in self.showData_Left:
            for _item in _col:
                if _item[0] == 'Case Version':
                    _item[1].SetValue( _info[0] )
                elif _item[0] == 'Case label':
                    _item[1].SetValue( _info[1] )
                elif _item[0] == 'Case  Step':
                    _item[1].SetValue( _info[2] )
                else:
                    continue

    #--------------------------------------------------
    #@更新平台的实时数据
    #--------------------------------------------------
    def updataTPSInfo( self, TPSNode ):
        "updata tps information."
        try:
            _abs1 = TPSNode.loadDeviceDic['rs'].getDataValue( 'coordinates_1' )
            _abs2 = TPSNode.loadDeviceDic['rs'].getDataValue( 'coordinates_2' )
            _blockId, _Abs = TrainRoute.getBlockandAbs( _abs1,
                                                        Type = "Running" )
        except:
            _abs1 , _abs2, _blockId, _Abs = 0, 0, 0, 0
            
        for _col in self.showData_Left:
            for _item in _col:
                if _item[0] == 'RealLocation.ExtBlock':
                    _item[1].SetValue( str( _blockId ) )
                elif _item[0] == 'RealLocation.ExtAbscissa':
                    _item[1].SetValue( str( _Abs ) )
                else:
                    continue            
        self.setSpeedValue( _abs2 - _abs1 )


#------------------------------------------------------------------------------------------
#用于OMAP图形显示的Frame
#------------------------------------------------------------------------------------------    
class ShowOMAPFigureDiag( wx.Dialog ):
    '''
    show OMAP figure dialog
    '''
    #用于记录当前的信息
    __FrameLabel = None
    __CurNum = 0
    
    #linewidthdic
    __LineWidthDic = {"1":1,
                      "1.5":1.5,
                      "2":2,
                      "2.5":2.5}
    
    #Zoom标尺字典
    __ZoomDic = {'0.2 s/div':0.2,
                 '0.5 s/div':0.5,
                 '1 s/div':1,
                 '2 s/div':2,
                 '5 s/div':5,
                 '10 s/div':10,
                 '20 s/div':20,
                 '50 s/div':50,
                 '100 s/div':100}
    
    OMAPDataHandle = None

    __LastSearchVariant = None #记录最后一次搜索的变量名字
    __LastSearchIndexList = [] #[index,...]
    __LastUseIndex = None
    
    NoneModifyFlag = False
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE,
            OMAPLog = None,
            OMAPLogTime = None,
            OMAPCompressFlag = None,
            FrameLabel = None,
            CurNum = 0  #当前的帧数
            ):      
        pre = wx.PreDialog()
        pre.SetExtraStyle( wx.DIALOG_EX_CONTEXTHELP )
        pre.Create( parent, ID, title, pos, size, style )
        self.PostCreate( pre )
        #OMAP数据类
        self.OMAPDataHandle = OMAPFigureDataHandle()
        #记录log列表的地址
        self.OMAPDataHandle.attachLogData( OMAPLog, OMAPLogTime, OMAPCompressFlag )
#        self.__FrameLabel = FrameLabel
#        self.__CurNum = CurNum
                
        #先布画面 
        self.figure = matplotlib.figure.Figure( figsize = ( 10, 5 ) )
        self.axes = self.figure.add_subplot( 1, 1, 1 )
        self.canvas = FigureCanvas( self, -1, self.figure )
        
        #布置其他界面
        self.SelectVariantList = wx.CheckListBox( self, -1, ( 150, 300 ), wx.DefaultSize, [] )
        SetCusFont( self.SelectVariantList, 10, Weight = wx.BOLD, Face = "Calibri" )
        _Framebox = wx.BoxSizer( wx.VERTICAL )
        _Box = wx.BoxSizer( wx.HORIZONTAL )
        _Box.Add( self.canvas, 9, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 2 )
        _Box.Add( self.SelectVariantList, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 2 )
        line = wx.StaticLine( self, -1, size = ( 20, -1 ), style = wx.LI_HORIZONTAL )
        _Framebox.Add( _Box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2 )
        _Framebox.Add( line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 2 )
        
        self.searchCtl = wx.SearchCtrl( self, size = ( 150, -1 ), style = wx.TE_PROCESS_ENTER )
        self.variantList = wx.ListBox( self, -1,
                                       size = ( 150, 100 ),
                                       choices = [],
                                       style = wx.LB_SINGLE )

        _Box1 = wx.StaticBoxSizer( wx.StaticBox( self, -1, "Variant config" ), wx.HORIZONTAL )
                
        _Box2 = wx.BoxSizer( wx.VERTICAL )
        _Box2.Add( self.searchCtl, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box2.Add( self.variantList, 4, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        
        self.AddButton = wx.Button( self, -1, ">>", size = ( 30, -1 ) )
        self.RemoveButton = wx.Button( self, -1, "<<", size = ( 30, -1 ) )
        
        self.VariantInfoShow = ShowGrid( self,
                                         ["Name", "Value"],
                                         size = ( 200, 150 ),
                                         OnSelectHandle = self.OnGridSelect,
                                         OnDoubleClickHandle = self.OnDClickGrid )
        
        _Box3 = wx.BoxSizer( wx.VERTICAL )
        _Box3.Add( wx.BoxSizer( wx.VERTICAL ), 1, wx.ALIGN_CENTER, 2 )
        _Box3.Add( self.AddButton, 1, wx.ALIGN_CENTER, 2 )
        _Box3.Add( wx.BoxSizer( wx.VERTICAL ), 1, wx.ALIGN_CENTER, 2 )
        _Box3.Add( self.RemoveButton, 1, wx.ALIGN_CENTER, 2 )
        _Box3.Add( wx.BoxSizer( wx.VERTICAL ), 1, wx.ALIGN_CENTER, 2 )
        
        _Box1.Add( _Box2, 3, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box1.Add( _Box3, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2 )
        _Box1.Add( self.VariantInfoShow, 4, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        
        _Box4 = wx.StaticBoxSizer( wx.StaticBox( self, -1, "Line config" ), wx.HORIZONTAL )
        
        grid1 = wx.FlexGridSizer( 0, 2, 7, 0 )
        Label = wx.StaticText( self, -1, "Min:", size = ( 70, -1 ) )
        self.minNumCtl = masked.Ctrl( self, integerWidth = 10, fractionWidth = 2, controlType = masked.controlTypes.NUMBER )
        grid1.Add( Label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        grid1.Add( self.minNumCtl, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        Label = wx.StaticText( self, -1, "Max:", size = ( 70, -1 ) )
        self.maxNumCtl = masked.NumCtrl( self, integerWidth = 10, fractionWidth = 2 )
        grid1.Add( Label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        grid1.Add( self.maxNumCtl, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        Label = wx.StaticText( self, -1, "Line Style:", size = ( 70, -1 ) )
        self.LineStyleCombox = wx.ComboBox( self,
                                            - 1,
                                            "",
                                            choices = ["-", "--", ":" , "-." ], style = wx.CB_DROPDOWN )
        self.LineStyleCombox.SetSelection( 0 )
        grid1.Add( Label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        grid1.Add( self.LineStyleCombox, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        Label = wx.StaticText( self, -1, "Line Width:", size = ( 70, -1 ) )
        self.LineWidthCombox = wx.ComboBox( self,
                                            - 1,
                                            "",
                                            choices = ["1", "1.5", "2", "2.5"], style = wx.CB_DROPDOWN )
        self.LineWidthCombox.SetSelection( 0 )
        grid1.Add( Label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        grid1.Add( self.LineWidthCombox, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        
        self.ColorButton = wx.Button( self, -1, "Line color", size = ( 70, -1 ) )
#        self.LineConfirmButton = wx.Button( self, -1, "OK.", size = ( 70, -1 ) )
        self.colorContent = wx.TextCtrl( self, -1, "", size = ( 70, -1 ) )
        self.colorContent.SetEditable( False )
        grid1.Add( self.ColorButton, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        grid1.Add( self.colorContent, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box4.Add( grid1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        
        _Box5 = wx.BoxSizer( wx.VERTICAL )
        self.GridRb = wx.RadioBox( self, -1, "Grid", wx.DefaultPosition, wx.DefaultSize,
                                   ["On", "Off"], 2, wx.RA_SPECIFY_COLS )
        
        _Box6 = wx.StaticBoxSizer( wx.StaticBox( self, -1, "Zoom" ), wx.VERTICAL )
        self.ZoomCombox = wx.ComboBox( self,
                                       - 1,
                                       "",
                                       choices = ['0.2 s/div',
                                                  '0.5 s/div',
                                                  '1 s/div',
                                                  '2 s/div',
                                                  '5 s/div',
                                                  '10 s/div',
                                                  '20 s/div',
                                                  '50 s/div',
                                                  '100 s/div'],
                                       style = wx.CB_DROPDOWN )
        self.ZoomCombox.SetSelection( 0 )
        self.ZoomInButton = wx.Button( self, -1, "+", size = ( 40, -1 ) )
        self.ZoomOutButton = wx.Button( self, -1, "-", size = ( 40, -1 ) )
        _Box8 = wx.BoxSizer( wx.HORIZONTAL )
        _Box8.Add( self.ZoomInButton, 1, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box8.Add( self.ZoomOutButton, 1, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box6.Add( self.ZoomCombox, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box6.Add( _Box8, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        
        _Box7 = wx.StaticBoxSizer( wx.StaticBox( self, -1, "Config" ), wx.HORIZONTAL )
        self.OpenConfigButton = wx.Button( self, -1, "open", size = ( 40, -1 ) )
        self.SaveConfigButtn = wx.Button( self, -1, "save", size = ( 40, -1 ) )        
        _Box7.Add( self.OpenConfigButton, 1, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box7.Add( self.SaveConfigButtn, 1, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
                
        _Box5.Add( self.GridRb, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box5.Add( _Box6, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box5.Add( _Box7, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        
        _configBox = wx.StaticBoxSizer( wx.StaticBox( self, -1, "" ), wx.HORIZONTAL )
        _configBox.Add( _Box1, 10, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _configBox.Add( _Box4, 3, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _configBox.Add( _Box5, 2, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        
        _Framebox.Add( _configBox, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2 )
        _Box9 = wx.BoxSizer( wx.HORIZONTAL )
        _Box9.Add( wx.StaticText( self, -1, "Num:", size = ( 40, -1 ) ), 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        self.FrameNum_Slider = wx.Slider( self, -1, minValue = 1, maxValue = self.OMAPDataHandle.getFrameSize( FrameLabel ) )
        self.FrameNum_Slider.SetValue( self.__CurNum + 1 )        
        self.FrameNum = FS.FloatSpin( self,
                                      - 1,
                                      increment = -1,
                                      min_val = 1,
                                      max_val = self.OMAPDataHandle.getFrameSize( FrameLabel ),
                                      agwStyle = FS.FS_LEFT )
        self.FrameNum.SetFormat( "%f" )
        self.FrameNum.SetDigits( 0 )
        self.FrameNum.SetValue( self.__CurNum + 1 )
        self.TimeTxt = wx.TextCtrl( self, -1, "" )
        self.TimeTxt.SetEditable( False )
        
        self.NumGridShowButton = wx.Button( self, -1, "Show Num", size = ( 100, -1 ) )
        _Box9.Add( self.FrameNum_Slider, 15, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box9.Add( self.FrameNum, 3, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box9.Add( self.TimeTxt, 5, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Box9.Add( self.NumGridShowButton, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        _Framebox.Add( _Box9, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 2 )
                
        self.SetSizer( _Framebox )
        _Framebox.Fit( self )
        self.defaultPlot()
        self.BindEvents()
        self.UpdataView( OMAPLog, OMAPLogTime, FrameLabel, CurNum )
        
    def BindEvents( self ):
        self.Bind( wx.EVT_BUTTON, self.AddNewVariant, self.AddButton )
        self.Bind( wx.EVT_LISTBOX_DCLICK, self.AddNewVariant, self.variantList )
        self.Bind( wx.EVT_BUTTON, self.RemoveVariant, self.RemoveButton )
        self.Bind( wx.EVT_BUTTON, self.ShowNum, self.NumGridShowButton )
        
        self.Bind( wx.EVT_COMBOBOX, self.ZoomComboxChange, self.ZoomCombox )
        self.Bind( wx.EVT_BUTTON, self.OnZoomIn, self.ZoomInButton )
        self.Bind( wx.EVT_BUTTON, self.OnZoomOut, self.ZoomOutButton )
        
        self.Bind( wx.EVT_RADIOBOX, self.GridRadioBox, self.GridRb )
        
        self.Bind( FS.EVT_FLOATSPIN, self.OnFrameNumChange, self.FrameNum )
        self.Bind( wx.EVT_SCROLL_CHANGED, self.OnFrameNumChange_slider, self.FrameNum_Slider )
        
        self.Bind( wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearchVar, self.searchCtl )  
        self.Bind( wx.EVT_TEXT_ENTER, self.OnSearchVar, self.searchCtl )       

        self.Bind( wx.EVT_LISTBOX, self.EvtSelectVariantListBox, self.SelectVariantList )
        self.Bind( wx.EVT_CHECKLISTBOX, self.EvtSelectVariantCheckListBox, self.SelectVariantList )
        
        #Lineconfig的相关配置
        self.Bind( masked.EVT_NUM, self.SetLineMin, self.minNumCtl )
        self.Bind( masked.EVT_NUM, self.SetLineMax, self.maxNumCtl )
        self.Bind( wx.EVT_COMBOBOX, self.SetLineStyle, self.LineStyleCombox )
        self.Bind( wx.EVT_COMBOBOX, self.SetLineWidth, self.LineWidthCombox )
        self.Bind( wx.EVT_BUTTON, self.OnChangeColor, self.ColorButton )
        
        #open&save config
        self.Bind( wx.EVT_BUTTON, self.OnOpenConfig, self.OpenConfigButton )
        self.Bind( wx.EVT_BUTTON, self.OnSaveConfig, self.SaveConfigButtn )
    
    def OnOpenConfig( self, event ):
        "on open config dialog"
        _diag = OpenOMAPFigureDiag( self, -1, "open OMAP Figure Config" )
        _diag.CenterOnScreen()
        if wx.ID_OK == _diag.ShowModal():
            _config = _diag.getSelectConfig()
            OMAPFigureConfigHandle.saveOMAPFigureFile( r'./TPConfig/OMAPFigureConfig.xml' )
            if None != _config:
                #reset前将原有的显示变量返回给variantList
                for _label in self.OMAPDataHandle.getConfigLabelList( self.__FrameLabel ):
                    #将变量从新放入到variant中去
                    _tmpindex = None
                    for _i, _item in enumerate( self.variantList.GetItems() ):
                        if cmp( _item, _label ) > 0: #需找插入的位置
                            _tmpindex = _i
                            break
                    if None == _tmpindex:
                        _tmpindex = _i
                    self.variantList.Insert( _label, _tmpindex )
                    
                self.OMAPDataHandle.resetConfigDic( _config )
                #将新的从variantList中删除
                for _label in self.OMAPDataHandle.getConfigLabelList( self.__FrameLabel ):
                    #从variant中抽取一个出来
                    for _i, _item in enumerate( self.variantList.GetItems() ):
                        if _label == _item:
                            self.variantList.Delete( _i )          
                
                self.variantList.SetSelection( -1 )
                #换Frame需要更新相关的显示
                self.UpdataSelectVariantList()
                #开始画图 
                self.defaultPlot()               
                self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
                self.canvas.draw()
                #更新Grid中的显示
                _data = self.OMAPDataHandle.getGridShowData( self.__FrameLabel, self.__CurNum )
                self.VariantInfoShow.setCustable( _data )
                self.EnableLineConfig( False )
            else:
                wx.MessageBox( "No config has been seleted", "ERROR" )
        _diag.Destroy()
    
    def OnSaveConfig( self, event ):
        "on save config dialog"
        _diag = SaveOMAPFigureDiag( self, -1, "save OMAP Figure Config" )
        _diag.CenterOnScreen()
        if wx.ID_OK == _diag.ShowModal():
            _name, _des = _diag.getNameAndDes()
            _configDic = self.OMAPDataHandle.getConfigDic()
            
            if None != OMAPFigureConfigHandle.addNewOMAPFigureConfig( _name, _configDic, _des ):
                OMAPFigureConfigHandle.saveOMAPFigureFile( r'./TPConfig/OMAPFigureConfig.xml' )
            else:
                _tmpdlg = wx.MessageDialog( self, 'The Config Name has Exist, it will be covered if you choose OK!',
                                            'Warnning',
                                            wx.OK | wx.CANCEL | wx.ICON_WARNING
                                            )
                if wx.ID_OK == _tmpdlg.ShowModal():
                    OMAPFigureConfigHandle.coverAnOMAPFigureConfig( _name, _configDic, _des )
                _tmpdlg.Destroy()
        _diag.Destroy()
    
    def OnDClickGrid( self, event ):
        "On Double Click Grid"
#        print self.VariantInfoShow.GetSelectData()
        self.RemoveVariant( event )
    
    def getCurNum( self ):
        return self.__CurNum
    
    def SetLineMin( self, event ):
        if self.NoneModifyFlag:
            return
#        print "start set Min"
        _minValue = self.minNumCtl.GetValue()
        _maxValue = self.maxNumCtl.GetValue()
        if _minValue >= _maxValue:
            wx.MessageBox( "min can't lager than max!", "Error" )
            return
        self.OMAPDataHandle.modifyLineMinValue( self.__FrameLabel,
                                                self.VariantInfoShow.GetSelectData()[0],
                                                _minValue,
                                                self.plot,
                                                0.1,
                                                self.__CurNum )

        #重新画图
#        self.defaultPlot()
#        self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
        self.canvas.draw()
        
    def SetLineMax( self, event ):
        if self.NoneModifyFlag:
            return        
#        print "start set max"
        _minValue = self.minNumCtl.GetValue()
        _maxValue = self.maxNumCtl.GetValue()
        if _minValue >= _maxValue:
            wx.MessageBox( "max can't lager than min!", "Error" )
            return
        self.OMAPDataHandle.modifyLineMaxValue( self.__FrameLabel,
                                                self.VariantInfoShow.GetSelectData()[0],
                                                _maxValue,
                                                self.plot,
                                                0.1,
                                                self.__CurNum )

        #重新画图
#        self.defaultPlot()
#        self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
        self.canvas.draw()
        
    def SetLineStyle( self, event ):
        if self.NoneModifyFlag:
            return
        self.OMAPDataHandle.modifyLineStyle( self.__FrameLabel,
                                             self.VariantInfoShow.GetSelectData()[0],
                                             self.LineStyleCombox.GetValue() )

        #重新画图
#        self.defaultPlot()
#        self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
        self.canvas.draw()
        
        #更新list的显示
        self.UpdataSelectVariantList()
        
    def SetLineWidth( self, event ):
        if self.NoneModifyFlag:
            return
        _lineWidth = self.__LineWidthDic[ self.LineWidthCombox.GetValue() ]
        self.OMAPDataHandle.modifyLineWidth( self.__FrameLabel,
                                             self.VariantInfoShow.GetSelectData()[0],
                                             _lineWidth )

        #重新画图
#        self.defaultPlot()
#        self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
        self.canvas.draw()
    
    def OnChangeColor( self, event ):
        _dlg = wx.ColourDialog( self )

        _dlg.GetColourData().SetChooseFull( True )

        if _dlg.ShowModal() == wx.ID_OK:
            _data = _dlg.GetColourData()
#            print _data.GetColour().Get()
            _tmpcolor = []
            for _tmp in _data.GetColour().Get():
                _tmpcolor.append( _tmp / 255.0 )
            self.OMAPDataHandle.modifyLineColor( self.__FrameLabel,
                                                 self.VariantInfoShow.GetSelectData()[0],
                                                 tuple( _tmpcolor ) )
            self.colorContent.SetValue( repr( tuple( _tmpcolor ) ) )
            #重新画图
#            self.defaultPlot()
#            self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
            self.canvas.draw()
            #更新list的显示
            self.UpdataSelectVariantList()
            
        _dlg.Destroy()
    
    def EvtSelectVariantListBox( self, event ):
        _index = self.SelectVariantList.GetSelection()
        _label = self.VariantInfoShow.GetData()[_index][0]
        self.OMAPDataHandle.setSelectionMarker( self.__FrameLabel,
                                                _label )
#        print "EvtSelectVariantListBox"
        self.canvas.draw()
        
    
    def EvtSelectVariantCheckListBox( self, event ):
        _index = event.GetSelection()
        _label = self.VariantInfoShow.GetData()[_index][0]
        if self.SelectVariantList.IsChecked( _index ):
            self.OMAPDataHandle.modifyLineShowFlag( self.__FrameLabel, _label, True )
        else:
            self.OMAPDataHandle.modifyLineShowFlag( self.__FrameLabel, _label, False ) 
        #重新画图
#        self.defaultPlot()
#        self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
        self.canvas.draw()       
    
    def UpdataSelectVariantList( self ):
        "updata select variant list according to OMAPDataHandle"
        #获取线的相关信息
        _infoList = self.OMAPDataHandle.getAllLineInfo( self.__FrameLabel )
        
        #生成SelectVariantList的相关显示
        self.SelectVariantList.SetItems( [_item[0] for _item in _infoList] )
        _checkedList = []
        #修改底色
        for _i, _info in enumerate( _infoList ):
            _tmpc = _info[1]
            _color = wx.Color( _tmpc[0] * 255, _tmpc[1] * 255, _tmpc[2] * 255 )
            self.SelectVariantList.SetItemForegroundColour( _i, _color )
            if True == _info[-1]:
                _checkedList.append( _i )
        
        self.SelectVariantList.SetChecked( _checkedList )
    
    #------------------------------------------------------------------
    #从variantList搜索变量variant,不区分大小写,返回下表列表
    #------------------------------------------------------------------
    def GetSearchVariantIndex( self, variant ):
        "Get Search Variant Index"
        _rev = []  ##[[label,page,row,col]]
        _variant_UPPER = variant.upper() #转换成大写以便搜索,实现大小写识别模糊
        for _i, _item in enumerate( self.variantList.GetItems() ):
            if _variant_UPPER in _item.upper():
                _rev.append( _i )
        return _rev
    
    def OnSearchVar( self, event ):
        "On Search Variant"
        _searchvalue = self.searchCtl.GetValue()   
#        print _searchvalue
        if "" == _searchvalue or None == _searchvalue: #no search for ""
            return 
        
        if self.__LastSearchVariant != _searchvalue :
            #新搜索
            self.__LastSearchVariant = _searchvalue 
            self.__LastSearchIndexList = self.GetSearchVariantIndex( _searchvalue )
            if len( self.__LastSearchIndexList ) > 0:
                self.__LastUseIndex = 0
            else:
                self.__LastUseIndex = -1
        else:
            #继续查找
            if len( self.__LastSearchIndexList ) > 0:
                self.__LastUseIndex = ( self.__LastUseIndex + 1 ) if \
                                        ( self.__LastUseIndex < ( len( self.__LastSearchIndexList ) - 1 ) )\
                                            else 0  #实现循环查找
            else:
                self.__LastUseIndex = -1  
        
        #进行查找显示
        if  self.__LastUseIndex >= 0:
            #选中查找到的Index
            self.variantList.SetSelection( self.__LastSearchIndexList[self.__LastUseIndex] )
        else:
            pass #没找到不做任何操作        
    
    def UpdataView( self, OMAPLog, OMAPLogTime, FrameLabel, CurNum ):
        #一下注释掉的几个可以赋值，只有修改的情况下赋值，在本窗口被创建出来的时候已经赋值了
#        print FrameLabel, CurNum
#        self.__OMAPLogData = OMAPLog
#        self.__OMAPLogData = OMAPLogTime
#        self.__FrameLabel = FrameLabel
#        self.__CurNum = CurNum
        self.FrameNum.SetRange( 1, self.OMAPDataHandle.getFrameSize( FrameLabel ) )
        self.FrameNum_Slider.SetMax( self.OMAPDataHandle.getFrameSize( FrameLabel ) )
        self.FrameNum.SetValue( CurNum + 1 )
        self.FrameNum_Slider.SetValue( CurNum + 1 )
        self.TimeTxt.SetValue( self.OMAPDataHandle.getCurTimeString( FrameLabel, CurNum ) )
        #判断是否需要进行变量的重新载入，如果标签不改变的话则不要进行此操作
        if FrameLabel != self.__FrameLabel or self.__CurNum != CurNum:
            self.__FrameLabel = FrameLabel
            self.__CurNum = CurNum
            #获取变量列表
            _tmpList = self.OMAPDataHandle.getOMAPVariantList( self.__FrameLabel )
            if _tmpList != self.variantList.GetItems():
                self.variantList.SetItems( _tmpList )
                self.variantList.SetSelection( -1 )
            #换Frame需要更新相关的显示
            self.UpdataSelectVariantList()
            #开始画图
            self.defaultPlot()
            self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )            
            self.canvas.draw()
            #更新Grid中的显示
            _data = self.OMAPDataHandle.getGridShowData( self.__FrameLabel, self.__CurNum )
            self.VariantInfoShow.setCustable( _data )
            self.EnableLineConfig( False )
            
    
    def OnFrameNumChange( self, event ):
        _Num = int( self.FrameNum.GetValue() ) - 1
        self.FrameNum_Slider.SetValue( _Num + 1 )
        self.TimeTxt.SetValue( self.OMAPDataHandle.getCurTimeString( self.__FrameLabel, self.__CurNum ) )
        self.__CurNum = _Num
        #开始画图
#        self.defaultPlot()
        self.OMAPDataHandle.removeAllLines( self.__FrameLabel )
        self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
        self.canvas.draw()
        #更新Grid中的显示
        _data = self.OMAPDataHandle.getGridShowData( self.__FrameLabel, self.__CurNum )
        self.VariantInfoShow.setCustable( _data ) 
        self.EnableLineConfig( False )       
        
    def OnFrameNumChange_slider( self, event ):
        _Num = self.FrameNum_Slider.GetValue() - 1
        self.FrameNum.SetValue( _Num + 1 )
        self.TimeTxt.SetValue( self.OMAPDataHandle.getCurTimeString( self.__FrameLabel, self.__CurNum ) )
        self.__CurNum = _Num
        #开始画图
#        self.defaultPlot()
        self.OMAPDataHandle.removeAllLines( self.__FrameLabel )
        self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
        self.canvas.draw()
        #更新Grid中的显示
        _data = self.OMAPDataHandle.getGridShowData( self.__FrameLabel, self.__CurNum )
        self.VariantInfoShow.setCustable( _data )
        
        self.EnableLineConfig( False ) 
    
    def GridRadioBox( self, event ):
        _selectIndex = self.GridRb.GetSelection()
        if 0 == _selectIndex:
            self.gridOn()
        else:
            self.gridOff()
    
    def OnZoomIn( self, event ):
        "on zoom in"
        _index = self.ZoomCombox.GetSelection()
        if _index < len( self.ZoomCombox.GetItems() ) - 1:
            self.ZoomCombox.SetSelection( _index + 1 )
        self.ZoomComboxChange( event )  
        
    def OnZoomOut( self, event ):
        "on zoom out"
        _index = self.ZoomCombox.GetSelection()
        if _index > 0:
            self.ZoomCombox.SetSelection( _index - 1 )  
        
        self.ZoomComboxChange( event )  
    
    def ZoomComboxChange( self, event ):
        "zoom combox change"
        _rangeMin = -5 * self.__ZoomDic[self.ZoomCombox.GetValue()] 
        _rangeMax = 5 * self.__ZoomDic[self.ZoomCombox.GetValue()]
        self.axes.set_xlim( _rangeMin, _rangeMax )
        self.setXticksTo10()
        
        self.canvas.draw()
        
    def AddNewVariant( self, event ):
        if self.variantList.GetSelection() in [-1, None]:
            print "AddNewVariant Error", self.variantList.GetSelection() 
            return
        _label = self.variantList.GetItems()[self.variantList.GetSelection()]
        self.OMAPDataHandle.addVariantToConfigDic( self.__FrameLabel, _label )
        self.OMAPDataHandle.addOneLineIntoAxes( self.__FrameLabel, _label, self.plot, 0.1, self.__CurNum )
        #重新画图
#        print time.time()
#        self.defaultPlot()
#        self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
        self.canvas.draw()
#        print time.time()
        #更新列表显示
        #从variant中抽取一个出来
        for _i, _item in enumerate( self.variantList.GetItems() ):
            if _label == _item:
                self.variantList.Delete( _i )
                #更新self.variantList的选中的变量
                if len( self.variantList.GetItems() ) > 0:
                    self.variantList.SetSelection( _i - 1 if _i > 0 else 0 )
                else:
                    self.variantList.SetSelection( -1 )
                break
        #更新Grid中的显示
        _data = self.OMAPDataHandle.getGridShowData( self.__FrameLabel, self.__CurNum )
        self.VariantInfoShow.setCustable( _data )
        
        #更新variantlist
        self.UpdataSelectVariantList()
        
        self.EnableLineConfig( False )
    
    def RemoveVariant( self, event ):
        _index = self.VariantInfoShow.GetSelection()
        if _index in [None, -1]:
            return
        
        _label = self.VariantInfoShow.GetSelectData()[0]
        self.OMAPDataHandle.removeVariantToConfigDic( self.__FrameLabel, _label )
        self.OMAPDataHandle.delOneLineFromAxes( self.__FrameLabel, _label )
        #重新画图
#        print time.time()
#        self.defaultPlot()
#        self.OMAPDataHandle.plotHandle( self.__FrameLabel, self.plot, 0.1, self.__CurNum )
        self.canvas.draw()
#        print time.time()
        #更新列表显示
        #将变量从新放入到variant中去
        _tmpindex = None
        for _i, _item in enumerate( self.variantList.GetItems() ):
            if cmp( _item, _label ) > 0: #需找插入的位置
                _tmpindex = _i
                break
        if None == _tmpindex:
            _tmpindex = _i
        self.variantList.Insert( _label, _tmpindex )
        self.variantList.SetSelection( _tmpindex )
        #更新Grid中的显示
        _data = self.OMAPDataHandle.getGridShowData( self.__FrameLabel, self.__CurNum )
        self.VariantInfoShow.setCustable( _data )
        #只能一个一个删除
        self.VariantInfoShow.SetSelection( None )
        
        #更新variantlist
        self.UpdataSelectVariantList()
        
        self.EnableLineConfig( False )
    
    def OnGridSelect( self, event ):
        self.VariantInfoShow.OnSelect( event )
        if self.VariantInfoShow.GetSelection() in [None, -1]: #未选中数据无需进行下面的操作
            return
#        _index = self.VariantInfoShow.GetSelection()
        _label = self.VariantInfoShow.GetSelectData()[0]
        #[Max,Min,linestype,linewidth,color,showflag]
        _info = self.OMAPDataHandle.getLineAllInfo( self.__FrameLabel, _label )
        #更新显示
        self.NoneModifyFlag = True
        self.maxNumCtl.SetValue( _info[0] )
#        print "max modify"
        self.minNumCtl.SetValue( _info[1] )
#        print "min modify"
        self.colorContent.SetValue( repr( _info[-2] ) )
        for _i, _linestyle in enumerate( self.LineStyleCombox.GetItems() ):
            if _info[2] == _linestyle:
                self.LineStyleCombox.SetSelection( _i )
                break

        for _i, _linestyle in enumerate( self.LineWidthCombox.GetItems() ):
            if str( _info[3] ) == _linestyle:
                self.LineWidthCombox.SetSelection( _i )
                break
        self.EnableLineConfig( True ) 
        self.SelectVariantList.SetSelection( self.VariantInfoShow.GetSelection() )
        self.EvtSelectVariantListBox( "event" )
        self.NoneModifyFlag = False
    
    def EnableLineConfig( self, flag ):
        "Enable line config"
        self.maxNumCtl.Enable( flag )
        self.minNumCtl.Enable( flag )
        self.LineStyleCombox.Enable( flag )
        self.LineWidthCombox.Enable( flag )
        self.ColorButton.Enable( flag )
        self.colorContent.Enable( flag )
#        self.LineConfirmButton.Enable( flag )
    
    def ShowNum( self, event ):
#        print "showNUm"
        self.Close()
#        self.EndModal()
        
    #---------------------------------------------------------------
    #@根据相关属性进行画图,dataX，dataY为一维列表（目前仅支持画二位图像）
    #@title:图标题目
    #@style = "r--"
    #@label:横纵坐标的标题名[xlabel,ylabel]
    #---------------------------------------------------------------
    def plot( self,
              dataX = [],
              dataY = [],
              style = "",
              color = ( 0, 0, 0 ),
              linewidth = 0.5 ):
        if len( dataX ) != len( dataY ):
            print "plot error!!! length of dataX and dataY are not equal!"
            return
        _tmpX = np.array( dataX )
        _tmpY = np.array( dataY )  
        _lines = self.axes.plot( dataX, dataY, style, color = color, linewidth = linewidth )
#        self.canvas.draw()
#        print dir( _lines[0] )
        _lines[0].set_marker( None )
#        _lines[0].set_markeredgecolor( ( 255, 255, 255 ) )
        return _lines[0]
    
    #----------------------------------------------------------------
    #设置X轴的ticks为10
    #----------------------------------------------------------------
    def setXticksTo10( self ):
        #保证图的网格为10
        _tmp = self.axes.get_xlim()
        list = []
        for _i in range( 10 ):
            list.append( _tmp[0] + ( _tmp[1] - _tmp[0] ) * _i / 10 )
        self.axes.set_xticks( list )        
    
    def setYticksTo5( self ):
        #保证图的网格为10
        _tmp = self.axes.get_ylim()
        list = []
        for _i in range( 5 ):
            list.append( _tmp[0] + ( _tmp[1] - _tmp[0] ) * _i / 5 )
        self.axes.set_yticks( list ) 
          
    #----------------------------------------------------------------
    #图像的基本设置
    #----------------------------------------------------------------
    def handleBasePlot( self ):
        #设置底色
        self.axes.set_axis_bgcolor( ( 1, 1, 1 ) )
        self.figure.set_facecolor( ( 0.94, 0.94, 0.94 ) )
        self.setXticksTo10()
        self.setYticksTo5()
        #不显示ticks
        self.axes.set_yticklabels( [] )
        self.axes.set_title( "OMAP Variables Show" )
        self.axes.set_ylabel( "Y: Variables" )
        self.axes.set_xlabel( "X: time (S)" )        
#        self.axes.set_xticklabels( [] )
        self.canvas.draw()    
    
    def gridOn( self ):
        "grid on"
        self.axes.grid( b = True )
        self.canvas.draw()
        
    def gridOff( self ):
        "grid off"
        self.axes.grid( b = False )
        self.canvas.draw()
    
    def defaultPlot( self ):
        self.figure.set_canvas( self.canvas )
        self.axes.clear()
        _rangeMin = -5 * self.__ZoomDic[self.ZoomCombox.GetValue()] 
        _rangeMax = 5 * self.__ZoomDic[self.ZoomCombox.GetValue()]
        self.axes.set_xlim( _rangeMin, _rangeMax ) #设置y坐标的最大最小值为固定值
        self.axes.set_ylim( 0, 1 )        
        self.handleBasePlot()
        self.GridRadioBox( "event" )
        self.plot( [0, 0], [0, 1] )
#        self.canvas.draw()
            
    def clear( self ):
        self.figure.set_canvas( self.canvas )
        self.axes.clear()
        self.canvas.draw()


#------------------------------------------------------------------------------------------
#用于显示OMAP记录的Frame
#------------------------------------------------------------------------------------------
class ShowOMAPLogFRM( wx.Frame ):
    '''
    Show OMAP Log Frame
    '''
    OMAPRowsLen = 40
    OMAPColLen = 3
    
    __FrameSize = None
    
    __LastSearchVariant = None #记录最后一次搜索的变量名字(Framelabel,VariantName)
    __LastSearchInfo = [] #[[label,page,row,col]]
    __LastFRMSet = {} # {case:framelabel,...}
    
    __CustomStoreDir = ''
    __Figurediag = None
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE
            ):      
        wx.Frame.__init__( self, parent, ID, title, pos, size, style )
        panel = wx.Panel( self, -1 ) #frame必须有panel，否则一些事件响应会有问题
        self.__HighlightItems = [] # [[framelabel, page, label],...] ,需要label在具体某一page中是唯一的
        ShowOMAPLogFRM.__CustomStoreDir = './TPConfig/custom/'
        try:
            os.makedirs( ShowOMAPLogFRM.__CustomStoreDir )
        except:
            pass
        #获取当前Log的路径
        _logpath = CaseParser.getEditCaseLogPath()
        #导入记录文件
#        OMAPParser.LoadOMAPData( _logpath )
        self.__OMAPLogData, \
        self.__OMAPPosData, \
        self.__OMAPTimeData, \
        self.__OMAPCompressFlag = OMAPParser.LoadZipOMAPData( _logpath )
#        print self.__OMAPPosData
#        print OMAPParser.OMAPLogData
        
        _Framebox = wx.BoxSizer( wx.VERTICAL )
        _Box = wx.BoxSizer( wx.HORIZONTAL )
                
        _framelabel = OMAPParser.getOMAPFrameList( self.__OMAPLogData ) if len( OMAPParser.getOMAPFrameList( self.__OMAPLogData ) ) > 0 else ["No Frame"]
        label = wx.StaticText( panel, -1, "Frame Label:", size = ( -1, -1 ) )
        self.FrameComBoBox = wx.ComboBox( panel, -1, _framelabel[0], \
                                          size = ( 150, -1 ), \
                                          choices = _framelabel,
                                          style = wx.CB_DROPDOWN )
        self.FrameComBoBox.SetSelection( 0 )
        _Box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Box.Add( self.FrameComBoBox, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        label = wx.StaticText( panel, -1, "Number:", size = ( -1, -1 ) )
        self.FrameNum = FS.FloatSpin( panel,
                                      - 1,
                                      increment = -1,
                                      min_val = 1,
                                      max_val = OMAPParser.getOMAPFrameSize( self.__OMAPLogData, _framelabel[0] ),
                                      agwStyle = FS.FS_LEFT )
        self.FrameNum.SetFormat( "%f" )
        self.FrameNum.SetDigits( 0 )
#        self.FrameNum = wx.Slider( self, -1, minValue = 1, maxValue = OMAPParser.getOMAPFrameSize( _framelabel[0] ) )
#        self.FrameNum.SetValue( 1 )
        _list = [str( _i + 1 ) for _i in range( OMAPParser.getOMAPFramePageSize( _framelabel[0] ) )]
        self.FrameNum_Slider = wx.Slider( panel, -1, minValue = 1, maxValue = OMAPParser.getOMAPFrameSize( self.__OMAPLogData, _framelabel[0] ) )
        self.FrameNum_Slider.SetValue( 1 )
        _Box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Box.Add( self.FrameNum_Slider, 3, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Box.Add( self.FrameNum, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        label = wx.StaticText( panel, -1, "Page Index:", size = ( -1, -1 ) )
#        self.FramePage = wx.SpinCtrl( panel, -1, "", min = 1, max = OMAPParser.getOMAPFramePageSize( _framelabel[0] ) )
#        self.FramePage.SetValue( 1 )
        _list = [str( _i + 1 ) for _i in range( OMAPParser.getOMAPFramePageSize( _framelabel[0] ) )]
        self.FramePageCBX = wx.ComboBox( panel, -1, "1", choices = _list, style = wx.CB_DROPDOWN )
        _Box.Add( label, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Box.Add( self.FramePageCBX, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
#        _Box.Add( self.FramePage, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        self.TimeTxt = wx.TextCtrl( panel, -1, self.__OMAPTimeData[_framelabel[0]][0] )
        self.TimeTxt.SetEditable( False )
        self.ShowFigureButton = wx.Button( panel, -1, "Figure" )
        _Box.Add( self.TimeTxt, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Box.Add( self.ShowFigureButton, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( _Box, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        label = wx.StaticText( panel, -1, "Search Variant:", size = ( -1, -1 ) )
        self.SearchCtrl = wx.SearchCtrl( panel, size = ( 240, -1 ), style = wx.TE_PROCESS_ENTER )
        _Box1 = wx.BoxSizer( wx.HORIZONTAL )
        _Box1.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        _Box1.Add( self.SearchCtrl, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )

        label = wx.StaticText( panel, -1, "BlockId:", size = ( -1, -1 ) )
        self.BlockIdTxt = wx.TextCtrl( panel, -1, '', size = ( 120, -1 ) )
        SetCusFont( self.BlockIdTxt, 12, Weight = wx.BOLD, Face = "Calibri" )
        self.BlockIdTxt.Enable( False )
        _Box1.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        _Box1.Add( self.BlockIdTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )

        label = wx.StaticText( panel, -1, "Abscissa:", size = ( -1, -1 ) )
        self.AbscissaTxt = wx.TextCtrl( panel, -1, '', size = ( 120, -1 ) )
        SetCusFont( self.AbscissaTxt, 12, Weight = wx.BOLD, Face = "Calibri" )
        self.AbscissaTxt.Enable( False )
        _Box1.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        _Box1.Add( self.AbscissaTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        
        label = wx.StaticText( panel, -1, "TrainStop:", size = ( -1, -1 ) )
        self.TrainStopTxt = wx.TextCtrl( panel, -1, '', size = ( 120, -1 ) )
        SetCusFont( self.TrainStopTxt, 12, Weight = wx.BOLD, Face = "Calibri" )
        self.TrainStopTxt.Enable( False )
        _Box1.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        _Box1.Add( self.TrainStopTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        
        label = wx.StaticText( panel, -1, "TrainSpeed:", size = ( -1, -1 ) )
        self.TrainSpeedTxt = wx.TextCtrl( panel, -1, '', size = ( 120, -1 ) )
        SetCusFont( self.TrainSpeedTxt, 12, Weight = wx.BOLD, Face = "Calibri" )
        self.TrainSpeedTxt.Enable( False )
        _Box1.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        _Box1.Add( self.TrainSpeedTxt, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )

        self.CustomView = wx.CheckBox( panel, -1, "Custom View" )#(65, 40), (150, 20), wx.NO_BORDER)
        self.Bind( wx.EVT_CHECKBOX, self.EvtCheckBox, self.CustomView )
        _Box1.Add( self.CustomView, 0, wx.ALIGN_CENTER | wx.ALL, 5 )
        
        _Framebox.Add( _Box1, 1, wx.ALIGN_LEFT , 5 )
        
        self.__LoadHighlight()

        self.ShowLog = ShowGrid( panel, ['Name', 'Value',
                                        'Name', 'Value',
                                        'Name', 'Value'], size = ( 1200, 600 ),
                                 OnSelectHandle = False,
                                 CopyFlag = True )
        self.ShowLog.Bind( Grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnGridRightUp )
#        self.ShowLog.EnableDragColSize( False )
        self.ShowLog.EnableDragRowSize( False )
        _Framebox.Add( self.ShowLog, 13, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        panel.SetSizer( _Framebox )
        _Framebox.Fit( self )
        
        self.BindEvents()
        
        key = CaseParser.getEditCaseInfo()[1]
        if ShowOMAPLogFRM.__LastFRMSet.has_key( key ):
            self.FrameComBoBox.SetValue( ShowOMAPLogFRM.__LastFRMSet[key] )
        self.UpDataGrid()
        
        self.Maximize()
    
    def OnGridRightUp( self, event ):
        if event.GetCol() % 2 != 0:
            return
        self.rightClickCell = event.GetRow(), event.GetCol()
        self.cellValue = self.ShowLog.GetCellValue( event.GetRow(), event.GetCol() )   
        if self.cellValue == "":
            return
        
        menu = wx.Menu()
        if self.CustomView.IsChecked() == False:
            item1 = menu.Append( wx.ID_ANY, "Add to custom" )
            self.Bind( wx.EVT_MENU, self.OnGridAddToCustom, item1 )
        item2 = menu.Append( wx.ID_ANY, "Del from custom" )
        self.Bind( wx.EVT_MENU, self.OnGridDelFromCustom, item2 )
        self.PopupMenu( menu )
        menu.Destroy() 
    
    def OnGridAddToCustom( self, event ):
        assert self.CustomView.IsChecked() == False
        row, col = self.rightClickCell
        _Framelabel = self.FrameComBoBox.GetValue()
#        _Page = self.FramePage.GetValue()
        _Page = self.FramePageCBX.GetSelection() + 1
        _Label = self.ShowLog.GetCellValue( *self.rightClickCell )
        if self.__IsHighlightLabel( _Framelabel, _Page, _Label ):
            return
        self.__AppendHighlight( [_Framelabel, _Page, _Label] )
        self.ShowLog.SetCellBackgroundColour( row, col, wx.Color( 0, 255, 0 ) )
        self.ShowLog.Refresh()
        
    def OnGridDelFromCustom( self, event ):
        row, col = self.rightClickCell
        _Framelabel = self.FrameComBoBox.GetValue()
        _Label = self.ShowLog.GetCellValue( *self.rightClickCell )
        
        if self.CustomView.IsChecked() == False:
#            _Page = self.FramePage.GetValue()
            _Page = self.FramePageCBX.GetSelection() + 1
            if self.__IsHighlightLabel( _Framelabel, _Page, _Label ) == False:
                return
            self.__RemoveHighlight( [_Framelabel, _Page, _Label] )
            self.ShowLog.SetCellBackgroundColour( row, col, wx.Color( 255, 255, 255 ) )
            self.ShowLog.Refresh()
        else:
            lst = _Label.split()
            assert len( lst ) == 2
            _Page = int( lst[0] )
            _Label = lst[1]
            self.__RemoveHighlight( [_Framelabel, _Page, _Label] )
            self.RefreshCustomGrid()
        
    def EvtCheckBox( self, event ):
        cb = event.GetEventObject()
        if cb.IsChecked():
            self.FrameComBoBox.Enable( False )
            self.FramePageCBX.Enable( False )
            self.SearchCtrl.Enable( False )
            
            self.RefreshCustomGrid()
        else:
            self.FrameComBoBox.Enable( True )
            self.FramePageCBX.Enable( True )
            self.SearchCtrl.Enable( True )
            
            self.OnFramePageChange_CBX( None )
            
    def __LoadHighlight( self ):
        f = None
        try:
            f = open( ShowOMAPLogFRM.__CustomStoreDir + CaseParser.getEditCaseInfo()[1] + '.his', 'r' )
            for line in f:
                lst = line.split()
                if len( lst ) == 3:
                    lst[0] = unicode( lst[0] )
                    lst[1] = int( lst[1] )
                    lst[2] = str( lst[2] )
                    self.__HighlightItems.append( lst )
        except:
            pass
        finally:
            if f != None:
                f.close()
                
    def __AppendHighlight( self, lst ):
        self.__HighlightItems.append( lst )
        f = None
        try:
            f = open( ShowOMAPLogFRM.__CustomStoreDir + CaseParser.getEditCaseInfo()[1] + '.his', 'a' )
            for i in lst:
                f.write( str( i ) )
                f.write( ' ' )
            f.write( '\n' )
        except:
            pass
        finally:
            if f != None:
                f.close()
                
    def __RemoveHighlight( self, lst ):
        self.__HighlightItems.remove( lst )
        f = None
        try:
            f = open( ShowOMAPLogFRM.__CustomStoreDir + CaseParser.getEditCaseInfo()[1] + '.his', 'w' )
            for item in self.__HighlightItems:
                for i in item:
                    f.write( str( i ) )
                    f.write( ' ' )
                f.write( '\n' )
        except:
            pass
        finally:
            if f != None:
                f.close()
        
    def BindEvents( self ):
        "bind events"
        self.Bind( wx.EVT_BUTTON, self.OnFigure, self.ShowFigureButton )
        self.Bind( wx.EVT_COMBOBOX, self.OnFrameChange, self.FrameComBoBox )
        self.Bind( FS.EVT_FLOATSPIN, self.OnFrameNumChange, self.FrameNum )
        self.Bind( wx.EVT_SCROLL_CHANGED, self.OnFrameNumChange_slider, self.FrameNum_Slider )
        self.Bind( wx.EVT_COMBOBOX, self.OnFramePageChange_CBX, self.FramePageCBX )
        self.Bind( wx.EVT_IDLE, self.CheckSize )
        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
        self.Bind( wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearchVariant, self.SearchCtrl )
        self.Bind( wx.EVT_TEXT_ENTER, self.OnSearchVariant, self.SearchCtrl )
#        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancelVariant, self.SearchCtrl)
    
    def OnFigure( self, event ):
        "show Figure"
        if None == self.__Figurediag:
            self.__Figurediag = ShowOMAPFigureDiag( self, -1, self.GetTitle(), size = ( 900, 618 ),
                                                    OMAPLog = self.__OMAPLogData,
                                                    OMAPLogTime = self.__OMAPTimeData,
                                                    OMAPCompressFlag = self.__OMAPCompressFlag,
                                                    FrameLabel = self.FrameComBoBox.GetValue(),
                                                    CurNum = int( self.FrameNum.GetValue() ) - 1 )
        else:
            self.__Figurediag.UpdataView( self.__OMAPLogData,
                                          self.__OMAPTimeData,
                                          self.FrameComBoBox.GetValue(),
                                          int( self.FrameNum.GetValue() ) - 1 )
        self.__Figurediag.CenterOnScreen()
        if wx.ID_CANCEL == self.__Figurediag.ShowModal():
#            print "show Num"
            _Num = self.__Figurediag.getCurNum()
            self.FrameNum.SetValue( _Num + 1 )
            self.OnFrameNumChange( "event" )

        
    
    def OnSearchVariant( self, event ):
        "On Search Variant"
        _framelabel = self.FrameComBoBox.GetValue()
        _searchvalue = self.SearchCtrl.GetValue()
            
        if "" == _framelabel or None == _framelabel:
            print "OnSearchVariant error!"
            return        

        if "" == _searchvalue or None == _searchvalue: #no search for ""
            return 
        
        if self.__LastSearchVariant != ( _framelabel, _searchvalue ):
            #新搜索
            self.__LastSearchVariant = ( _framelabel, _searchvalue )
            self.__LastSearchInfo = OMAPParser.GetSearchVariantInfo( _framelabel, _searchvalue )
            if len( self.__LastSearchInfo ) > 0:
                self.__SearchVariantIndex = 0
            else:
                self.__SearchVariantIndex = -1
        else:
            #继续查找
            if len( self.__LastSearchInfo ) > 0:
                self.__SearchVariantIndex = ( self.__SearchVariantIndex + 1 ) if \
                                             ( self.__SearchVariantIndex < ( len( self.__LastSearchInfo ) - 1 ) )\
                                             else 0  #实现循环查找
            else:
                self.__SearchVariantIndex = -1  
        
        #进行查找显示
        if  self.__SearchVariantIndex >= 0:
            _info = self.__LastSearchInfo[self.__SearchVariantIndex] #[[label,page,row,col]]
            #开始翻页
            self.FramePageCBX.SetSelection( _info[1] - 1 )
            
            _Num = int( self.FrameNum.GetValue() ) - 1
            _Page = _info[1]
            
            _datadic = OMAPParser.getShowDataListByPage( self.__OMAPLogData, _framelabel, _Page, _Num, self.__OMAPCompressFlag )
            
            self.RefreshGrid( _datadic )
            #高亮显示
            self.SetNameValueBackgroundColour( _info[2] - 1, _info[3] - 1, wx.Colour( 255, 255, 0 ) )  
            #刷新grid
            self.ShowLog.Refresh()
        else:
            pass #没找到不做任何操作         
            
    def OnCloseWindow( self, event ):
        "On close windows"
        _case = CaseParser.getEditCaseInfo()[1]
        _framelabel = self.FrameComBoBox.GetValue()
        ShowOMAPLogFRM.__LastFRMSet[_case] = _framelabel
        self.GetParent().DelNumOfOMAPFrame()
        self.Destroy()
    
    def CheckSize( self, event ):
        "Check Size change"
        if self.__FrameSize != self.GetSize():
#            print "Size change!", self.GetSize()
            self.ShowLog.Resize( self.GetSize() )
            self.__FrameSize = self.GetSize()
            #其他控件现在先不进行操作，等有需求的时候再改
        
    def OnFramePageChange_CBX( self, event ):
        "On Frame Page Change"
        #将数据赋初始值
        _Num = int( self.FrameNum.GetValue() ) - 1
        
        _Page = int( self.FramePageCBX.GetValue() )
#        self.FramePage.SetValue( _Page )
        _Framelabel = self.FrameComBoBox.GetValue()
        
        
        _datadic = OMAPParser.getShowDataListByPage( self.__OMAPLogData, _Framelabel, _Page, _Num, self.__OMAPCompressFlag )
        
        self.RefreshGrid( _datadic )
    
    def OnFrameChange( self, event ):
        "On Frame Change"
#        print "1111", time.time()
        _Framelabel = self.FrameComBoBox.GetValue()
        _pagesize = OMAPParser.getOMAPFramePageSize( _Framelabel )
        _NumSize = OMAPParser.getOMAPFrameSize( self.__OMAPLogData, _Framelabel )
        self.FrameNum.SetValue( 1 )
        self.FrameNum.SetRange( 1, _NumSize )
#        self.FrameNum.SetRange( 1, _NumSize )
        self.FrameNum_Slider.SetValue( 1 )
        self.FrameNum_Slider.SetMax( _NumSize )
#        self.FramePage.SetValue( 1 )
#        self.FramePage.SetRange( 1, _pagesize )
        self.FramePageCBX.SetItems( [str( _i + 1 ) for _i in range( _pagesize )] )
        self.FramePageCBX.SetSelection( 0 )
        
        _Num = int( self.FrameNum.GetValue() ) - 1

        _Page = self.FramePageCBX.GetSelection() + 1
        if "" == _Framelabel or None == _Framelabel:
            print "OnFrameChange error!"
            return
        
        _datadic = OMAPParser.getShowDataListByPage( self.__OMAPLogData, _Framelabel, _Page, _Num, self.__OMAPCompressFlag )

        #更新位置
        self.BlockIdTxt.SetValue( self.__OMAPPosData[_Framelabel][_Num][0] )
        self.AbscissaTxt.SetValue( self.__OMAPPosData[_Framelabel][_Num][1] )
        self.TimeTxt.SetValue( self.__OMAPTimeData[_Framelabel][_Num] )
        try:
            stop = OMAPParser.getShowDataValue( self.__OMAPLogData[_Framelabel][_Num], 'TRAIN_MOTION.filtered_stop', *OMAPParser.OMAPFormat[_Framelabel]['TRAIN_MOTION.filtered_stop'] )
            self.TrainStopTxt.SetValue( stop )
            speed = OMAPParser.getShowDataValue( self.__OMAPLogData[_Framelabel][_Num], 'TRAIN_MOTION.train_speed', *OMAPParser.OMAPFormat[_Framelabel]['TRAIN_MOTION.train_speed'] )
            self.TrainSpeedTxt.SetValue( speed )
        except:
            pass        
        self.RefreshGrid( _datadic )    
    
    def OnFrameNumChange_slider( self, event ):
        "On Frame Page Change"
        _Num = self.FrameNum_Slider.GetValue() - 1
        self.FrameNum.SetValue( self.FrameNum_Slider.GetValue() )
#        _Page = self.FramePage.GetValue()
        _Page = self.FramePageCBX.GetSelection() + 1
        _Framelabel = self.FrameComBoBox.GetValue()
        if "" == _Framelabel or None == _Framelabel:
            print "OnFrameChange error!"
            return
        
        if self.CustomView.IsChecked():
            self.RefreshCustomGrid()
        else:
            _datadic = OMAPParser.getShowDataListByPage( self.__OMAPLogData, _Framelabel, _Page, _Num, self.__OMAPCompressFlag )
            self.RefreshGrid( _datadic )    
        #更新位置
        self.BlockIdTxt.SetValue( self.__OMAPPosData[_Framelabel][_Num][0] )
        self.AbscissaTxt.SetValue( self.__OMAPPosData[_Framelabel][_Num][1] )
        self.TimeTxt.SetValue( self.__OMAPTimeData[_Framelabel][_Num] )
        
        try:
            stop = OMAPParser.getShowDataValue( self.__OMAPLogData[_Framelabel][_Num], 'TRAIN_MOTION.filtered_stop', *OMAPParser.OMAPFormat[_Framelabel]['TRAIN_MOTION.filtered_stop'] )
            self.TrainStopTxt.SetValue( stop )
            speed = OMAPParser.getShowDataValue( self.__OMAPLogData[_Framelabel][_Num], 'TRAIN_MOTION.train_speed', *OMAPParser.OMAPFormat[_Framelabel]['TRAIN_MOTION.train_speed'] )
            self.TrainSpeedTxt.SetValue( speed )
        except:
            pass
    
    def OnFrameNumChange( self, event ):
        "On Frame Page Change"
        _Num = int( self.FrameNum.GetValue() ) - 1
        self.FrameNum_Slider.SetValue( int( self.FrameNum.GetValue() ) )
#        _Page = self.FramePage.GetValue()
        _Page = self.FramePageCBX.GetSelection() + 1
        _Framelabel = self.FrameComBoBox.GetValue()
        if "" == _Framelabel or None == _Framelabel:
            print "OnFrameChange error!"
            return
        
        if self.CustomView.IsChecked():
            self.RefreshCustomGrid()
        else:
            _datadic = OMAPParser.getShowDataListByPage( self.__OMAPLogData, _Framelabel, _Page, _Num, self.__OMAPCompressFlag )
            self.RefreshGrid( _datadic )      
        #更新位置
        self.BlockIdTxt.SetValue( self.__OMAPPosData[_Framelabel][_Num][0] )
        self.AbscissaTxt.SetValue( self.__OMAPPosData[_Framelabel][_Num][1] )
        self.TimeTxt.SetValue( self.__OMAPTimeData[_Framelabel][_Num] )
        try:
            stop = OMAPParser.getShowDataValue( self.__OMAPLogData[_Framelabel][_Num], 'TRAIN_MOTION.filtered_stop', *OMAPParser.OMAPFormat[_Framelabel]['TRAIN_MOTION.filtered_stop'] )
            self.TrainStopTxt.SetValue( stop )
            speed = OMAPParser.getShowDataValue( self.__OMAPLogData[_Framelabel][_Num], 'TRAIN_MOTION.train_speed', *OMAPParser.OMAPFormat[_Framelabel]['TRAIN_MOTION.train_speed'] )
            self.TrainSpeedTxt.SetValue( speed )
        except:
            pass
    
    #datadic:{(row,col):(label,Value),}
    def RefreshGrid( self, datadic ):
        "refresh Grid"
#        _Page = self.FramePage.GetValue()
        _Page = self.FramePageCBX.GetSelection() + 1
        _Framelabel = self.FrameComBoBox.GetValue()
        _data = []
        #(OMAP数据6*29)这里不能用[[‘’]*6]*29,这个会导致表的各个值有关联！！！
        for _i in range( self.OMAPRowsLen ): 
            _list = []
            for _j in range( self.OMAPColLen * 2 ):
                _list.append( "" )
            _data.append( _list ) 
        for _j in range( self.OMAPColLen ):
            for _i in range( self.OMAPRowsLen ):
                #先给背景赋初始值
                self.SetNameValueBackgroundColour( _i, _j, wx.WHITE )                 
                if True == datadic.has_key( ( _i + 1, _j + 1 ) ):
#                    print _i, _j, datadic[( _i + 1, _j + 1 )]
                    _data[_i][2 * _j] = datadic[( _i + 1, _j + 1 )][0]
                    _data[_i][2 * _j + 1] = datadic[( _i + 1, _j + 1 )][1]
                    
                    if "TRUE" in datadic[( _i + 1, _j + 1 )][1]:
                        self.ShowLog.SetCellTextColour( _i, 2 * _j + 1, wx.Color( 0, 0, 255 ) )
                    else:
                        self.ShowLog.SetCellTextColour( _i, 2 * _j + 1, wx.Color( 255, 0, 0 ) )
                        
                    if self.__IsHighlightLabel( _Framelabel, _Page, datadic[( _i + 1, _j + 1 )][0] ):
                        self.ShowLog.SetCellBackgroundColour( _i, 2 * _j, wx.Color( 0, 255, 0 ) )
                        
        self.ShowLog.RefreshData( _data )       
#        self.ShowLog.AutoSize()
        self.ShowLog.Refresh()
        self.ShowLog.Update()
        
    def RefreshCustomGrid( self ):
        _Framelabel = self.FrameComBoBox.GetValue()
        _Num = int( self.FrameNum.GetValue() ) - 1
        _data = []
        for _i in range( self.OMAPRowsLen ): 
            _list = []
            for _j in range( self.OMAPColLen * 2 ):
                self.ShowLog.SetCellBackgroundColour( _i, _j, wx.Color( 255, 255, 255 ) )
                _list.append( "" )
            _data.append( _list )
        
        bQuit = False
        n = -1
        for _j in range( self.OMAPColLen ):
            if ( bQuit ):
                break
            for _i in range( self.OMAPRowsLen ):
                n += 1
                while n < len( self.__HighlightItems ):
                    if self.__HighlightItems[n][0] == _Framelabel:
                        break
                    n += 1
                else:
                    bQuit = True
                    break
                # _datalst: [value, ...]
                _datalst = OMAPParser.getShowDataValueByLabel( self.__OMAPLogData,
                                                               self.__HighlightItems[n][0],
                                                               self.__HighlightItems[n][1],
                                                               _Num,
                                                               self.__HighlightItems[n][2],
                                                               self.__OMAPCompressFlag )
                _data[_i][2 * _j] = str( self.__HighlightItems[n][1] ) + ' ' + self.__HighlightItems[n][2];
                if len( _datalst ) > 0:
                    _data[_i][2 * _j + 1] = _datalst[0]
                else:
                    _data[_i][2 * _j + 1] = ''
                
                self.ShowLog.SetCellBackgroundColour( _i, 2 * _j, wx.Color( 0, 255, 0 ) )
                if 'TRUE' in _data[_i][2 * _j + 1]:
                    self.ShowLog.SetCellTextColour( _i, 2 * _j + 1, wx.Color( 0, 0, 255 ) )
                else:
                    self.ShowLog.SetCellTextColour( _i, 2 * _j + 1, wx.Color( 255, 0, 0 ) )

        self.ShowLog.RefreshData( _data )
        self.ShowLog.Refresh()
        self.ShowLog.Update()  
        
    def __IsHighlightLabel( self, framelabel, page, label ):
        for i in self.__HighlightItems:
            if ( i == [framelabel, page, label] ):
                return True
        return False
        
    def SetNameValueBackgroundColour( self, row, col, colour ):
        "Set Name Value Background Colour"
        self.ShowLog.SetCellBackgroundColour( row, 2 * col, colour )
        self.ShowLog.SetCellBackgroundColour( row, 2 * col + 1, colour )
        
    def UpDataGrid( self ):
        "up Data Grid"
        _data = []
        for _i in range( self.OMAPRowsLen ): #(OMAP数据6*29)
            _list = []
            for _j in range( self.OMAPColLen * 2 ):
                _list.append( "" )
            _data.append( _list ) 
        self.ShowLog.setCustable( _data )
        _fontValue = GetFont( 10, Weight = wx.BOLD, Face = "Calibri" )
        _fontName = GetFont( 10, Weight = wx.BOLD, Face = "Calibri" )
        for _j in range( self.OMAPColLen * 2 ):
            if _j % 2 == 1:
                for _i in range( self.OMAPRowsLen ):
                    self.ShowLog.SetCellFont( _i, _j, _fontValue )
                    self.ShowLog.SetCellTextColour( _i, _j, wx.Color( 255, 0, 0 ) )
            else:
                for _i in range( self.OMAPRowsLen ):
                    self.ShowLog.SetCellFont( _i, _j, _fontName )                
            
        #赋初始值
        self.OnFrameChange( "event" )


class DistanceTransFromFrm( wx.Frame ):
    
    __PreSce = None
    __trainInfo = None
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
                  style = wx.DEFAULT_FRAME_STYLE, CaseEditNode = None ):
        wx.Frame.__init__( self, parent, ID, title, pos, size, style )
        self.__casenode = CaseEditNode        
        self.panel_1 = wx.Panel( self, -1 )
        self.label_1 = wx.StaticText( self.panel_1, -1, u"车辆坐标(毫米)" )
        self.text_ctrl_1 = wx.TextCtrl( self.panel_1, -1, "" )
        self.button_1 = wx.Button( self.panel_1, -1, "-->" )
        self.label_2 = wx.StaticText( self.panel_1, -1, "BlockID" )
        self.text_ctrl_2 = wx.TextCtrl( self.panel_1, -1, "" )
        self.label_4 = wx.StaticText( self.panel_1, -1, "" )
        self.label_5 = wx.StaticText( self.panel_1, -1, "" )
        self.button_2 = wx.Button( self.panel_1, -1, "<--" )
        self.label_3 = wx.StaticText( self.panel_1, -1, u"Absicssa(毫米)" )
        self.text_ctrl_3 = wx.TextCtrl( self.panel_1, -1, "" )

        self.__set_properties()
        self.__do_layout()

        self.Bind( wx.EVT_BUTTON, self.onTrain2Block, self.button_1 )
        self.Bind( wx.EVT_BUTTON, self.onBlock2Train, self.button_2 )
        # end wxGlade
        #获取相关路径位置
        _MapBinPath = self.__casenode.getMapPath()
        _MapTxtPath = self.__casenode.getTxtMapPath()
        _TrainRoutePath = self.__casenode.getScenarioPath() + "/train_route.xml"
        
        #初始化计算距离所需的数据
        simdata.MapData.loadMapData( _MapBinPath,
                                     _MapTxtPath,
                                     Type = "Edit" )
        simdata.TrainRoute.loadTrainData( _TrainRoutePath,
                                          Type = "Edit" )
#        self.__PreSce = Senariopreproccess(r'./scenario/train_route.xml')
#        self.__trainInfo = commlib.loadTrainRout(r'./scenario/train_route.xml')
#        self.__PreSce.getblockinfolist(r'./datafile/atpCpu1Binary.txt', r'./datafile/atpText.txt')

    def __set_properties( self ):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle( u"坐标转换工具" )
        # end wxGlade

    def __do_layout( self ):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer( wx.VERTICAL )
        grid_sizer_1 = wx.GridSizer( 2, 5, 0, 0 )
        grid_sizer_1.Add( self.label_1, 0, 0, 0 )
        grid_sizer_1.Add( self.text_ctrl_1, 0, 0, 0 )
        grid_sizer_1.Add( self.button_1, 0, 0, 0 )
        grid_sizer_1.Add( self.label_2, 0, 0, 0 )
        grid_sizer_1.Add( self.text_ctrl_2, 0, 0, 0 )
        grid_sizer_1.Add( self.label_4, 0, 0, 0 )
        grid_sizer_1.Add( self.label_5, 0, 0, 0 )
        grid_sizer_1.Add( self.button_2, 0, 0, 0 )
        grid_sizer_1.Add( self.label_3, 0, 0, 0 )
        grid_sizer_1.Add( self.text_ctrl_3, 0, 0, 0 )
        self.panel_1.SetSizer( grid_sizer_1 )
        sizer_1.Add( self.panel_1, 1, wx.EXPAND, 0 )
        self.SetSizer( sizer_1 )
        sizer_1.Fit( self )
        self.Layout()
        # end wxGlade

    def onTrain2Block( self, event ): # wxGlade: MyFrame.<event_handler>
        #print "Event handler `onTrain2Block' not implemented"
        #event.Skip()
        _ablocation = int( self.text_ctrl_1.GetValue() )
        _blockid, _abscissa = simdata.TrainRoute.getBlockandAbs( _ablocation,
                                                                 Type = "Edit" )
        
        self.text_ctrl_2.SetValue( str( _blockid ) )
        self.text_ctrl_3.SetValue( str( _abscissa ) )

    def onBlock2Train( self, event ): # wxGlade: MyFrame.<event_handler>
        #print "Event handler `onBlock2Train' not implemented"
        _blockid = int( self.text_ctrl_2.GetValue() )
        _abscissa = int( self.text_ctrl_3.GetValue() )

        _ablocation = simdata.TrainRoute.getabsolutedistance( _blockid,
                                                              _abscissa,
                                                              Type = "Edit" )
        self.text_ctrl_1.SetValue( str( _ablocation ) )


#--------------------------------------------------------------------
#通用需求OP的配置界面
#--------------------------------------------------------------------
class CommRuleConfigFrm( wx.Frame ):
    __CommRule = None #保存CommRule实例
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE
            ):      
        wx.Frame.__init__( self, parent, ID, title, pos, size, style )
        panel = wx.Panel( self, -1 ) #frame必须有panel，否则一些事件响应会有问题
        self.__HighlightItems = [] # [[framelabel, page, label],...] ,需要label在具体某一page中是唯一的
        ShowOMAPLogFRM.__CustomStoreDir = './TPConfig/custom/'
        try:
            os.makedirs( ShowOMAPLogFRM.__CustomStoreDir )
        except:
            pass        
    
        
    def BindEvents( self ):
        "bind events"



class AnalysisVarConfigWizard( wiz.WizardPageSimple ):
    '''
    Analysis variants configuration wizard
    '''
    
    __LoadFileFlag = False
    
    __FormatVariantShowList = [] #由于Format中的变量较多，因此，这里需要维护一个固定的地址
    def __init__( self, parent, title = None, size = wx.DefaultSize, pos = wx.DefaultPosition, Create = True, AnalysisEditNode = None ):
#        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        wiz.WizardPageSimple.__init__( self, parent )
        self.sizer = makePageTitle( self, title )
            
        self.__analysisNode = AnalysisEditNode
        
        #创建数据来源类型 comboBox
        self.__DataTypeCombo = wx.ComboBox( self, -1, 'OMAPFMT', \
                                            size = ( 150, -1 ), \
                                            choices = ['OMAPFMT', 'CONST', 'USRDEF', 'MAP'],
                                            style = wx.CB_DROPDOWN )
        self.__DataTypeCombo.SetSelection( -1 )
        
        self.__DataNameList = wx.ListBox( self, -1, size = ( 150, 100 ), \
                                          choices = [],
                                          style = wx.LB_SINGLE )
        SetCusFont( self.__DataNameList, 12, Face = "Calibri" )
        box1 = wx.BoxSizer( wx.VERTICAL )
        box1.Add( self.__DataTypeCombo, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box1.Add( self.__DataNameList, 10, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        #属性和描述
        label1 = wx.StaticText( self, -1, "Attrubute:", size = ( 150, -1 ) )
        self.__NewAttrText = wx.TextCtrl( self, -1, "", size = ( 150, -1 ), style = wx.TE_MULTILINE )
        self.__NewAttrText.SetEditable( False )
        label2 = wx.StaticText( self, -1, "Description:", size = ( 150, -1 ) )
        self.__NewDesText = wx.TextCtrl( self, -1, "", size = ( 150, -1 ), style = wx.TE_MULTILINE )

        SetCusFont( self.__NewAttrText, 12, Face = "Calibri" )
        SetCusFont( self.__NewDesText, 12, Face = "Calibri" )
        SetCusFont( label1, 12, Face = "Times New Roman" )
        SetCusFont( label2, 12, Face = "Times New Roman" )
        
        box2 = wx.BoxSizer( wx.VERTICAL )
        box2.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box2.Add( self.__NewAttrText, 4, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box2.Add( label2, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box2.Add( self.__NewDesText, 5, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
                
        self.__AddVarButton = wx.Button( self, -1, "= >", size = ( 100, -1 ) )
        self.__RemoveVarButton = wx.Button( self, -1, "< =", size = ( 100, -1 ) )
        
        box31 = wx.BoxSizer( wx.VERTICAL )
        box32 = wx.BoxSizer( wx.VERTICAL )
        box33 = wx.BoxSizer( wx.VERTICAL )
        box34 = wx.BoxSizer( wx.VERTICAL )
        box35 = wx.BoxSizer( wx.VERTICAL )
        
        box33.Add( self.__AddVarButton, 0, wx.ALIGN_CENTER_VERTICAL , 5 )
        box34.Add( self.__RemoveVarButton, 0, wx.ALIGN_CENTER_VERTICAL , 5 )
        box3 = wx.BoxSizer( wx.VERTICAL )        
        box3.Add( box31, 1, wx.ALIGN_CENTRE , 5 )
        box3.Add( box32, 1, wx.ALIGN_CENTRE , 5 )
        box3.Add( box33, 1, wx.ALIGN_CENTRE , 5 )
        box3.Add( box34, 1, wx.ALIGN_CENTRE , 5 )
        box3.Add( box35, 1, wx.ALIGN_CENTRE , 5 )  
              
        label1 = wx.StaticText( self, -1, "Variant List:", size = ( 150, -1 ) )
        SetCusFont( label1, 12, Face = "Times New Roman" )
        self.__VariantList = wx.ListBox( self, -1, size = ( 150, 450 ), \
                                          choices = [],
                                          style = wx.LB_SINGLE )
        SetCusFont( self.__VariantList, 12, Face = "Calibri" )
        box4 = wx.BoxSizer( wx.VERTICAL )
        box4.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box4.Add( self.__VariantList, 10, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        #属性和描述
        label1 = wx.StaticText( self, -1, "Type:", size = ( 150, -1 ) )
        self.__ExistTypeText = wx.TextCtrl( self, -1, "", size = ( 150, -1 ), style = wx.TE_MULTILINE )
        self.__ExistTypeText.SetEditable( False )
        label2 = wx.StaticText( self, -1, "Attrubute:", size = ( 150, -1 ) )
        self.__ExistAttrText = wx.TextCtrl( self, -1, "", size = ( 150, -1 ), style = wx.TE_MULTILINE )
        self.__ExistAttrText.SetEditable( False )
        label3 = wx.StaticText( self, -1, "Description:", size = ( 150, -1 ) )
        self.__ExistDesText = wx.TextCtrl( self, -1, "", size = ( 150, -1 ), style = wx.TE_MULTILINE )
        
        SetCusFont( label1, 12, Face = "Times New Roman" )
        SetCusFont( label2, 12, Face = "Times New Roman" )
        SetCusFont( label3, 12, Face = "Times New Roman" )

        box5 = wx.BoxSizer( wx.VERTICAL )
        box5.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box5.Add( self.__ExistTypeText, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box5.Add( label2, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box5.Add( self.__ExistAttrText, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box5.Add( label3, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box5.Add( self.__ExistDesText, 4, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )

        
        _Framebox = wx.BoxSizer( wx.HORIZONTAL )
        _Framebox.Add( box1, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box2, 3, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box3, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box4, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        _Framebox.Add( box5, 3, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.BindEvents()
        
        self.sizer.Add( _Framebox, 8, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        self.SetSizer( self.sizer )
        self.sizer.Fit( self )          
        
    def UpdateView( self ):
        "update view"
        #加载文件
        if not self.__LoadFileFlag:
            _tmpdir = CaseParser.getEditCaseInfo()[-1] + "/Script/analysis"
            _tmppath = _tmpdir + "/autoAnalysis.xml"
            #判断是否存在分析文件不存在则放入默认值
            if not os.path.exists( _tmppath ):
                _FromFolder = commlib.joinPath( commlib.getCurFileDir(), "/default case/analysis" )
                filehandle.CopyFolder( _FromFolder, _tmpdir )
                print "can't find analysis file and we will use the default xml to create a new one."
            #在程序路径下找相关的配置文件
            _formatpath = commlib.getCurFileDir() + "/TPConfig/OMAPFormat.xml"
            _usrDefpath = commlib.getCurFileDir() + "/autoAnalysis/config/usrData.xml"
            self.__analysisNode.iniAnalysisEdit( _tmppath, _formatpath, _usrDefpath )
        self.__DataTypeCombo.SetSelection( 0 ) #设置
        _Type = self.__DataTypeCombo.GetValue()
        #获取Namelist
        if not self.__LoadFileFlag:
            self.__FormatVariantShowList = self.__analysisNode.getVarListWithoutSelected( "OMAPFMT" )
        self.__DataNameList.SetItems( self.__FormatVariantShowList )
        self.__DataNameList.SetSelection( -1 )
        
        #VariantList
        self.__VariantList.SetItems( self.__analysisNode.getVarNameList() )
        self.__VariantList.SetSelection( -1 )
        self.__LoadFileFlag = True
       
    def BindEvents( self ):
        "bind events"
        self.Bind( wx.EVT_BUTTON, self.OnAddVarToList, self.__AddVarButton )
        self.Bind( wx.EVT_BUTTON, self.OnRemoveVarToList, self.__RemoveVarButton )
        
        self.Bind( wx.EVT_COMBOBOX, self.OnDataComboChange, self.__DataTypeCombo )
        self.Bind( wx.EVT_TEXT, self.OnEditExistDes, self.__ExistDesText )
        self.Bind( wx.EVT_LISTBOX, self.OnDataNameChange, self.__DataNameList )
        self.Bind( wx.EVT_LISTBOX, self.OnVarSelectChange, self.__VariantList )  
    
    def OnDataNameChange( self, event ):
        "OnDataNameChange"
        _Type = self.__DataTypeCombo.GetValue()
        
        #['OMAPFMT', 'CONST', 'USRDEF', 'MAP']
        if _Type in ['OMAPFMT', 'CONST', 'MAP']: 
            self.__NewAttrText.SetValue( self.__DataNameList.GetItems()[self.__DataNameList.GetSelection()] )
        elif 'USRDEF' == _Type:
            _content = self.__analysisNode.getUsrDefVarContentByName( self.__DataNameList.GetItems()[self.__DataNameList.GetSelection()] ) 
            self.__NewAttrText.SetValue( _content[0] )
            self.__NewDesText.SetValue( _content[1] )
        
    def OnVarSelectChange( self, event ):
        "OnVarSelectChange"
        _index = self.__VariantList.GetSelection()
        if _index < 0:
            "do nothing"
            self.__ExistTypeText.SetValue( "" )
            self.__ExistAttrText.SetValue( "" )
            self.__ExistDesText.SetValue( "" ) 
            self.__ExistDesText.SetEditable( False )           
            return
        self.__ExistDesText.SetEditable( True )
        _Name = self.__VariantList.GetItems()[_index]
        
        _contentList = self.__analysisNode.getVarInfoByName( _Name )
        self.__ExistTypeText.SetValue( _contentList[0] )
        self.__ExistAttrText.SetValue( _contentList[2] )
        self.__ExistDesText.SetValue( _contentList[-1] )
    
    def OnAddVarToList( self, event ):
        "OnAddVarToList"
        _index = self.__DataNameList.GetSelection()
        _Type = self.__DataTypeCombo.GetValue()
        if _index < 0 or  _Type not in ['OMAPFMT', 'CONST', 'USRDEF', 'MAP']:
            print "OnAddVarToList Error!"
            return
        _Name = self.__DataNameList.GetItems()[_index]
        _Attr = self.__NewAttrText.GetValue()
        _Des = self.__NewDesText.GetValue()
        self.__analysisNode.addOneVar( _Name, _Type, _Attr, _Des )
        
        self.__VariantList.SetItems( self.__analysisNode.getVarNameList() )
        for _i, _content in enumerate( self.__analysisNode.getVarNameList() ):
            if _content == _Name:
                self.__VariantList.SetSelection( _i )
                break
            
        #更新显示
        _content = self.__analysisNode.getVarInfoByName( _Name )
        self.__ExistTypeText.SetValue( _content[0] )
        self.__ExistAttrText.SetValue( _content[2] )
        self.__ExistDesText.SetValue( _content[-1] )
        
        #更新左边的list
        self.__DataNameList.Delete( _index )
        self.__DataNameList.Refresh()        
#        print "6", time.time()
        self.__DataNameList.SetSelection( _index - 1 if _index > 0 else -1 )
        self.OnDataNameChange( event )
        
    def OnRemoveVarToList( self, event ):
        "OnRemoveVarToList"
        _index = self.__VariantList.GetSelection()
        if _index < 0:
            wx.MessageBox( "Please select a variant to remove!" )
            return
        
        _Name = self.__VariantList.GetItems()[_index]
        self.__analysisNode.delOneVar( _Name )
        
        #更新显示
        self.__VariantList.SetItems( self.__analysisNode.getVarNameList() )
        self.__VariantList.SetSelection( _index - 1 if _index > 0 else -1 )
        self.OnVarSelectChange( event )
        
        _Type = self.__DataTypeCombo.GetValue()
        _tmpindex = None
        for _i, _tmpName in enumerate( self.__DataNameList.GetItems() ):
            if cmp( _tmpName, _Name ) > 0: #需找插入的位置
                _tmpindex = _i
                break
        self.__DataNameList.Insert( _Name, _tmpindex )
#        self.__DataNameList.SetItems( self.__analysisNode.getVarListWithoutSelected( _Type ) )
        
    def OnDataComboChange( self, event ):
        "OnDataComboChange"
        _Type = self.__DataTypeCombo.GetValue()
        if "USRDEF" == _Type:
            self.__NewDesText.SetEditable( False )
        else:
            self.__NewDesText.SetEditable( True )
        #获取Namelist
        self.__DataNameList.SetItems( self.__analysisNode.getSrcVarNameDic()[_Type] )
        
    def OnEditExistDes( self, event ):
        "OnEditExistDes"
        _index = self.__VariantList.GetSelection()
        if _index < 0:
            print "OnEditExistDes Error!"
            return
        _Name = self.__VariantList.GetItems()[_index]
        _Type = self.__ExistTypeText.GetValue()
        _Attr = self.__ExistAttrText.GetValue()
        _Des = self.__ExistDesText.GetValue()
        self.__analysisNode.modOneVar( _Name, _Type, _Attr, _Des )
    
class AnalysisRuleConfigWizard( wiz.WizardPageSimple ):
    '''
    Analysis rules configuration wizard
    '''
    
    def __init__( self, parent, title = None, size = wx.DefaultSize, pos = wx.DefaultPosition, AnalysisEditNode = None ):
#        wx.Panel.__init__( self, parent, -1, size = size, pos = pos )
        wiz.WizardPageSimple.__init__( self, parent )
        self.sizer = makePageTitle( self, title )
            
        self.__analysisNode = AnalysisEditNode
        
        #Rule List
        label1 = wx.StaticText( self, -1, "Rule List:", size = ( 100, -1 ) )
        self.__RuleList = wx.ListBox( self, -1, size = ( 100, -1 ), \
                                      choices = [],
                                      style = wx.LB_SINGLE ) 
               

        SetCusFont( self.__RuleList, 12, Weight = wx.BOLD, Face = "Calibri" )
        box1 = wx.BoxSizer( wx.VERTICAL )
        box1.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box1.Add( self.__RuleList, 11, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        
        #单条Rule的编辑
        label1 = wx.StaticText( self, -1, "Pos.Start:", size = ( 100, -1 ) )
        self.__PosStartText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ) )
        label2 = wx.StaticText( self, -1, "Pos.End:", size = ( 100, -1 ) )
        self.__PosEndText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ) )
        label3 = wx.StaticText( self, -1, "Time.Start:", size = ( 100, -1 ) )
        self.__TimeStartText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ) )
        label4 = wx.StaticText( self, -1, "Time.End:", size = ( 100, -1 ) )
        self.__TimeEndText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ) )

        SetCusFont( self.__PosStartText, 12, Weight = wx.BOLD, Face = "Calibri" )
        SetCusFont( self.__PosEndText, 12, Weight = wx.BOLD, Face = "Calibri" )
        SetCusFont( self.__TimeStartText, 12, Weight = wx.BOLD, Face = "Calibri" )
        SetCusFont( self.__TimeEndText, 12, Weight = wx.BOLD, Face = "Calibri" )
        
        box2 = wx.BoxSizer( wx.HORIZONTAL )
        box2.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box2.Add( self.__PosStartText, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        box2.Add( label2, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box2.Add( self.__PosEndText, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        box2.Add( label3, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box2.Add( self.__TimeStartText, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        box2.Add( label4, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box2.Add( self.__TimeEndText, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        
        label1 = wx.StaticText( self, -1, "Pos.Description:", size = ( 100, -1 ) )
        self.__PosDesText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ) )
        label2 = wx.StaticText( self, -1, "Time.Description:", size = ( 100, -1 ) )
        self.__TimeDesText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ) )        
        box11 = wx.BoxSizer( wx.HORIZONTAL )               
        box11.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box11.Add( self.__PosDesText, 3, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        box11.Add( label2, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box11.Add( self.__TimeDesText, 3, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )        
        
        #OP部分
        #Rule List
        label1 = wx.StaticText( self, -1, "OP List:", size = ( 100, -1 ) )
        self.__OPList = wx.ListBox( self, -1, size = ( 100, -1 ), \
                                    choices = [],
                                    style = wx.LB_SINGLE )         
        box3 = wx.BoxSizer( wx.VERTICAL )
        box3.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box3.Add( self.__OPList, 10, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )        
       
        #condition
        label1 = wx.StaticText( self, -1, "Condition:", size = ( 60, -1 ) )
        self.__ConditionContentText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ), style = wx.TE_MULTILINE )       
        self.__ConditionContentText.SetEditable( False )
        self.__EditConditionButton = wx.Button( self, -1, "Edit...", size = ( 60, -1 ) )
        box12 = wx.BoxSizer( wx.HORIZONTAL )
        box12.Add( label1, 4, wx.ALIGN_LEFT | wx.ALL, 3 )
        box12.Add( self.__ConditionContentText, 11, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 ) 
        box12.Add( self.__EditConditionButton, 3, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )        
        
        label1 = wx.StaticText( self, -1, "Description:", size = ( 60, -1 ) )
        self.__ConditionDesText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ), style = wx.TE_MULTILINE )
        
        box13 = wx.BoxSizer( wx.HORIZONTAL )
        box13.Add( label1, 4, wx.ALIGN_LEFT | wx.ALL, 3 )
        box13.Add( self.__ConditionDesText, 11, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )         
        
        box4 = wx.StaticBoxSizer( wx.StaticBox( self, -1, "Condition Config Panel" ), wx.HORIZONTAL )
        box4.Add( box12, 6, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 3 )
        box4.Add( box13, 5, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )         

        #result
        label1 = wx.StaticText( self, -1, "Result List:", size = ( 100, -1 ) )
        self.__ResultList = wx.ListBox( self, -1, size = ( 100, -1 ), \
                                        choices = [],
                                        style = wx.LB_SINGLE )         
        box5 = wx.BoxSizer( wx.VERTICAL )
        box5.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box5.Add( self.__ResultList, 5, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 ) 
        
        label1 = wx.StaticText( self, -1, "Result:", size = ( 100, -1 ) )
        self.__ResultContentText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ) , style = wx.TE_MULTILINE )       
        self.__ResultContentText.SetEditable( False )
        self.__EditResultButton = wx.Button( self, -1, "Edit...", size = ( 60, -1 ) )
        label2 = wx.StaticText( self, -1, "Description:", size = ( 100, -1 ) )
        self.__ResultDesText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ) , style = wx.TE_MULTILINE )       
        self.__AddOneResultButton = wx.Button( self, -1, "Add Result", size = ( 100, -1 ) )
        self.__DelOneResultButton = wx.Button( self, -1, "Del Result", size = ( 100, -1 ) )
        
        box15 = wx.BoxSizer( wx.VERTICAL )
        box15.Add( self.__AddOneResultButton, 0, wx.ALIGN_RIGHT | wx.ALL | wx.ALIGN_BOTTOM, 3 )
        box15.Add( self.__DelOneResultButton, 0, wx.ALIGN_RIGHT | wx.ALL | wx.ALIGN_BOTTOM, 3 )
        
        box16 = wx.BoxSizer( wx.VERTICAL )
        box16.Add( label2, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box16.Add( self.__ResultDesText, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )        
        
        box17 = wx.BoxSizer( wx.HORIZONTAL )
        box17.Add( box16, 3, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 3 )
        box17.Add( box15, 1, wx.ALIGN_RIGHT | wx.ALL | wx.ALIGN_BOTTOM , 3 )        
        
        box20 = wx.BoxSizer( wx.HORIZONTAL )
        box20.Add( self.__ResultContentText, 5, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 3 )
        box20.Add( self.__EditResultButton, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND , 3 )         
        
        box6 = wx.BoxSizer( wx.VERTICAL )
        box6.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 3 )
        box6.Add( box20, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )         
        box6.Add( box17, 3, wx.ALIGN_LEFT | wx.ALL, 0 )        
        
        box19 = wx.StaticBoxSizer( wx.StaticBox( self, -1, "Result Config Panel" ), wx.HORIZONTAL )
        box19.Add( box5, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 3 )
        box19.Add( box6, 4, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )         
        
        label1 = wx.StaticText( self, -1, "OP Type:", size = ( 100, -1 ) )
        self.__OPTypeComBox = wx.ComboBox( self, -1, "UserDef", ( 80, -1 ), ( 160, -1 ), ["UserDef", "CommDef"], wx.CB_DROPDOWN )
        label2 = wx.StaticText( self, -1, "Comm OP ID:", size = ( 100, -1 ) )
        #这里的combox需要从COMMOP里面获取信息
        self.__CommOPIDCombox = wx.ComboBox( self, -1, "", ( 80, -1 ), ( 160, -1 ), [], wx.CB_DROPDOWN )
        self.__AddOneOPButton = wx.Button( self, -1, "Add OP", size = ( 100, -1 ) )
        self.__DelOneOPButton = wx.Button( self, -1, "Del OP", size = ( 100, -1 ) )
        box18 = wx.StaticBoxSizer( wx.StaticBox( self, -1, "OP Handle Panel" ), wx.VERTICAL )
        box18.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 6 )
        box18.Add( self.__OPTypeComBox, 1, wx.ALIGN_LEFT | wx.ALL, 6 )
        box18.Add( label2, 1, wx.ALIGN_LEFT | wx.ALL, 6 )
        box18.Add( self.__CommOPIDCombox, 1, wx.ALIGN_LEFT | wx.ALL, 6 )
        box18.Add( self.__AddOneOPButton, 0, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 6 )
        box18.Add( self.__DelOneOPButton, 0, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 6 )
        
        box7 = wx.BoxSizer( wx.HORIZONTAL )
        box7.Add( box19, 3, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 0 )
        box7.Add( box18, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 0 )
        
        box8 = wx.BoxSizer( wx.VERTICAL )
        box8.Add( box4, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 3 )
        box8.Add( box7, 3, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )               

        box9 = wx.StaticBoxSizer( wx.StaticBox( self, -1, "OP Config Panel" ), wx.HORIZONTAL )
        box9.Add( box3, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 3 )
        box9.Add( box8, 6, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        
        label1 = wx.StaticText( self, -1, "Description:", size = ( 100, -1 ) )
        self.__RuleDesText = wx.TextCtrl( self, -1, "", size = ( 100, -1 ) )
        self.__AddOneRuleButton = wx.Button( self, -1, "Add Rule", size = ( 100, -1 ) )
        self.__DelOneRuleButton = wx.Button( self, -1, "Del Rule", size = ( 100, -1 ) )
        
        box14 = wx.BoxSizer( wx.HORIZONTAL )
        box14.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL , 3 )
        box14.Add( self.__RuleDesText, 5, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 3 )   
        box14.Add( self.__AddOneRuleButton, 0, wx.ALIGN_RIGHT | wx.ALL , 3 )
        box14.Add( self.__DelOneRuleButton, 0, wx.ALIGN_RIGHT | wx.ALL , 3 )   

        
        box10 = wx.StaticBoxSizer( wx.StaticBox( self, -1, "Rule Config Panel" ), wx.VERTICAL )
        box10.Add( box2, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 3 )
        box10.Add( box11, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 3 )
        box10.Add( box9, 9, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        box10.Add( box14, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        
        _Framebox = wx.BoxSizer( wx.HORIZONTAL )
        _Framebox.Add( box1, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        _Framebox.Add( box10, 7, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        
        self.BindEvents()
        
        self.sizer.Add( _Framebox, 8, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 3 )
        
        self.SetSizer( self.sizer )
        self.sizer.Fit( self )          


    
    def UpdateView( self ):
        "update view"
        self.__RuleList.SetItems( self.__analysisNode.getRuleNameList() )
        self.__RuleList.SetSelection( -1 )
        
        #先设置好库OP的combox
        self.__CommOPIDCombox.SetItems( self.__analysisNode.getCommOPNameList() )
        self.__CommOPIDCombox.SetSelection( 0 )
        #禁用其他的控件
        self.EnableAllRuleCtl( False )
        self.__AddOneRuleButton.Enable( True )
#        print self.__analysisNode
        
    
    def EnablePosCtl( self, Flag ):
        self.__PosStartText.Enable( Flag )
        self.__PosEndText.Enable( Flag )
        self.__PosDesText.Enable( Flag )
    
    def EnableTimeCtl( self, Flag ):
        self.__TimeDesText.Enable( Flag )
        self.__TimeEndText.Enable( Flag )
        self.__TimeStartText.Enable( Flag )
    
    def EnableConditionCtl( self, Flag ):
        self.__ConditionContentText.Enable( Flag )
        self.__EditConditionButton.Enable( Flag )
        self.__ConditionDesText.Enable( Flag )
        
    def EnableResultCtl( self, Flag ):
        self.__ResultContentText.Enable( Flag )
        self.__EditResultButton.Enable( Flag )
        self.__ResultDesText.Enable( Flag )
    
    def EnableAllResultCtl( self, Flag ):
        self.EnableResultCtl( Flag )
        self.__ResultList.Enable( Flag )
        self.__AddOneResultButton.Enable( Flag )
        self.__DelOneResultButton.Enable( Flag )
        
    def EnableAllOPCtl( self, Flag ):
        self.EnableConditionCtl( Flag )
        self.EnableAllResultCtl( Flag )
        self.__AddOneOPButton.Enable( Flag )
        self.__DelOneOPButton.Enable( Flag )
        self.__OPList.Enable( Flag )
        self.__OPTypeComBox.Enable( Flag )
        self.__CommOPIDCombox.Enable( Flag )
    
    def EnableAllRuleCtl( self, Flag ):
        self.EnablePosCtl( Flag )
        self.EnableTimeCtl( Flag )
        self.EnableAllOPCtl( Flag )
        self.__RuleDesText.Enable( Flag )
        self.__AddOneRuleButton.Enable( Flag )
        self.__DelOneRuleButton.Enable( Flag )
    
    def BindEvents( self ):
        "bind events"
        self.Bind( wx.EVT_LISTBOX, self.OnRuleSelChange, self.__RuleList )
        self.Bind( wx.EVT_TEXT, self.OnPosStartInfoChange, self.__PosStartText )
        self.Bind( wx.EVT_TEXT, self.OnPosEndInfoChange, self.__PosEndText )
        self.Bind( wx.EVT_TEXT, self.OnPosDesInfoChange, self.__PosDesText )
        self.Bind( wx.EVT_TEXT, self.OnTimeStartInfoChange, self.__TimeStartText )
        self.Bind( wx.EVT_TEXT, self.OnTimeEndInfoChange, self.__TimeEndText )
        self.Bind( wx.EVT_TEXT, self.OnTimeDesInfoChange, self.__TimeDesText )
        self.Bind( wx.EVT_TEXT, self.OnRuleDesChange, self.__RuleDesText )
        self.Bind( wx.EVT_LISTBOX, self.OnOPSelChange, self.__OPList )
        self.Bind( wx.EVT_LISTBOX, self.OnResultSelChange, self.__ResultList )
        self.Bind( wx.EVT_TEXT, self.OnConditionDesChange, self.__ConditionDesText )
        self.Bind( wx.EVT_TEXT, self.OnResultDesChange, self.__ResultDesText )
        self.Bind( wx.EVT_COMBOBOX, self.OnOPTypeChange, self.__OPTypeComBox )
        self.Bind( wx.EVT_COMBOBOX, self.OnCommOPComBoxChange, self.__CommOPIDCombox )
        self.Bind( wx.EVT_BUTTON, self.OnAddRule, self.__AddOneRuleButton )
        self.Bind( wx.EVT_BUTTON, self.OnDelRule, self.__DelOneRuleButton )
        self.Bind( wx.EVT_BUTTON, self.OnAddOP, self.__AddOneOPButton )
        self.Bind( wx.EVT_BUTTON, self.OnDelOP, self.__DelOneOPButton )
        self.Bind( wx.EVT_BUTTON, self.OnAddReslut, self.__AddOneResultButton )
        self.Bind( wx.EVT_BUTTON, self.OnDelResult, self.__DelOneResultButton )
        self.Bind( wx.EVT_BUTTON, self.OnEditCondition, self.__EditConditionButton )
        self.Bind( wx.EVT_BUTTON, self.OnEditResult, self.__EditResultButton )
    
    def OnEditResult( self, event ):
        _diag = EditExpDiag( self,
                             - 1,
                             "Result Expression Config",
                              AnalysisNode = self.__analysisNode,
                              ExpStr = self.__ResultContentText.GetValue() )
        _diag.CenterOnScreen()
        
        if _diag.ShowModal() == wx.ID_OK:
            if not _diag.checkExp():
                wx.MessageBox( "Error Expression and the Expression will not change!", "Error" )
                return
            _Value = _diag.getExpValue()
            self.__ResultContentText.SetValue( _Value )
            #修改字典
            _ruleIndex = self.__RuleList.GetSelection()
            _RuleName = self.__RuleList.GetItems()[_ruleIndex]
            _opIndex = self.__OPList.GetSelection()
            _opName = self.__OPList.GetItems()[_opIndex]
            _resIndex = self.__ResultList.GetSelection()
            _ruleDic = ExpressionParser.transStringToRuleDic( self.__ResultContentText.GetValue() )
            self.__analysisNode.modOneRuleOPResultContent( _RuleName, _opName, _opIndex, _resIndex, _ruleDic )
        
        _diag.Destroy()        
    
    def OnEditCondition( self, event ):
        _diag = EditExpDiag( self,
                             - 1,
                             "Condition Expression Config",
                             AnalysisNode = self.__analysisNode,
                             ExpStr = self.__ConditionContentText.GetValue() )
        _diag.CenterOnScreen()
        
        if _diag.ShowModal() == wx.ID_OK:
            if not _diag.checkExp():
                wx.MessageBox( "Error Expression and the Expression will not change!", "Error" )
                return
            _Value = _diag.getExpValue()
            self.__ConditionContentText.SetValue( _Value )
            #修改字典
            _ruleIndex = self.__RuleList.GetSelection()
            _RuleName = self.__RuleList.GetItems()[_ruleIndex]
            _opIndex = self.__OPList.GetSelection()
            _opName = self.__OPList.GetItems()[_opIndex]
            _ruleDic = ExpressionParser.transStringToRuleDic( self.__ConditionContentText.GetValue() )
            self.__analysisNode.modOneRuleOPCondContent( _RuleName, _opName, _opIndex, _ruleDic )
        
        _diag.Destroy()
    
    def OnDelResult( self, event ):
        _ruleIndex = self.__RuleList.GetSelection()
        _opIndex = self.__OPList.GetSelection()
        _resIndex = self.__ResultList.GetSelection()
        if _ruleIndex < 0 or _opIndex < 0 or _resIndex < 0:
            return
        
        _ruleName = self.__RuleList.GetItems()[_ruleIndex] 
        _opName = self.__OPList.GetItems()[_opIndex]
               
        self.__analysisNode.delOneRuleOPResult( _ruleName,
                                                _opName,
                                                _opIndex,
                                                _resIndex )

        _OPInfo = self.__analysisNode.getOPInfo( _ruleName,
                                                 _opName,
                                                 _opIndex )
        
        self.__ResultList.SetItems( [str( _i ) for _i in range( len( _OPInfo["result"] ) )] )
        self.__ResultList.SetSelection( -1 )
        self.EnableAllResultCtl( False )
        self.__ResultList.Enable( True )
        self.__AddOneResultButton.Enable( True )          
        
    def OnAddReslut( self, event ):
        _ruleIndex = self.__RuleList.GetSelection()
        _opIndex = self.__OPList.GetSelection()
        if _ruleIndex < 0 or _opIndex < 0:
            return
        _RuleName = self.__RuleList.GetItems()[_ruleIndex]
        _opName = self.__OPList.GetItems()[_opIndex]
        self.__analysisNode.addOneRuleOPResult( _RuleName, _opName, _opIndex ) 
        
        _OPInfo = self.__analysisNode.getOPInfo( _RuleName,
                                                 _opName,
                                                 _opIndex )
        
        self.__ResultList.SetItems( [str( _i ) for _i in range( len( _OPInfo["result"] ) )] )
        self.__ResultList.SetSelection( -1 )
        self.EnableAllResultCtl( False )
        self.__ResultList.Enable( True )
        self.__AddOneResultButton.Enable( True )       
    
    def OnDelOP( self, event ):
        _ruleIndex = self.__RuleList.GetSelection()
        _opIndex = self.__OPList.GetSelection()
        if _ruleIndex < 0 or _opIndex < 0:
            return
        _RuleName = self.__RuleList.GetItems()[_ruleIndex]
        _opName = self.__OPList.GetItems()[_opIndex]
        self.__analysisNode.delOneRuleOP( _RuleName, _opName, _opIndex )
        self.__OPList.SetItems( self.__analysisNode.getOneRuleOPNameList( _RuleName ) )
        self.__OPList.SetSelection( -1 )
        #禁用其他的控件
        self.EnableAllOPCtl( False )
        self.__OPList.Enable( True ) 
        self.__AddOneOPButton.Enable( True )
        
    def OnAddOP( self, event ):
        "on add OP"
        _ruleIndex = self.__RuleList.GetSelection()
        if _ruleIndex < 0:
            wx.MessageBox( "Please Select a Rule to add OP Faile!", "Warnning" )
            return
        dlg = wx.TextEntryDialog( self,
                                 'New OP Name:',
                                 'Add New OP' )

        if dlg.ShowModal() == wx.ID_OK:
            _value = dlg.GetValue()
            _RuleName = self.__RuleList.GetItems()[_ruleIndex]
            if True != self.__analysisNode.addOneRuleOP( _RuleName, _value ):
                wx.MessageBox( "Add OP Faile!" + _value, "Warnning" )
            else:
                #更新显示
                self.__OPList.SetItems( self.__analysisNode.getOneRuleOPNameList( _RuleName ) )
                self.__OPList.SetSelection( -1 )
                #禁用其他的控件
                self.EnableAllOPCtl( False )
                self.__OPList.Enable( True )
        dlg.Destroy()            
    
    def OnDelRule( self, event ):
        "delete rule"
        _index = self.__RuleList.GetSelection()
        if _index < 0:
            return
        _RuleName = self.__RuleList.GetItems()[_index]
        self.__analysisNode.delOneRule( _RuleName )
        self.__RuleList.SetItems( self.__analysisNode.getRuleNameList() )
        self.__RuleList.SetSelection( -1 )
        #禁用其他的控件
        self.EnableAllRuleCtl( False )   
        self.__AddOneRuleButton.Enable( True )     
        
    def OnAddRule( self, event ):
        "add Rule"
        dlg = wx.TextEntryDialog( self,
                                 'New Rule Name:',
                                 'Add New Rule' )

        if dlg.ShowModal() == wx.ID_OK:
            _value = dlg.GetValue()
#            print "OnAddRule", _value
            if True != self.__analysisNode.addOneRule( _value ):
                wx.MessageBox( "Add Rule Faile!" + _value, "Warnning" )
            else:
                #更新显示
                self.__RuleList.SetItems( self.__analysisNode.getRuleNameList() )
                self.__RuleList.SetSelection( -1 )
                #禁用其他的控件
                self.EnableAllRuleCtl( False )
        dlg.Destroy()        
    
    def OnCommOPComBoxChange( self, event ):
        "on comm op combox change"
        _Type = self.__OPTypeComBox.GetValue()
        _ruleIndex = self.__RuleList.GetSelection()
        _opIndex = self.__OPList.GetSelection()
        if "CommDef" != _Type or _ruleIndex < 0 or _opIndex < 0:
            print "OnOPTypeChange error", _Type, _ruleIndex, _opIndex
            return
        _RuleName = self.__RuleList.GetItems()[_ruleIndex]
        _OPName = self.__OPList.GetItems()[_opIndex]        
        
        self.__analysisNode.changeOneRuleOPToCommOPByName( _RuleName, self.__CommOPIDCombox.GetValue(), _opIndex )
        self.__OPList.SetItems( self.__analysisNode.getOneRuleOPNameList( _RuleName ) )
        self.__OPList.SetSelection( _opIndex )
        self.OnOPSelChange( event )            
    
    def OnOPTypeChange( self, event ):
        "On OP Type Change"
        _Type = self.__OPTypeComBox.GetValue()
        _ruleIndex = self.__RuleList.GetSelection()
        _opIndex = self.__OPList.GetSelection()
        if _Type not in ["UserDef", "CommDef" ] or _ruleIndex < 0 or _opIndex < 0:
            print "OnOPTypeChange error", _Type, _ruleIndex, _opIndex
            return
        _RuleName = self.__RuleList.GetItems()[_ruleIndex]
        _OPName = self.__OPList.GetItems()[_opIndex]        
        if "UserDef" == _Type:
            self.__CommOPIDCombox.Enable( False )
            self.__analysisNode.changeOPTypeToUsrDef( _RuleName, _OPName, _opIndex )
            #开启相关的编辑
            self.EnableConditionCtl( True )
            if self.__ResultList.GetSelection() >= 0:#有选中的项
                self.EnableAllResultCtl( True )
                
        else:
            self.__CommOPIDCombox.Enable( True )
            self.__analysisNode.changeOneRuleOPToCommOPByName( _RuleName, self.__CommOPIDCombox.GetValue(), _opIndex )
            self.__OPList.SetItems( self.__analysisNode.getOneRuleOPNameList( _RuleName ) )
            self.__OPList.SetSelection( _opIndex )
            self.OnOPSelChange( event )    
    
    def OnConditionDesChange( self, event ):
        _ruleIndex = self.__RuleList.GetSelection()
        _opIndex = self.__OPList.GetSelection()
        if _ruleIndex < 0 or _opIndex < 0:
            return
        _RuleName = self.__RuleList.GetItems()[_ruleIndex]
        _opName = self.__OPList.GetItems()[_opIndex]        
        self.__analysisNode.modOneRuleOPCondDes( _RuleName,
                                                 _opName,
                                                 _opIndex,
                                                 self.__ConditionDesText.GetValue() )
    
    def OnResultDesChange( self, event ):
        _ruleIndex = self.__RuleList.GetSelection()
        _opIndex = self.__OPList.GetSelection()
        _resIndex = self.__ResultList.GetSelection()
        if _ruleIndex < 0 or _opIndex < 0 or _resIndex < 0:
            print "OnResultDesChange", _ruleIndex, _opIndex, _resIndex
            return
        _RuleName = self.__RuleList.GetItems()[_ruleIndex]
        _opName = self.__OPList.GetItems()[_opIndex] 
#        print "OnResultDesChange!!!"
        self.__analysisNode.modOneRuleOPResultDes( _RuleName,
                                                   _opName,
                                                   _opIndex,
                                                   _resIndex,
                                                   self.__ResultDesText.GetValue() )
    
    def OnResultSelChange( self, event ):
        _ruleIndex = self.__RuleList.GetSelection()
        _opIndex = self.__OPList.GetSelection()
        _resIndex = self.__ResultList.GetSelection()
        if _ruleIndex < 0 or _opIndex < 0 or _resIndex < 0:
            return        
        
        _RuleName = self.__RuleList.GetItems()[_ruleIndex]
        _opName = self.__OPList.GetItems()[_opIndex]
        _OPInfo = self.__analysisNode.getOPInfo( _RuleName,
                                                 _opName,
                                                 _opIndex )
                
        if "UserDef" == _OPInfo["Type"]: #控制显示
            self.EnableAllResultCtl( True )
#        print _resIndex
        _content = self.__analysisNode.getOneRuleOPResultInfo( _RuleName,
                                                               _opName,
                                                               _opIndex,
                                                               _resIndex )
        self.__ResultContentText.SetValue( ExpressionParser.transRuleDicToString( _content[0] ) )
        self.__ResultDesText.SetValue( _content[1] )
        
        
    def OnOPSelChange( self, evnet ):
        _ruleIndex = self.__RuleList.GetSelection()
        _opIndex = self.__OPList.GetSelection()
        if _ruleIndex < 0 or _opIndex < 0:
            return
        #获取内容
        _RuleName = self.__RuleList.GetItems()[_ruleIndex]
        _opName = self.__OPList.GetItems()[_opIndex]
        _OPInfo = self.__analysisNode.getOPInfo( _RuleName,
                                                 _opName,
                                                 _opIndex )
#        print _OPInfo
        self.EnableAllOPCtl( True )
        self.EnableAllResultCtl( False )
        self.__ResultList.Enable( True )
        self.__AddOneResultButton.Enable( True )
        
        if "CommDef" == _OPInfo["Type"]:
            self.__OPTypeComBox.SetSelection( 1 )
            self.__CommOPIDCombox.Enable( True )
            self.__CommOPIDCombox.SetValue( _OPInfo["Value"] )
            self.__ConditionContentText.SetValue( ExpressionParser.transRuleDicToString( _OPInfo["condition"][0] ) )
            self.__ConditionDesText.SetValue( _OPInfo["condition"][1] ) 
            #CommDef只能观看不能修改
            self.EnableAllResultCtl( False )
            self.EnableConditionCtl( False )
            self.__ResultList.Enable( True )
                      
        else:
            self.__ConditionContentText.SetValue( ExpressionParser.transRuleDicToString( _OPInfo["condition"][0] ) )
            self.__ConditionDesText.SetValue( _OPInfo["condition"][1] )
            self.__OPTypeComBox.SetSelection( 0 )
            self.__CommOPIDCombox.Enable( False )
        
        self.__ResultList.SetItems( [str( _i ) for _i in range( len( _OPInfo["result"] ) )] )
        self.__ResultList.SetSelection( -1 )
        
    def OnRuleDesChange( self, event ):
        _index = self.__RuleList.GetSelection()
        if _index < 0:
            print "OnRuleDesChange error", _index
            return
        _RuleName = self.__RuleList.GetItems()[_index]
        self.__analysisNode.modOneRuleDes( _RuleName, self.__RuleDesText.GetValue() )
    
    
    def OnPosStartInfoChange( self, event ):
        try:
            _index = self.__RuleList.GetSelection()
            _RuleName = self.__RuleList.GetItems()[_index]
            _start = int( self.__PosStartText.GetValue() )
            self.__analysisNode.modOneRuleStartPos( _RuleName, _start )
        except:
            self.__analysisNode.modOneRuleStartPos( _RuleName, None )
            return

    def OnPosEndInfoChange( self, event ):
        try:
            _index = self.__RuleList.GetSelection()
            _RuleName = self.__RuleList.GetItems()[_index]
            _end = int( self.__PosEndText.GetValue() )
            self.__analysisNode.modOneRuleEndPos( _RuleName, _end )
        except:
            self.__analysisNode.modOneRuleEndPos( _RuleName, None )
            return

    def OnPosDesInfoChange( self, event ):
        try:
            _index = self.__RuleList.GetSelection()
            _RuleName = self.__RuleList.GetItems()[_index]
            _Des = self.__PosDesText.GetValue()
            self.__analysisNode.modOneRulePosDes( _RuleName, _Des )
        except:
            self.__analysisNode.modOneRulePosDes( _RuleName, "" )
            return

    def OnTimeStartInfoChange( self, event ):
        try:
            _index = self.__RuleList.GetSelection()
            _RuleName = self.__RuleList.GetItems()[_index]
            _start = int( self.__TimeStartText.GetValue() )
            self.__analysisNode.modOneRuleStartTime( _RuleName, _start )
        except:
            self.__analysisNode.modOneRuleStartTime( _RuleName, None )
            return

    def OnTimeEndInfoChange( self, event ):
        try:
            _index = self.__RuleList.GetSelection()
            _RuleName = self.__RuleList.GetItems()[_index]
            _end = int( self.__TimeEndText.GetValue() )
            self.__analysisNode.modOneRuleEndTime( _RuleName, _end )
        except:
            self.__analysisNode.modOneRuleEndTime( _RuleName, None )
            return

    def OnTimeDesInfoChange( self, event ):
        try:
            _index = self.__RuleList.GetSelection()
            _RuleName = self.__RuleList.GetItems()[_index]
            _Des = self.__TimeDesText.GetValue()
            self.__analysisNode.modOneRuleTimeDes( _RuleName, _Des )
        except:
            self.__analysisNode.modOneRuleTimeDes( _RuleName, "" )
            return
    
           
    def OnRuleSelChange( self, event ):
        _index = self.__RuleList.GetSelection()
        if _index < 0:
            return
        self.EnableAllRuleCtl( True )
        self.EnableAllOPCtl( False )
        self.__OPList.Enable( True )
        self.__AddOneOPButton.Enable( True ) #具备添加OP的功能
        _RuleName = self.__RuleList.GetItems()[_index]
        _posInfo = self.__analysisNode.getOneRulePosInfo( _RuleName )
        _timeInfo = self.__analysisNode.getOneRuleTimeInfo( _RuleName )
        
        self.__PosStartText.SetValue( str( _posInfo[0] ) )
        self.__PosEndText.SetValue( str( _posInfo[1] ) )
        self.__PosDesText.SetValue( _posInfo[2] )
        
        self.__TimeStartText.SetValue( str( _timeInfo[0] ) )
        self.__TimeEndText.SetValue( str( _timeInfo[1] ) )
        self.__TimeDesText.SetValue( _timeInfo[2] )
        
        self.__RuleDesText.SetValue( self.__analysisNode.getOneRuleDes( _RuleName ) )
        
        self.__OPList.SetItems( self.__analysisNode.getOneRuleOPNameList( _RuleName ) )
        self.__OPList.SetSelection( -1 )



#------------------------------------------------------------------------------------------
#用于编辑公式的窗口
#------------------------------------------------------------------------------------------
class EditExpDiag( wx.Dialog ):
    '''
    Edit Expression Diag
    '''
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE,
            useMetal = False,
            AnalysisNode = None,
            ExpStr = ""
            ): 
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle( wx.DIALOG_EX_CONTEXTHELP )
        pre.Create( parent, ID, title, pos, size, style )

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate( pre )

        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle( wx.DIALOG_EX_METAL )
            
        self.__analysisNode = AnalysisNode
        self.__ExpStr = ExpStr
        # Now continue with the normal construction of the dialog
        # contents
        label1 = wx.StaticText( self, -1, "Variant List:", size = ( 100, -1 ) )
        self.__VariantList = wx.ListBox( self, -1, size = ( 150, 100 ), \
                                         choices = [], \
                                         style = wx.LB_SINGLE )
        
        box1 = wx.BoxSizer( wx.VERTICAL )
        box1.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box1.Add( self.__VariantList, 6, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        label1 = wx.StaticText( self, -1, "Expression:", size = ( 100, -1 ) )
        self.__ExpressionTxt = wx.TextCtrl( self, -1, "", size = ( 300, -1 ) , style = wx.TE_MULTILINE )        
        self.__CheckButton = wx.Button( self, -1, "Check Valid", size = ( 100, -1 ) )
        
        box2 = wx.BoxSizer( wx.VERTICAL )
        box2.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box2.Add( self.__ExpressionTxt, 6, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box2.Add( self.__CheckButton, 0, wx.ALIGN_RIGHT | wx.ALL , 5 )
        
        box = wx.BoxSizer( wx.HORIZONTAL )
        box.Add( box1, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box.Add( box2, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        line = wx.StaticLine( self, -1, size = ( 20, -1 ), style = wx.LI_HORIZONTAL )
        sizer.Add( line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5 )

        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button( self, wx.ID_OK )
        btn.SetDefault()
        btnsizer.AddButton( btn )

        btn = wx.Button( self, wx.ID_CANCEL )
        btnsizer.AddButton( btn )
        btnsizer.Realize()

        sizer.Add( btnsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )

        self.SetSizer( sizer )
        sizer.Fit( self ) 
        self.UpdateView()
        self.BindEvent()
        
    def BindEvent( self ):
        self.Bind( wx.EVT_BUTTON, self.OnCheckExp, self.__CheckButton )
        self.Bind( wx.EVT_LISTBOX_DCLICK , self.OnListDoubleClick, self.__VariantList )
        self.Bind( wx.EVT_TEXT, self.OnExpTXT, self.__ExpressionTxt )
    
    def OnListDoubleClick( self, event ):
        _index = self.__VariantList.GetSelection()
        if _index < 0:
            return
        self.__ExpStr = self.__ExpressionTxt.GetValue() + self.__VariantList.GetItems()[_index]
        self.__ExpressionTxt.SetValue( self.__ExpStr )
    
    def OnExpTXT( self, event ):
        self.__ExpStr = self.__ExpressionTxt.GetValue()
    
    def getExpValue( self ):
        return self.__ExpStr
    
    def checkExp( self ):
        _expression = self.__ExpressionTxt.GetValue()
        if dict != type( ExpressionParser.transStringToRuleDic( _expression ) ):
            return False
        else:
            return True      
    
    def OnCheckExp( self, event ):
        _expression = self.__ExpressionTxt.GetValue()
        
        if dict != type( ExpressionParser.transStringToRuleDic( _expression ) ):
            wx.MessageBox( "Error Expression， Please check it!" )
        else:
            wx.MessageBox( "O.K." ) 


    def UpdateView( self ):
        "update view"
        self.__VariantList.SetItems( self.__analysisNode.getVarNameList() )
        self.__VariantList.SetSelection( -1 )
        
        self.__ExpressionTxt.SetValue( self.__ExpStr )
        
        

#------------------------------------------------------------------------------------------
#用于编辑Blocklist的窗口
#------------------------------------------------------------------------------------------
class EditBlockListDiag( wx.Dialog ):
    '''
    Edit block list Diag
    '''
    __dirDic = {"1":0, "-1":1, 0:"1", 1:"-1"}
    
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE,
            useMetal = False,
            blockListStr = None,
            dir = None,
            ): 
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle( wx.DIALOG_EX_CONTEXTHELP )
        pre.Create( parent, ID, title, pos, size, style )

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate( pre )

        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle( wx.DIALOG_EX_METAL )
        
        self.__blockListStr = blockListStr
        self.__dir = self.__dirDic[dir] #转换
        # Now continue with the normal construction of the dialog
        # contents
        label1 = wx.StaticText( self, -1, "Block List:", size = ( 100, -1 ) )
        self.__blockList = wx.ListBox( self, -1, size = ( 150, -1 ), \
                                         choices = [], \
                                         style = wx.LB_SINGLE )
        
        box1 = wx.BoxSizer( wx.VERTICAL )
        box1.Add( label1, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box1.Add( self.__blockList, 8, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        label1 = wx.StaticText( self, -1, "Start Block ID:", size = ( 100, -1 ) )
        self.__StartBlockIdTxt = wx.TextCtrl( self, -1, "", size = ( 200, -1 ) )
        box3 = wx.BoxSizer( wx.HORIZONTAL ) 
        box3.Add( label1, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        box3.Add( self.__StartBlockIdTxt, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
               
        label2 = wx.StaticText( self, -1, "End Block ID:", size = ( 100, -1 ) )
        self.__EndBlockIdTxt = wx.TextCtrl( self, -1, "", size = ( 200, -1 ) )        
        box4 = wx.BoxSizer( wx.HORIZONTAL ) 
        box4.Add( label2, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        box4.Add( self.__EndBlockIdTxt, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )

        label4 = wx.StaticText( self, -1, "Direction:", size = ( 100, -1 ) )
        self.__DirectionComB = wx.ComboBox( self, -1, "up", ( 80, -1 ), ( 200, -1 ), ["up", "down"], wx.CB_DROPDOWN )         
        box5 = wx.BoxSizer( wx.HORIZONTAL ) 
        box5.Add( label4, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        box5.Add( self.__DirectionComB, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        label3 = wx.StaticText( self, -1, "Select Block List Content:", size = ( 200, -1 ) )
        self.__SelectBlockListTxt = wx.TextCtrl( self, -1, "", size = ( 300, -1 ) , style = wx.TE_MULTILINE )        
        self.__SelectBlockListTxt.SetEditable( False )
        self.__CalBlockListButton = wx.Button( self, -1, "get block list", size = ( 100, -1 ) )
        
        box2 = wx.BoxSizer( wx.VERTICAL )
        box2.Add( box3, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box2.Add( box4, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box2.Add( box5, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box2.Add( label3, 1, wx.ALIGN_LEFT | wx.ALL, 5 )
        box2.Add( self.__SelectBlockListTxt, 4, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box2.Add( self.__CalBlockListButton, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )
        
        box = wx.BoxSizer( wx.HORIZONTAL )
        box.Add( box1, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box.Add( box2, 2, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        line = wx.StaticLine( self, -1, size = ( 20, -1 ), style = wx.LI_HORIZONTAL )
        sizer.Add( line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5 )

        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button( self, wx.ID_OK )
        btn.SetDefault()
        btnsizer.AddButton( btn )

        btn = wx.Button( self, wx.ID_CANCEL )
        btnsizer.AddButton( btn )
        btnsizer.Realize()

        sizer.Add( btnsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )

        self.SetSizer( sizer )
        sizer.Fit( self ) 
        self.UpdateView()
        self.BindEvents()
        
    def BindEvents( self ):
        self.Bind( wx.EVT_BUTTON, self.OnCalBlockList, self.__CalBlockListButton )
        self.Bind( wx.EVT_LISTBOX_DCLICK , self.OnListDoubleClick, self.__blockList )
        self.Bind( wx.EVT_TEXT, self.OnStartBlockIDTxt, self.__StartBlockIdTxt )
        self.Bind( wx.EVT_TEXT, self.OnEndBlockIDTxt, self.__EndBlockIdTxt )
#        self.Bind( wx.EVT_COMBOBOX, self.OnDirChange, self.__DirectionComB )
        
    def OnStartBlockIDTxt( self, event ):
        try:
            self.__StartBlockId = int( self.__StartBlockIdTxt.GetValue() )
        except:
            print "OnStartBlockIDTxt Error", self.__StartBlockIdTxt.GetValue()
            
    def OnEndBlockIDTxt( self, event ):
        try:
            self.__EndBlockId = int( self.__EndBlockIdTxt.GetValue() )
        except:
            print "OnEndBlockIDTxt Error", self.__EndBlockIdTxt.GetValue()

#    def OnDirChange( self, event ):
#        self.__dir = self.__DirectionComB.GetSelection()
    
    def OnListDoubleClick( self, event ):
        _index = self.__blockList.GetSelection()
        if _index < 0:
            return
        
        self.__SelectBlockListTxt.SetValue( self.__blockList.GetItems()[_index] )
        self.__blockListStr = self.__blockList.GetItems()[_index]
        
    
    def getDirection( self ):
        "get direction"
        return self.__dirDic[self.__dir]
    
    def getBlockListStr( self ):
        "get block list string"
        return self.__blockListStr
    
    def OnCalBlockList( self, event ):
        "On Calculate Block List"
        self.__dir = self.__DirectionComB.GetSelection()
        _blocklist = simdata.TrainRoute.getBlockListInfoByblockID( self.__StartBlockId,
                                                                   self.__EndBlockId,
                                                                   int( self.__dirDic[self.__dir] ),
                                                                   False,
                                                                   Type = "Edit" )
        
#        print self.__StartBlockId, self.__EndBlockId, self.__dir
        if len( _blocklist ) > 0:
            _ShowList = []
            for _content in _blocklist:
                _ShowList.append( repr( _content )[1:-1] )
            self.__blockList.SetItems( _ShowList )
            
            self.__blockList.SetSelection( -1 )
        else:
            wx.MessageBox( "No Block List find, please check the block id and direction!", "Warnning" )

    def UpdateView( self ):
        "update view"
        self.__SelectBlockListTxt.SetValue( self.__blockListStr )
        #计算起始和终点的block id
        _tempBlockList = [int( _i ) for _i in self.__blockListStr.split( "," )]
        self.__StartBlockId = _tempBlockList[0]
        self.__EndBlockId = _tempBlockList[-1]
        self.__StartBlockIdTxt.SetValue( str( self.__StartBlockId ) )
        self.__EndBlockIdTxt.SetValue( str( self.__EndBlockId ) )
        self.__DirectionComB.SetSelection( self.__dir )
        

#------------------------------------------------------------------------------------------
#用于打开OMAP Figure config的dialog
#------------------------------------------------------------------------------------------
class OpenOMAPFigureDiag( wx.Dialog ):
    '''
    Open OMAP Figure dialog
    '''
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE,
            useMetal = False
            ): 
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle( wx.DIALOG_EX_CONTEXTHELP )
        pre.Create( parent, ID, title, pos, size, style )

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate( pre )

        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle( wx.DIALOG_EX_METAL )
        
        _label = wx.StaticText( self, -1, "Config List:", size = ( 100, -1 ) )
        self.__configList = wx.ListBox( self, -1, size = ( 100, 100 ), \
                                        choices = [], \
                                        style = wx.LB_SINGLE )
        
        self.__configList.SetItems( OMAPFigureConfigHandle.getConfigNameList() )
        self.__configList.SetSelection( -1 )
        box1 = wx.BoxSizer( wx.VERTICAL )
        box1.Add( _label, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 2 )
        box1.Add( self.__configList, 6, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 2 )
        
        _label = wx.StaticText( self, -1, "Config Name:", size = ( 100, -1 ) )
        self.__ConfigName = wx.TextCtrl( self, -1, "", size = ( 150, -1 ) )
        box2 = wx.BoxSizer( wx.VERTICAL )
        box2.Add( _label, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 2 )
        box2.Add( self.__ConfigName, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 2 )
        _label = wx.StaticText( self, -1, "Description:", size = ( 100, -1 ) )
        self.__DescriptionTxt = wx.TextCtrl( self, -1, "", size = ( 150, -1 ), style = wx.TE_MULTILINE )      
        self.__DeleteConfigButton = wx.Button( self, -1, "Delete", size = ( 75, -1 ) )
        self.__ReNameButton = wx.Button( self, -1, "ReName", size = ( 75, -1 ) )
        self.__DeleteConfigButton.Enable( False )
        self.__ReNameButton.Enable( False )
        self.__DescriptionTxt.SetEditable( False )
        self.__ConfigName.SetEditable( False )
        
        box2.Add( _label, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 2 )
        box2.Add( self.__DescriptionTxt, 5, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 2 )
        box3 = wx.BoxSizer( wx.HORIZONTAL )
        box3.Add( self.__ReNameButton, 0, wx.ALIGN_RIGHT | wx.ALL, 0 )
        box3.Add( self.__DeleteConfigButton, 0, wx.ALIGN_RIGHT | wx.ALL, 0 )
        
        box2.Add( box3, 0, wx.ALIGN_RIGHT | wx.ALL, 2 )

        box = wx.BoxSizer( wx.HORIZONTAL )
        box.Add( box1, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box.Add( box2, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        line = wx.StaticLine( self, -1, size = ( 20, -1 ), style = wx.LI_HORIZONTAL )
        sizer.Add( line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5 )

        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button( self, wx.ID_OK )
        btn.SetDefault()
        btnsizer.AddButton( btn )

        btn = wx.Button( self, wx.ID_CANCEL )
        btnsizer.AddButton( btn )
        btnsizer.Realize()

        sizer.Add( btnsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )

        self.SetSizer( sizer )
        sizer.Fit( self ) 
        self.BindEvents()
        
    def BindEvents( self ):
        self.Bind( wx.EVT_LISTBOX, self.OnChangeConfig, self.__configList )
        self.Bind( wx.EVT_BUTTON, self.DeleteConfig, self.__DeleteConfigButton )
        self.Bind( wx.EVT_TEXT, self.OnDesChange, self.__DescriptionTxt )
        self.Bind( wx.EVT_BUTTON, self.ReNameConfig, self.__ReNameButton )
        
    def ReNameConfig( self, event ):
        _index = self.__configList.GetSelection()
        if _index in [-1, None]:
            print "ReNameConfig Error!"
            return        
        _NewName = self.__ConfigName.GetValue()
        _oldName = self.__configList.GetItems()[_index]
        if False == OMAPFigureConfigHandle.renameConfig( _oldName, _NewName ):
            wx.MessageBox( "rename config error", "ERROR" )
        else:
            self.__configList.SetItems( OMAPFigureConfigHandle.getConfigNameList() )
            for _i, _Name in enumerate( self.__configList.GetItems() ):
                if _Name == _NewName:
                    self.__configList.SetSelection( _i )
                    break            
    
    def DeleteConfig( self, event ):
        _index = self.__configList.GetSelection()
        if _index in [-1, None]:
            print "DeleteConfig Error!"
            return
        _configName = self.__configList.GetItems()[_index]        
        
        OMAPFigureConfigHandle.delNewOMAPFigureConfig( _configName )
        self.__configList.SetItems( OMAPFigureConfigHandle.getConfigNameList() )
        self.__configList.SetSelection( -1 )
        self.__ConfigName.SetEditable( False )
        self.__DescriptionTxt.SetEditable( False )
        self.__DeleteConfigButton.Enable( False )
        self.__ReNameButton.Enable( False )        
    
    def OnChangeConfig( self, event ):
        _index = self.__configList.GetSelection()
        if _index in [-1, None]:
            print "OnChangeConfig Error!"
            return
        _configName = self.__configList.GetItems()[_index]
        self.__ConfigName.SetValue( _configName )
        self.__DescriptionTxt.SetValue( OMAPFigureConfigHandle.getConfigDescriptionByName( _configName ) )
        self.__ConfigName.SetEditable( True )
        self.__DescriptionTxt.SetEditable( True )
        self.__DeleteConfigButton.Enable( True )
        self.__ReNameButton.Enable( True )
        
    def OnDesChange( self, event ):
        _index = self.__configList.GetSelection()
        if _index in [-1, None]:
            print "OnDesChange Error!"
            return
        _configName = self.__configList.GetItems()[_index]
        OMAPFigureConfigHandle.setConfigDescription( _configName, self.__DescriptionTxt.GetValue() )
        
    def getSelectConfig( self ):
        "get select config"
        _index = self.__configList.GetSelection()
        if _index in [-1, None]:
            print "getSelectConfig Error!"
            return
        _configName = self.__configList.GetItems()[_index]
        return OMAPFigureConfigHandle.getConfigByName( _configName )

#------------------------------------------------------------------------------------------
#用于保存OMAP Figure config的dialog
#------------------------------------------------------------------------------------------
class SaveOMAPFigureDiag( wx.Dialog ):
    '''
    Save OMAP Figure dialog
    '''
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE,
            useMetal = False
            ): 
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle( wx.DIALOG_EX_CONTEXTHELP )
        pre.Create( parent, ID, title, pos, size, style )

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate( pre )

        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle( wx.DIALOG_EX_METAL )
        
        _label = wx.StaticText( self, -1, "Config Name:", size = ( 100, -1 ) )
        self.__NameTxt = wx.TextCtrl( self, -1, "", size = ( 150, -1 ) )
        
        box1 = wx.BoxSizer( wx.HORIZONTAL )
        box1.Add( _label, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box1.Add( self.__NameTxt, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        _label = wx.StaticText( self, -1, "Description:", size = ( 100, -1 ) )
        self.__DescriptionTxt = wx.TextCtrl( self, -1, "", size = ( 150, -1 ), style = wx.TE_MULTILINE )      
        
        box2 = wx.BoxSizer( wx.HORIZONTAL )
        box2.Add( _label, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box2.Add( self.__DescriptionTxt, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )

        box = wx.BoxSizer( wx.VERTICAL )
        box.Add( box1, 1, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box.Add( box2, 3, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        line = wx.StaticLine( self, -1, size = ( 20, -1 ), style = wx.LI_HORIZONTAL )
        sizer.Add( line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5 )

        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button( self, wx.ID_OK )
        btn.SetDefault()
        btnsizer.AddButton( btn )

        btn = wx.Button( self, wx.ID_CANCEL )
        btnsizer.AddButton( btn )
        btnsizer.Realize()

        sizer.Add( btnsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )

        self.SetSizer( sizer )
        sizer.Fit( self ) 

    def getNameAndDes( self ):
        return self.__NameTxt.GetValue(), self.__DescriptionTxt.GetValue()


#------------------------------------------------------------------------------------------
#通用的Combox编辑dialog
#------------------------------------------------------------------------------------------
class ComboBoxDiag( wx.Dialog ):
    '''
    ComboBox dialog
    '''
    
    def __init__( self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE,
            useMetal = False,
            choicelist = None,
            ): 
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle( wx.DIALOG_EX_CONTEXTHELP )
        pre.Create( parent, ID, title, pos, size, style )

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate( pre )

        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle( wx.DIALOG_EX_METAL )
        
        _label = wx.StaticText( self, -1, "Choices:", size = ( 100, -1 ) )
        self.__Combox = wx.ComboBox( self, -1, choicelist[0], ( 80, -1 ), ( 160, -1 ), choicelist, wx.CB_DROPDOWN )
        
        box = wx.BoxSizer( wx.HORIZONTAL )
        box.Add( _label, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        box.Add( self.__Combox, 0, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
        
        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )

        line = wx.StaticLine( self, -1, size = ( 20, -1 ), style = wx.LI_HORIZONTAL )
        sizer.Add( line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5 )

        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button( self, wx.ID_OK )
        btn.SetDefault()
        btnsizer.AddButton( btn )

        btn = wx.Button( self, wx.ID_CANCEL )
        btnsizer.AddButton( btn )
        btnsizer.Realize()

        sizer.Add( btnsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )

        self.SetSizer( sizer )
        sizer.Fit( self ) 
    
    def getSelectValue( self ):
        "get select value"
        return self.__Combox.GetValue()

class test( object ):
    a = 1
    def __init__( self ):
#        self.a = 3
        pass
     
if __name__ == "__main__": 
    t = test()
    print t.a
    print test.a

