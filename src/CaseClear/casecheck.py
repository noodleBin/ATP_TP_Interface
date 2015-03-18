#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     casecheck.py
# Description:  用于校验用例文件的完整性以及对用例文件进行规范化
#               主要提供以下功能：
#               1.将数据拷贝到需要的地方，并检测用用例是end1还是end2
#               2.检验文件是否都存在，并对不存在的文件进行复制添加
#               3.对需要更新的文件进行更新
# Author:       XiongKunpeng
# Version:      0.0.1
# Created:      date 2012-03-14
# Company:      CASCO
# LastChange:   Created 2012-03-14
# History:      
#----------------------------------------------------------------------------
from base import commlib
from base.caseprocess import CaseParser
from lxml import etree
import os
import readfile
import win32file
from base.xmlparser import XmlParser 
from base import filehandle
import struct

class CaseCheck( object ):
    """
    Case check
    """

    #脚本读取时使用的信息
    nodePaths = {'viom_setting_in':'/VIOM_Settings/VIOM_IN/Item',
                 'viom_setting_out':'/VIOM_Settings/VIOM_OUT/Item'
                }
    attributes = {'viom_setting':['@Index', '@Name', '@VIOM', '@Description']
                }

    #用于检测文件是否满足要求
    __scriptfile = ['/beacon_msg_setting.xml', \
                    '/bm_beacons.xml', \
                    '/ccnv_rules.xml', \
                    '/ccnv_scenario.xml', \
                    '/ci_scenario.xml', \
                    '/datp_scenario.xml', \
                    '/lc_scenario.xml', \
                    '/lc_tsr_setting.xml', \
                    '/rs_expectSpeed.xml', \
                    '/rs_rules.xml', \
                    '/rs_scenario.xml', \
                    '/rs_viom_setting.xml', \
                    '/train_route.xml', \
                    '/ts_scenario.xml', \
                    '/viom_scenario.xml', \
                    '/zc_scenario.xml', \
                    '/zc_variant_ini.xml', \
                    '/zc_variant_scenario.xml']
    
    _Logfile = []

    __rs_viomsettinglist_in = ["IN_ANCS1", "IN_ANCS2",
                               "IN_BM1", "IN_BM2",
                               "IN_CBTC1", "IN_CBTC2",
                               "IN_EDDNO1", "IN_EDDNO2",
                               "IN_KSON1", "IN_KSON2",
                               "IN_REV1", "IN_REV2",
                               "IN_RM_PB1", "IN_RM_PB2",
                               "IN_RMF1", "IN_RMF2",
                               "IN_TDCL1", "IN_TDCL2",
                               "IN_TI1", "IN_TI2",
                               "IN_ZVBA11", "IN_ZVBA12",
                               "IN_ZVBA21", "IN_ZVBA22",
                               "IN_EBNA1", "IN_EBNA2"
                               ]
    __rs_viomsettinglist_out = ["OUT_DE_A1", "OUT_DE_A2",
                                "OUT_DE_B1", "OUT_DE_B2",
                                "OUT_EBRD11", "OUT_EBRD12",
                                "OUT_EBRD21", "OUT_EBRD22",
                                "OUT_EDDL1", "OUT_EDDL2",
                                "OUT_FWD1", "OUT_FWD2",
                                "OUT_HDC_A1", "OUT_HDC_A2",
                                "OUT_HDC_B1", "OUT_HDC_B2",
                                "OUT_REV1", "OUT_REV2",
                                "OUT_ZVI1", "OUT_ZVI2",
                                "OUT_ZVRD11", "OUT_ZVRD12",
                                "OUT_ZVRD21", "OUT_ZVRD22",
                                "OUT_RM_ACT1", "OUT_RM_ACT2"
                                ]
    def __init__( self ):
        "map check init"
        
    
    @classmethod
    def CopyFile( cls, FromFile, ToFile ):
        "copy file"
#        os.system( "copy %s %s" % ( FromFile, ToFile ) )
        filehandle.CopyFile( FromFile, ToFile )
    
    @classmethod
    def CopyFolder( cls, FromFolder, ToFolder ): 
        "copy folder"
        filehandle.CopyFolder( FromFolder, ToFolder )
