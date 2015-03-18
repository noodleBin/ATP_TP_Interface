#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     simview.py
# Description:  模拟器界面      
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      2011-07-24
# Company:      CASCO
# LastChange:   
# History:      create 2011-07-24
#----------------------------------------------------------------------------
import wx
from base import commlib
from simmain import TPSim
import time

WIDTH = 800
HEIGHT = 600

class MyLog( wx.PyLog ):

    def __init__( self, textCtrl, logTime = 0 ):
        wx.PyLog.__init__( self )
        self.tc = textCtrl
        self.logTime = logTime

    def DoLogString( self, message, timeStamp ):
        if self.tc:
            self.tc.AppendText( message + '\n' )


class SimFrame( wx.Frame ):
    """
    simulator ui
    """
    
    cycle = 100  #ms
    tpSim = None
    
    def __init__( self, *args, **kwds ):
        # begin wxGlade: RBCFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__( self, *args, **kwds )
        
        
        #实例模拟器
        self.tpSim = TPSim( 'tps', 1 )
        # Menu Bar
        self.main_1_menubar = wx.MenuBar()
        self.mFileMenu = wx.Menu()
        self.mQuitMenu = wx.MenuItem( self.mFileMenu, wx.NewId(), u"退出", u"退出程序", wx.ITEM_NORMAL )
        self.mFileMenu.AppendItem( self.mQuitMenu )
        self.main_1_menubar.Append( self.mFileMenu, u"文件" )
        self.mFunctionMenu = wx.Menu()
        self.mDebugMenu = wx.MenuItem( self.mFunctionMenu, wx.NewId(), u"调试", u"打开调试对话框", wx.ITEM_NORMAL )
        self.mFunctionMenu.AppendItem( self.mDebugMenu )
        self.main_1_menubar.Append( self.mFunctionMenu, u"功能" )
        self.mHelpMenu = wx.Menu()
        self.mAboutMenu = wx.MenuItem( self.mHelpMenu, wx.NewId(), u"关于", u"关于", wx.ITEM_NORMAL )
        self.mHelpMenu.AppendItem( self.mAboutMenu )
        self.main_1_menubar.Append( self.mHelpMenu, u"帮助" )
        self.SetMenuBar( self.main_1_menubar )
        # Menu Bar end
        
        #status bar
        self.sim_statusbar = self.CreateStatusBar( 1, 0 )

        # 分割窗口
        self.sp = wx.SplitterWindow( self )
        self.p1 = wx.Panel( self.sp, style = wx.SUNKEN_BORDER | wx.EXPAND )
        self.p2 = wx.Panel( self.sp, style = wx.SUNKEN_BORDER | wx.EXPAND )

        # 日志
        self.logText = wx.TextCtrl( self.p2, -1, "", style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.EXPAND )
        wx.Log_SetActiveTarget( MyLog( self.logText ) )
        
        # notebook
        self.notebook = wx.Notebook( self.p1, -1, style = 0 )
        self.notebook_pane_1 = wx.Panel( self.notebook, -1 )
        
        # notebook 设置页面
        self.run_button_1 = wx.Button( self.notebook_pane_1, -1, u"运行" )
        self.load_button_2 = wx.Button( self.notebook_pane_1, -1, u"加载" )
        self.end_button_3 = wx.Button( self.notebook_pane_1, -1, u"结束" )
        self.reset_button_4 = wx.Button( self.notebook_pane_1, -1, u"重置" )
        
        # 定时器
        #self.time1 = wx.Timer(self, id = wx.NewId())

        self.__set_properties()
        self.__do_layout()

        self.Bind( wx.EVT_MENU, self.OnQuit, self.mQuitMenu )
        self.Bind( wx.EVT_MENU, self.OnDebug, self.mDebugMenu )
        self.Bind( wx.EVT_MENU, self.OnAbout, self.mAboutMenu )
        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
        #self.Bind(wx.EVT_TIMER, self.OnTimer, self.time1)
        
        #操作
        self.Bind( wx.EVT_BUTTON, self.OnRun, self.run_button_1 )
        self.Bind( wx.EVT_BUTTON, self.OnLoad, self.load_button_2 )
        self.Bind( wx.EVT_BUTTON, self.OnEnd, self.end_button_3 )
        self.Bind( wx.EVT_BUTTON, self.OnReset, self.reset_button_4 )
        
    def __set_properties( self ):
        "set windows properties"
        self.SetTitle( "SIM" )
        self.SetSize( ( WIDTH, HEIGHT ) )
        self.sim_statusbar.SetStatusWidths( [-1] )
        # status fields
        sim_statusbar_fields = [u""]
        for i in range( len( sim_statusbar_fields ) ):
            self.sim_statusbar.SetStatusText( sim_statusbar_fields[i], i )
        self.sp.SetMinimumPaneSize( 100 )


    def __do_layout( self ):
        self.sp.SplitHorizontally( self.p1, self.p2, HEIGHT - 400 )
        
        # pane_1
        nb_1_sizer_1 = wx.BoxSizer( wx.VERTICAL )
        nb_1_sizer_1.Add( self.load_button_2, 0, wx.EXPAND, 0 )
        nb_1_sizer_1.Add( self.run_button_1, 0, wx.EXPAND, 0 )
        nb_1_sizer_1.Add( self.end_button_3, 0, wx.EXPAND, 0 )
        nb_1_sizer_1.Add( self.reset_button_4, 0, wx.EXPAND, 0 )      
        self.notebook_pane_1.SetSizer( nb_1_sizer_1 )       
        nb_1_sizer_1.Fit( self.notebook_pane_1 )
        self.notebook_pane_1.Layout()
      
        #p1布局
        sizer_p1 = wx.BoxSizer( wx.VERTICAL )
        self.notebook.AddPage( self.notebook_pane_1, u"操作" )
        sizer_p1.Add( self.notebook, 1, wx.EXPAND, 0 )
        self.p1.SetSizer( sizer_p1 )
        sizer_p1.Fit( self.p1 )
        self.p1.Layout()
        
        #P2窗口布局
        sizer_p2 = wx.GridSizer( 1, 1, 0, 0 ) 
        sizer_p2.Add( self.logText, 0, wx.EXPAND, 0 )
        self.p2.SetSizer( sizer_p2 )
        sizer_p2.Fit( self.p2 )
        self.p2.Layout()
    
    def OnQuit( self, event ):
        "OnQiut button"
        #print "Event handler `OnQuit' not implemented"
        self.Destroy()
    
    def OnCloseWindow( self, event ):
        "close me"
        self.Destroy()

    def OnDebug( self, event ):
        "OnDebug button"
        #print "Event handler OnDebug not implemented"

    def OnAbout( self, event ):
        "on about me"
        #print "Event handler OnAbout not implemented"
    
    def OnLoad( self, event ):
        "button load"
        self.logLog( u"设备加载" )
        self.tpSim.deviceRunstart = False
        #tps init
        self.tpSim.deviceInit( varFile = r'/setting/tps_variant.xml', \
            msgFile = r'/setting/tps_message.xml', \
            netWorkFile = r'/setting/tps_networks.xml', \
            paraFile = r'/setting/tps_parameter.xml', \
            track_map = r'/datafile/atpCpu1Binary.txt', \
            train_route = r'/scenario/train_route.xml', \
            track_maptxt = r'/datafile/atpText.txt', \
            log = r'/log/tps.log' , \
            telnet = r'/setting/telnet_config.xml' )
                
        for _d in self.tpSim.loadDeviceList:
            self.logLog( u"加载设备:" + _d )
            
        #开启telnet连接
