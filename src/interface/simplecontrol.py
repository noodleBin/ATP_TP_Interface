#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     simplecontrol.py
# Description:  table 
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2011-11-03
# Company:      CASCO
# LastChange:   create 2011-11-03
# History:          
#----------------------------------------------------------------------------
#import wx.wizard
import  wx
import  wx.grid as Grid
#import sys
#import time
#import  wx.lib.filebrowsebutton as filebrowse
#import images
    
# -- SizeReportCtrl --
# (a utility control that always reports it's client size)
class SizeReportCtrl( wx.PyControl ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition,
                size = wx.DefaultSize, mgr = None ):

        wx.PyControl.__init__( self, parent, id, pos, size, style = wx.NO_BORDER )
        self._mgr = mgr

        self.Bind( wx.EVT_PAINT, self.OnPaint )
        self.Bind( wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground )
        self.Bind( wx.EVT_SIZE, self.OnSize )


    def OnPaint( self, event ):
    
        dc = wx.PaintDC( self )
        size = self.GetClientSize()

        s = "Size: %d x %d" % ( size.x, size.y )

        dc.SetFont( wx.NORMAL_FONT )
        w, height = dc.GetTextExtent( s )
        height += 3
        dc.SetBrush( wx.WHITE_BRUSH )
        dc.SetPen( wx.WHITE_PEN )
        dc.DrawRectangle( 0, 0, size.x, size.y )
        dc.SetPen( wx.LIGHT_GREY_PEN )
        dc.DrawLine( 0, 0, size.x, size.y )
        dc.DrawLine( 0, size.y, size.x, 0 )
        dc.DrawText( s, ( size.x - w ) / 2, ( size.y - height * 5 ) / 2 )

        if self._mgr:
        
            pi = self._mgr.GetPane( self )

            s = "Layer: %d" % pi.dock_layer
            w, h = dc.GetTextExtent( s )
            dc.DrawText( s, ( size.x - w ) / 2, ( ( size.y - ( height * 5 ) ) / 2 ) + ( height * 1 ) )

            s = "Dock: %d Row: %d" % ( pi.dock_direction, pi.dock_row )
            w, h = dc.GetTextExtent( s )
            dc.DrawText( s, ( size.x - w ) / 2, ( ( size.y - ( height * 5 ) ) / 2 ) + ( height * 2 ) )

            s = "Position: %d" % pi.dock_pos
            w, h = dc.GetTextExtent( s )
            dc.DrawText( s, ( size.x - w ) / 2, ( ( size.y - ( height * 5 ) ) / 2 ) + ( height * 3 ) )

            s = "Proportion: %d" % pi.dock_proportion
            w, h = dc.GetTextExtent( s )
            dc.DrawText( s, ( size.x - w ) / 2, ( ( size.y - ( height * 5 ) ) / 2 ) + ( height * 4 ) )

        
    def OnEraseBackground( self, event ):

        pass
    

    def OnSize( self, event ):
    
        self.Refresh()


