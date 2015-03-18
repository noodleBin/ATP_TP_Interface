#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     caseprocess.py
# Description:  本文件主要用于配置用例的处理，包含读取配置文件，导入配置，保存配置，修改配置    
# Author:       XIONG KUNPENG
# Version:      0.0.3
# Created:      2011-11-10
# Company:      CASCO
# LastChange:   update 2011-11-10
# History:      finished in 2011-11-14
#               add CaseParser in 2012-02-17
#               add CaseEdit in 2012-03-22
#----------------------------------------------------------------------------
from xmlparser import XmlParser
import lxml
from lxml import etree
import os
import commlib
from base.xmldeal import XMLDeal
from base.simdata import MapData
import copy
import filehandle
from base.simdata import TrainRoute

TestPlatformFlag = "ATP"
class CaseProcess( object ):
    """
    case Process class
    """
    __data = None #{casepath:[Filename,casename,type],...}
    #__datapathinfo = None #[casepath,...]
    __dataotherinfo = None #[[casepath,status,content],...]
    #__Userpath = r"//case"
    def __init__( self ):
        pass
    
    def importUserCase( self, Usrefile ):
        "import User Case "
        _f = XmlParser()
        _f.loadXmlFile( Usrefile )
        self.__data = {}
        #self.__datapathinfo = []
        self.__dataotherinfo = []
        _case = _f.getAttrListManyElement( r".//case", ["path"] )
        for _i, _c in enumerate( _case ):
            _key = _c[0]  #path
            #self.__datapathinfo.append(_key)
            self.__dataotherinfo.append( [_key, 'untest', 'write content here!'] )
            _Filename = _key.strip().split( "/" )[-1]
            _fcase = XmlParser()
            _fcase.loadXmlFile( _key + "/case_config.xml" )
            _attr = _fcase.getAttrListManyElement( r".//info", ["casename", "type"] )[0]
            #print _attr
            self.__data[_key] = [_Filename, _attr[0], _attr[1]]
            _fcase.closeXmlFile()
        _f.closeXmlFile()
        #print self.__data
        #print self.__datapathinfo
    #-------------------------------------------------------------
    #添加新的case
    #@path:用例的主路径
    #@attr:用例的属性值[casename,type]
    #-------------------------------------------------------------
    def addNewCase( self, path, attr ):
        "添加新case，并更新相关的文件，也即user_case_config.xml"
        if self.checkCaseValid( path ):
            #将数据添加到data
            _filename = path.strip().split( "/" )[-1]
            self.__data["path"] = [_filename] + attr
            #更新__dataindex
            #self.__datapathinfo.append(path)
            self.__dataotherinfo.append( [path, 'untest', 'write content here!'] )
            #更新user_case_config.xml
            self.updataconfig( path )
            #创建case_config.xml
            self.ModifyCaseConfigXML( path, attr )
        else:
            print "invalid path!!!!!"
    
    #-------------------------------------------------------------
    #@创建或修改的case_config.xml
    #@path：case_config.xml的存放路径
    #@attr：[casename,type]
    #-------------------------------------------------------------
    def ModifyCaseConfigXML( self, path, attr ):
        "Modify case config"
        _file = open( path + '/case_config.xml', 'w' ) #创建新的文件
        _file.write( r'<?xml version="1.0" encoding="utf-8"?-->\n' ) #添加xml头
        _file.write( r'<!--用例的相关配置-->\n' ) #添加xml头
        
        #添加初始化数据
        _case_config = etree.Element( "case" )
        #写入info
        _case_info = etree.SubElement( _case_config, "info" )
        #_case_info.set("name", attr[0])
        _case_info.set( "casename", attr[0] )
        _case_info.set( "type", attr[1] )
        #写入初始的history,后续值修改需要进入xml文件内部进行
        _case_history = etree.SubElement( "history" )
        _case_info.set( "result", "untest" )
        _case_info.set( "date", commlib.curTime() )
        _case_info.set( "content", "created" )
        
        
    #-------------------------------------------------------------
    #@根据__data内容更新user_case_config.xml
    #-------------------------------------------------------------
    def updataconfig( self, path ):
        _file = open( '../testcaseconfig/user_case_config.xml' , 'w' ) #打开文件
        _file.write( r'<?xml version="1.0" encoding="utf-8"?-->\n' ) #添加xml头
        _file.write( r'<!--测试平台中的用例配置脚本-->\n' ) #添加xml头
        
        #根据__data添加相关内容
        _case_Config = etree.Element( "User_case_Config" )
        for _Key in self.__data:
            _case = etree.SubElement( _case_Config, "case" )
            _case.set( "path", path )
        _Config_String = etree.tostring( _case_Config, pretty_print = True )           
        _file.write( _Config_String )
        _file.close()
        
    #-------------------------------------------------------------
    #@删除用例
    #index:用例对应的index
    #-------------------------------------------------------------            
    def deleCase( self, index ):
        "删除case，并更新相关的文件，也即user_case_config.xml"
        #先找到该值
        if index < len( self.__dataotherinfo ):
            self.__data.pop( self.__dataotherinfo[index][0] )
            #self.__datapathinfo.pop(index)
            self.__dataotherinfo.pop( index )
        else:
            print "deleCase: index out of range!!!"
        
    #---------------------------------------------------
    #@检测用例所需的文件是否具备
    #@包括文件四个文件夹datafile,log,scenario,setting
    #---------------------------------------------------
    def checkCaseValid( self, path ):
        "检验case路径下的case时候有效，无效则返回false"
        _revflag = False
        if False == os.path.exists( path + "/datafile" ):
            print "Not exist datafile folder!"
        elif False == os.path.exists( path + "/log" ):
            print "Not exist datafile folder!"
        elif False == os.path.exists( path + "/setting" ):
            print "Not exist setting folder!"
        elif False == os.path.exists( path + "/scenario" ):
            print "Not exist scenario folder!"
        else:
            _revflag = True
        
        return _revflag
        
    def addCaseHistory( self ):
        "给某个case添加历史记录"
        pass
    
    #------------------------------------------------------------
    #@获取用于界面显示的消息
    #本函数通过数据__data以及__datapathinfo获取用于界面显示的数据
    #返回数据revdata:[Filename,casename,type,status,content]
    #------------------------------------------------------------
    def getCaseDispalyInfo( self ):
        "获取case的用于显示的消息"
        _revdata = []
        #print self.__data
        #print self.__dataotherinfo
        for _item in self.__dataotherinfo:
            _tmpitem = self.__data[_item[0]] + _item[1:]
            #print '_tmpitem', _tmpitem
            _revdata.append( _tmpitem )
        return _revdata
    #-----------------------------------------------------------
    #@通过界面的更新，修改__data以及__dataotherinfo中对应的值
    #@attr:[Filename,casename,type,status,content]
    #-----------------------------------------------------------
    def UpdataCaseInfo( self, index, attr ):
        "更新用例Info，这里要更新data和case_config.xml"
        if index >= len( self.__dataotherinfo ):
            print "UpdataCaseInfo: index out of range!"
        else:
            _path = self.__dataotherinfo[index][0]
            self.__data[_path] = attr[0:3]
            self.__dataotherinfo[index] = [_path] + attr[3:]

    #----------------------------------------------------------
    #@获取__data
    #----------------------------------------------------------
    def getConfigData( self ):
        "get __data"
        return self.__data
    
    #----------------------------------------------------------
    #@获取__dataotherinfo
    #----------------------------------------------------------
    def getOtherData( self ):
        "get __dataotherinfo"
        return self.__dataotherinfo
    
    #----------------------------------------------------------
    #@通过casename获取用例的整个配置信息
    #@返回值：[casename,type,status,content]
    #----------------------------------------------------------
    def getCaseInfobyName( self, casename ):
        "get case information through casename"
        for _item in self.__dataotherinfo:
            _path = _item[0]
            _tmpdata = self.data[_path]
            if casename == _tmpdata[0]:
                return [_tmpdata[0], _tmpdata[1], _item[1], _item[2]]
        
        return None


#-------------------------------------------------------------------------------------
#用于导入用例，并管理用例路径时使用，后面还将添加管理地图和配置文件的工作，主要是管理和更新用例对应的脚本和路径，该类将保存所有的界面辅助数据
#-------------------------------------------------------------------------------------
class CaseParser( object ):
    "case parser"
    __pathinfo = []  #用于存储导入的用例库的路劲消息，[被测版本标签号,{测试用例编号1:{测试步骤编号1:[LogPath,ScriptPath,DownLogPath],...},...}]
    __CurWorkPath = None  #用于存储当前用例的work路径
    __CurSelectCases = [] #保存当前选中的用例，以及对应的内容：[[被测版本标签号,测试用例编号,测试步骤编号,测试状态],...]
    __Mapinfo = []   #用于保存地图的信息，这个信息是由地图库中获得的[CC offline版本号,{地图编号：[atp_up_path,atp_down_path,ccnv_path,tp_map_path,tp_txt_path],...}]
    __Configinfo = [] #配置文件版本：本项目待定
    __CurRunCaseIndex = -1
    
    __EditCaseInfo = None  #正在编辑的用例的信息，[测试用例编号, 测试步骤编号,测试状态]
    
    __EditCaseConfig = {} #当前用例配置，{'map':[version,mapNum,description],
                                    #'fileconfig'：[TrainEnd,DataplugPath,Description],
                                    #'endconfig':[type,para,Desription],
                                    #'history':[[date,status,description],...]}
                                    
    __CurRunCaseConfig = {} #当前运行的用例配置，{'map':[version,mapNum,description],
                                    #'fileconfig'：[TrainEnd,DataplugPath,Description],
                                    #'endconfig':[type,para,Desription],
                                    #'history':[[date,status,description],...]}
                                    
    __UpLoadConfig = {}  #用于保存配置文件上传的相关信息主要格式如下：{host:[[fileName,Type,Path,Description],...]}
    
    Status = {0:'Waiting',
              1:'Load',
              2:'Running',
              3:'End',
              4:'Error!!!',
              5:"Start Analysis",
              6:"End Analysis"}
    
    xmlNode = {'MapConfig':{'path':r'.//MapConfig', 'attr':['Version', 'MapNum', 'Description']},
               'FileConfig':{'path':r'.//FileConfig', 'attr':['TrainEnd', 'DataPlugPath', 'Description']},
               'EndConfig':{'path':r'.//EndConfig', 'attr':['EndType', 'Para', 'Description']},
               'History':{'path':r'.//His', 'attr':['Date', 'Status', 'Description']} ,
               'configfile_host':{'path':r'.//Host', 'attr':['Name']},
               'configfile_File':{'path':r'.//File', 'attr':['Name', 'Type', 'Path', 'Description']}
               }
    
    __CurEndType = None
    
    __CurMapPath = None
    
    __LastConfig = None
    def __init__( self ):
        "init"
        self.__pathinfo = []

    @classmethod
    def importPlatformInfo( cls, path ):
        "import platform information"
        cls.__PlatformInfo = XMLDeal.importPlatformInfo( path )
#        print cls.__PlatformInfo
    
    @classmethod
    def getTestedProductLabel( cls ):
        "get tested product label"
        return cls.__PlatformInfo['TestedProduct'][0]
    
    @classmethod
    def importLastConfig( cls, path ):
        "import Last Configuration"
        cls.__LastConfig = XMLDeal.importLPFConfig( path )

    @classmethod
    def getLastConfig_MapLib( cls ):
        "get last configuration map lib"
        return cls.__LastConfig['MapLib']

    @classmethod
    def getLastConfig_CaseLib( cls ):
        "get last configuration case lib"
        return cls.__LastConfig['CaseLib']

    @classmethod
    def getLastConfig_CaseVersion( cls ):
        "get last configuration Case Version"
        return cls.__LastConfig['CaseVersion']

    @classmethod
    def getLastConfig_LastMap( cls ):
        "set last configuration Last Map"
        return cls.__LastConfig['LastMap']    

    @classmethod
    def getLastConfig_LastConfig( cls ):
        "set last configuration Last Config"
        return cls.__LastConfig['LastConfig']
    
    @classmethod
    def setLastConfig_MapLib( cls, path, value ):
        "set last configuration map lib"
        cls.__LastConfig['MapLib'] = value
        XMLDeal.ExportLPFConfig( path, cls.__LastConfig )   

    @classmethod
    def setLastConfig_CaseLib( cls, path, value ):
        "set last configuration Case Lib"
        cls.__LastConfig['CaseLib'] = value
        XMLDeal.ExportLPFConfig( path, cls.__LastConfig )   

    @classmethod
    def setLastConfig_CaseVersion( cls, path, value ):
        "set last configuration Case Version"
        cls.__LastConfig['CaseVersion'] = value
        XMLDeal.ExportLPFConfig( path, cls.__LastConfig )   

    @classmethod
    def setLastConfig_LastMap( cls, path, value ):
        "set last configuration Last Map"
        cls.__LastConfig['LastMap'] = value
        XMLDeal.ExportLPFConfig( path, cls.__LastConfig )   

    @classmethod
    def setLastConfig_LastConfig( cls, path, value ):
        "set last configuration Last Config"
        cls.__LastConfig['LastConfig'] = value
        XMLDeal.ExportLPFConfig( path, cls.__LastConfig )  
            
    @classmethod
    def importUpLoadConfig( cls, path ):
        "import Up load configuration."
        cls.__UpLoadConfig = {}
        _f = XmlParser()
        _f.loadXmlFile( path )
        
        _host = _f.getAllElementByName( cls.xmlNode['configfile_host']['path'] )
        
        for _h in _host:
            _hostname = _f.getAttrListOneNode( _h, cls.xmlNode['configfile_host']['attr'] )[0]
        
            _filelist = []
            
            _nodes = _f.getNodeListInNode( _h, cls.xmlNode['configfile_File']['path'] )
            
            for _n in _nodes:
                _attrlist = _f.getAttrListOneNode( _n, cls.xmlNode['configfile_File']['attr'] )
                _attrlist[2] = commlib.joinPath( commlib.getCurFileDir(), _attrlist[2] )
                _filelist.append( _attrlist )
                
            cls.__UpLoadConfig[_hostname] = _filelist
        
