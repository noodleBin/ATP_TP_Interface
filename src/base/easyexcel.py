#!/usr/bin/env python
#coding=utf-8
#----------------------------------------------------------------------------
# FileName:     easyexcel.py
# Description:  用于对excel文件进行处理，该文件参考值网络代码   
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2012-04-04
# Company:      CASCO
# LastChange:   update 2012-04-04
# History:      
#---------------------------------------------------------------------------
from win32com.client import Dispatch
#import win32com.client
import os
#import locale
class EasyExcel:
    """A utility to make it easier to get at Excel.Remembering
      to save the data is your problem, as is error handling.
      Operates on one workbook at a time.
    """

    def __init__( self, filename = None, visible = 0 ):
        if filename:
            self.xlApp = Dispatch( 'Excel.Application' )
            self.xlApp.Visible = visible

            #判断文件是否已经打开，若打开则直接引用
            filename = filename.strip()
#            print filename
            if not os.path.isfile( filename ):
                print filename + 'does not exit.'
                raise ValueError
            opended_file = [self.xlApp.Workbooks.Item( i ).FullName\
                for i in  range( 1, self.xlApp.Workbooks.Count + 1 )]#知道其意义，但不知是何种语法？
            
            if '/' in filename:
                filename = filename.replace( '/', '\\' )

            if filename in opended_file:
                #print 'Document %s opened!' % filename
                #f_name 不包含路径
                f_name = ( filename.split( '\\' )[-1] ).strip()
                #print f_name
                self.xlBook = self.xlApp.Workbooks.Item( f_name )
            else:
                #print 'open new.'
                self.xlBook = self.xlApp.Workbooks.Open( filename )
        else:
            self.xlBook = self.xlApp.Workbooks.Add()
            self.filename = ''

    def save( self, newfilename = None ):
        if newfilename:
            self.filename = newfilename
            self.xlBook.SaveAs( newfilename )
        else:
            self.xlBook.Save()

    def close( self ):
        self.xlBook.Close( SaveChanges = 0 )
        del self.xlApp

    def getCell( self, sheet, row, col ):
        "Get value of one cell"

        sht = self.xlBook.Worksheets( sheet )#页码

        return sht.Cells( row, col ).Value   #返回所要获得的位置的值
    
    def setColor( self, sheet, row, col, value ):
        sht = self.xlBook.Worksheets( sheet )
        sht.Cells( row, col ).Interior.ColorIndex = value
        

    def setCell( self, sheet, row, col, value ):
        "set value of one cell"
        sht = self.xlBook.Worksheets( sheet )
        sht.Cells( row, col ).Value = value

    def getRange( self, sheet, row1, col1, row2, col2 ):
        "return a 2d array (i.e. tuple of tuples)"
        sht = self.xlBook.Worksheets( sheet )
        return sht.Range( sht.Cells( row1, col1 ), sht.Cells( row2, col2 ) ).Value

    def addPicture( self, sheet, pictureName, Left, Top, Width, Height ):
        "Insert a picture in sheet"
        sht = self.xlBook.Worksheets( sheet )
        sht.Shapes.AddPicture( pictureName, 1, 1, Left, Top, Width, Height )

    def cpSheet( self, before ):
        "copy sheet"
        shts = self.xlBook.Worksheets
        shts( 1 ).Copy( None, shts( 1 ) )
    
    def usedRows( self, sheet ):
        "retured used rows"
        sht = self.xlBook.Worksheets( sheet )
        return sht.UsedRange.Rows.Count
    
    def usedColumns( self, sheet ):
        "retured used rows"
        sht = self.xlBook.Worksheets( sheet )
        return sht.UsedRange.Columns.Count
    
    def sheetNum( self ):
        "return the num of the sheet"
        num = len( self.xlBook.Sheets )
        return num
    
    def sheetName( self, index ):
        "return the name of sheet[index]"
        name = self.xlBook.Sheets[index].name
        return name
    
    def cell_row_col( self, sheet, key ):
        "return the row col  of a cell by key "
        x_length = self.usedRows( sheet )
        y_length = self.usedColumns( sheet )
        find = 0
        
        for row in range( 1, x_length + 1 ):
            for col in range( 1, y_length + 1 ):
                value = self.getCell( sheet, row, col )
                if value == key:
                    find = 1
                    break
            if find == 1:
                break
        if find == 0:
            row , col = None, None

        return row, col

#get excel list
def get_list( excel, sht_num ):
        sheetlist = []
        for i in range( sht_num ):
            sheetlist.append( excel.sheetName( i ) )
        return sheetlist

if __name__ == '__main__': 
    a = EasyExcel( filename = u"C:\\Users\\60844\\Desktop\\CCNV文档\\CCNV_TC_TR_table.xls" )
    print a.sheetName( 0 )
    print a.getCell( 1, 2, 1 )
    a.close()