class SimpleDataTable( Grid.PyGridTableBase ):
    def __init__( self, rowLines, colname, dataType, data ):
        Grid.PyGridTableBase.__init__( self )
        self.rowLines = rowLines
        self.colLabels = colname
        self.dataTypes = dataType
        self.data = data
        
        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols() 
    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface
    def GetNumberRows( self ):
        #return len(self.data)
        return self.rowLines
    
    def GetNumberCols( self ):
        try:
            return len( self.data[0] )
        except IndexError, e:
            return 0
    
    def IsEmptyCell( self, row, col ):
        try:
            return not self.data[row][col]
        except IndexError:
            return True
    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue( self, row, col ):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue( self, row, col, value ):
        def innerSetValue( row, col, value ):
            try:
                self.data[row][col] = value
            except IndexError:
                # add a new row
                self.data.append( [''] * self.GetNumberCols() )
                innerSetValue( row, col, value )
                # tell the grid we've added a row
                msg = Grid.GridTableMessage( self, # The table
                        Grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                        1                                       # how many
                        )
                self.GetView().ProcessTableMessage( msg )
        innerSetValue( row, col, value ) 
    #--------------------------------------------------
    # Some optional methods
    # Called when the grid needs to display labels
    def GetColLabelValue( self, col ):
        return self.colLabels[col]
    
    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName( self, row, col ):
        return self.dataTypes[col]
    
    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs( self, row, col, typeName ):
        colType = self.dataTypes[col].split( ':' )[0]
        if typeName == colType:
            return True
        else:
            return False
    
    def CanSetValueAs( self, row, col, typeName ):
        return self.CanGetValueAs( row, col, typeName )

    def AppendRows( self, numRows = 1 ):
        self.rowLines += 1
        #print 'tsrData = ', self.data
        return True

    def ResetView( self, grid ):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        grid.BeginBatch()

        for current, new, delmsg, addmsg in [
                ( self._rows, self.GetNumberRows(), Grid.GRIDTABLE_NOTIFY_ROWS_DELETED, Grid.GRIDTABLE_NOTIFY_ROWS_APPENDED ),
                ( self._cols, self.GetNumberCols(), Grid.GRIDTABLE_NOTIFY_COLS_DELETED, Grid.GRIDTABLE_NOTIFY_COLS_APPENDED ),
                ]:
            if new < current:
                msg = Grid.GridTableMessage( self, delmsg, new, current - new )
                grid.ProcessTableMessage( msg )
            elif new > current:
                msg = Grid.GridTableMessage( self, addmsg, new - current )
                grid.ProcessTableMessage( msg )
                self.UpdateValues( grid )

        grid.EndBatch()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

        # update the scrollbars and the displayed part of the grid
        grid.AdjustScrollbars()
        grid.ForceRefresh() 
        
    def UpdateValues( self, grid ):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = Grid.GridTableMessage( self, Grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES )
        grid.ProcessTableMessage( msg ) 

    def addRow( self, data ):
        self.data.append( data )
        return data
    
    
#--------------------------------------------------------
#List控件
#--------------------------------------------------------
class SimpleList( wx.ListCtrl ):
    def __init__( self, parent, size = ( 100, 200 ) ):
        wx.ListCtrl.__init__( self, parent, -1, size = size,
                             style = wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_HRULES | wx.LC_VRULES )
        self.data = []  #用于保存list数据，此数据主要作用是便于使用
        self.curItem = [] #当前选择的Item数据
        self.curRowIndex = None #
        self.SetItemCount( 50 )
        self.NRows = 0
        self.NCols = 0
        self.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected )
    
    def ListIni( self, Label, data ):
        "给列表添加初始化数据"
        self.SetColumn( Label )
        for _item in data:
            self.AddNewItem( _item )
        
    def SetColumn( self, coldata ):
        "将coldata中的数据作为list的列放入其中"
        for i, item in enumerate( coldata ):
            self.InsertColumn( i, item, wx.LIST_FORMAT_LEFT ) 
            self.NCols = self.NCols + 1
            self.SetColumnWidth( i, 300 )

    def AddNewItem( self, Item ):
        "添加元素"
        self.data.append( Item )
        self.curItem = Item
        #显示
        _index = len( self.data ) - 1
        for _i in range( len( Item ) ):
            self.SetStringItem( _index, _i, Item[_i] )

        self.curRowIndex = _index
        self.NRows = self.curRowIndex + 1
        self.SetItemState( _index, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED )
        
        
    def OnItemSelected( self, event ):
        "选择操作"
        self.curRowIndex = event.m_itemIndex
        print "On select!", self.curRowIndex
        #将行中的数据放入curItem中
        if self.curRowIndex < self.NRows:#在范围内
            self.curItem = self.data[self.curRowIndex] #取值
        else:
            print 'out of range！'  #不做操作
        
    def OnDeleItem( self ):
        "删除Item"
        #先删除显示
        _curItem = self.GetFocusedItem()
        if -1 != _curItem:
            self.DeleteItem( _curItem )
            self.curRowIndex = self.curRowIndex - 1 if self.curRowIndex > 0 else None
            if self.curRowIndex != None:
                self.data.pop( self.curRowIndex + 1 )
                self.curItem = self.data[self.curRowIndex]
                
        
        
        