#        print  cls.__UpLoadConfig   
        _f.closeXmlFile()        
    
    #--------------------------------------------------------------------
    #@endtype:'End1','End2',其他不换
    #--------------------------------------------------------------------
    @classmethod
    def uploadconfigfiles( cls , telnetnode , endtype ):
        "upload all config file."
        _Num = 0
#        if ( cls.__CurEndType == endtype ) or ( endtype not in ['End1', 'End2'] ): #不换头不需要重传配置文件
#            print "uploadconfigfiles: endtype error or don't need to upload files!"
#            return _Num
        if ( cls.getLastConfig_LastConfig() == endtype ) or ( endtype not in ['End1', 'End2'] ): #不换头不需要重传配置文件
            print "uploadconfigfiles: endtype error or don't need to upload files!"
            return _Num
              
        _uplist = None
        if "" == cls.getLastConfig_LastConfig() or None == cls.getLastConfig_LastConfig():
            _uplist = [endtype, 'All']
        else:
            _uplist = [endtype, ]
        
        #记录最新的改动    
        cls.setLastConfig_LastConfig( r'./TPConfig/LastPlatformConfig.xml',
                                      endtype )
        
        _temp = '/tffs0/'    
        
        for _host in cls.__UpLoadConfig:
            for _file in cls.__UpLoadConfig[_host]:
                if _file[1] in _uplist:
                    telnetnode.SendFileToHardWareByFTP( _host, _file[2], _temp , _file[0] )
                    _Num = _Num + 1
        
        cls.__CurEndType = endtype                    
        return _Num
        
    #------------------------------------------------------------------
    #@上传地图,mappaths:[atp_up_path,atp_down_path,ccnv_path,tp_map_path,tp_txt_path]
    #------------------------------------------------------------------
    @classmethod
    def uploadMapfile( cls, telnetnode , mappaths ):
        "upload map files"
        _Num = 0
        _mapFolder = os.path.split( mappaths[0] )[0] 
#        if  cls.__CurMapPath == mappaths: #不换头不需要重传配置文件
#            print "uploadMapfile: mappaths error or don't need to upload files!"
#            return _Num

        if  cls.getLastConfig_LastMap() == _mapFolder: #不换头不需要重传配置文件
            print "uploadMapfile: mappaths error or don't need to upload files!"
            return _Num
        
        #记录最新的改动
        cls.setLastConfig_LastMap( r'./TPConfig/LastPlatformConfig.xml',
                                   _mapFolder )
        
        _temp = '/tffs0/' 
        _uplist = ['Map0', 'Map1', 'Map2', 'Map3', 'Map4', 'Map5']
        for _host in cls.__UpLoadConfig:
            for _file in cls.__UpLoadConfig[_host]:
                if _file[1] in _uplist:
                    _index = int( _file[1][-1] )
                    telnetnode.SendFileToHardWareByFTP( _host, mappaths[_index], _temp , _file[0] )            
                    _Num = _Num + 1

        cls.__CurMapPath = mappaths
                
        return _Num
    
    #--------------------------------------------------
    #获取当前Run的用例的平台地图路径
    #--------------------------------------------------
    @classmethod
    def getCurRunCaseMappath( cls ):
        "get current run case map path"
        return cls.__Mapinfo[1][cls.getCurRunCaseConfig()['map'][1]][3:5]
    
                    
    #----------------------------------------------------------------------
    #@根据当前的用例配置上传说有配置文件
    #----------------------------------------------------------------------
    @classmethod
    def uploadAllFiles( cls, telnetnode ):
        "upload all files to hardwares."
        _EndType = cls.getCurRunCaseConfig()['fileconfig'][0]
        _MapPaths = cls.__Mapinfo[1][cls.getCurRunCaseConfig()['map'][1]]
        
        _Num1 = cls.uploadconfigfiles( telnetnode, _EndType )
        
        _Num2 = cls.uploadMapfile( telnetnode, _MapPaths )
        
        return _Num1 + _Num2
    
    @classmethod
    def getCurSelectCaseInfo( self ):
        "get Current select cases."
        return self.__CurSelectCases
    
    @classmethod
    def getCurCasePath( cls ):
        "get Cur Case Path."
        _CaseNum = cls.__CurSelectCases[cls.__CurRunCaseIndex][1]
        _CaseStep = cls.__CurSelectCases[cls.__CurRunCaseIndex][2]
        return cls.getCasePathByCaseNum( _CaseNum, _CaseStep )

    #-----------------------------------------------------
    #@返回当前用例的的相关信息[用例版本，用例编号，步骤编号，用例状态,用例的路径]
    #-----------------------------------------------------
    @classmethod
    def getCurCaseInfo( cls ):
        "get current case info."
        _Version = cls.__CurSelectCases[cls.__CurRunCaseIndex][0]
        _CaseNum = cls.__CurSelectCases[cls.__CurRunCaseIndex][1]
        _CaseStep = cls.__CurSelectCases[cls.__CurRunCaseIndex][2]
        _CaseStatus = cls.__CurSelectCases[cls.__CurRunCaseIndex][3]
        _CasePath = os.path.split( cls.getCasePathByCaseNum( _CaseNum, _CaseStep )[0] )[0]
        return ( _Version, _CaseNum, _CaseStep, _CaseStatus, _CasePath )
    
    #-----------------------------------------------------
    #@返回当前用例的的相关信息[用例版本，用例编号，步骤编号，用例状态,用例的路径]
    #-----------------------------------------------------
    @classmethod
    def getEditCaseInfo( cls ):
        "get current case info."
        _Version = cls.__pathinfo[0]
        _CaseNum = cls.__EditCaseInfo[0]
        _CaseStep = cls.__EditCaseInfo[1]
        _CaseStatus = cls.__EditCaseInfo[2]
        _CasePath = os.path.split( cls.getCasePathByCaseNum( _CaseNum, _CaseStep )[0] )[0]
        return ( _Version, _CaseNum, _CaseStep, _CaseStatus, _CasePath )
        
    @classmethod
    def getEditCaseLogPath( cls ):
        "get Edit Case OMAP Log path"
        _CaseNum = cls.__EditCaseInfo[0]
        _CaseStep = cls.__EditCaseInfo[1]
        return cls.getCasePathByCaseNum( _CaseNum, _CaseStep )[-1]    
    
    @classmethod
    def deleteCaseFromWorkSpace( cls, index ):
        "get Cur Case Path."
#        cls.__CurSelectCases = []
        if index in range( len( cls.__CurSelectCases ) ):
            cls.__CurSelectCases.pop( index )
            cls.__CurRunCaseIndex = -1
        else:
            print "deleteCaseFromWorkSpace: index is out of range."
    
    #-------------------------------------------
    #caseinfo:[[被测版本标签号,测试用例编号,测试步骤编号],...]
    #-------------------------------------------
    @classmethod
    def InitCurselectCaseInfo( self , caseinfo ):
        "set Current select case."
        self.__CurSelectCases = []
        for _case in caseinfo:
            _tmp = _case
            _tmp.append( "Waiting" )
            self.__CurSelectCases.append( _tmp )
        if len( self.__CurSelectCases ) > 0:
            self.__CurRunCaseIndex = 0
        else:
            self.__CurRunCaseIndex = -1
    
    #---------------------------------------------
    #@设置__CurRunCaseIndex
    #---------------------------------------------
    @classmethod
    def setCurRunCaseIndex( self, index ):
        "set Current Run case index"
        if index in range( len( self.__CurSelectCases ) ):
            self.__CurRunCaseIndex = index
            print 'self.__CurRunCaseIndex', self.__CurRunCaseIndex
        else:
            print "setCurRunCaseIndex: error index!"

    #-----------------------------------------------
    #@设置__EditCaseInfo
    #-----------------------------------------------
    @classmethod
    def setEditCaseInfo( cls, caseNum, CaseStep, CaseStatus ):
        "set edit case infomation."
        cls.__EditCaseInfo = [caseNum, CaseStep, CaseStatus]
    
    @classmethod
    def setEditCaseInfoByCurIndex( cls ):
        "set Edit case info by current index."
        cls.__EditCaseInfo = [cls.__CurSelectCases[cls.__CurRunCaseIndex][1], \
                              cls.__CurSelectCases[cls.__CurRunCaseIndex][2], \
                              cls.__CurSelectCases[cls.__CurRunCaseIndex][3] ]
        
    #---------------------------------------------
    #status:0:3
    #---------------------------------------------
    @classmethod
    def SetCurselectCaseStatus( self, caseindex, status ):
        "set current select case status."
        if caseindex in range( len( self.__CurSelectCases ) ):
            self.__CurSelectCases[caseindex][-1] = self.Status[status]
        else:
            print "error caseindex", caseindex
    
    #-------------------------------------------------------------
    #@根据输入的本版本地图存放路径，将地图路径与相应的地图版本进行关联
    #导入的用例文件的格式参见软件确认测试执行规范_V1.0.0.doc的测试记录保存格式
    #将遍历后出来的结果存入字典中，具体格式如下：
    #__Mapinfo:[CC offline版本号,{地图编号：[atp_up_path,atp_down_path,ccnv_path,tp_map_path,tp_txt_path],...}]
    #-------------------------------------------------------------
    @classmethod
    def LoadMapFolder( self, Map_File_Path ):
        "load Case folder."
        Map_File_Path = commlib.joinPath( commlib.getCurFileDir(), Map_File_Path ) 
#        print Map_File_Path
        self.__Mapinfo = []
        _offline_version = Map_File_Path.strip().split( "\\" )[-1]
        self.__Mapinfo.append( _offline_version )
        #遍历该路径下的的所有文件夹
        _path_dic = {}
        root, dirs, files = self.getFolderlist( Map_File_Path ) 
        for _dir in dirs:
            _Map_Num = _dir
            _path_dic[_Map_Num] = {}
            _tmp_map_path = os.path.join( root, _dir )
            if False == self.checkMapFolderValid( _tmp_map_path ):
                print "Invalid path!", _tmp_map_path
            else:
                _tmp_mappath_atp_up = os.path.join( _tmp_map_path + "\\Up", "data.vle.md5" )
                _tmp_mappath_atp_down = os.path.join( _tmp_map_path + "\\Down", "data.vle.md5" )
                _tmp_mappath_ccnv = os.path.join( _tmp_map_path, "ccnvBinary.txt" )
#                _tmp_mappath_tp = os.path.join( _tmp_map_path, "atpCpu1Binary.txt" )
#                _tmp_mappath_text = os.path.join( _tmp_map_path, "atptext.txt" )
                #修改为读取CCNV的地图 2012-12-27 by xiongkunpeng
                _atp_up_o_path = os.path.join( _tmp_map_path + "\\Up", "cfg.vle.md5" )
                _atp_down_o_path = os.path.join( _tmp_map_path + "\\Down", "cfg.vle.md5" )
                _ccnv_o_path = os.path.join( _tmp_map_path, "CCNV_NVS.out" )
                _path_dic[_Map_Num] = [_tmp_mappath_atp_up,
                                       _tmp_mappath_atp_down,
                                       _tmp_mappath_ccnv,
                                       _atp_up_o_path,
                                       _atp_down_o_path,
                                       _ccnv_o_path]
                                   
        self.__Mapinfo.append( _path_dic )

        return self.__Mapinfo

    @classmethod
    def getMaplist( cls ):
        "get Map list from Mapinfo"
        _list = []
        for _map in cls.__Mapinfo[1]:
            _list.append( _map )
        #排序一下
        _list.sort()
        return _list
    