#        for root, dirs, files in os.walk( FromFolder ):
#            for file in files:
#                cls.CopyFile( os.path.join( FromFolder, file ), \
#                              os.path.join( ToFolder, file ) )
#            break #保证只拷贝更目录的文件
        
#        print '''xcopy "%s" "%s" /S''' % ( FromFolder, ToFolder )
#        os.system( '''xcopy "E:/a" "E:b" /E /y /i''' )
#        os.system( "A" )

    #-------------------------------------------------------------------------
    #检测脚本的规范性，包括检测压缩log是否存在，是否有多个，还有描述是否都已经添加
    #-------------------------------------------------------------------------
    @classmethod
    def checkCaseValid( cls, casepath ):
        "check Case Validity"
        root, dirs, files = CaseParser.getFolderlist( casepath ) 
        for _dir in dirs:
            if _dir not in [u"CR_Regression_Script", u"CR_Validate" ]:
                _test_case_Num = _dir
                _tmppath = os.path.join( root, _dir )
                case_root, case_dirs, case_files = CaseParser.getFolderlist( _tmppath )
                for _case_dir in case_dirs:
                    if _case_dir not in  [u"被测试软件程序和测试平台程序", "log", "script", "Log", "Script"]:
                        _test_case_step_Num = _case_dir
                        _tmp_casepath = os.path.join( case_root, _case_dir )
                        _tmp_casepath_Log = os.path.join( _tmp_casepath, "Log" )
                        _tmp_casepath_Script = os.path.join( _tmp_casepath, "Script" )
                        _tmp_casepath_root = os.path.join( _tmp_casepath, "root_case_setting.xml" )
                        
                        #检查是否有OMAP记录
                        _tmp_casepath_DownLog = os.path.join( _tmp_casepath_Log, "DownLog" )
                        
                        _NumofLog = cls.getZipfileNum( _tmp_casepath_DownLog )
                        if 0 == _NumofLog:
                            print _tmp_casepath, "Not have Log!"
                        if 1 < _NumofLog:
                            print _tmp_casepath, "have more than one Log!"
                            
                        
                        #检查是否有写描述
                        if 0 == cls.CheckIfHasCaseDescription( _tmp_casepath_root ):
                            print _tmp_casepath, "Not have Case Description!"
                        
    #--------------------------------------------------------------
    #检查是否存在用例的描述
    #--------------------------------------------------------------
    @classmethod
    def CheckIfHasCaseDescription( cls, path ):
        "check If has case description"
        try:
            _f = XmlParser()
            _f.loadXmlFile( path )
    
            _hiss = _f.getAttrListManyElement( './/His', \
                                               ['Date', 'Status', 'Description'] )
                
            _f.closeXmlFile()
        
            return len( _hiss )
        except:
            return 0
        
    
    #----------------------------------------
    #检查log中omap记录的个数
    #----------------------------------------
    @classmethod
    def getZipfileNum( cls, casepath ):
        "get zip file number in case path"
        root, dirs, files = CaseParser.getFolderlist( casepath ) 
        _hasOMAPFlag = False
        _NumOfOMAP = 0
        for _f in files:
            if  "OMAPData.zip" == _f:
                _hasOMAPFlag = True
                _NumOfOMAP += 1
            elif ".zip" in _f:
                _NumOfOMAP += 1
        
        if  _hasOMAPFlag:
            return _NumOfOMAP
        else:
            return 0
        
    
            
    
    #将文件夹下的scenario的所有文件拷贝到目的地址
    @classmethod
    def CopyScriptToDest( cls, Frompath, ToPath ):
        "copy script to destpath"
        #遍历路径
        index = 0
        root, dirs, files = CaseParser.getFolderlist( Frompath ) 
        for _dir in dirs:
            if _dir not in [u"CR_Regression_Script", u"CR_Validate" ]:
                _test_case_Num = _dir
                index = index + 1
                _tmppath = os.path.join( root, _dir )
                case_root, case_dirs, case_files = CaseParser.getFolderlist( _tmppath )
                _Case_Flag = False
                for _case_dir in case_dirs:
                    if _case_dir not in  [u"被测试软件程序和测试平台程序", "log", "script", "Log", "Script"]:
                        _Case_Flag = True