class SimpleGrid( Grid.Grid ):
    def __init__( self, parent, colname, dataType, mysize ):
        Grid.Grid.__init__( self, parent, -1, size = mysize )
        self.colname = colname
        self.dataType = dataType
        #self.rowLines = rowLines

    def setCustable( self, data ):
        self.data = data
        self.rowLines = len( self.data )
        self.tableBase = SimpleDataTable( self.rowLines, self.colname,
                                         self.dataType,
                                         self.data )
        self.SetTable( self.tableBase, True )
        self.SetRowLabelSize( 40 )
        self.SetMargins( 0, 0 )
        self.AutoSizeColumns( True )
        self.EnableEditing( True )
        
        self.Bind( Grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClicked ) 
        
        #更新大小
        self.Resize()
        self.Refresh()
        self.Update()
    
    def RefreshData( self, data ):
        "refresh data"
        self.data = data
        for _r, _d in enumerate( data ):
            for _c, _v in enumerate( _d ):
                self.SetCellValue( _r, _c, _v )

    def OnLabelRightClicked( self, evt ):
        row, col = evt.GetRow(), evt.GetCol()
        if col == -1:
            self.rowPopup( row, evt )
    
    def rowPopup( self, row, evt ):
        """
        (row, evt) -> display a popup menu when a row label is right clicked
        """
        changeID = wx.NewId()
        deleteID = wx.NewId()

        menu = wx.Menu()
        menu.Append( changeID, u'确定' )
        
        def change( event, self = self, row = row ):
            print 'on change TSR'
            data = []
            for j, value in enumerate( [self.GetCellValue( row, i ) for i in range( self.GetNumberCols() )] ):
                if value:
                        data.append( value )
                else:
                    dlg = wx.MessageDialog( self, u'当前行数据不能为空',
                            u'警告',
                            wx.OK | wx.ICON_INFORMATION
                        )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            print 'data = ', data
        
        self.Bind( wx.EVT_MENU, change, id = changeID )
        
        self.PopupMenu( menu )
        menu.Destroy()
        return

    def resSet( self ):
        self.tableBase.ResetView( self )
    
    def addRow( self, data ):
        self.tableBase.addRow( data )
        #self.data.append(object)

    def delRow( self, data ):
        if data in self.data:
            self.data.remove( data )
        else:
            print 'data = ', data , 'not in curent dataList'
        self.setCustable( data )
    
    def Resize( self , size = None ):
        _size = self.GetSize()[0] if size == None else size[0]
#        print _size
        try:
            _len = len( self.data[0] )
        except IndexError, e:
            _len = 1
        _colSize = ( _size - 60 ) / _len
        for i in range( _len ):
            self.SetColSize( i, _colSize )



class ShowGrid( Grid.Grid ):
    "show grid"
    
    __CurIndex = None
    def __init__( self, parent, colname, size = ( 100, 200 ), OnSelectHandle = None, CopyFlag = False, OnDoubleClickHandle = None ):
        Grid.Grid.__init__( self, parent, -1, size = size )
        self.colname = colname
        self.dataType = []
        for i in range( len( colname ) ):
            self.dataType.append( Grid.GRID_VALUE_STRING )