#    @classmethod
#    def getMapPathByNum( cls, mapNum ):
#        "get Map list from Mapinfo by mapNum."
#        return cls.__Mapinfo[1][mapNum]
    
    
    #--------------------------------------------------------------------
    #@导入用例的配置文件配置到__EditCaseConfig
    #{'map':[version,mapNum,description],'fileconfig'：[TrainEnd,DataplugPath,Description],'endconfig':[type,para,Desription],'history':[[date,status,description],...]}
    #--------------------------------------------------------------------
    @classmethod
    def importEditCaseConfig( cls ):
        "import Current Edit Case configuration from xml"
        try:
            _basepath = cls.getEditCaseInfo()[-1]
        except TypeError, e:
            _basepath = ""
#        cls.__EditCaseConfig = {}
        cls.__EditCaseConfig = cls.importCaseConfig( _basepath )
        
        return cls.__EditCaseConfig
    
    #--------------------------------------------------------------------
    #@导入用例的配置文件配置到__EditCaseConfig
    #{'map':[version,mapNum,description],'fileconfig'：[TrainEnd,DataplugPath,Description],'endconfig':[type,para,Desription],'history':[[date,status,description],...]}
    #--------------------------------------------------------------------
    @classmethod
    def importCurRunCaseConfig( cls ):
        "import Current Run Case configuration from xml"
        _basepath = cls.getCurCaseInfo()[-1]
#        cls.__EditCaseConfig = {}
        cls.__CurRunCaseConfig = cls.importCaseConfig( _basepath ) 
        
        return cls.__CurRunCaseConfig
    
    @classmethod
    def importCaseConfig( cls , basepath ):
        "import case configuration."
        _caseConfig = {}
        try:
            _configPath = os.path.join( basepath, 'root_case_setting.xml' )
#            print _configPath
            _f = XmlParser()
            _f.loadXmlFile( _configPath )
            _MapConfig = _f.getAttrListManyElement( cls.xmlNode['MapConfig']['path'], \
                                                   cls.xmlNode['MapConfig']['attr'] )[0]
            _caseConfig['map'] = _MapConfig
            
            _fileconfig = _f.getAttrListManyElement( cls.xmlNode['FileConfig']['path'], \
                                                    cls.xmlNode['FileConfig']['attr'] )[0]
            _caseConfig['fileconfig'] = _fileconfig
            
            _EndConfig = _f.getAttrListManyElement( cls.xmlNode['EndConfig']['path'], \
                                                    cls.xmlNode['EndConfig']['attr'] )[0]
            _caseConfig['endconfig'] = _EndConfig
            _caseConfig['endconfig'][1] = float( _caseConfig['endconfig'][1] )
                                                    
                                                    
            _hiss = _f.getAttrListManyElement( cls.xmlNode['History']['path'], \
                                              cls.xmlNode['History']['attr'] )
            
            _caseConfig['history'] = _hiss
            _f.closeXmlFile()
            
        except ( IOError, lxml.etree.XMLSyntaxError ):
            #有问题的时候用默认值
            _caseConfig['map'] = [cls.__Mapinfo[0], u'原始地图', u'原始地图' ]
            
            _caseConfig['fileconfig'] = ['End1', '', 'END1']
            
            _caseConfig['endconfig'] = ['1', 300, '']
            
            _caseConfig['history'] = []
        
        #对于地图库修改的，自动修改地图库的版本
        if _caseConfig['map'][0] != cls.__Mapinfo[0]:
            print "Map Version has been change from ", _caseConfig['map'][0], "to ", cls.__Mapinfo[0]
            _caseConfig['map'][0] = cls.__Mapinfo[0]
        return _caseConfig
        
        
    @classmethod
    def getEditCaseConfig( cls ):
        "get Current Case configuration"
        return cls.__EditCaseConfig
               
    @classmethod
    def getCurRunCaseTrainEnd( cls ):
        "get Current Case Train End configuration"
        return cls.__CurRunCaseConfig['fileconfig'][0]
        
    @classmethod
    def getCurRunCaseConfig( cls ):
        "get Current Case configuration."
        return cls.__CurRunCaseConfig
    
    @classmethod
    def setMapConfig( cls, mapNum, des ):
        "set Map configuration."
        cls.__EditCaseConfig['map'][1] = mapNum
        cls.__EditCaseConfig['map'][2] = des

    @classmethod
    def setMapConfig_Num( cls, mapNum ):
        "set Map configuration Num."
        cls.__EditCaseConfig['map'][1] = mapNum
                
    @classmethod
    def setMapConfig_Des( cls, des ):
        "set Map configuration Des."
        cls.__EditCaseConfig['map'][2] = des
    
    @classmethod
    def setfileConfig( cls, end, path, des ):
        "set file configuration."
        cls.__EditCaseConfig['fileconfig'] = [end, path, des]

    @classmethod
    def setfileConfig_end( cls, end ):
        "set file configuration."
        cls.__EditCaseConfig['fileconfig'][0] = end
        
    @classmethod
    def setfileConfig_path( cls, path ):
        "set file configuration."
        cls.__EditCaseConfig['fileconfig'][1] = path
        
    @classmethod
    def setfileConfig_des( cls, des ):
        "set file configuration."
        cls.__EditCaseConfig['fileconfig'][2] = des       
        
    @classmethod
    def setendTypeConfig( cls, type, para, des ):
        "set end type configuration."
        cls.__EditCaseConfig['endconfig'] = [type, int( para ), des]

    @classmethod
    def setendTypeConfig_Type( cls, type ):
        "set end type configuration."
        cls.__EditCaseConfig['endconfig'][0] = type
        
    @classmethod
    def setendTypeConfig_Para( cls, para ):
        "set end type configuration."
        cls.__EditCaseConfig['endconfig'][1] = para     
        
    @classmethod
    def setendTypeConfig_Des( cls, des ):
        "set end type configuration."
        cls.__EditCaseConfig['endconfig'][2] = des             
                
    @classmethod
    def addHistory( cls, date, status, des ):
        "add history."
        cls.__EditCaseConfig['history'].append( [date, status, des] )

    @classmethod
    def editHistory( cls, date, status, des, Index ):
        "edit history."
        cls.__EditCaseConfig['history'][Index] = [date, status, des]
        
    @classmethod
    def delHistory( cls, index ):
        "add history."
        cls.__EditCaseConfig['history'].pop( index )
    
    @classmethod
    def SaveEditCaseConfig( cls ):
        "save current edit case configuration."
        _configPath = os.path.join( cls.getEditCaseInfo()[-1], 'root_case_setting.xml' )
        
        cls.SaveCaseConfig( _configPath )
        
#    @classmethod
#    def SaveCurRunCaseConfig( cls ):        
#        "save current run case configuration."
#        _configPath = os.path.join( cls.getCurCaseInfo()[-1], 'root_case_setting.xml' )
#        
#        cls.SaveCaseConfig( _configPath )
            
    @classmethod
    def SaveCaseConfig( cls, configpath ):
        "save case config."
#        print cls.__EditCaseConfig
        _file = open( configpath, 'w' )
        #创建XML根节点
        _Case_Config = etree.Element( "CaseInfo" )
        
        _config = etree.SubElement( _Case_Config, 'Config' )
        _hiss = etree.SubElement( _Case_Config, 'History' )
        
        _mapconfig = etree.SubElement( _config, 'MapConfig' )
        _mapconfig.set( 'Version', cls.__EditCaseConfig['map'][0] )
        _mapconfig.set( 'MapNum', cls.__EditCaseConfig['map'][1] )
        _mapconfig.set( 'Description', cls.__EditCaseConfig['map'][2] )
        
        _fileconfig = etree.SubElement( _config, 'FileConfig' )
        _fileconfig.set( 'TrainEnd', cls.__EditCaseConfig['fileconfig'][0] )
        _fileconfig.set( 'DataPlugPath', cls.__EditCaseConfig['fileconfig'][1] )
        _fileconfig.set( 'Description', cls.__EditCaseConfig['fileconfig'][2] )  

        _fileconfig = etree.SubElement( _config, 'EndConfig' )
        _fileconfig.set( 'EndType', cls.__EditCaseConfig['endconfig'][0] )
        _fileconfig.set( 'Para', str( cls.__EditCaseConfig['endconfig'][1] ) )
        _fileconfig.set( 'Description', cls.__EditCaseConfig['endconfig'][2] ) 
              
        for _h in cls.__EditCaseConfig['history']:
            _his = etree.SubElement( _hiss, 'His' )
            _his.set( 'Date', _h[0] )
            _his.set( 'Status', _h[1] )
            _his.set( 'Description', _h[2] )             
           

        _Config_String = etree.tostring( _Case_Config, pretty_print = True, encoding = "utf-8" )           
        _file.write( r'''<?xml version="1.0" encoding="utf-8"?>
<!--用例配置文件：主要用于配置地图版本,配置文件版本，运行记录等等-->
<!--MapConfig:配置地图信息，Version：地图版本，MapNum:地图编号，Description：相关描述-->
<!--FileConfig:配置数据信息,配置数据主要是指上位机的xml文件和下位机的dataplug以及sdts（ccnv）的RMS配置-->
<!--TrainEnd：1,2分别表示end1，end2，DataPlugPath：默认情况不需填写，如果其需要传异常配置时，则需要给出其路径-->
<!--EndConfig：EndType:表示结束条件，1为时间条件，Para为条件的参数，EndType为1时，Para为时间单位为秒，表示多少秒结束用例-->
<!--His:记录历史，Date为运行时间，Status记录运行后保存的状态，描述为用户自行记录的东西，His记录会逐行添加-->'''
                    ) #保存数据
        _file.write( "\n" ) #保存数据
        _file.write( _Config_String ) #保存数据
        _file.close()        
    
    @classmethod
    def getMapPathByMapName( self , mapname ):
        "根据地图标签获取地图路径"
        try:
            return self.__Mapinfo[1][mapname]
        except KeyError, e:
            print "no have mapname:", mapname, e
        
    @classmethod
    def getCurWorkPath( cls ):
        "get cur work path"
        return cls.__CurWorkPath            
    
    @classmethod
    def getCurCaseVersion( cls ):
        "get cur case version"
        return cls.__pathinfo[0]
    
    @classmethod
    def CreateNewCaseStep( cls, CaseNum, CaseStep ):
        "create new case step"
        _path = filehandle.joinpaths( cls.__CurWorkPath, [CaseNum, CaseStep] )
        
        if True == cls.ExistCase( CaseNum, CaseStep ):
            return False
        else:
            #不存在创建用例
            _defaultpath = commlib.joinPath( commlib.getCurFileDir(), "/default case" ) 
            #添加用例相关数据至 __pathinfo,测试用例编号1:{测试步骤编号1:[LogPath,ScriptPath,DownLogPath]
            _LogPath = os.path.join( _path, "Log" )
            _ScripPath = os.path.join( _path, "Script" )
            _DownLogPath = os.path.join( _LogPath, "DownLog" )
            #拷贝默认文件至路径
            filehandle.CopyFolder( _defaultpath, _ScripPath )
            #检验是否需要创建目录
            cls.checkLogFolderValid( _LogPath, False )
            #更新__pathinfo
            if cls.__pathinfo[1].has_key( CaseNum ):
                cls.__pathinfo[1][CaseNum][CaseStep] = [_LogPath, _ScripPath, _DownLogPath]
            else:
                cls.__pathinfo[1][CaseNum] = {}
                cls.__pathinfo[1][CaseNum][CaseStep] = [_LogPath, _ScripPath, _DownLogPath]
#            print 'CreateNewCaseStep', cls.__pathinfo[1][CaseNum][CaseStep]
            #更新__EditCaseInfo
            cls.__EditCaseInfo = [CaseNum, CaseStep, 0]  #[测试用例编号, 测试步骤编号, 测试状态]                
            return True
        
    @classmethod
    def ExistCase( cls, CaseNum, CaseStep ):
        "check exist case"
        try:
            cls.__pathinfo[1][CaseNum][CaseStep]
        except KeyError, e:
            return False
        return True
        
    #-------------------------------------------------------------
    #@根据输入的本版本脚本存放路径，将脚本路径和log存放路径，以及用例间的层次进行关联
    #导入的用例文件的格式参见软件确认测试执行规范_V1.0.0.doc的测试记录保存格式
    #将遍历后出来的结果存入字典中，具体格式如下：
    #_pathinfo:[被测版本标签号,{测试用例编号1:{测试步骤编号1:[LogPath,ScriptPath,UpLogPath],...},...}]
    #-------------------------------------------------------------
    @classmethod
    def LoadCaseFolder( self, Case_File_Path ):
        "load Case folder."
        #如果是相对路径，则以当前程序路径进行拼接 
        Case_File_Path = commlib.joinPath( commlib.getCurFileDir(), Case_File_Path ) 
        self.__CurWorkPath = Case_File_Path #记录当前路径
        self.__pathinfo = []
        _Software_version = Case_File_Path.strip().split( "\\" )[-1]
        self.__pathinfo.append( _Software_version )
        #遍历该路径下的的所有文件夹
        _path_dic = {}
        root, dirs, files = self.getFolderlist( Case_File_Path ) 
        for _dir in dirs:
            if _dir not in [u"CR_Regression_Script", u"CR_Validate" ]:
                _test_case_Num = _dir
                _path_dic[_test_case_Num] = {}
                _tmppath = os.path.join( root, _dir )
                case_root, case_dirs, case_files = self.getFolderlist( _tmppath )
                #print "case_dirs", case_dirs
                for _case_dir in case_dirs:
                    #print _case_dir
                    if _case_dir != u"被测试软件程序和测试平台程序":
                        _test_case_step_Num = _case_dir
                        _tmp_casepath = os.path.join( case_root, _case_dir )
                        #print _case_dir
                        #print "_tmp_casepath", _tmp_casepath
                        #检测文件中是否包含所有的文件夹
                        _tmp_casepath_Log = os.path.join( _tmp_casepath, "Log" )
                        _tmp_casepath_Script = os.path.join( _tmp_casepath, "Script" )
                        if False == self.checkLogFolderValid( _tmp_casepath_Log ) or \
                            False == self.checkScriptFolderValid( _tmp_casepath_Script ):
                            print "Invalid path!", _tmp_casepath
                        else:
                            _tmp_casepath_UpLog = os.path.join( _tmp_casepath_Log, "DownLog" )
                            _path_dic[_test_case_Num][_test_case_step_Num] = [_tmp_casepath_Log, \
                                                                              _tmp_casepath_Script, \
                                                                              _tmp_casepath_UpLog]
                                   
        self.__pathinfo.append( _path_dic )