#                        index = index + 1
                        _test_case_step_Num = _case_dir
                        _tmp_casepath = os.path.join( case_root, _case_dir )
                        _tmp_casepath_Log = os.path.join( _tmp_casepath, "Log" )
                        _tmp_casepath_Script = os.path.join( _tmp_casepath, "Script" )
                        

                        if False == os.path.exists( _tmp_casepath_Log ):
                            _tmp_casepath_Log = os.path.join( _tmp_casepath, "log" )
                        if False == os.path.exists( _tmp_casepath_Script ):
                            _tmp_casepath_Script = os.path.join( _tmp_casepath, "script" )
                        
                        #校验log文件夹是否为空
                        if False == os.path.exists( _tmp_casepath_Log ):
                            print "not have log1:", _tmp_casepath_Log
                            continue
                        if False == os.path.exists( _tmp_casepath_Script ):
                            print "not have Script1:", _tmp_casepath_Script
                            continue
                        
                        _tmp_casepath_Scenario = os.path.join( _tmp_casepath_Script, "scenario" )
                        #校验log文件夹是否为空                                 
                        if cls.getdirsize( _tmp_casepath_Log ) == 0:
                            print "not have log2", _tmp_casepath_Log
                            _tmp_casepath_Log = None

                        #校验log文件夹是否为空                                 
                        if cls.getdirsize( _tmp_casepath_Script ) == 0:
                            print "not have script2", _tmp_casepath_Script
                            _tmp_casepath_Script = None
                            continue
#                        print "_tmp_casepath_Script",_tmp_casepath_Script
                        #将_tmp_casepath_Script中的scenario文件夹进行复制
                        _destPath_Num = os.path.join( ToPath, _test_case_Num )
                        _destPath_Step = os.path.join( _destPath_Num, _test_case_step_Num )
                        _destPath_Script = os.path.join( _destPath_Step, "Script" )
                        _destPath_Scenario = os.path.join( _destPath_Script, "scenario" )
                        if False == os.path.exists( _destPath_Scenario ):
                            os.makedirs( _destPath_Scenario )
                        
#                        print _tmp_casepath_Scenario, _destPath_Scenario
                        cls.CopyFolder( _tmp_casepath_Scenario, _destPath_Scenario )
                        
                        #检验scenario文件是否符合标准
                        if False == cls.checkScriptFolderValid( _destPath_Scenario ):
                            pass
#                            print "not have Scenario:", _destPath_Scenario
                        else:
                            pass
                        cls.ReplaceFile( _destPath_Scenario )
                        cls.CheckViom_Setting( _destPath_Scenario )
                        if None != _tmp_casepath_Script:
                            endtype = cls.detectEndType( os.path.join( _tmp_casepath_Script, "setting" ) )
                            endtime = cls.detectTime( _tmp_casepath_Log )
                        
                            cls.SaveCaseConfig( _destPath_Step, endtype, endtime )
                    else:
                        print "Case Error:", case_root , _case_dir
                if False == _Case_Flag:
                    print  "Case Error:", case_root  
        print index     
    
    #------------------------------------------------
    #@检测车头并生成用例的相关配置,path为setting路径
    #------------------------------------------------
    @classmethod
    def detectEndType( cls, path ):
        "detect end type"
        _file = os.path.join( path, "tps_parameter.xml" )
        _f = XmlParser()
        try:
            _f.loadXmlFile( _file )      
        except:
            print "tps_parameter.xml error:", _file, "may be not have setting!"
            return "End1"
        _para = _f.getAttrListManyElement( './/Dev',
                                           ['Name', 'SSTY', 'LogID', 'SSID'] ) 
        
        for _p in _para:
            if "atp" == _p[0]:
                return "End" + _p[-1] 
        
    
    #------------------------------------------------------
    #@检测运行时间，没有的话则用默认时间300，path路径为log路径
    #------------------------------------------------------
    @classmethod
    def detectTime( cls, path ):
        "detect Time"
        if path == None:
            return 300
        root, dirs, files = CaseParser.getFolderlist( path ) 
        