#        self.SetSelectionBackground()
#        print self.GetSelectionMode()
#        self.SetSelectionMode(Grid.Grid.SelectRows)
#        self.EnableEditing( False )
        #self.rowLines = rowLines
        if None == OnSelectHandle:
            self.Bind( Grid.EVT_GRID_CELL_LEFT_CLICK, self.OnSelect )
        elif False != OnSelectHandle:
            self.Bind( Grid.EVT_GRID_CELL_LEFT_CLICK, OnSelectHandle )
        self.__CopyFlag = CopyFlag
        if True == self.__CopyFlag:#保证能copy不能修改
            self.Bind( Grid.EVT_GRID_CELL_CHANGE, self.OnCellChange )
        if None != OnDoubleClickHandle:
            self.Bind( Grid.EVT_GRID_CELL_LEFT_DCLICK, OnDoubleClickHandle )
#    def setSelMode( self, type ):
#        "set Sel Mode"
#        if 1 == type:
#            self.SetSelectionMode( Grid.Grid.SelectRows )
#        elif 2 == type:
#            self.SetSelectionMode( Grid.Grid.SelectedCols )
#        elif 3 == type:
#            self.SetSelectionMode( Grid.Grid.SelectCells )
#        else:
#            self.Enable( False )
    def OnCellChange( self, event ):
        "OnCellChange"
        event.Veto()
    
    def setCustable( self, data ):
        self.data = data
        self.rowLines = len( self.data )
        self.tableBase = SimpleDataTable( self.rowLines if len( data ) > 0 else 1,
                                          self.colname,
                                          self.dataType,
                                          data if len( data ) > 0 else [['No data'] * len( self.colname )] )
        self.SetTable( self.tableBase, True )
        self.EnableEditing( self.__CopyFlag )
#        self.EnableCellEditControl( False )
        self.SetSelectionMode( Grid.Grid.SelectRows )
#        self.SetSelectionMode( Grid.Grid.SelectCells )
        self.SetRowLabelSize( 30 )
        self.SetMargins( 0, 0 )
        self.AutoSizeColumns( True )
#        self.EnableEditing( True )
        
        #更新大小
        self.Resize()
        self.Refresh()
        self.Update()
    
    def GetData( self ):
        "get data"
        return self.data
    
    def AddOneData( self, data ):
        "add one data."
#        print dir( self )
        self.data.append( data )
        self.setCustable( self.data )
        
    def EditOneData( self, data ):
        "edit one data"
        if self.__CurIndex not in [None, -1]:
            self.data[self.__CurIndex] = data
            self.RefreshData( self.data )
        else:
            print "EditOneData error!!!", data
        
    def GetSelectData( self ):
        "get select data"
        if self.__CurIndex not in [-1, None]:
            return self.data[self.__CurIndex]
        else:
            return None
        
    def DelOneData( self, index ):
        "delete one data."
        self.data.pop( index )
        self.setCustable( self.data ) 
        self.__CurIndex = None      #只能一个一个删除  
    
    def OnSelect( self, event ):
        "on select"
        _CellRow = event.GetRow()

        if -1 == _CellRow or _CellRow >= len( self.data ):
            print "OnSelect:", "Invalid index!"
            self.__CurIndex = None
        else:
            self.changeCurLineColour( _CellRow )
            self.__CurIndex = _CellRow

    def changeCurLineColour( self, index ):
        "change current index."
        if index not in range( len( self.data ) ):
            return
        
        #高亮显示
        if None != self.__CurIndex:#去除高亮
            for _i in range( len( self.colname ) ):
                self.SetCellBackgroundColour( self.__CurIndex, _i, wx.WHITE )
                self.SetCellTextColour( self.__CurIndex, _i, wx.BLACK )
        
        for _i in range( len( self.colname ) ):
            self.SetCellBackgroundColour( index, _i, wx.BLUE )
            self.SetCellTextColour( index, _i, wx.WHITE )

        self.Refresh()
            
    def GetSelection( self ):
        "get selection"
        return self.__CurIndex
    
    def SetSelection( self, index ):
        "Set Selection"
        self.__CurIndex = index

    def RefreshData( self, data ):
        "refresh data"
        self.data = data
        for _r, _d in enumerate( data ):
            for _c, _v in enumerate( _d ):
                self.SetCellValue( _r, _c, _v )

    def Resize( self , size = None ):
        _size = self.GetSize()[0] if size == None else size[0]