#        print "LoadCaseFolder", self.__pathinfo
        return self.__pathinfo

    
    
    #---------------------------------------------------
    #@检测Map所需的文件是否具备
    #@包括文件四个文件夹ccnvBinary,atptext,atpCpu1Binary,atpCpu2Binary
    #---------------------------------------------------
    @classmethod
    def checkMapFolderValid( self, path ):
        "检验case路径下的case时候有效，无效则返回false"
        _revflag = False
        if False == os.path.exists( path + "/ccnvBinary.txt" ) and "CCNV" == TestPlatformFlag:
            print "Not exist file ccnvBinary.txt!"
        elif False == os.path.exists( path + "/Up/data.vle.md5" ) and TestPlatformFlag in ["CCNV", "ATP"]:
            print "Not exist file data.vle.md5 in up!"
        elif False == os.path.exists( path + "/Down/data.vle.md5" ) and TestPlatformFlag in ["CCNV", "ATP"]:
            print "Not exist file data.vle.md5 in down!"
        else:
            _revflag = True
            
        return _revflag   

    
    #---------------------------------------------------
    #@检测用例所需的文件是否具备
    #@包括文件三个文件夹datafile,scenario,setting
    #---------------------------------------------------
    @classmethod
    def checkScriptFolderValid( self, path ):
        "检验case路径下的case时候有效，无效则返回false"
        _revflag = False
#        if False == os.path.exists( path + "/datafile" ):
#            print "Not exist datafile folder!"
#        elif False == os.path.exists( path + "/setting" ):
#            print "Not exist setting folder!"
        if False == os.path.exists( path + "/scenario" ):
            print "Not exist scenario folder!"
        else:
            _revflag = True
            
        return _revflag    
    
    #---------------------------------------------------
    #@检测用例所需的文件是否具备
    #@包括文件一个文件夹UP_Log
    #---------------------------------------------------
    @classmethod
    def checkLogFolderValid( self, path, PrintLog = True ):
        "检验case路径下的case时候有效，无效则返回false"
        if False == os.path.exists( path + u"/DownLog" ):
            if PrintLog:
                print "Not exist Down_Log folder!"
            os.makedirs( path + u"/DownLog" )
        
        if False == os.path.exists( path + u"/log" ):
            if PrintLog:  
                print "Not exist log folder !" 
            os.makedirs( path + u"/log" )

            
        return True
    
    #-------------------------------------------------------
    #@获取文件夹下的所有文件夹
    #-------------------------------------------------------
    @classmethod
    def getFolderlist( self, path ):
        "get folder list."
        for root, dirs, files in os.walk( path ):
#            print "fdasfa", root, dirs, files
            return root, dirs, files
    
    #--------------------------------------------------------
    #获取pathinfo信息
    #--------------------------------------------------------
    @classmethod
    def getPathInfo( self ):
        "get path info"
        return self.__pathinfo
    
    
    #---------------------------------------------------------
    #根据用例的编号和步骤编号获取用例的相关path
    #---------------------------------------------------------
    @classmethod
    def getCasePathByCaseNum( self, casenum, stepnum ):
        "get case path by case num and step num."
        try:
            return self.__pathinfo[1][casenum][stepnum]
        except KeyError, e:
            print "can't find case path", casenum, stepnum
            return None
    
    #--------------------------------------------------------
    #注意删除只能在程序还没有运行的时候进行
    #--------------------------------------------------------
    @classmethod
    def delEditCaseStep( cls ):
        "delete Edit Case Step"
        #该过程涉及以下变量的调整：
        #__pathinfo，__CurSelectCases，__CurRunCaseIndex，__EditCaseInfo,__EditCaseConfig
        _info = cls.getEditCaseInfo()#( _Version, _CaseNum, _CaseStep, _CaseStatus, _CasePath )
        _path = _info[-1]
        _CaseNum = _info[1]
        _CaseStep = _info[2]
        filehandle.deleteFolder( _path )
        
        #删除__pathinfo中的对应项
        cls.__pathinfo[1][_CaseNum].pop( _CaseStep )
        if 0 == len( cls.__pathinfo[1][_CaseNum] ): #用例step为0时需要将Num也清除掉
            cls.__pathinfo[1].pop( _CaseNum )
            #删除文件夹
            filehandle.deleteFolder( os.path.join( cls.__CurWorkPath, _CaseNum ) )
        
        #查看是否删除了在test_config_panel中的用例的删除
        _deleteIndex = None
        for _index, _caseinfo in enumerate( cls.__CurSelectCases ):    
            if cls.__EditCaseInfo[0:2] == _caseinfo[1:3]:
                _deleteIndex = _index
                break

        #清除edit
        cls.__EditCaseInfo = None
        cls.__EditCaseConfig = {}
        
        #删除cls.__CurSelectCases中对应的用例，并返回标志位
        if None != _deleteIndex:
            cls.__CurSelectCases.pop( _deleteIndex )
            cls.__CurRunCaseIndex = -1
            return True
        else:
            return False
        

    #--------------------------------------------------------
    #注意编辑只能在程序还没有运行的时候进行，以免出现不必要的问题
    #返回值有三种形式：1：改值成功,但不在__CurSelectCases中，
    #                 2该值成功,但在__CurSelectCases中
    #                 False失败，
    #                 None：不需要改值
    #--------------------------------------------------------
    @classmethod
    def RenameEditCaseStep( cls, newName ):
        "rename Edit Case Step"
        #该过程涉及以下变量的调整：
        #__pathinfo，__CurSelectCases，__EditCaseInfo
        _info = cls.getEditCaseInfo()#( _Version, _CaseNum, _CaseStep, _CaseStatus, _CasePath )
        _path = _info[-1]
        _CaseNum = _info[1]
        _CaseStep = _info[2]
        
        #编辑__pathinfo中的对应项：
        #先检查是否重名，有重名则不能更改名字
        if newName == _CaseStep:
            #没有该名字直接退出
            return None
        if cls.__pathinfo[1][_CaseNum].has_key( newName ):
            #存在同名的不能该值
            print "RenameEditCaseStep Error: Exist Name ", newName
            return False
        
        #先改改实体的路径，有可能失败
        _basepath = os.path.split( _path )[0]
        _newpath = os.path.join( _basepath, newName )
        if False == filehandle.ReNameFolder( _path, _newpath ):
            #存在同名的不能该值
            print "RenameEditCaseStep Error: Can not Rename Case ", newName
            return False            
        #条件满足可以进行改名字
#        cls.__pathinfo[1][_CaseNum][newName] = cls.__pathinfo[1][_CaseNum][_CaseStep]
        cls.__pathinfo[1][_CaseNum].pop( _CaseStep )  
        #计算新的path：[LogPath,ScriptPath,DownLogPath]
        _LogPath = os.path.join( _newpath, "Log" )
        _ScripPath = os.path.join( _newpath, "Script" )
        _DownLogPath = os.path.join( _LogPath, "DownLog" )
        cls.__pathinfo[1][_CaseNum][newName] = [_LogPath, _ScripPath, _DownLogPath]
        
        #查看是否编辑了在test_config_panel中的用例的删除
        _editIndex = None
        #[[被测版本标签号,测试用例编号,测试步骤编号,测试状态],...]
        for _index, _caseinfo in enumerate( cls.__CurSelectCases ):    
            if [_CaseNum, _CaseStep] == _caseinfo[1:3]:
                _editIndex = _index
                break

        #修改edit
        cls.__EditCaseInfo[1] = newName  #[测试用例编号, 测试步骤编号,测试状态]
        
        #是否修改了cls.__CurSelectCases中对应的用例，并返回标志位
        if None != _editIndex:
            cls.__CurSelectCases[_editIndex][2] = newName
            return 2
        else:
            return 1


    #--------------------------------------------------------
    #注意编辑只能在程序还没有运行的时候进行，以免出现不必要的问题
    #返回值有三种形式：1：改值成功,但不在__CurSelectCases中，
    #                 2该值成功,但在__CurSelectCases中
    #                 False失败，
    #                 None：不需要改值
    #--------------------------------------------------------
    @classmethod
    def RenameEditCaseNum( cls, oldName, newName ):
        "rename Edit Case Step"
        #该过程涉及以下变量的调整：
        #__pathinfo，__CurSelectCases，__EditCaseInfo        
        #编辑__pathinfo中的对应项：
        #先检查是否重名，有重名则不能更改名字
        
        if newName == oldName:
            #没有该名字直接退出
            return None
        if False == cls.__pathinfo[1].has_key( oldName ):
            #存在同名的不能该值
            print "RenameEditCaseNum Error: Not Exist Case Name: ", newName
            return False
        if cls.__pathinfo[1].has_key( newName ):
            #存在同名的不能该值
            print "RenameEditCaseNum Error: Exist Name ", newName
            return False
        
        #获取old,new文件夹路径
        _basepath = cls.getCurWorkPath()
        _oldpath = os.path.join( _basepath, oldName )
        _newpath = os.path.join( _basepath, newName )
        #先改改实体的路径，有可能失败
        if False == filehandle.ReNameFolder( _oldpath, _newpath ):
            #存在同名的不能该值
            print "RenameEditCaseNum Error: Can not Rename Case ", newName
            return False            
        #条件满足可以进行改名字
        cls.__pathinfo[1][newName] = cls.__pathinfo[1][oldName]
        cls.__pathinfo[1].pop( oldName )  
        
        #修改各个脚本的路径
        for _caseStep in cls.__pathinfo[1][newName]:
            _stepPath = os.path.join( _newpath, _caseStep )
            _LogPath = os.path.join( _stepPath, "Log" )
            _ScripPath = os.path.join( _stepPath, "Script" )
            _DownLogPath = os.path.join( _LogPath, "DownLog" )
            cls.__pathinfo[1][newName][_caseStep] = [_LogPath, _ScripPath, _DownLogPath]

        #查看是否编辑了在test_config_panel中的用例的删除
        _editIndex = None
        #[[被测版本标签号,测试用例编号,测试步骤编号,测试状态],...]
        for _index, _caseinfo in enumerate( cls.__CurSelectCases ):    
            if oldName == _caseinfo[1]:
                _editIndex = _index
                cls.__CurSelectCases[_index][1] = newName

        #修改edit
        if ( None != cls.__EditCaseInfo ) and\
            ( 3 == len( cls.__EditCaseInfo ) ) and\
            ( cls.__EditCaseInfo[0] == oldName ):#有且在其中才会修改
            cls.__EditCaseInfo[0] = newName  #[测试用例编号, 测试步骤编号,测试状态]
        
        #是否修改了cls.__CurSelectCases中对应的用例，并返回标志位
        if None != _editIndex:
            return 2
        else:
            return 1        

#-------------------------------------------------------------------------------------——
#本类用于保存用例脚本编辑时的数据，主要实现用例脚本文件的读取(存入到对应的变量中去),提供界面修修改变量内容的接口，最后提供储存数据数据至相关路径
#注意在编辑用例时跑车应该停止，否则会出错
#---------------------------------------------------------------------------------------
class CaseEdit( object ):
    '''
    case edit
    '''
    __scenariopath = None
    __binmappath = None
    __txtmappath = None
    
    __DevScenarioDic = None    #{devicename:[defScenario, TimeScenario],...}
    __DevScenarioDesDic = None
    __DevVarDic = None         #{devicename:[Varname1,varname2,...}
    __DevVarDesDic = None         #{devicename:[Varname1 Description,varname2 Description,...}
    
    __TrainRouteList = None  #[routeV, startV, direV, trainLen, Cog_dir]
    __ExpectSpeedList = None #[[type,...],]
    __EB_EndPos = None       #EB缓解后的终点
    __ExpectSpeedDes = None  #__ExpectSpeedList对应的描述
    
    __BMBeacons = None
    __BeaconMsgSetting = None  #{beaconid:[Beacon_ID, Beacon_Name, Disabled, Msg_Beacon_ID, Use_Default_Msg, Available, Check_Word_1=, Check_Word_2, deta_dis],}
    
    def __init__( self ):
        pass
        
    def SetPath( self, scepath, setpath, binpath, txtpath ):
