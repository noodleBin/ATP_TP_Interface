#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     simpleplot.py
# Description:  基于matplotlib写的用于数据图形显示的类 
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2011-11-21
# Company:      CASCO
# LastChange:   create 2011-11-21
# History:          
#----------------------------------------------------------------------------
import wx
# import matplotlib
#from matplotlib.figure import Figure
# from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas                            
# import numpy as np
#from pylab import *
# import matplotlib.pyplot as plt

#--------------------------------------------------------------
#画图类:用于通过matplotlib提供的plot功能进行显示
#--------------------------------------------------------------
class DataPlot( wx.Panel ):
    
    def __init__( self, parent, _size = wx.DefaultSize ):
        #初始化窗口，并将画布初始化
        wx.Panel.__init__( self, parent, -1, size = _size )
        self.Sizer = wx.BoxSizer( wx.HORIZONTAL )
        self.figure = matplotlib.figure.Figure( figsize = ( 10, 1 ), dpi = 100 )
        
        self.axes = self.figure.add_subplot( 1, 1, 1 )
        self.canvas = FigureCanvas( self, -1, self.figure )
        self.Sizer.Add( self.canvas, 5, wx.ALIGN_CENTRE | wx.ALL | wx.EXPAND, 5 )
    
    #---------------------------------------------------------------
    #@根据相关属性进行画图,dataX，dataY为一维列表（目前仅支持画二位图像）
    #@title:图标题目
    #@style = "r--"
    #@label:横纵坐标的标题名[xlabel,ylabel]
    #---------------------------------------------------------------
    def plot( self, dataX = [], \
             dataY = [], title = "", \
             style = "", label = ["", ""] , color = ( 1, 1, 1 ) ):
        if len( dataX ) != len( dataY ):
            print "plot error!!! length of dataX and dataY are not equal!"
        _tmpX = np.array( dataX )
        _tmpY = np.array( dataY )  
        self.axes.plot( dataX, dataY, style, color = color )
        self.axes.grid()
        self.axes.set_axis_bgcolor( ( 1, 1 , 1 ) )
        self.figure.set_facecolor( ( 0.94, 0.94 , 0.94 ) )
        _tmp = self.axes.get_ylim()
        self.axes.set_title( title )
        self.axes.set_xlabel( label[0] )
        self.axes.set_ylabel( label[1] )
        #不显示ticks
        self.axes.set_yticklabels( [] )
        self.axes.set_xticklabels( [] )
        self.canvas.draw()
    
    def gridOn( self ):
        "grid on"
        self.axes.grid( b = True )
    
    def gridOff( self ):
        "grid off"
        self.axes.grid( b = False )
    
    def clear( self ):
        self.figure.set_canvas( self.canvas )
        self.axes.clear()
        self.canvas.draw()
        



if __name__ == '__main__':
    pass