#        _exist = False
        for file in files:
            if "ATP_UP.xml" in file:
#                _exist = True
                _path = os.path.join( root, file )
                _f = XmlParser()
                try:
                    _f.loadXmlFile( _path )      
                except:
                    print "log xml error:", _path
                    return 300
                _offset = 956
                _len = 32
                _node = _f.getAllElementByName( ".//CH" )[-1]#取最后一帧
                _data = _f.getNodeText( _node )[2 * _offset: 2 * ( _offset + ( _len / 8 ) )]
                _value = cls.HexStrToInt( "!I", _data )
                
                if _value > 2 ** 29:
                    _value = _value - 2 ** 29
#                _para = _f.getAttrListManyElement( './/FRAME',
#                                                   ['datacount', ] )[0]
#                print "_value", _value             
                return  _value / 5 + 5  #提高5秒
                              
        return 300
    

    @classmethod
    def HexStrToInt( self, Type, str, Len = None ):
        "tranform string to int"
        _str = ""
        if None == str:
            return "0"
#        print "TranStrToInt:", Type, str, Len 
        if None == Len:
            Len = len( str ) / 2
        
        if Len == 3:#24的要补值
            str = "00" + str
            
        for _i in range( Len ):
#            print _i
            _str += chr( int( str[2 * _i: 2 * ( _i + 1 )], 16 ) )
        return struct.unpack( Type, _str )[0]
    
    #--------------------------------------------------------------
    #替换文件，有些文件需要替换成默认文件，这里主要是rule和viomsetting
    #path为需要替换文件的文件夹路径
    #---------------------------------------------------------------
    @classmethod
    def ReplaceFile( self, path ):
        "replace file"
        _filename = "rs_rules.xml"
        _path = os.path.join( path, _filename )
        
        _From_path = r"../default case/scenario/rs_rules.xml"
        
        win32file.CopyFile( _From_path, _path, 0 )
        
    
    #----------------------------------------------
    #检测viom_setting并替换为最新格式
    #----------------------------------------------
    @classmethod
    def CheckViom_Setting( cls, path ):
        "check viom setting path."
        _viom_setting_path = os.path.join( path, "rs_viom_setting.xml" )

        _Defalut_in, _Defalut_out = cls.ReadViom_Setting( "../default case/scenario/rs_viom_setting.xml" )
        _Modify_in, _Modify_out = cls.ReadViom_Setting( _viom_setting_path )
        
        for _inName in _Defalut_in:
            if _Modify_in.has_key( _inName ):#存在则用Modify的值
                _Defalut_in[_inName] = _Modify_in[_inName]
        
        for _outName in _Defalut_out:
            if _Modify_out.has_key( _outName ):#存在则用Modify的值
                _Defalut_out[_outName] = _Modify_out[_outName]   
                
                
        #将修改的值进行存储
        cls.SaveViomSetting( _viom_setting_path, \
                             _Defalut_in, \
                             _Defalut_out )
        
    @classmethod
    def SaveViomSetting( cls, path, dic_in, dic_out ):
        "Save viom setting."
        _viom_setting_file = open( path, 'w' )
        _viom_setting_file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _viom_setting = etree.Element( "VIOM_Settings" )
        
        _viom_in = etree.SubElement( _viom_setting, "VIOM_IN" )
        for _inName in cls.__rs_viomsettinglist_in:
            _viom_in_item = etree.SubElement( _viom_in, "Item" )
            _viom_in_item.set( "Index", str( dic_in[_inName][0] ) )
            _viom_in_item.set( "Name", _inName )
            _viom_in_item.set( "VIOM", str( dic_in[_inName][1] ) )
            _viom_in_item.set( "Description", dic_in[_inName][2] )
        
        _viom_out = etree.SubElement( _viom_setting, "VIOM_OUT" )
        for _outName in cls.__rs_viomsettinglist_out:
            _viom_out_item = etree.SubElement( _viom_out, "Item" )
            _viom_out_item.set( "Index", str( dic_out[_outName][0] ) )
            _viom_out_item.set( "Name", _outName )
            _viom_out_item.set( "VIOM", str( dic_out[_outName][1] ) )
            _viom_out_item.set( "Description", dic_out[_outName][2] )

        _viom_setting_file.write( '''
<!--配置rs发送给viom的信息中变量和码位的对应关系-->
<!--rs->viom的信息有16个，分别对应码位0-15，当码位为-1表示无该变量的码位-->
<!--viom->rs的信息有10个，分别对应码位0-9，当码位为-1表示无该变量的码位-->
<!--属性中的Index即为码位信息(变量在viom端口中的位置)-->        
'''
        )
        _str = etree.tostring( _viom_setting, pretty_print = True, encoding = "utf-8" )
        _viom_setting_file.write( _str )
        _viom_setting_file.close()


    @classmethod
    def SaveCaseConfig( cls, configpath, endtype, time ):
        "save case config."
        _path = os.path.join( configpath, "root_case_setting.xml" )
        _file = open( _path, 'w' )
        #创建XML根节点
        _Case_Config = etree.Element( "CaseInfo" )
        
        _config = etree.SubElement( _Case_Config, 'Config' )
        _hiss = etree.SubElement( _Case_Config, 'History' )
        
        _mapconfig = etree.SubElement( _config, 'MapConfig' )
        _mapconfig.set( 'Version', "Bcode_CC_OFFLINE_VN_Build20111227" )
        _mapconfig.set( 'MapNum', "ATP_TM_LL-0000" )
        _mapconfig.set( 'Description', u"原始地图" )
        
        _fileconfig = etree.SubElement( _config, 'FileConfig' )
        _fileconfig.set( 'TrainEnd', endtype )
        _fileconfig.set( 'DataPlugPath', "" )
        _fileconfig.set( 'Description', endtype )  

        _fileconfig = etree.SubElement( _config, 'EndConfig' )
        _fileconfig.set( 'EndType', "1" )
        _fileconfig.set( 'Para', str( time ) )
        _fileconfig.set( 'Description', u"按照时间方式结束用例" ) 
              
