#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     filehandle.py
# Description:  用于处理文件的复制删除等相关操作     
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2012-03-28
# Company:      CASCO
# LastChange:   update 2012-03-28
# History:      
            
#---------------------------------------------------------------------------
import win32file
import os

def CopyFile( FromFile, ToFile ):
    "copy file"
#    os.system( "copy %s %s" % ( FromFile, ToFile ) )
    win32file.CopyFile( FromFile, ToFile, 0 )  #0为覆盖，1为不覆盖

#----------------------------------------------------------
#注：本函数主要用用于更文件夹路径的名字，
#注意：os.rename不能将一个硬盘下的文件弄到另一个硬盘上
#但是可以将文件更名并放在任意已经存在的文件夹下
#----------------------------------------------------------
def ReNameFolder( oldPath, NewPath ):
    "Rename  folder"
    if False == os.path.exists( oldPath ) or\
       False == os.path.isdir( oldPath ):
        return False
    else:
        _newPath = os.path.split( NewPath )[0]
        if  False == os.path.isdir( _newPath ): #检查上层目录是否存在，不存在需要创建
            os.makedirs( _newPath )
        
        try:    
            os.rename( oldPath, NewPath )
        except:
            return False
        return True


def deleteFile( File ):
    "delete file"
    win32file.DeleteFile( File )

def deleteFolder( Folder ): #包括文件
    "delete folder"
    if False == os.path.exists( Folder ):
        print "deleteFolder error: Not exist folder", Folder
        return
    for root, dirs, files in os.walk( Folder ):
        for file in files:
            deleteFile( os.path.join( Folder, file ) )
        for dir in dirs:
            deleteFolder( os.path.join( Folder, dir ) )
        break #只删除第一层，后面的由递归解决
    win32file.RemoveDirectory( Folder ) #该目录必须为空的

#------------------------------------------------
#将basepath和filelist中的名字一次连接成path
#------------------------------------------------
def joinpaths( basepath, filelist ):
    "join paths"
    _revpath = basepath
    for _f in filelist:
        _revpath = os.path.join( _revpath, _f )
    return _revpath
    
def MakeDir( path ):
    "make direction"
    os.makedirs( path )
    
def CopyFolder( FromFolder, ToFolder ): 
    "copy folder"
    if False == os.path.exists( FromFolder ):
        print "deleteFolder error: Not exist folder", FromFolder
        return
    if False == os.path.exists( ToFolder ):
        os.makedirs( ToFolder )
    for root, dirs, files in os.walk( FromFolder ):
        for file in files:
            CopyFile( os.path.join( FromFolder, file ), \
                      os.path.join( ToFolder, file ) )
        for dir in dirs:
            CopyFolder( os.path.join( FromFolder, dir ), \
                        os.path.join( ToFolder, dir ) )
        break #保证只拷贝更目录的文件
        

if __name__ == '__main__':
    print ReNameFolder( "D:/ab", "D:/a/ab" )
#    a = '\xcf\xb5\xcd\xb3\xd5\xd2\xb2\xbb\xb5\xbd\xd6\xb8\xb6\xa8\xb5\xc4\xce\xc4\xbc\xfe\xa1\xa3'
#    print a.decode('gb2312')
#    CopyFolder("D://1212121", "D://121")    
#    deleteFolder( "D://121" )
#    print os.walk( "D://1212121" )