#        print scepath
#        print setpath
#        print binpath
#        print txtpath
        self.__scenariopath = scepath
        self.__binmappath = binpath
        self.__txtmappath = txtpath
        self.__settingpath = setpath

    def loadMap( self ):
        "load map"
        MapData.loadMapData( self.__binmappath,
                             self.__txtmappath,
                             Type = "Edit" )

    def getMapPath( self ):
        "get Map Path"
        return self.__binmappath  

    def getTxtMapPath( self ):
        "get Txt Map Path"
        return self.__txtmappath  

    def getScenarioPath( self ):
        "get Scenario Path"
        return self.__scenariopath  
                
    def getDeviceList( self ):
        "get Device list from folder"
        #从scenario中获取设备数，主要是遍历文件，找出文件名为_scenario.xml结尾的文件
        _devicelist = []
        for root, dirs, files in os.walk( self.__scenariopath ):
            for _file in files:
                if ( '_scenario.xml' in _file ) and ( 'variant' not in _file ):
                    _devicelist.append( _file[0:-13] )
            return _devicelist
        
    def getDevVarListDic( self ):
        "get Device variant list Dic"
        self.__DevVarDic = {}
        self.__DevVarDesDic = {}
        _devicelist = self.getDeviceList()
        for _devName in _devicelist:
            _path = os.path.join( self.__settingpath, _devName + '_variant.xml' )
#            print _path
            _variants = XMLDeal.importVariant( _path )
#            print _variants
            self.__DevVarDic[_devName] = [_v[0] for _v in _variants]
            self.__DevVarDesDic[_devName] = {}
            for _i, _varName in enumerate( self.__DevVarDic[_devName] ):
                self.__DevVarDesDic[_devName][_varName] = "Name: " + _variants[_i][0] + "\n" + \
                                                          "Type: " + _variants[_i][1] + "\n" + \
                                                          "Description: " + _variants[_i][4]
    
    def getDevVarList( self, devicename ):
        "get device variant list."
        return  self.__DevVarDic[devicename]   
            
    def getDevVarDes( self, devicename, varName ):
        "get Device Variant Description"
        return self.__DevVarDesDic[devicename][varName]
            
    def getScenarioDic( self ):
        "get Scenario dic"
        self.__DevScenarioDic = {}
        self.__DevScenarioDesDic = {}
        _devicelist = self.getDeviceList()
        for _devName in _devicelist:
            _path = os.path.join( self.__scenariopath, _devName + '_scenario.xml' )
            _defScenario, _TimeScenario, _defScenarioDes, _TimeScenarioDes = XMLDeal.importDefSce( _path, ReadDes = True )
            self.__DevScenarioDic[_devName] = [_defScenario, _TimeScenario]
            self.__DevScenarioDesDic[_devName] = [_defScenarioDes, _TimeScenarioDes]
    
    #------------------------------------------
    #删除一条位置定义的脚本
    #deviceName:设备名称
    #index:脚本对应的编号：从0开始编号
    #------------------------------------------
    def DeleteOneScePos( self, deviceName, index ):
        "delete one scenario position."
        try:
            self.__DevScenarioDic[deviceName][0].pop( index )
            self.__DevScenarioDesDic[deviceName][0].pop( index )
        except IndexError, e:
            print "DeleteOneScePos", deviceName, index, e        
    
    #------------------------------------------
    #删除一条时间定义的脚本
    #deviceName:设备名称
    #index:脚本对应的编号：从0开始编号
    #------------------------------------------
    def DeleteOneSceTime( self, deviceName, index ):
        "delete one scenario position."
        try:
            self.__DevScenarioDic[deviceName][1].pop( index )
            self.__DevScenarioDesDic[deviceName][1].pop( index )
        except IndexError, e:
            print "DeleteOneSceTime", deviceName, index, e
    
    #---------------------------------------------------------
    #删除一条脚本，type：0位置定义的脚本，1时间定义的脚本        
    #---------------------------------------------------------
    def DeleteOneSce( self, deviceName, type, index ): 
        "delete one scenario." 
        if index == -1:
            return
        if 0 == type:
            self.DeleteOneScePos( deviceName, index )
        else:
            self.DeleteOneSceTime( deviceName, index )
        
    #------------------------------------------
    #添加一条位置定义的脚本
    #deviceName:设备名称
    #content：[blockid,abs,delay,[[],...]]
    #------------------------------------------
    def AddOneScePos( self, deviceName, content ):
        "Add one scenario position."
        self.__DevScenarioDic[deviceName][0].append( content )
        self.__DevScenarioDesDic[deviceName][0].append( "" ) #设置默认值     
    
    #------------------------------------------
    #添加一条时间定义的脚本
    #deviceName:设备名称
    #content：[loophour,[[],...]]
    #------------------------------------------
    def AddOneSceTime( self, deviceName, content ):
        "Add one scenario position."
        self.__DevScenarioDic[deviceName][1].append( content )
        self.__DevScenarioDesDic[deviceName][1].append( "" )

    
    #---------------------------------------------------------
    #添加一条脚本，type：0位置定义的脚本，1时间定义的脚本        
    #content：[blockid,abs,delay,[[],...]]
    #---------------------------------------------------------
    def AddOneSce( self, deviceName, type, content ): 
        "Add one scenario." 
        if 0 == type:
            self.AddOneScePos( deviceName, content )
        else:
            self.AddOneSceTime( deviceName, content )

    def getOneSceDes( self, deviceName, type, index ):
        "get one scenario description"
        if 0 == type:
            return self.__DevScenarioDesDic[deviceName][0][index]
        else:
            return self.__DevScenarioDesDic[deviceName][1][index]        

    def EditOneSceDes( self, deviceName, type, index, content ):
        "get one scenario description"
        if 0 == type:
            self.__DevScenarioDesDic[deviceName][0][index] = content
        else:
            self.__DevScenarioDesDic[deviceName][1][index] = content  
        
    #------------------------------------------
    #编辑一条位置定义的脚本
    #deviceName:设备名称
    #index:位置
    #content：[blockid,abs,delay,[[],...]]
    #------------------------------------------
    def EditOneScePos( self, deviceName, index, content ):
        "Add one scenario position."
        _NameValuecontent = self.__DevScenarioDic[deviceName][0][index][-1]
        self.__DevScenarioDic[deviceName][0][index] = content
        self.__DevScenarioDic[deviceName][0][index][-1] = _NameValuecontent
    
    #------------------------------------------
    #编辑一条时间定义的脚本
    #deviceName:设备名称
    #index:位置
    #content：[loophour,[[],...]]
    #------------------------------------------
    def EditOneSceTime( self, deviceName, index, content ):
        "Add one scenario time."
        _NameValuecontent = self.__DevScenarioDic[deviceName][1][index][-1]
        self.__DevScenarioDic[deviceName][1][index] = content
        self.__DevScenarioDic[deviceName][1][index][-1] = _NameValuecontent
    
    #---------------------------------------------------------
    #编辑一条脚本的条件（内容不改），type：0位置定义的脚本，1时间定义的脚本        
    #content：[blockid,abs,delay,[[],...]]
    #---------------------------------------------------------
    def EditOneSce( self, deviceName, type, index, content ): 
        "Add one scenario." 
        if 0 == type:
            self.EditOneScePos( deviceName, index, content )
        else:
            self.EditOneSceTime( deviceName, index, content )

    
    #------------------------------------------
    #修改一条位置定义的脚本的内容,现只支持改内容，不支持该位置和时间，只能删除添加完成该操作
    #deviceName:设备名称
    #index:脚本对应的编号：从0开始编号
    #content：[[name,value],....]
    #------------------------------------------
    def ModifyOneScePos( self, deviceName, index, content ):
        "Modify one scenario position."
        try:
            self.__DevScenarioDic[deviceName][0][index][-1] = content
        except IndexError, e:
            print "ModifyOneScePos", deviceName, index, e        
    
    #------------------------------------------
    #修改一条时间定义的脚本，,现只支持改内容，不支持该位置和时间，只能删除添加完成该操作
    #deviceName:设备名称
    #index:脚本对应的编号：从0开始编号
    #content：[[name,value],....]    
    #------------------------------------------
    def ModifyOneSceTime( self, deviceName, index, content ):
        "Modify one scenario position."
        try:
            self.__DevScenarioDic[deviceName][1][index][-1] = content
        except IndexError, e:
            print "ModifyOneSceTime", deviceName, index, e
    
    #---------------------------------------------------------
    #修改一条脚本，type：0位置定义的脚本，1时间定义的脚本  
    #content：[[name,value],....]          
    #---------------------------------------------------------
    def ModifyOneSce( self, deviceName, type, index, content ): 
        "Modify one scenario." 
        if -1 == index:
            print "ModifyOneSce wrong index", deviceName, type, index, content
            return
        
        if 0 == type:
            self.ModifyOneScePos( deviceName, index, content )
        elif 1 == type :
            self.ModifyOneSceTime( deviceName, index, content )
        else:
            print "ModifyOneSce: error", deviceName, type, index, content 

    #--------------------------------------------------
    #获取当前选中的一条位置定义的脚本的content：[[name,value],....]
    #--------------------------------------------------
    def getOneSceContentPos( self, deviceName, index ):
        "get One Scenario content."
        try:
            return self.__DevScenarioDic[deviceName][0][index][-1]
        except IndexError, e:
            print "getOneSceContentPos", deviceName, index, e
            return None        

    #--------------------------------------------------
    #获取当前选中的一条位置定义的脚本的位置信息：[blockid,abss,dwelltime]
    #--------------------------------------------------
    def getOneScePosContent( self, deviceName, index ):
        "get One Scenario Position content."
        try:
            return self.__DevScenarioDic[deviceName][0][index][0:3]
        except IndexError, e:
            print "getOneScePosContent", deviceName, index, e
            return None   
    
    #--------------------------------------------------
    #获取脚本的Pos显示内容
    #--------------------------------------------------
    def getSceContentShowList( self, deviceName ):
        "get scenario content show list"
        _rev = []
        for _Pos in self.__DevScenarioDic[deviceName][0]:
            _rev.append( "Block Id:" + str( _Pos[0] ) + \
                         "   Abscissa:" + str( _Pos[1] ) + \
                         "   Delay:" + str( _Pos[2] ) )
        return _rev

    #--------------------------------------------------
    #获取脚本的Pos显示内容
    #--------------------------------------------------
    def getTimeContentShowList( self, deviceName ):
        "get scenario content show list"
        _rev = []
        for _Time in self.__DevScenarioDic[deviceName][1]:
            _rev.append( "Loophour:" + str( _Time[0] ) )
        return _rev
    
    #--------------------------------------------------
    #获取当前选中的一条时间定义的脚本的content：[[name,value],....]
    #--------------------------------------------------
    def getOneSceContentTime( self, deviceName, index ):
        "get One Scenario content."
        try:
            return self.__DevScenarioDic[deviceName][1][index][-1]
        except IndexError, e:
            print "getOneSceContentTime", deviceName, index, e
            return None   

    #--------------------------------------------------
    #获取当前选中的一条时间定义的脚本的time:loophour
    #--------------------------------------------------
    def getOneSceTimeContent( self, deviceName, index ):
        "get One Time Scenario content."
        try:
            return self.__DevScenarioDic[deviceName][1][index][0]
        except IndexError, e:
            print "getOneSceTimeContent", deviceName, index, e
            return None  
    
    #--------------------------------------------------
    #获取当前选中的一条脚本的content：[[name,value],....]
    #--------------------------------------------------
    def getOneSceContent( self, deviceName, type, index ):
        "get One Scenario content."
        if 0 == type:
            return self.getOneSceContentPos( deviceName, index )
        else:
            return self.getOneSceContentTime( deviceName, index )
    
    #--------------------------------------------------
    #保存所有的scenario脚本至路径的xml中
    #--------------------------------------------------
    def SaveScenarioDicToXML( self ):
        "save scenario dic to xml."
        for _devName in self.__DevScenarioDic:
            _path = os.path.join( self.__scenariopath, _devName + '_scenario.xml' )
            _defScenario = self.__DevScenarioDic[_devName][0]
            _TimeScenario = self.__DevScenarioDic[_devName][1]
            _defScenarioDes = self.__DevScenarioDesDic[_devName][0]
            _TimeScenarioDes = self.__DevScenarioDesDic[_devName][1]            
            XMLDeal.ExportDefSce( _path, _defScenario, _TimeScenario, _defScenarioDes, _TimeScenarioDes )
            

    #----------------------------------------
    #获取train_route的相关信息
    #----------------------------------------
    def getTrainRouteList( self ):
        "get Train Route List."
        self.__TrainRouteList = []
        _path = os.path.join( self.__scenariopath, "train_route.xml" )
        _routeV, _startV, _direV, _trainLen, _Cog_dir = XMLDeal.importTrainRoute( _path )        
        self.__TrainRouteList.append( _routeV )
        self.__TrainRouteList.append( _startV )
        self.__TrainRouteList.append( _direV )
        self.__TrainRouteList.append( _trainLen )
        self.__TrainRouteList.append( _Cog_dir )
        
    #----------------------------------------
    #记录train_route
    #----------------------------------------
    def saveTrainRouteList( self ):
        "save train route list"
        _path = os.path.join( self.__scenariopath, "train_route.xml" )
        XMLDeal.ExportTrainRoute( _path, *self.__TrainRouteList )
    
    def getTRBlockList( self ):
        "get block list in train route"
        return repr( self.__TrainRouteList[0] ).strip()[1:-1]    
    
    def getTRStartBlockID( self ):
        "get start block id in train route."
        return str( self.__TrainRouteList[1][0] )
    
    def getTRStartAbs( self ):
        "get start Abs in train route."
        return str( self.__TrainRouteList[1][1] )
    
    def getTRDirect( self ):
        "get Direct in train route."
        return str( self.__TrainRouteList[2] ) 
    
    def getTRTrainLen( self ):
        "get Train length in train route"
        return str( self.__TrainRouteList[3] ) 
    
    def getTRCogDir( self ):
        "get Cog direction in train route"
        return str( self.__TrainRouteList[4] )     
    
    def setTRBlockList( self, content ):
        "get block list in train route"
        try:
            self.__TrainRouteList[0] = [int( _s ) for _s in content.strip().split( ',' )]
        except ValueError, e:
            print 'setTRBlockList', e, content
            
    def setTRStartBlockID( self, content ):
        "get start block id in train route."
        self.__TrainRouteList[1][0] = int( content )
    
    def setTRStartAbs( self, content ):
        "get start Abs in train route."
        self.__TrainRouteList[1][1] = int( content )
    
    def setTRDirect( self, content ):
        "get Direct in train route."
        self.__TrainRouteList[2] = int( content )
    
    def setTRTrainLen( self, content ):
        "get Train length in train route"
        self.__TrainRouteList[3] = int( content )
    
    def setTRCogDir( self, content ):
        "get Cog direction in train route"
        self.__TrainRouteList[4] = int( content )

    def getExpectSpeedList( self ):
        "get expect speed list."
        _path = os.path.join( self.__scenariopath, "rs_expectSpeed.xml" )
        self.__ExpectSpeedList, self.__EB_EndPos, self.__ExpectSpeedDes = XMLDeal.importExpectSpeed( _path, ReadDes = True )