#        for _h in cls.__EditCaseConfig['history']:
#            _his = etree.SubElement( _hiss, 'His' )
#            _his.set( 'Date', _h[0] )
#            _his.set( 'Status', _h[1] )
#            _his.set( 'Description', _h[2] )             
           

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

    #----------------------------------------------
    #读取viom——setting
    #----------------------------------------------\
    @classmethod
    def ReadViom_Setting( self, path ):
        "read viom setting"        
        tree = etree.parse( path )
        #先读取VIOMIN的相关配置
        r = tree.xpath( self.nodePaths['viom_setting_in'] )
        #print r
        _dic_in = {}
        for node in r:  
            _para_name = node.xpath( self.attributes['viom_setting'][1] )[0]
            _para_index = int( node.xpath( self.attributes['viom_setting'][0] )[0] )
            _para_VIOM = int( node.xpath( self.attributes['viom_setting'][2] )[0] )
            _para_Des = node.xpath( self.attributes['viom_setting'][3] )[0]
            _dic_in[_para_name] = [_para_index, _para_VIOM, _para_Des]
        
        #读取VIOMOUT的相关配置
        r = tree.xpath( self.nodePaths['viom_setting_out'] )
        _dic_out = {}
        for node in r:  
            _para_name = node.xpath( self.attributes['viom_setting'][1] )[0]
            _para_index = int( node.xpath( self.attributes['viom_setting'][0] )[0] )
            _para_VIOM = int( node.xpath( self.attributes['viom_setting'][2] )[0] )
            _para_Des = node.xpath( self.attributes['viom_setting'][3] )[0] 
            _dic_out[_para_name] = [_para_index, _para_VIOM, _para_Des]

        
        return _dic_in, _dic_out
        
        
    #----------------------------------------------
    #@path:为绝对路径
    #----------------------------------------------
    @classmethod
    def CheckScript( self, path ):
        "import map"
        #遍历该路径下的的所有文件夹
        root, dirs, files = CaseParser.getFolderlist( path ) 
        for _dir in dirs:
            _tmppath = os.path.join( root, _dir )
            if False == self.checkScriptFolderValid( _tmppath ):
                print "Wrong scenario!", _tmppath
            else:
                print "right scenario:", _tmppath


    #---------------------------------------------------
    #@检测用例所需的文件是否具备
    #@包括文件一个文件夹UP_Log
    #---------------------------------------------------
    @classmethod
    def checkScriptFolderValid( self, path ):
        "检验case路径下的case时候有效，无效则返回false"
        _rev = True
        for _f in self.__scriptfile:
            if False == os.path.exists( path + _f ):
                print "Not exist Script file:", _f[1:], "path:", path
                #拷贝默认文件进去
                _Frompath = "../default case/scenario/" + _f
                win32file.CopyFile( _Frompath, path + _f, 0 )
                _rev = False
            
        return _rev

    @classmethod
    def getdirsize( cls, dir ):
        "get directory size"
        size = 0L
        for root, dirs, files in os.walk( dir ):
            size += sum( [os.path.getsize( os.path.join( root, name ) ) for name in files] )
        
        return size

