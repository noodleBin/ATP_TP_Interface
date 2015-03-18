#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     CasePack.py
# Description:  用于将用例和地图进行分开打包
# Author:       XiongKunpeng
# Version:      0.0.1
# Created:      date 2012-06-18
# Company:      CASCO
# LastChange:   Created 2012-06-18
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
import zipfile

class CasePack( object ):
    """
    Case Pack
    """
    #用例的所有文件名
    default_file_name = ["beacon_msg_setting.xml",
                         "bm_beacons.xml",
                         "ccnv_rules.xml",
                         "ccnv_scenario.xml",
                         "ci_scenario.xml",
                         "datp_scenario.xml",
                         "lc_scenario.xml",
                         "lc_tsr_setting.xml",
                         "rs_expectSpeed.xml",
                         "rs_rules.xml",
                         "rs_scenario.xml",
                         "rs_viom_setting.xml",
                         "train_route.xml",
                         "ts_scenario.xml",
                         "viom_scenario.xml",
                         "zc_scenario.xml",
                         "zc_variant_ini.xml",
                         "zc_variant_scenario.xml"]
    
    defalut_map_file = ["1.xml",
                        "2.xml",
                        "3.xml",
                        "atpCpu1Binary.txt",
                        "atpCpu2Binary.txt",
                        "ccnvBinary.txt",
                        "nv.xml",
                        "srd.xml",
                        "v.xml" ]

    def __init__( self ):
        "case pack init"
    
    #--------------------------------------------
    #将测试用例，log按照要求进行打包处理
    #--------------------------------------------
    @classmethod    
    def PackCase( cls, path ):
        "Pack Case"
        root, dirs, files = CaseParser.getFolderlist( path )
        Case_PACK_Path = os.path.join( root, u"Pack_Case.zip" )
        Log_PACK_Path = os.path.join( root, u"Pack_Log.zip" )
        _fZip_Case = zipfile.ZipFile( Case_PACK_Path, "w", zipfile.ZIP_DEFLATED )
        _fZip_Log = zipfile.ZipFile( Log_PACK_Path, "w", zipfile.ZIP_DEFLATED )
#        _fZip_Case1 = zipfile.ZipFile( Case_PACK_Path1, "w", zipfile.ZIP_DEFLATED ) 
        for _dir in dirs:
            _Bcode_path = os.path.join( root, _dir )
            _Bcode_root, _Bcode_dirs, _Bcode_files = CaseParser.getFolderlist( _Bcode_path )
#            print _Bcode_root, _Bcode_dirs, _Bcode_files 
            for _Bcode_dir in _Bcode_dirs:
                _casepath = os.path.join( _Bcode_root, _Bcode_dir )
                case_root, case_dirs, case_files = CaseParser.getFolderlist( _casepath )
                for case_dir in case_dirs:
                    _steppath = os.path.join( case_root, case_dir )
                    step_root, step_dirs, step_files = CaseParser.getFolderlist( _steppath )
#                    print step_root, step_dirs, step_files
                    for step_dir in step_dirs:
#                        print step_dir
                        if step_dir in ["Script", "script"]:
#                            print step_dir
                            _tmppath = os.path.join( step_root, step_dir )
                            _tmppath = os.path.join( _tmppath, "scenario" )
                            _tmproot, _tmpdirs, _tmpfiles = CaseParser.getFolderlist( _tmppath )
#                            print "_tmproot", _tmproot, _tmpdirs, _tmpfiles
                            for _tmp_file in _tmpfiles:
                                if _tmp_file in cls.default_file_name:
                                    _tmpfilepath = os.path.join( _tmproot, _tmp_file )
                                    _packname = _dir + u"\\" + _Bcode_dir + u"\\" + case_dir + u"\\" + step_dir + u"\\" + u"scenario" + u"\\" + _tmp_file
                                    _fZip_Case.write( _tmpfilepath,
                                                      _packname )
                                else:
                                    print "unknow file", _tmproot, _tmp_file
                        elif step_dir in ["Log", "log"]:
                            _log = os.path.join( step_root, step_dir )
                            _downlog = os.path.join( _log, "DownLog" )
                            _uplog = os.path.join( _log, "log" )
                            _tmpdownroot, _tmpdowndirs, _tmpdownfiles = CaseParser.getFolderlist( _downlog )
                            for _tmp_file in _tmpdownfiles:
                                _tmpfilepath = os.path.join( _tmpdownroot, _tmp_file )
                                _packname = _dir + u"\\" + _Bcode_dir + u"\\" + case_dir + u"\\" + step_dir + u"\\" + "DownLog" + u"\\" + _tmp_file
                                _fZip_Log.write( _tmpfilepath,
                                                 _packname )   
                            _tmpuproot, _tmpupdirs, _tmpupfiles = CaseParser.getFolderlist( _uplog )
                            for _tmp_file in _tmpupfiles:
                                _tmpfilepath = os.path.join( _tmpuproot, _tmp_file )
                                _packname = _dir + u"\\" + _Bcode_dir + u"\\" + case_dir + u"\\" + step_dir + u"\\" + "log" + u"\\" + _tmp_file
#                                print _tmpfilepath
                                _fZip_Log.write( _tmpfilepath,
                                                 _packname )                                  
                                                         
                    _case_config_path = os.path.join( step_root, "root_case_setting.xml" )
#                    print _case_config_path
                    if os.path.exists( _case_config_path ):
                        _fZip_Case.write( _case_config_path,
                                          _dir + u"\\" + _Bcode_dir + u"\\" + case_dir + u"\\" + "root_case_setting.xml" )
                    else:
                        print "unknow case config", step_root, _case_config_path
#        _fZip_Case1.close()
        _fZip_Case.close()
        _fZip_Log.close()

    #--------------------------------------------
    #将地图按照要求进行打包处理
    #--------------------------------------------
    @classmethod    
    def PackMap( cls, path ):
        "Pack Case"
        root, dirs, files = CaseParser.getFolderlist( path )
        Map_PACK_Path = os.path.join( root, u"Pack_Map.zip" )
        _fZip_Map = zipfile.ZipFile( Map_PACK_Path, "w", zipfile.ZIP_DEFLATED )
        for _dir in dirs:
            _Bcode_path = os.path.join( root, _dir )
            _Bcode_root, _Bcode_dirs, _Bcode_files = CaseParser.getFolderlist( _Bcode_path )
#            print _Bcode_root, _Bcode_dirs, _Bcode_files 
            for _Bcode_dir in _Bcode_dirs:
                _Mappath = os.path.join( _Bcode_root, _Bcode_dir )
                map_root, map_dirs, map_files = CaseParser.getFolderlist( _Mappath )
                for map_file in map_files:
                    if map_file in cls.defalut_map_file:
                        _tmpfilepath = os.path.join( map_root, map_file )
                        _packname = _dir + u"\\" + _Bcode_dir + u"\\" + map_file
                        _fZip_Map.write( _tmpfilepath,
                                        _packname )
#        _fZip_Case1.close()
        _fZip_Map.close()


if __name__ == '__main__':        
    "case pack check"
#    a = "\xbe\xdc\xbe\xf8\xb7\xc3\xce\xca\xa1\xa3"
#    print a.decode( 'gb2312' )
#    CasePack.PackCase( u"E:\\test1" )
    CasePack.PackMap( u"E:\\test1\\map" )