#        print self.__ExpectSpeedList, self.__EB_EndPos, self.__ExpectSpeedDes
        
    def saveExpectSpeedListToXML( self ):
        "save except speed list to xml"
        _path = os.path.join( self.__scenariopath, "rs_expectSpeed.xml" )
        XMLDeal.ExportExpectSpeed( _path, self.__ExpectSpeedList, self.__EB_EndPos, self.__ExpectSpeedDes )
    
    def AddExpectSpeedOneContent( self, content ):
        "add expect speed one content"
        _SpeedPosStatus = self.getExpectSpeedStartEndSpeedPosStatus() #[[startspeed,endspeed,start,end],]
#        print '_SpeedPosStatus', _SpeedPosStatus
        #先找是否有合适的位置对应
        #从末尾开始找
        _revFalg = self.CheckSpeedEnable( _SpeedPosStatus[-1], content )
        if _revFalg < 0:
            print "AddExpectSpeedOneContent1:", _revFalg
        if True == _revFalg: 
            self.__ExpectSpeedList.append( content )
            self.__ExpectSpeedDes.append( "" )#设置默认值
            return True
        
        _startPos = content[1]
        _PossibleIndexList = [] #对应可插入位置的Index
        
        #先检查中间部分是否有满足情况
        for _i, _value in enumerate( _SpeedPosStatus[1:] ):
#            print _value, _SpeedPosStatus[_i]
            if 1 == content[0]:
                _endPos = content[2]
            elif 0 == content[0]:
                _startspeed = _SpeedPosStatus[_i][1]
                _endspeed = content[3]
                _time = ( _endspeed - _startspeed ) / content[2]
                _endPos = _startPos + ( _endspeed + _startspeed ) * _time / 2
#            print _SpeedPosStatus[_i][3], _value[2], _startPos, _endPos
            #将前后在其之间的提出出来
            if ( _SpeedPosStatus[_i][3] - _startPos ) * ( _value[2] - _startPos ) <= 0 and\
                ( _SpeedPosStatus[_i][3] - _endPos ) * ( _value[2] - _endPos ) <= 0 :
                _PossibleIndexList.append( _i + 1 ) #从1开始
        
        _WorkIndex = None
        #由后往前查找一个满足条件的位置
        _PossibleIndexList.reverse()
        for _index in _PossibleIndexList:
            _revFalg = self.CheckSpeedEnable( _SpeedPosStatus[_index - 1], content, _SpeedPosStatus[_index] )
            if _revFalg < 0:
                print  "AddExpectSpeedOneContent2:", _revFalg
            if True == _revFalg:
                _WorkIndex = _index
                print  "AddExpectSpeedOneContent3:", _WorkIndex
                break
        if None != _WorkIndex:    
            self.__ExpectSpeedList.insert( _WorkIndex, content )
            self.__ExpectSpeedDes.insert( _WorkIndex, "" )#设置默认值
            return True
        else:
            return False

    #------------------------------------------------------------------
    #校验Speedcontent是否能够放在StartSpeedPosStatus的后面,EndSpeedPosStatus的前面
    #StartSpeedPosStatus:[startspeed,endspeed,start,end]
    #------------------------------------------------------------------
    def CheckSpeedEnable( self, StartSpeedPosStatus, Speedcontent, EndSpeedPosStatus = None ):
        "Check Speed Enable"
#        print 'StartSpeedPosStatus', StartSpeedPosStatus
#        print 'Speedcontent', Speedcontent
#        print 'EndSpeedPosStatus', EndSpeedPosStatus
        if StartSpeedPosStatus[1] > 0:
            #检查位置
            if StartSpeedPosStatus[3] > Speedcontent[1] or Speedcontent[3] < 0 : #查看是否不满足，不满足则跳出
                return -1
        elif StartSpeedPosStatus[1] < 0:
            if StartSpeedPosStatus[3] < Speedcontent[1] or Speedcontent[3] > 0 : #查看是否不满足，不满足则跳出
                return -2
        else:
            if StartSpeedPosStatus[3] != Speedcontent[1]: #查看是否不满足，不满足则跳出
                return -3
        
        #检查起始数据参数的问题
        if ( 1 == Speedcontent[0] ) and\
            ( False == self.GetRunTimeByType1( StartSpeedPosStatus[1], \
                                               Speedcontent[1], \
                                               Speedcontent[3], \
                                               Speedcontent[2] ) ):
            return -4
        elif ( 0 == Speedcontent[0] ) and\
            ( False == self.GetRunTimeByType0( StartSpeedPosStatus[1], \
                                               Speedcontent[1], \
                                               Speedcontent[3], \
                                               Speedcontent[2] ) ):
            return -5
        
        #速度大于0的时候不能dweeltime
        if 1 == Speedcontent[0]:
            if Speedcontent[3] != 0 and Speedcontent[-1] > 0:
                return -6        
           
        if  EndSpeedPosStatus != None: #End应该只参考最终速度和起始位置，其他的不用考虑,会有变化的
            #计算终点坐标
            if 0 == Speedcontent[0]:
                if 0 != Speedcontent[2]:#不是匀速
                    _startPos = Speedcontent[1]
                    _endspeed = Speedcontent[3]
                    _startspeed = StartSpeedPosStatus[1]
                    _time = ( _endspeed - _startspeed ) / Speedcontent[2]
                    if _time < 0:
                        return -7
                    _endPos = _startPos + ( _endspeed + _startspeed ) * _time / 2
                else:#匀速
                    _endPos = _startPos #可以认为是起始点
            else:
                _endPos = Speedcontent[2]
            
            if Speedcontent[3] * EndSpeedPosStatus[1] < 0: #速度方向不能反向
                return -8
            elif EndSpeedPosStatus[0] < 0:
                if EndSpeedPosStatus[2] > _endPos : #查看是否不满足，不满足则跳出
                    return -9
            elif  EndSpeedPosStatus[0] > 0:
                if EndSpeedPosStatus[2] < _endPos : #查看是否不满足，不满足则跳出
                    return -10
            else:
                if EndSpeedPosStatus[2] != _endPos: #查看是否不满足，不满足则跳出
                    return -11
                
        return True                
    
    #-------------------------------------------
    #用于校验跑车数据在type1的情况下是否合理时使用
    #-------------------------------------------    
    def GetRunTimeByType1( self, v0, s0, v1, s1 ):
        "GetRunTimeBy Type=1"
#        print' GetRunTimeByType1：', v0, s0, v1, s1 
        if v0 * v1 < 0: #保证不能出现反向
            return False
        try:
            if s0 == s1:
                if v0 != 0 or v1 != 0:
                    return False
            else:
                _time = ( 2 * ( s1 - s0 ) ) / ( v0 + v1 )
                if _time < 0.1: #出现
                    return False
        except:
            return False
        
        return True

    #-------------------------------------------
    #用于校验跑车数据在type0的情况下是否合理时使用
    #-------------------------------------------    
    def GetRunTimeByType0( self, v0, s0, v1, a1 ):
        "GetRunTimeBy Type=1"
#        print 'GetRunTimeByType0', v0, s0, v1, a1
        if v0 * v1 < 0: #保证不能出现反向
            return False
        try:
            if a1 == 0:
                if v0 != v1:
                    return False
            else:
                _time = ( v1 - v0 ) / a1 
                if _time < 0.1: #出现
                    return False
        except:
            return False
        
        return True
        
    
    #-----------------------------------------------------------------------------
    #计算所有exceptSpeed的运行方向以及开始和结束位置[[startspeed,endspeed,start,end],]
    #dir:0,1,-1,停止，前进，后退
    #注意每条只能有一个方向也即[startspeed,endspeed,]有七种形式[0,0][0,1],[0,-1],[1,1],[1,0],[-1,-1],[-1,0] *abs(speed)
    #注意self.__ExpectSpeedList的最初始必有一条停车信息
    #------------------------------------------------------------------------------
    def getExpectSpeedStartEndSpeedPosStatus( self ):
        "get ExpectSpeed Start End Speed Position Status"
        _rev = []
        _rev.append( [0, 0, 0, 0] )
        for _item in self.__ExpectSpeedList[1:]:
            _startspeed = _rev[-1][1]
            _startPos = _item[1]
            if 1 == _item[0]:#type1
                _endspeed = _item[3]
                _endPos = _item[2]
            elif 0 == _item[0]:#type0
                _endspeed = _item[3]
                _time = ( _endspeed - _startspeed ) / _item[2]
                _endPos = _startPos + ( _endspeed + _startspeed ) * _time / 2
            
            _rev.append( [_startspeed, _endspeed, _startPos, _endPos] )
        return _rev                 
    
    def ModifyExpectSpeedOneDes( self, index, content ):
        "modify expect speed one description"
        self.__ExpectSpeedDes[index] = content

    def getExpectSpeedOneDes( self, index ):
        "get expect speed one description"
        return self.__ExpectSpeedDes[index]
    
    def ModifyExpectSpeedOneContent( self, index, content ):
        "Modify expect speed one content"
        try:
            #先检验是否符合原
            _SpeedPosStatus = self.getExpectSpeedStartEndSpeedPosStatus() #[[startspeed,endspeed,start,end],]
            if 0 == index:
                return False
            elif index == len( self.__ExpectSpeedList ) - 1:#最后一个
#                print "ModifyExpectSpeedOneContent1", _SpeedPosStatus[-2], content
                _revFalg = self.CheckSpeedEnable( _SpeedPosStatus[-2], content ) 
                print "ModifyExpectSpeedOneContent1", _revFalg
                if _revFalg < 0:
                    return False
            else:#中间