if __name__ == '__main__':        
    "casecheck"
#    a = "\xbe\xdc\xbe\xf8\xb7\xc3\xce\xca\xa1\xa3"
#    print a.decode( 'gb2312' )
    #Bcode_ATP_VN_Build20111228版本
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\蒋仁钢\\Bcode_ATP_VN_Build20111228", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20111228" )
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\景立青\\Bcode_ATP_VN_Build20111228", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20111228" )
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\刘莉\\Bcode_ATP_VN_Build20111228\VCP", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20111228" )
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\叶漪\\Bcode_ATP_VN_Build20111228", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20111228" )
    
    #Bcode_ATP_VN_Build20120217版本
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\蒋仁钢\\Bcode_ATP_VN_Build20120217", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120217" )
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\景立青\\Bcode_ATP_VN_Build20120217", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120217" )    
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\刘莉\\Bcode_ATP_VN_Build20120217\\VCP", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120217" ) 
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\叶漪\\Bcode_ATP_VN_Build20120217", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120217" )         

    #Bcode_ATP_VN_Build20120305版本
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\刘莉\\Bcode_ATP_VN_Build20120305\\VCP", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120305" )    
    
    #Bcode_ATP_VN_Build20120309版本
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\叶漪\\Bcode_ATP_VN_Build20120309", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120309" ) 

    
    #Bcode_ATP_VN_Build20120315版本
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\蒋仁钢\\Bcode_ATP_VN_Build20120315", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120315" )
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\刘莉\\Bcode_ATP_VN_Build20120315\VCP", \
                                u"E:\ATP_Validate_2012_04_04\Bcode_ATP_VN_Build20120315" )    
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\叶漪\\Bcode_ATP_VN_Build20120315", \
                                u"E:\ATP_Validate_2012_04_04\Bcode_ATP_VN_Build20120315" )
    
    #Bcode_ATP_VN_Build20120320版本
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\蒋仁钢\\Bcode_ATP_VN_Build20120320", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120320" )
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\刘莉\\Bcode_ATP_VN_Build20120320", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120320" )
    
    #Bcode_ATP_VN_Build20120327版本
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\蒋仁钢\\Bcode_ATP_VN_Build20120327", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120327" )    
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\刘莉\\Bcode_ATP_VN_Build20120327", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120327" )    
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\叶漪\Bcode_ATP_VN_Build20120327", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120327" )    
    
    #Bcode_ATP_VN_Build20120330版本
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\蒋仁钢\\Bcode_ATP_VN_Build20120330", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120330" )
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\叶漪\\Bcode_ATP_VN_Build20120330", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120330" )    
    
    #Bcode_ATP_VN_Build20120331版本
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\蒋仁钢\\Bcode_ATP_VN_Build20120331", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120331" )
    
    #Bcode_ATP_VN_Build20120401版本
    CaseCheck.CopyScriptToDest( u"E:\\ATP软件确认测试\\蒋仁钢\\Bcode_ATP_VN_Build20120401", \
                                u"E:\\ATP_Validate_2012_04_04\\Bcode_ATP_VN_Build20120401" )    