#        print _size
        try:
            _len = len( self.colname )
        except IndexError, e:
            _len = 1
        _colSize = ( _size - 50 ) / _len
        for i in range( _len ):
            self.SetColSize( i, _colSize )



class EditGrid( Grid.Grid ):
    "Edit grid"
    
    __CurIndex = None
    def __init__( self, parent, colname, editType = None, cell_change_fun = None ):
        Grid.Grid.__init__( self, parent, -1, size = ( 100, 200 ) )
        self.colname = colname
        self.dataType = []
        for i in range( len( colname ) ):
            self.dataType.append( Grid.GRID_VALUE_STRING )
        self.__EditType = editType #某列是否可编辑，与colname对应的，True为可编辑，False为不可编辑[True,False,...]
#        self.SetSelectionMode(Grid.Grid.SelectRows)
        if None == cell_change_fun:
            self.Bind( Grid.EVT_GRID_CELL_CHANGE, self.OnCellChange )
        else:
            self.Bind( Grid.EVT_GRID_CELL_CHANGE, cell_change_fun )

    def setCustable( self, data ):
        #注意该函数将会引发EVT_GRID_CELL_CHANGE事件！！！！！
        self.data = data
        self.rowLines = len( self.data )
        self.tableBase = SimpleDataTable( self.rowLines if len( data ) > 0 else 1,
                                          self.colname,
                                          self.dataType,
                                          data if len( data ) > 0 else [['No data'] * len( self.colname )] )
        
#        self.data = data
#        self.rowLines = len( self.data )
#        self.tableBase = SimpleDataTable( self.rowLines, self.colname,
#                                         self.dataType,
#                                         self.data )

        self.SetTable( self.tableBase, True )
        self.SetRowLabelSize( 30 )
        self.SetMargins( 0, 0 )
        self.AutoSizeColumns( True )
        self.EnableEditing( True )
        
        #更新大小
        self.Resize()
        self.Refresh()
        self.Update()
    
    def GetData( self ):
        "get data"
        return self.data

    def OnCellChange( self, event ):
#        _old_value = event.GetOldValue()
#        print dir( event )
        _CellRow = event.GetRow()
        _CellCol = event.GetCol()
        _Change = False
#        print _CellRow, _CellCol, self.__EditType
        #最后一列的值的修改，既value的修改
        if ( _CellCol >= 0 ) and ( self.__EditType[_CellCol] ):
#            print '12121', _CellCol, self.__EditType
            _Change = True
            self.data[_CellRow][_CellCol] = self.GetCellValue( _CellRow, _CellCol )

#        self.RefreshData( self.data ) 
        self.__CurIndex = _CellRow
        return _Change
    
    def OnSelect( self, event ):
        "on select"
        _CellRow = event.GetRow()

        if -1 == _CellRow or _CellRow >= len( self.data ):
            print "OnSelect:", "Invalid index!"
            self.__CurIndex = None
        else:
            self.__CurIndex = _CellRow
            
    def GetSelection( self ):
        "get selection"
        return self.__CurIndex
    
    def SetSelection( self, index ):
        "Set Selection"
        self.__CurIndex = index

    def RefreshData( self, data ):
        "refresh data"
        self.data = data
        for _r, _d in enumerate( data ):
            for _c, _v in enumerate( _d ):
                self.SetCellValue( _r, _c, _v )

    def Resize( self ):
        _size = self.GetSize()[0]
        #print _size
        try:
            _len = len( self.colname )
        except IndexError, e:
            _len = 1
        _colSize = ( _size - 50 ) / _len
        for i in range( _len ):
            self.SetColSize( i, _colSize )


if __name__ == '__main__':
    pass