#                print "ModifyExpectSpeedOneContent2", _SpeedPosStatus[index - 1], content, _SpeedPosStatus[index + 1]
                _revFalg = self.CheckSpeedEnable( _SpeedPosStatus[index - 1], \
                                                  content, \
                                                  _SpeedPosStatus[index + 1] )
                print "ModifyExpectSpeedOneContent2", _revFalg
                if  _revFalg < 0:
                    return False                
            
            self.__ExpectSpeedList[index] = content
            return True
        except IndexError, e:
            print "ModifyExpectSpeedOneContent", index, e
            return False
    
    def DeleteExpectSpeedOneContent( self, index ):
        "delete expect speed one content"
        try:
            self.__ExpectSpeedList.pop( index )
            self.__ExpectSpeedDes.pop( index )    
        except IndexError, e:
            print "DeleteExpectSpeedOneContent", index, e
            
    def getExpectSpeedShowList( self ):
        "get expect speed show list."
        _revlist = []
        for _list in self.__ExpectSpeedList:
            if 1 == _list[0]:
                _revlist.append( [str( _list[0] ),
                                  str( _list[1] ),
                                  str( _list[2] ),
                                  str( _list[3] ),
                                  str( _list[4] )] )
            elif 0 == _list[0]:
                _revlist.append( [str( _list[0] ),
                                  str( _list[1] ),
                                  str( _list[2] ),
                                  str( _list[3] ),
                                  "NONE"] )                
            
        return _revlist
    
    def getExpectSpeedEndPos( self ):
        "get expect speed end postion"
        try:
            return str( self.__EB_EndPos )
        except:
            return '' 
        
    def setExpectSpeedEndPos( self, content ):
        "get expect speed end postion"
        try:
            self.__EB_EndPos = int( content )
        except:
            self.__EB_EndPos = None
            return '' 
    
    #-----------------------------------------------------------------------
    #获取bmbeacon的方法有些特殊，这里不仅要读取默认的xml文件，还要读取地图，
    #从而对xml文件中获得的BMbeacon消息进行校验和重新审核(删除没有的
    #BMbeacon，添加没有的BMbeacon，同时查看上下行属性和变量个数是否相同)
    #注处于效率考虑，函数仅对没有的添加，有的
    #-----------------------------------------------------------------------
    def getBMBeaconDic( self ):
        "get BMBeacon Dic"
        self.__BMBeacons = {}
        _path = os.path.join( self.__scenariopath, "bm_beacons.xml" )
        self.__BMBeacons = XMLDeal.importBMBeacons( _path, ReadDes = True )
#        print "-----", self.__BMBeacons 
        #校验bmbeacon，导入地图文件
        MapData.loadMapData( self.__binmappath,
                             self.__txtmappath,
                             Type = "Edit" )
        _BM_beacons = MapData.getBMBeaconData( Type = "Edit" )
        _BM_BeaconIdList = [_b[0] for _b in _BM_beacons] #获取BMBeaconid list
        
        _deleteList = []
        #先检查已有的
        for _BM_Beacon in self.__BMBeacons:
            try:
                _index = _BM_BeaconIdList.index( int( _BM_Beacon ) )
            except:
                _deleteList.append( _BM_Beacon )
                continue
            
            #检查变量个数和上下行问题
            if 0 == _BM_beacons[_index][1]:
                self.__BMBeacons[_BM_Beacon][0] = 'up'
            elif 1 == _BM_beacons[_index][1]:
                self.__BMBeacons[_BM_Beacon][0] = 'down'
            else:
                self.__BMBeacons[_BM_Beacon][0] = 'all'
            
            #检查变量个数，同时将在变量个数范围内的var为-1的变为0
            if int( self.__BMBeacons[_BM_Beacon][1] ) > _BM_beacons[_index][2]:
                print self.__BMBeacons[_BM_Beacon][1], _BM_Beacon, _BM_beacons[_index]
                for _i in range( _BM_beacons[_index][2], 16 ):
                    self.__BMBeacons[_BM_Beacon][2][_i][1] = '-1'
            elif int( self.__BMBeacons[_BM_Beacon][1] ) < _BM_beacons[_index][2]: 
                print self.__BMBeacons[_BM_Beacon][1], _BM_Beacon, _BM_beacons[_index]
                for _i in range( int( self.__BMBeacons[_BM_Beacon][1] ), _BM_beacons[_index][2] ):
                    self.__BMBeacons[_BM_Beacon][2][_i][1] = '0'
                                    
            self.__BMBeacons[_BM_Beacon][1] = str( _BM_beacons[_index][2] )
        
        #删除没有的id
        for _id in _deleteList:
            self.__BMBeacons.pop( _id )
        
        #查找没有id并添加
        for _BM in _BM_beacons :
            if False == self.__BMBeacons.has_key( str( _BM[0] ) ):
                self.__BMBeacons[str( _BM[0] ) ] = []
                if _BM[1] == 0:
                    self.__BMBeacons[str( _BM[0] ) ].append( "up" )
                elif _BM[1] == 1:
                    self.__BMBeacons[str( _BM[0] ) ].append( "down" )
                elif _BM[1] == 2:
                    self.__BMBeacons[str( _BM[0] ) ].append( "all" )
                
                self.__BMBeacons[str( _BM[0] ) ].append( str( _BM[2] ) )
                _varlist = []
                for _count in range( 0, 16 ):
                    if _count < _BM[2]:
                        _varlist.append( [str( _count ), '0', ''] )#description取默认值
                    else:
                        _varlist.append( [str( _count ), '-1', ''] )#description取默认值
                        
                self.__BMBeacons[str( _BM[0] ) ].append( _varlist )        

    def saveBMBeaconDic( self ):
        "save BM Beacon Dic."
        _path = os.path.join( self.__scenariopath, 'bm_beacons.xml' )
        XMLDeal.ExportBMBeacons( _path, self.__BMBeacons )
    
    def getBMBeaconShowData( self ):
        "get BM Beacon show data"
        _rev = []
        _clientData = []
        for _Bm in self.__BMBeacons:
#            print _Bm, self.__BMBeacons
            _rev.append( "ID: " + _Bm + \
                        " Dir: " + self.__BMBeacons[_Bm][0] + \
                        " VNum: " + self.__BMBeacons[_Bm][1] )
            _clientData.append( _Bm )
            
        return _rev, _clientData
    
    #----------------------------------------------------------
    #注：函数中的两个变量中的终结元素都为string类型的
    #----------------------------------------------------------
    def ModifyBMBeaconVariants( self, BeaconId, Variantlist ):
        "modify Variants of BM Beacon." 
#        print type( BeaconId ), BeaconId, Variantlist
        self.__BMBeacons[BeaconId][2] = copy.deepcopy( Variantlist )
        #注意对于字典值可以用下面的方式进行复制
#        self.__BMBeacons[BeaconId][2] = Variantlist.copy()


    #----------------------------------------------------------
    #根据线路计算BM信标的default状态，使得车能够正确的行驶
    #----------------------------------------------------------
    def SetBMBeaconSetVarToDefault( self ):
        "set BM Beacon Variant to default"
        _blocklist = self.__TrainRouteList[0]
        _tmpVariantList = TrainRoute.getAllZCVariantInfoInBlockList( _blocklist, Type = "Edit" )
#            print _blocklist
#        print len( _tmpVariantList )
        _BeaconDic = TrainRoute.getBMVariantInfoByZCVariantInfo( _blocklist, _tmpVariantList, Type = "Edit" )
#            print _BeaconDic
#            print self.__BMBeacons_Set[_index]
        #修改__BMBeacons_Set
        for _BeaconId in _BeaconDic:
            _BeaconIdStr = str( _BeaconId )
            
            for _Var in _BeaconDic[_BeaconId]:
                self.__BMBeacons[_BeaconIdStr][2][_Var[0]][0] = str( _Var[0] )
                self.__BMBeacons[_BeaconIdStr][2][_Var[0]][1] = str( _Var[1] )
#            print _BeaconId, _BeaconDic[_BeaconId]


    #----------------------------------------------------------
    #获取variant
    #----------------------------------------------------------
    def getBMBeaconVariants( self, BeaconId ):
        "get Variants of BM Beacon." 
        #注意这种返回有一定风险，因为后面的修改都会牵涉到该值本身的修改
#        print 'getBMBeaconVariants', self.__BMBeacons[BeaconId][2]
        _rev = copy.deepcopy( self.__BMBeacons[BeaconId][2] )
#        for _i in self.__BMBeacons[BeaconId][2]:
#            _rev.append( _i )
        return _rev
#        return self.__BMBeacons[BeaconId][2].copy()    
    
    def getBeaconMsgSetting( self ):
        "get Beacon Msg setting"
        self.__BeaconMsgSetting = {}
        _path = os.path.join( self.__scenariopath, "beacon_msg_setting.xml" )
        self.__BeaconMsgSetting = XMLDeal.importBeaconMsgSetting( _path )
    
    def saveBeaconMsgSetting( self ):
        "save beacon msg setting."
        _path = os.path.join( self.__scenariopath, "beacon_msg_setting.xml" )
        XMLDeal.ExportBeaconMsgSetting( _path, self.__BeaconMsgSetting )

    #-----------------------------------------------
    #content：[beaconid, Beacon_Name, Disabled, Msg_Beacon_ID, Use_Default_Msg, Available, Check_Word_1, Check_Word_2, deta_dis]
    #-----------------------------------------------
    def AddOneBeaconMsgSetting( self, content ):
        "add one Beacon msg setting"
        self.__BeaconMsgSetting[content[0]] = content[1:]

    #-----------------------------------------------
    #content：[beaconid, Beacon_Name, Disabled, Msg_Beacon_ID, Use_Default_Msg, Available, Check_Word_1, Check_Word_2, deta_dis]
    #-----------------------------------------------
    def DeleteOneBeaconMsgSetting( self, content ):
        "delete one Beacon msg setting."
        self.__BeaconMsgSetting.pop( content[0] )
    
    def getBeaconMsgSettingShowData( self ):
        "get beacon msg setting show data"
        _rev = []
        for _Beacon in self.__BeaconMsgSetting:
            _rev.append( [_Beacon] + self.__BeaconMsgSetting[_Beacon] )
            
        return _rev            

    def getZCVariantIni( self ):
        "get ZC Variant Ini"
        self.__ZC_Variant_dic = {}
        self.__ZC_Variant_type_EQID = {}
        _path = os.path.join( self.__scenariopath, "zc_variant_ini.xml" )
#        print _path
        self.__ZC_Variant_dic, \
        _variant_dic_len, \
        _variant_dic_Num, \
        self.__ZC_Variant_type_EQID = XMLDeal.importZCVariantIni( _path )
    
    def saveZCVariantIni( self ):
        "save variant Ini"
        _path = os.path.join( self.__scenariopath, "zc_variant_ini.xml" )
        XMLDeal.ExportZCVariantIni( _path, \
                                    self.__ZC_Variant_dic, \
                                    self.__ZC_Variant_type_EQID )
    
    #-----------------------------------------------------------
    #content:[Index, Value ,Type, EquipmentID ],都为str类型
    #-----------------------------------------------------------
    def AddOneZCVariant( self, Linesec, content ):
        "add one variant"
        _linesec = int( Linesec )
        _index = int( content[0] ) - 1
        self.__ZC_Variant_type_EQID[_linesec][_index] = content[2:]
        self.__ZC_Variant_dic[_linesec][_index] = int( content[1] )
        
    #-----------------------------------------------------------
    #content:[Index, Value ,Type, EquipmentID ],都为str类型
    #-----------------------------------------------------------
    def DeleteOneZCVariant( self, Linesec, content ):
        "add one variant"
        _linesec = int( Linesec )
        _index = int( content[0] ) - 1
        self.__ZC_Variant_type_EQID[_linesec][_index] = 0
        self.__ZC_Variant_dic[_linesec][_index] = 0
        
  
    def getLineSecList( self ):
        "get line section list"
        return [str( key ) for key in self.__ZC_Variant_dic]
    
    #-----------------------------------------------------------
    #revlist:[[Index:  Value: Type: EquipmentID: ],]都为str类型
    #-----------------------------------------------------------    
    def getZCVariantShowData( self, Linesec ):
        "get ZC Variant Show Data"
        _revlist = []
        _line = int( Linesec )
#        for _line in self.__ZC_Variant_type_EQID:
        for _index, _EQ in enumerate( self.__ZC_Variant_type_EQID[_line] ):
            if 0 != _EQ: #只显示非零的值