#         self.tpSim.telnet.ConnectTelnet( self.logLog )
        #print 'dev dic', self.tpSim.loadDeviceDic
        
    def OnRun( self, event ):
        "button run"
        self.logLog( u"设备运行" )
        #self.time1.Start(self.cycle)      #milliseconds
        self.tpSim.telnet.StartSaveTelnetContent()
        #开启线程，并运行
        self.tpSim.deviceRunstart = True
        self.tpSim.sendStartCommand = True
        self.tpSim.createThread( self.tpSim.deviceRunthread, '', "sim_device_Run_thread" )
#        self.tpSim.getDataValue( 'sim_device_Run_thread' ).start()
        self.tpSim.getDataValue( 'sim_device_Run_thread' ).StartThread( "ABOVE_NORMAL" )
        self.tpSim.createThread( self.tpSim.deviceSendMsg, '', "send_to_ccnv_thread" )
        self.tpSim.createThread( self.tpSim.deviceSerialSendMsg, '', "send_to_serial_thread" )
#        self.tpSim.getDataValue( 'send_to_ccnv_thread' ).start()
        self.tpSim.getDataValue( 'send_to_serial_thread' ).StartThread( "ABOVE_NORMAL" )
        
        self.tpSim.createThread( self.tpSim.SendCBKMsg, '', "send_cbk_Msg_thread" )
        self.tpSim.getDataValue( 'send_cbk_Msg_thread' ).start()        
                
    def OnEnd( self, event ):
        "button run"
        #self.time1.Stop()   
#         self.tpSim.telnet.CloseTelnet()   
        self.tpSim.deviceRunstart = False    
        self.tpSim.inQ.put( "END Case" )   
        self.tpSim.deviceEnd()        
        self.logLog( u"结束设备运行" )

    def OnReset( self, event ):
        "button run"
        self.logLog( u"设备重置" ) 
                      
    def logLog( self, logStr ):
        logs = unicode( commlib.curTime(), 'UTF-8' ) + u' --- ' + logStr
        #logs = u' --- ' + logStr
        wx.LogMessage( logs )

class MyApp( wx.App ): 
    def OnInit( self ):
        wx.InitAllImageHandlers()
        sim = SimFrame( None, -1, "" )
        self.SetTopWindow( sim )
        sim.Show()
        return 1

# end of class MyApp

if __name__ == "__main__":
    app = MyApp( 0 )
    app.MainLoop()