#                _revlist.append( 'Index:' + str( _index + 1 ) + \
#                                 ' Value:' + str( self.__ZC_Variant_dic[_line][_index] ) + \
#                                 ' Type:' + _EQ[0] + \
#                                 ' EquipmentID:' + _EQ[1] )
                _revlist.append( [ str( _index + 1 ),
                                   str( self.__ZC_Variant_dic[_line][_index] ),
                                   _EQ[0],
                                   _EQ[1]] )
        
        return _revlist
            
    def getZCVariantSce( self ):
        "get ZC Variant Scenario"
        self.__ZC_Scenario = []
        self.__ZC_ScenarioDes = []
        _path = os.path.join( self.__scenariopath, "zc_variant_scenario.xml" )
        self.__ZC_Scenario, self.__ZC_ScenarioDes = XMLDeal.importZCVarSce( _path, ReadDes = True )
        
    def saveZCVariantSce( self ):
        "save zc variant scenario."
        _path = os.path.join( self.__scenariopath, "zc_variant_scenario.xml" )
        XMLDeal.ExportZCVarSce( _path, self.__ZC_Scenario, self.__ZC_ScenarioDes )


    def getOneZCVariantSceDes( self, index ):
        "modify one scenario position Des"
        return self.__ZC_ScenarioDes[index]
        
    def ModifyOneZCVariantSceDes( self, index, content ):
        "modify one scenario position Des"
        self.__ZC_ScenarioDes[index] = content
        
    def DeleteOneZCVariantSce( self, index ):
        "delete one scenario position."
        try:
            self.__ZC_Scenario.pop( index )
            self.__ZC_ScenarioDes.pop( index )
        except IndexError, e:
            print "DeleteOneZCVariantSce", index, e        
        
    def getZCVariantSceShowData( self ):
        "get zc variant scenario show data."
        rev = []
        for _content in self.__ZC_Scenario:
            rev.append( 'block Id:' + _content[0] + '   Abscissa:' + _content[1] + '   Delay:' + _content[2] )
        return rev
            
    def getOneZCVariantSceNameValue( self, index ):
        "get one zc variant sceanrio name value list"
        if -1 != index:
            return self.__ZC_Scenario[index]
    
    #------------------------------------------
    #添加一条ZC定义的脚本
    #content：[blockid,abs,delay,[[],...]]
    #------------------------------------------
    def AddOneZCVariantSce( self, content ):
        "Add one scenario position."
        self.__ZC_Scenario.append( content )
        self.__ZC_ScenarioDes.append( "" )#设置默认值      
    
    
    #------------------------------------------
    #修改一条ZC定义的脚本的内容,现只支持改内容，不支持该位置和时间，只能删除添加完成该操作
    #index:脚本对应的编号：从0开始编号
    #content：[[name,value],....]
    #------------------------------------------
    def ModifyOneZCVariantSce( self, index, content ):
        "Modify one scenario position."
        try:
            self.__ZC_Scenario[index][-1] = content
        except IndexError, e:
            print "ModifyOneZCVariantSce", index, e        


    #----------------------------------------------------
    #根据现在跑的线路将ZC的相关变量设置成允许和限制状态
    #主要包括道岔位置,信号机的状态等等
    #----------------------------------------------------
    def SetOneZCVariantSceToDefault( self, index ):
        "set one zc variant scenario to default"
#        print self.__TrainRouteList
        _blocklist = self.__TrainRouteList[0]
#        print _blocklist
        _tmpVariantList = TrainRoute.getAllZCVariantInfoInBlockList( _blocklist, Type = "Edit" )
        #将数据转换为字符型的
        _tmplist = []
#        print _tmpVariantList
        for _item in _tmpVariantList:
#            print _item
            _tmp = [str( _i ) for _i in _item]
            _tmplist.append( _tmp )
        try:
            self.__ZC_Scenario[index][-1] = _tmplist
        except IndexError, e:
            print "SetOneZCVariantSceToDefault", index, e   

    #------------------------------------------
    #修改一条ZC定义的脚本的内容,现在已经支持改内容
    #index:脚本对应的编号：从0开始编号
    #content：[blockid,abs,dwelltime]
    #------------------------------------------
    def ModifyOneZCVariantScePos( self, index, content ):
        "Modify one scenario position."
        try:
            self.__ZC_Scenario[index][0] = content[0]
            self.__ZC_Scenario[index][1] = content[1]
            self.__ZC_Scenario[index][2] = content[2]
        except IndexError, e:
            print "ModifyOneZCVariantScePos", index, e   
    
    #--------------------------------------------------
    #获取当前选中的一条位置定义的脚本的content：[[linesec,index,value],....]
    #--------------------------------------------------
    def getOneZCVariantSceContent( self, index ):
        "get One Scenario content."
        try:
            return self.__ZC_Scenario[index][-1]
        except IndexError, e:
            print "getOneZCVariantSceContent", index, e
            return None        

    #--------------------------------------------------
    #获取当前选中的一条位置定义的脚本的content：[blockid,abs,dwelltime]
    #--------------------------------------------------
    def getOneZCVariantScePos( self, index ):
        "get One Scenario Pos info."
        try:
            return self.__ZC_Scenario[index][0:3]
        except IndexError, e:
            print "getOneZCVariantScePos", index, e
            return None  
        
#===============================================================================
# 向导页“CI Scenario Config Page”的一些处理函数
# 主要对输入的ci_variant_scenario.xml文件数据进行处理
#===============================================================================
    def getCIVariantSce( self ):
        "get CI Variant Scenario"
        self.__CI_Scenario = []
        self.__CI_ScenarioDes = []
        _path = os.path.join( self.__scenariopath, "ci_variant_scenario.xml" )
        #_path = os.path.join( "E:\\Jyno\\Python\\scenario", "ci_variant_scenario.xml" )
        self.__CI_Scenario, self.__CI_ScenarioDes = XMLDeal.importCIVarSce( _path, ReadDes = True )
        
    def saveCIVariantSce( self ):
        "save CI variant scenario."
        _path = os.path.join( self.__scenariopath, "ci_variant_scenario.xml" )             
        #_path = os.path.join( "E:\\Jyno\\Python\\scenario", "ci_variant_scenario.xml" )
        XMLDeal.ExportCIVarSce( _path, self.__CI_Scenario, self.__CI_ScenarioDes )
       
    def getCIVariantSceShowData( self ):
        "get CI variant scenario show data."
        rev = []
        for _content in self.__CI_Scenario:            
            rev.append( 'block Id:' + _content[0] + '   Abscissa:' + _content[1] + '   Delay:' + _content[2] )
        return rev  
    
    def AddOneCIVariantSce( self , content ):
        "Add one scenario position."
        self.__CI_Scenario.append( content )
        self.__CI_ScenarioDes.append( "" ) 
    
    def DeleteOneCIVariantSce( self , index ):
        "delete one scenario position."
        try:
            self.__CI_Scenario.pop( index )
            self.__CI_ScenarioDes.pop( index )
        except IndexError, e:
            print "DeleteOneCIVariantSce", index, e

    def ModifyOneCIVariantScePos( self, index, content ):
        "Modify one scenario position."
        try:
            self.__CI_Scenario[index][0] = content[0]
            self.__CI_Scenario[index][1] = content[1]
            self.__CI_Scenario[index][2] = content[2]
        except IndexError, e:
            print "ModifyOneCIVariantScePos", index, e   
    
    def ModifyOneCIVariantSce( self, index, content ):
        "Modify one scenario position."
        try:
            self.__CI_Scenario[index][-1] = content
        except IndexError, e:
            print "ModifyOneCIVariantSce", index, e        


    #----------------------------------------------------
    #根据现在跑的线路将ZC的相关变量设置成允许和限制状态
    #主要包括道岔位置,信号机的状态等等
    #----------------------------------------------------
    def SetOneCIVariantSceToDefault( self, index ):
        "set one ci variant scenario to default"
#        print self.__TrainRouteList
        _blocklist = self.__TrainRouteList[0]
#        print _blocklist
        _tmpVariantList = TrainRoute.getAllCIVariantInfoInBlockList( _blocklist, Type = "Edit" )
        #将数据转换为字符型的
        _tmplist = []
#        print _tmpVariantList
        
        for _item in _tmpVariantList:
#            print _item
            _tmp = [str( _i ) for _i in _item]
            _tmplist.append( _tmp )
        try:
            self.__CI_Scenario[index][-1] = _tmplist
        except IndexError, e:
            print "SetOneCIVariantSceToDefault", index, e   

    
    def getOneCIVariantSceDes( self, index ):
        "modify one scenario position Des"
        return self.__CI_ScenarioDes[index]

    def getOneCIVariantSceContent( self, index ):
        "get One Scenario content."
        try:
            return self.__CI_Scenario[index][-1]
        except IndexError, e:
            print "getOneCIVariantSceContent", index, e
            return None 

    def getOneCIVariantScePos( self, index ):
        "get One Scenario Pos info."
        try:
            return self.__CI_Scenario[index][0:3]
        except IndexError, e:
            print "getOneCIVariantScePos", index, e
            return None  

    def ModifyOneCIVariantSceDes( self, index, content ):
        "modify one scenario position Des"
        self.__CI_ScenarioDes[index] = content
    
    
    def getCBIIDList( self ):
        "get CBI_ID list"
        #return [str( key ) for key in self.__CI_Variant_dic]
        return ['1', '2', '3', '4', '5', '6']

#===============================================================================
# end
# 向导页"CI Scenario Config Page"处理函数  
# end        
#===============================================================================

    def getVIOMSetting( self ):
        "get viom setting"
        self.__VIOM_Setting_dic_in = {}
        self.__VIOM_Setting_dic_out = {}
        _path = os.path.join( self.__scenariopath, "rs_viom_setting.xml" )

        self.__VIOM_Setting_dic_in, \
        self.__VIOM_Setting_dic_out = XMLDeal.importVIOMSetting( _path )
        
    def saveVIOMSettingToXML( self ):
        "save viom setting to xml"
        _path = os.path.join( self.__scenariopath, "rs_viom_setting.xml" )
        XMLDeal.ExportVIOMSetting( _path, \
                                   self.__VIOM_Setting_dic_in, \
                                   self.__VIOM_Setting_dic_out )
            
    #-----------------------------------------------
    #type:0:in,1:out
    #name:变量名字
    #index：设置的index
    #-----------------------------------------------
    def ModifyVIOMSetting( self, type, name, index ):
        "modify viom setting."
        if 0 == type:
            self.__VIOM_Setting_dic_in[name][0] = index
        elif 1 == type:
            self.__VIOM_Setting_dic_out[name][0] = index
            
    #-----------------------------------------------
    #type:0:in,1:out,
    #返回：[[viomtype,name,index]]
    #-----------------------------------------------
    def getVIOMSettingShowData( self, type ):
        "get viom setting show data."
        _dic = {}
        if 0 == type:
            _dic = self.__VIOM_Setting_dic_in
        elif 1 == type:
            _dic = self.__VIOM_Setting_dic_out
        
        _rev = []
        
        for _item in _dic:
            _rev.append( [str( _dic[_item][1] ), _item, str( _dic[_item][0] )] )
        
        return _rev
    
    def getTSRSetting( self ):
        "get TSR setting"
        _path = os.path.join( self.__scenariopath, "lc_tsr_setting.xml" )
        self.__TSRSetting, self.__TSRSettingDes = XMLDeal.importTSRSetting( _path, ReadDes = True )
#        print 'getTSRSetting', self.__TSRSetting
        
    def getTSRSettingIndex( self ):
        "get TSR Setting Index."
        _indexList = []
        for _Tsr in self.__TSRSetting:
            _indexList.append( str( _Tsr ) )
        return _indexList
    
    def getOneTSRSetting( self, index ):
        "get TSR setting"
        return self.__TSRSetting[int( index )]   
    
    def getOneTSRSettingDes( self, index ):
        "get TSR setting Description"
        return self.__TSRSettingDes[int( index )] 
        
    def saveTSRSetting( self ):
        "save TSR Setting"
        _path = os.path.join( self.__scenariopath, "lc_tsr_setting.xml" )
        XMLDeal.ExportTSRSetting( _path, self.__TSRSetting, self.__TSRSettingDes )
        
    #-------------------------------------------
    #content:内容依次如下
    #<TSR_Speed Value="50" />
    #<First_Block_ID_Of_TSR Value="247" />
    #<Start_Abscissa_On_First_Block_Of_TSR Value="10" />
    #<Number_Of_Intermediate_Blocks_Of_TSR Value="0" />
    #<Intermediate_Block_ID_Of_TSR Value="" />
    #<Last_Block_ID_Of_TSR Value="247" />
    #<End_Abscissa_On_Last_Block_Of_TSR Value="100" />
    #-------------------------------------------    
    def ModifyTSRSetting( self, index, content ):
        "modify tsr setting"
        self.__TSRSetting[int( index )] = content
    
    def ModifyTSRSettingDes( self, index, content ):
        "modify tsr setting"
#        print index, content
        self.__TSRSettingDes[int( index )] = content
    
    def AddTSRSetting( self, content ):
        "add TSR setting."
        _index = len( self.__TSRSetting ) + 1
        self.__TSRSetting[_index] = content
        self.__TSRSettingDes[_index] = ""  #设置默认值
    
    def deleteTSRSetting( self, index ):
        "delete TSR Setting."
        #先将其移至最后一位，再pop
        for _i in range( int( index ), len( self.__TSRSetting ) ) :
            self.__TSRSetting[_i] = self.__TSRSetting[_i + 1]
            self.__TSRSettingDes[_i] = self.__TSRSettingDes[_i + 1]
        self.__TSRSetting.pop( len( self.__TSRSetting ) )
        self.__TSRSettingDes.pop( len( self.__TSRSettingDes ) )
    
if __name__ == '__main__':
#    test = CaseProcess()
#    test.importUserCase( r"../testcaseconfig/user_case_config.xml" )
    case = CaseParser()
    dic = case.LoadCaseFolder( u"E:\eclipse_GTP\ATP_TP_Interface\src\被测版本标签号\\" )
    for _key in dic[1]:
        print _key
        for __key in dic[1][_key]:
            print __key, dic[1][_key][__key][0], dic[1][_key][__key][1], dic[1][_key][__key][2]
