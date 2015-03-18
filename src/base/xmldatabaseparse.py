#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     xmldatabaseparse.py
# Description:  解析项目数据文件   
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      date: 2013-05-07
# Company:      CASCO
# LastChange:   2013-05-07 创建文件
# History: 
#----------------------------------------------------------------------------
from xmlparser import XmlParser 
import os
from lxml import etree

variantParser = {"path":"Variant",
                 "sectionId":"Line_section_id",
                 "Index":"Index_on_line_section"}

CBIVariantParser = {"path":"Radio_block_mode_variant",
                    "CBI_id":"CBI_id",
                    "Index_on_CBI":"Index_on_CBI"}

Next_BlockParser = {"path":"Next_block",
                    "Id":"Id",
                    "Direction":"Direction",
                    "Variant":variantParser }

BMBeaconParser = {"direction":"Block_mode_variant_direction",
                  "BMVariant":{"path": "Block_mode_variant",
                               "Index":"Index",
                               "Variant":variantParser
                               } 
                  }
    
BeaconParser = {"path":"Beacon",
                "Id": "Id",
                "Abscissa":"Abscissa",
                "BMBeacon":BMBeaconParser}

ZCCBIIndexParser = {"path":"/Vital_setting/Variants/Block_mode/Mapping",
                    "ZCVaraint": variantParser,
                    "CBIVaraint":CBIVariantParser}

ProtectionZoneParser = {"path":"Protection_zone",
                        "abscissa":"Begin_abscissa",
                        "Length":"Length",
                        "Variant":variantParser}

SignalParser = {"path":"Signal",
                "abscissa":"Abscissa",
                "Overlap":"Overlap",
                "Block_mode": "Block_mode",
                "Direction":"Direction",
                "Variant":variantParser
                }

SSAParser = {"path":"Service_stopping_area",
             "Id": "Id",
             "abscissa":"Begin_abscissa",
             "Length":"Length"
            }

PSDParser = {"path":"PSD_zone",
             "Id": "Id",
             "abscissa":"Begin_abscissa",
             "Length":"Length",
             "Variant":variantParser,
             "Platform":{"path":"Platform",
                         "Side":"Side",
                         "Id": "PSD_platform_id"}
            }
    
class CCDataBaseXmlParser():
    """
    CC database xmlfile parser
    """
    FileParser = {"ZC_ID":"/ZC_area/Id",
                  "Block": {"path":"/ZC_area/Block",
                            "subNode":{"Id":"Id",
                                       "Length":"Length",
                                       "Next_block":Next_BlockParser,
                                       "Beacon":BeaconParser,
                                       "ProtectionZone":ProtectionZoneParser,
                                       "Signal":SignalParser,
                                       "SSA":SSAParser,
                                       "PSD":PSDParser }
                            },
                  "BlockCbi": {"path":"/ZC_area/Block",
                                "subNode":{"Id":"Id",
                                           "CBI_id":"CBI_id" }
                               },
                  "VIOM":{"path":"/Non_vital_setting/Train_type/Special_intermediate_data",
                          "vital_Inputs":"s_vital_inputs_index",
                          "vital_Outputs":"s_vital_outputs_index",
                          "novital_Inputs":"s_function_inputs_index",
                          "novital_Outputs":"s_function_outputs_index",
                          },
                  "ZCCBIIndex":ZCCBIIndexParser
                  }

    #需要读取的码位数据
    __rs_viomsettinglist_vital_in = ["IN_ANCS1", "IN_ANCS2",
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
    __rs_viomsettinglist_vital_out = ["OUT_DE_A1", "OUT_DE_A2",
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
    
    __rs_viomsettinglist_novital_in = ["IN_ATB_PB1", "IN_ATB_PB2", \
                                       "IN_BM_PB1", "IN_BM_PB2", \
                                       "IN_CPB_A1", "IN_CPB_A2", \
                                       "IN_CPB_B1", "IN_CPB_B2", \
                                       "IN_DBY1", "IN_DBY2", \
                                       "IN_DMS_FA1", "IN_DMS_FA2", \
                                       "IN_DMS_HA1", "IN_DMS_HA2", \
                                       "IN_EBNA1", "IN_EBNA2", \
                                       "IN_MCS1", "IN_MCS2", \
                                       "IN_NDC1", "IN_NDC2", \
                                       "IN_OPB_A1", "IN_OPB_A2", \
                                       "IN_OPB_B1", "IN_OPB_B2", \
                                       "IN_START_PB1", "IN_START_PB2"
                                       ]
    
    __rs_viomsettinglist_novital_out = ["OUT_ATB_IND1", "OUT_ATB_IND2", \
                                       "OUT_ATO_OP1", "OUT_ATO_OP2", \
                                       "OUT_BDR1", "OUT_BDR2", \
                                       "OUT_BMR1", "OUT_BMR2", \
                                       "OUT_CSR1", "OUT_CSR2", \
                                       "OUT_DCC_A1", "OUT_DCC_A2", \
                                       "OUT_DCC_B1", "OUT_DCC_B2", \
                                       "OUT_DOC_A1", "OUT_DOC_A2", \
                                       "OUT_DOC_B1", "OUT_DOC_B2", \
                                       "OUT_MDR1", "OUT_MDR2", \
                                       "OUT_RM_IND1", "OUT_RM_IND2", \
                                       "OUT_START_IND1", "OUT_START_IND2", \
                                       "OUT_ATB_OP1", "OUT_ATB_OP2", \
                                       "OUT_PWR_ON1", "OUT_PWR_ON2", \
                                       "OUT_TSP1", "OUT_TSP2", \
                                       "OUT_ASP1", "OUT_ASP2", \
                                       "OUT_EB_RST1", "OUT_EB_RST2"
                                       ]

    
    #注意：本类中的所有长度数据都是毫米为单位的
    #读取XMl文件的初始数据记录
    #格式描述如下：
    #{ZCId:{blockId:BlockInfoList,...},...}
    #BlockInfoList:[length,sectionID,NextBlockInfoList,BeaconList,BMBeaconList,SingsDic,PSDInfoList]
    #NextBlockInfoList:[nun,nunidx,nunSecid,nur,nuridx,nurSecid,ndn,ndnidx,ndnSecid,ndr,ndridx,ndrSecid]
    #BeaconList:[[id,type,abs,b_id,abscissa,dir],...] #注意只有BM信标有方向，type：BM信标为4，其余不填,平台需要的时候再添加
    #BMBeaconList:[[id,direction,VARnumber,VARSectionID_0,VariantRank_0,ValidityTime_0,…,VARSectionID_15,VariantRank_15,ValidityTime_15],...]
    #SingsDic:{"Protection_Zone":SingInfoList,
                #"SIGNAL":SingInfoList,
                #"SIGNAL_BM_INIT":SingInfoList,
                #"SIGNAL_OVERLAP":SingInfoList,
                #"SIGNAL_OVERLAP_BM":SingInfoList,
                #"SIGNAL_OVERLAP_END":SingInfoList,这个暂时不处理
                #"SSA":SingInfoList,
                #"PSD":SingInfoList}
    #SingInfoList:[type,id,abs,pre_computed_energy[0],pre_computed_energy[1],attribute,orientation,section_id]
    #PSDInfoList：[PSDID,Side,SectionID,VariantRank]
    __WholeInitDataBase = None
    
    __DirectionDic = {"Up":0, "Down":1, "Both":2}
    
    __SideDic = {"Left":0, "Right":1, "Both":2}
    
    
    #线路数据
    __Blocks = None
    __Zcs = None
    __Beacons = None
    __BMBeacons = None
    __Sings = None
    __Psds = None
    __Viom_Port_dic = None
    __MTIBs = None
    
    #用于存储block id和CBI id的对应关系
    __BlockIdToCBIIdDic = None  #{ZCId:{BlockId:CBIId},...}
    #用于存储CBI的Index和ZC的Index的对应关系
    __CBIIndexToZCIndexDic = None #{(Index_on_CBI,CBI_id):(Index_on_line_section,Line_section_id),...}
    __ZCIndexToCBIIndexDic = None  #{(Index_on_line_section,Line_section_id):(Index_on_CBI,CBI_id),...}
    
    #用于存储ZC变量代表的具体意义
    __ZCVariantInfoDic = None
    
    #用于存储CBI变量代表的具体意义
    __CBIVariantInfoDic = None

    #用于存储BMBeacon变量代表的具体意义
    __BMBeaconVariantInfoDic = None
        
    def __init__( self ):
        "init"
        self.__WholeInitDataBase = {}
        self.__PZId = 0
        self.__SignalId = 0
        self.__PSDIdList = []
        self.__BlockIdToCBIIdDic = {}
        
    def loadXMLFile( self, FileFolder ):
        "load XML File"
        self.__WholeInitDataBase = {}
        
        #先读取线路数据
        for root, dirs, files in os.walk( FileFolder ):
            for _file in files:
                if ( ".xml" in _file ): #只读取xml文件
                    _filepath = os.path.join( root, _file )
                    if "nv" in _file: #读取v.xml
                        self.loadNVSettingFile( _filepath )
                    elif "v" in _file: #读取nv.xml
                        self.loadVSettingFile( _filepath )
                    elif "srd" in _file:  #读取srd.xml
                        self.loadSRDFile( _filepath )
                    else:
                        self.loadRouteDataFile( _filepath )
            break
        
        #拆分信息数据，获取需要的离线数据
        self.__Blocks = self.calBlocks()
        self.__Sings = self.calSings()
        self.__BMBeacons = self.calBMBeacons()
        self.__Beacons = self.calBeacons()
        self.__Psds = self.calPsds()
        
        self.__ZCVariantInfoDic = self.calZCVariantInfo()
        self.__CBIVariantInfoDic = self.calCBIVariantInfo()
        self.__BMBeaconVariantInfoDic = self.calBMBeaconVariantInfo()
        
    def getZCVariantDicInfo( self ):
        "get ZC Variant Dic Inforamtion"
        return self.__ZCVariantInfoDic

    def getCBIVariantDicInfo( self ):
        "get CBI Variant Dic Inforamtion"
        return self.__CBIVariantInfoDic
    
    def getBMBeaconVariantDicInfo( self ):
        "get BM Beacon Variant Dic Inforamtion"
        return self.__BMBeaconVariantInfoDic 
    
    def getBlocks( self ):
        "get Blocks"
        return self.__Blocks
    
    def getZCs( self ):
        "get ZCs"
        return self.__Zcs #暂时不输出
    
    def getCBIToZCDic( self ):
        "get CBI Index to ZC Index dic"
        return self.__CBIIndexToZCIndexDic
    
    def getZCToCBIDic( self ):
        "get ZC Index to CBI Index dic"
        return self.__ZCIndexToCBIIndexDic
    
    def getVIOMPorts( self ):
        "get VIOM Ports"
        return self.__Viom_Port_dic
    
    def getSings( self ):
        "get sings"
        return self.__Sings
    
    def getBeacons( self ):
        "get Beacons"
        return self.__Beacons
    
    def getBMBeacons( self ):
        "get BM beacons"
        return self.__BMBeacons
    
    def getPsds( self ):
        "get Psds"
        return self.__Psds
    
    def getMTIBs( self ):
        "get MTIBs"
        return self.__MTIBs

    def getBlockCBIs( self ):
        "get Block CBI info"
        return self.__BlockIdToCBIIdDic
    
    #---------------------------------------------------------------------------
    #获取ZC CBI中的Index的对应关系
    #VNode为VS的xml文件读取的根节点
    #---------------------------------------------------------------------------    
    def calZCCBIIndex( self, VNode ):
        "calculate ZC CBI Dic"
        self.__ZCIndexToCBIIndexDic = {}
        self.__CBIIndexToZCIndexDic = {}
        
        _ZCCBIIndexParserDic = self.FileParser["ZCCBIIndex"]
        
        #获取所有的Mapping的节点
        _MappingNodeList = VNode.xpath( _ZCCBIIndexParserDic["path"] )
#        print _ZCCBIIndexParserDic["path"] , VNode
        #遍历节点进行数据的读取
        for _mapNode in _MappingNodeList:
#            print _mapNode
            _ZCVariantInfo = self.getVariantInfo( _mapNode )
            _CBIVariantInfo = self.getCBIVariantInfo( _mapNode )
#            print _ZCVariantInfo, _CBIVariantInfo
            
            if None in [_ZCVariantInfo, _CBIVariantInfo]:
                print "calZCCBIIndex error!", _ZCVariantInfo, _CBIVariantInfo
                self.__ZCIndexToCBIIndexDic = None
                self.__CBIIndexToZCIndexDic = None
                return
            else:
                self.__ZCIndexToCBIIndexDic[ tuple( _ZCVariantInfo ) ] = tuple( _CBIVariantInfo )
                self.__CBIIndexToZCIndexDic[tuple( _CBIVariantInfo ) ] = tuple( _ZCVariantInfo )               
    
    
    #--------------------------------------------------------------------------------------
    #获取ZC变量以及其的具体意义，比如lineSectionId = 1，Index=2定义的是道岔1,2的定位表示，等等
    #具体返回格式为：{(index,lineSection):TypeInfo,...}
    #TypeInfo,现在暂时定义为一个StringList，不同的Type的定义是不同的，先给出已有的定义如下：
    #道岔：定位："blockId1-BlockId2-Switch-DBJ"，反位："blockId1-BlockId2-Switch-FBJ"
    #普通信号机："BlockId-Abs-Signal"
    #BM信号机："BlockId-Abs-Signal-BMIni"
    #BM overlap信号机："BlockId-Abs-Signal-BM-Overlap"
    #overlap信号机："BlockId-Abs-Signal-Overlap"
    #overlapEnd："Overlap-End"
    #PretectionZone："BlockId-Abs-PZ"
    #PSDZone："BlockId-PSDID-PSD"
    #--------------------------------------------------------------------------------------
    def calZCVariantInfo( self ):
        "calculate ZC Varaint Infomation"
        _ZCVariantInfo = {}
        
        for _zcId in self.__WholeInitDataBase:
            for _BId in self.__WholeInitDataBase[_zcId]:
                #先处理道岔信息
                #[nun,nunidx,nunSecid,nur,nuridx,nurSecid,ndn,ndnidx,ndnSecid,ndr,ndridx,ndrSecid]
                _NextBlockInfo = self.__WholeInitDataBase[_zcId][_BId][2]

                if -1 != _NextBlockInfo[1]: #up 定位
#                    print "aaaaaaaaaaaa", _NextBlockInfo[1]
                    self.addNewStringToVariantList( _ZCVariantInfo,
                                                    ( _NextBlockInfo[1], _NextBlockInfo[2] ),
                                                    str( _BId ) + "-" + str( _NextBlockInfo[0] ) + "-Switch-up" + "-DBJ" )
                    
                if -1 != _NextBlockInfo[4]: #up 反位
#                    print "bbbbbbbbbbbbbbbbb", _NextBlockInfo[4]
                    self.addNewStringToVariantList( _ZCVariantInfo,
                                                    ( _NextBlockInfo[4], _NextBlockInfo[5] ),
                                                    str( _BId ) + "-" + str( _NextBlockInfo[3] ) + "-Switch-up" + "-FBJ" )
#                    if 91 == _BId:
#                        print _ZCVariantInfo[( 16, 2 )]
                    
                if -1 != _NextBlockInfo[7]: #down 定位
#                    print "cccccccccc", _NextBlockInfo[7]
                    self.addNewStringToVariantList( _ZCVariantInfo,
                                                    ( _NextBlockInfo[7], _NextBlockInfo[8] ),
                                                    str( _BId ) + "-" + str( _NextBlockInfo[6] ) + "-Switch-down" + "-DBJ" )
                    
                if -1 != _NextBlockInfo[10]: #down 反位
#                    print "dddddddddddddddd", _NextBlockInfo[10]
                    self.addNewStringToVariantList( _ZCVariantInfo,
                                                    ( _NextBlockInfo[10], _NextBlockInfo[11] ),
                                                    str( _BId ) + "-" + str( _NextBlockInfo[9] ) + "-Switch-down" + "-FBJ" )
                
#                if 91 == _BId:
#                    print "11111111111111", _NextBlockInfo, tuple( _NextBlockInfo[4:6] )
#                    print "222222222222", _ZCVariantInfo[( 15, 2 )]
                
                
                #处理奇点中的Varaint信息
                _SingsDic = self.__WholeInitDataBase[_zcId][_BId][-2]


                #SingsDic:{"Protection_Zone":SingInfoList,
                            #"SIGNAL":SingInfoList,
                            #"SIGNAL_BM_INIT":SingInfoList,
                            #"SIGNAL_OVERLAP":SingInfoList,
                            #"SIGNAL_OVERLAP_BM":SingInfoList,
                            #"SIGNAL_OVERLAP_END":SingInfoList,这个暂时不处理
                            #"SSA":SingInfoList,
                            #"PSD":SingInfoList}                
                #SingInfoList:[type,id,abs,pre_computed_energy[0],pre_computed_energy[1],attribute,orientation,section_id]

                for _singName in _SingsDic:
                    if "Protection_Zone" == _singName:
                        for _sing in _SingsDic[_singName]:
                            self.addNewStringToVariantList( _ZCVariantInfo,
                                                            ( _sing[-3], _sing[-1] ),
                                                            str( _BId ) + "-" + str( _sing[2] ) + "-PZ" )
                            
                    elif "SIGNAL" == _singName:
                        for _sing in _SingsDic[_singName]:
                            self.addNewStringToVariantList( _ZCVariantInfo,
                                                            ( _sing[-3], _sing[-1] ),
                                                            str( _BId ) + "-" + str( _sing[2] ) + "-Signal" )
                        
                    elif "SIGNAL_BM_INIT" == _singName:
                        for _sing in _SingsDic[_singName]:
                            self.addNewStringToVariantList( _ZCVariantInfo,
                                                            ( _sing[-3], _sing[-1] ),
                                                            str( _BId ) + "-" + str( _sing[2] ) + "-Signal-BMIni" )
                    
                    elif "SIGNAL_OVERLAP" == _singName:
                        for _sing in _SingsDic[_singName]:
                            self.addNewStringToVariantList( _ZCVariantInfo,
                                                            ( _sing[-3], _sing[-1] ),
                                                            str( _BId ) + "-" + str( _sing[2] ) + "-Signal-Overlap" )
                            self.addNewStringToVariantList( _ZCVariantInfo,
                                                            ( _sing[-3] + 1, _sing[-1] ),
                                                            "Overlap-End" )
                            
                    elif "SIGNAL_OVERLAP_BM" == _singName:
                        for _sing in _SingsDic[_singName]:
                            self.addNewStringToVariantList( _ZCVariantInfo,
                                                            ( _sing[-3], _sing[-1] ),
                                                            str( _BId ) + "-" + str( _sing[2] ) + "-Signal-BM-Overlap" )
                            self.addNewStringToVariantList( _ZCVariantInfo,
                                                            ( _sing[-3] + 1, _sing[-1] ),
                                                            str( _BId ) + "-" + str( _sing[2] ) + "-Overlap-End" )
                   

                    elif "PSD" == _singName:
                        for _sing in _SingsDic[_singName]:
                            _PsdInfo = self.getPSDInfoById( _sing[1] ) #[PSDID,Side,SectionID,VariantRank]
                            self.addNewStringToVariantList( _ZCVariantInfo,
                                                            ( _PsdInfo[-1], _PsdInfo[-2] ),
                                                            str( _BId ) + "-" + str( _sing[1] ) + "-PSD" )

        return _ZCVariantInfo
        
    #----------------------------------------------------------------------------
    #本函数专门给calZCVariantInfo使用，用于将新的变量对应的线路控制信息，写入到字典中
    #Dic：带写入字典
    #VariantKey：(index,lineSection)
    #String:新的描述
    #--------------------------------------------------------------
    def addNewStringToVariantList( self, Dic, VariantKey, String ):
        "add new string to variant list"    
        if Dic.has_key( VariantKey ):
            if String not in Dic[VariantKey]: #只添加不重复的
                Dic[VariantKey].append( String )
        else:
            Dic[VariantKey] = [String]
    
    #---------------------------------------------------------------------------
    #根据ZC Variant Index 与实际控制变量的对应关系，以及CBI和ZC变量 的对应关系
    #计算获得CBI的变量和变量描述的对应关系
    #{(index,CBI_ID):TypeInfo,...}
    #---------------------------------------------------------------------------
    def calCBIVariantInfo( self ):
        "calculate CBI Variant Information"
        _CBIVariantInfo = {}
        
#        print self.getZCToCBIDic()
        
        for _ZCVariant in self.getZCVariantDicInfo():
            try:
                _CBIVariantInfo[self.getZCToCBIDic()[_ZCVariant]] = self.getZCVariantDicInfo()[_ZCVariant]
            except KeyError, e:
#                print "calCBIVariantInfo Error", _ZCVariant, self.getZCVariantDicInfo()[_ZCVariant]
                continue
        
        return _CBIVariantInfo

    #---------------------------------------------------------------------------
    #根据ZC Variant Index 与实际控制变量的对应关系，以及CBI和ZC变量 的对应关系
    #计算获得CBI的变量和变量描述的对应关系
    #{(BMBecaonId,index):TypeInfo,...}
    #---------------------------------------------------------------------------
    def calBMBeaconVariantInfo( self ):
        "calculate BM Beacon Variant Information"
        _BMBeaconVariantInfo = {}
        
        #[[id,direction,VARnumber,VARSectionID_0,VariantRank_0,ValidityTime_0,…,VARSectionID_15,VariantRank_15,ValidityTime_15],...]
        for _BMBeacon in self.getBMBeacons():
            _Id = _BMBeacon[0]
            _Num = _BMBeacon[2]
            for _i in range( _Num ):
                try:
                    _VariantInfo = ( _BMBeacon[3 + _i * 3 + 1], _BMBeacon[3 + _i * 3 ] )
                    _BMBeaconVariantInfo[( _Id, _i )] = self.getZCVariantDicInfo()[_VariantInfo]
                except KeyError, e:
                    if ( -1, -1 ) != _VariantInfo:
                        print "calBMBeaconVariantInfo Error", _VariantInfo, ( _Id, _i ), _Num
                    continue
                
        return _BMBeaconVariantInfo        
    
    #---------------------------------------------------------------------------
    #获取VIOM的各个码位端口
    #NVNode为NVS的xml文件读取的根节点
    #---------------------------------------------------------------------------
    def calVIOMPorts( self, NVNode ):
        "calculate viom port"
        #返回字典列表
        _revDic = {} #保存,{'vital_in':{'portName':Index,...},...}
        _revDic['vital_in'] = {}
        _revDic['vital_out'] = {}
        _revDic['novital_in'] = {}
        _revDic['novital_out'] = {}
        
        _viomPortParserDic = self.FileParser["VIOM"]
        
#        print  _viomPortParserDic["path"]
        
        _fatherNode = NVNode.xpath( _viomPortParserDic["path"] )[0]
        #获取vital_in
        _vital_in_node = _fatherNode.xpath( _viomPortParserDic["vital_Inputs"] )[0]
        
        for _tag in self.__rs_viomsettinglist_vital_in:
            _tmpTag = "VIOM_" + _tag
            try:
#                print _tmpTag
                _revDic['vital_in'][_tag] = int( _vital_in_node.xpath( _tmpTag )[0].text )
            except IndexError, e:
                _revDic['vital_in'][_tag] = -1

        #获取vital_out
        _vital_out_node = _fatherNode.xpath( _viomPortParserDic["vital_Outputs"] )[0]
        
        for _tag in self.__rs_viomsettinglist_vital_out:
            _tmpTag = "VIOM_" + _tag
            try:
                _revDic['vital_out'][_tag] = int( _vital_out_node.xpath( _tmpTag )[0].text )
            except IndexError, e:
                _revDic['vital_out'][_tag] = -1        

        #获取novital_in
        _novital_in_node = _fatherNode.xpath( _viomPortParserDic["novital_Inputs"] )[0]
        
        for _tag in self.__rs_viomsettinglist_vital_in:
            _tmpTag = "VIOM_" + _tag
            try:
                _revDic['novital_in'][_tag] = int( _novital_in_node.xpath( _tmpTag )[0].text )
            except IndexError, e:
                _revDic['novital_in'][_tag] = -1

        #获取novital_out
        _novital_out_node = _fatherNode.xpath( _viomPortParserDic["novital_Outputs"] )[0]
        
        for _tag in self.__rs_viomsettinglist_vital_out:
            _tmpTag = "VIOM_" + _tag
            try:
                _revDic['novital_out'][_tag] = int( _novital_out_node.xpath( _tmpTag )[0].text )
            except IndexError, e:
                _revDic['novital_out'][_tag] = -1   
                
        return _revDic
    
    #------------------------------------------------
    #本函数需要在getBlocks之后调用    
    #------------------------------------------------
    def calSings( self ):
        "calculate sings"
        _singsInfo = []
        _SingIndex = 0
        
        _blockIndex = 0
        for _zcId in self.__WholeInitDataBase:
            for _BId in self.__WholeInitDataBase[_zcId]:
                _SingLength = 0
                for _singName in  self.__WholeInitDataBase[_zcId][_BId][-2]:
                    _singsInfo += self.__WholeInitDataBase[_zcId][_BId][-2][_singName]

                    _SingLength += len( self.__WholeInitDataBase[_zcId][_BId][-2][_singName] )
                
                #修改block的
                self.__Blocks[_blockIndex][3] = _SingIndex
                self.__Blocks[_blockIndex][4] = _SingIndex + _SingLength - 1
                self.__Blocks[_blockIndex][5] = _SingLength
#                print _SingLength, _SingIndex, _blockIndex, len( _singsInfo )
                _SingIndex += _SingLength
                _blockIndex += 1
        
#        print "calSings", len( _singsInfo ), _singsInfo
        return _singsInfo
            
    
    def calBeacons( self ):
        "calculate Beacons"
        _beaconInfo = []
        for _zcId in self.__WholeInitDataBase:
            for _BId in self.__WholeInitDataBase[_zcId]:
                _beaconInfo += self.__WholeInitDataBase[_zcId][_BId][3] 
        
        return _beaconInfo        

    def calBMBeacons( self ):
        "calculate BM Beacons"
        _BMBeaconInfo = []
        for _zcId in self.__WholeInitDataBase:
            for _BId in self.__WholeInitDataBase[_zcId]:
                _BMBeaconInfo += self.__WholeInitDataBase[_zcId][_BId][4] 
        
        return _BMBeaconInfo       
    
    def calPsds( self ):
        "calculate Psds"
        #psd内容由于后面部分是不用，所以这边只取了前面4个变量
        _psdInfo = []
        for _zcId in self.__WholeInitDataBase:
            for _BId in self.__WholeInitDataBase[_zcId]:
                _psdInfo += self.__WholeInitDataBase[_zcId][_BId][-1] 
        
        return _psdInfo
                        
    def calBlocks( self ):
        "calculate blocks"
        _BlockInfo = []
        for _zcId in self.__WholeInitDataBase:
            for _BId in self.__WholeInitDataBase[_zcId]:
                _BlockInfo.append( [_BId] + self.__WholeInitDataBase[_zcId][_BId][0:2] + [-1, -1, -1] + self.__WholeInitDataBase[_zcId][_BId][2] )
                
        return _BlockInfo
        
    def loadVSettingFile( self, path ):
        "load VSetting File"
        _filetree = etree.parse( path )
#        print path
        self.calZCCBIIndex( _filetree )
        
    def loadNVSettingFile( self, path ):
        "load NVSetting File"
        _filetree = etree.parse( path )
        try:
            self.__Viom_Port_dic = self.calVIOMPorts( _filetree )
        except:
            self.__Viom_Port_dic = None
#        print "loadNVSettingFile", self.__Viom_Port_dic
        
    def loadSRDFile( self, path ):
        "load SRD File"
        
    def loadRouteDataFile( self, path ):
        "load Route Data File"
        
        #由于这里的路径对于项目来说都是固定的,因此直接写上，但是不建议其他程序这样做，这是不对的！！！
        _filetree = etree.parse( path )
        
        #获取当前文件的ZC_ID
        _ZC_ID = self.getZCID( _filetree, self.FileParser["ZC_ID"] )
#        print _ZC_ID, type( _ZC_ID )
#        self.__WholeInitDataBase[_ZC_ID] = {}
        
        #获取Block信息
        self.__WholeInitDataBase[_ZC_ID] = self.getBlockListInfo( _filetree, _ZC_ID )
        
        #获取Block CBI 对应关系
        self.__BlockIdToCBIIdDic[_ZC_ID] = self.getBlockToCBIInfo( _filetree, _ZC_ID )
        
#        print self.__BlockIdToCBIIdDic
        
    #----------------------------------------------
    #获取__WholeInitDataBase中定义的block的所有信息
    #----------------------------------------------
    def getBlockToCBIInfo( self, filetree, sectionId ):
        "get block list information"
        _blockToCBIInfoDic = {}    #{BlockId:CBIId}
        #获取所有的block的根节点
        _blockcbiParserDic = self.FileParser["BlockCbi"]
        _blockNodeList = filetree.xpath( _blockcbiParserDic["path"] )
        
        for _blockNode in _blockNodeList:
#            print _blockNode.xpath( "Id" )
            _blockId = int( _blockNode.xpath( _blockcbiParserDic["subNode"]["Id"] )[0].text )
#            print _blockId
            _blockToCBIInfoDic[_blockId] = int( _blockNode.xpath( _blockcbiParserDic["subNode"]["CBI_id"] )[0].text )
        
        return _blockToCBIInfoDic

    #----------------------------------------------
    #获取__WholeInitDataBase中定义的block的所有信息
    #----------------------------------------------
    def getBlockListInfo( self, filetree, sectionId ):
        "get block list information"
        _blockInfoDic = {}
        #获取所有的block的根节点
        _blockParserDic = self.FileParser["Block"]
        _blockNodeList = filetree.xpath( _blockParserDic["path"] )
        
        for _blockNode in _blockNodeList:
#            print _blockNode.xpath( "Id" )
            _blockId = int( _blockNode.xpath( _blockParserDic["subNode"]["Id"] )[0].text )
#            print _blockId
            _blockInfoDic[_blockId] = []
            _length = int( float( _blockNode.xpath( _blockParserDic["subNode"]["Length"] )[0].text ) * 1000 )
            _blockInfoDic[_blockId].append( _length )
            _blockInfoDic[_blockId].append( sectionId )
            _blockInfoDic[_blockId].append( self.getNextBlockInfoList( _blockNode ) )
            _Beacon, BMBeacon = self.getBeaconAndBMBeaconInfoList( _blockNode, _blockId )
            _blockInfoDic[_blockId].append( _Beacon )
            _blockInfoDic[_blockId].append( BMBeacon )
            _singsInfo = {}
            _singsInfo["Protection_Zone"] = self.getProtectZoneSingsInfo( _blockNode )
            self.getSignalSingsInfo( _blockNode, _singsInfo )
            _singsInfo["SSA"] = self.getSSASingsInfo( _blockNode )
            _psdInfo = self.getPSDSingsInfo( _blockNode, _singsInfo )
            
            _blockInfoDic[_blockId].append( _singsInfo )
            _blockInfoDic[_blockId].append( _psdInfo )
#        print _blockInfoDic
        return _blockInfoDic
    
    
    def getProtectZoneSingsInfo( self, node ):
        "get Protect zone sings information"
        _protectZoneList = []
        _protectionZoneParserDic = self.FileParser["Block"]["subNode"]["ProtectionZone"]
        
        #先查看这个block里面是否有protection zone的信息
        _PZNodeList = node.xpath( _protectionZoneParserDic["path"] )
        
        for _pz in _PZNodeList:
            _type = 2
            self.__PZId += 1
            _id = self.__PZId
            _abs = int( float( _pz.xpath( _protectionZoneParserDic["abscissa"] )[0].text ) * 1000 )
            _length = int( float( _pz.xpath( _protectionZoneParserDic["Length"] )[0].text ) * 1000 )
            _variantInfo = self.getVariantInfo( _pz )
            
            _protectZoneList.append( [_type,
                                      _id,
                                      _abs,
                                      0,
                                      0,
                                      _variantInfo[0],
                                      0, #方向现在还不知道怎么获取，这里暂时设置为-1
                                      _variantInfo[1]] )
            _protectZoneList.append( [_type,
                                      _id,
                                      _length,
                                      0,
                                      0,
                                      _variantInfo[0],
                                      1, #方向现在还不知道怎么获取，这里暂时设置为-1
                                      _variantInfo[1]] )
            
            #获取奇点信息
            #[type,id,abs,pre_computed_energy[0],pre_computed_energy[1],attribute,orientation,section_id]
            
        return _protectZoneList
    
    def getSSASingsInfo( self, node ):
        "get ssa sings information"
        _SSAList = []
        _SSAParserDic = self.FileParser["Block"]["subNode"]["SSA"]
        
        #先查看这个block里面是否有SSA的信息
        _SSANodeList = node.xpath( _SSAParserDic["path"] )
        
        for _ssa in _SSANodeList:
            _type = 16
            _id = int( _ssa.xpath( _SSAParserDic["Id"] )[0].text )
            _abs = int( float( _ssa.xpath( _SSAParserDic["abscissa"] )[0].text ) * 1000 )
            _length = int( float( _ssa.xpath( _SSAParserDic["Length"] )[0].text ) * 1000 )
            
            #有两个方向的，一个上行，一个下行,后续还需要考虑SSA在多个block上面的情况，
            #这里暂时不考虑后续需要添加这个功能
            #上行的
            _SSAList.append( [_type,
                              _id,
                              _abs,
                              0,
                              0,
                              _id,
                              0,
                              - 1] )
            #下行
            _SSAList.append( [_type,
                              _id,
                              _length,
                              0,
                              0,
                              _id,
                              1,
                              - 1] )
            #获取奇点信息
            #[type,id,abs,pre_computed_energy[0],pre_computed_energy[1],attribute,orientation,section_id]
            
        return _SSAList    
    
    def getPSDInfoById( self, PsdId ):
        "get PSD Info By Id"
        for _PSD in self.getPsds():
            if PsdId == _PSD[0]:
                return _PSD
    
    #---------------------------------------------------
    #用于获取PSD的奇数点信息以及PSD的其他信息
    #---------------------------------------------------
    def getPSDSingsInfo( self, node, singsDic ):
        "get PSD sings information"
        _PSDList = []  #[PSDID,Side,SectionID,VariantRank]
        _PSDParserDic = self.FileParser["Block"]["subNode"]["PSD"]
        
        singsDic["PSD"] = []
        
        #先查看这个block里面是否有protection zone的信息
        _PSDNodeList = node.xpath( _PSDParserDic["path"] )
        
        for _psd in _PSDNodeList:
            _platformList = _psd.xpath( _PSDParserDic["Platform"]["path"] )
            for _platform in _platformList:
#            _platform = _psd.xpath( _PSDParserDic["Platform"]["path"] )[0]
                _id = int( _platform.xpath( _PSDParserDic["Platform"]["Id"] )[0].text )
                _Side = self.__SideDic[_platform.xpath( _PSDParserDic["Platform"]["Side"] )[0].text] 
                
                _abs = int( float( _psd.xpath( _PSDParserDic["abscissa"] )[0].text ) * 1000 )
                _length = int( float( _psd.xpath( _PSDParserDic["Length"] )[0].text ) * 1000 )
                _variantInfo = self.getVariantInfo( _psd )
                
                singsDic["PSD"].append( [12,
                                         _id,
                                         _abs,
                                         0,
                                         0,
                                         _Side,
                                         0,
                                         _variantInfo[1]] )
                
                singsDic["PSD"].append( [12,
                                         _id,
                                         _length,
                                         0,
                                         0,
                                         _Side,
                                         1,
                                         _variantInfo[1]] )
                
                if _id not in self.__PSDIdList:
                    _PSDList.append( [_id, _Side, _variantInfo[1], _variantInfo[0]] )
            #获取奇点信息
            #[type,id,abs,pre_computed_energy[0],pre_computed_energy[1],attribute,orientation,section_id]
            
        return _PSDList

    #------------------------------------------------------------------------------------------
    #这里信号机有一下几种类型
    #"SIGNAL" 普通类型：在ZC_area/Block/Signal不存在Overlap子标签并且不存在Block_mode子标签
    #"SIGNAL_BM_INIT"： 在ZC_area/Block/Signal标签中不存在Overlap子标签并且存在Block_mode子标签
    #"SIGNAL_OVERLAP"： 在ZC_area/Block/Signal标签中存在Overlap子标签并且不存在Block_mode子标签
    #"SIGNAL_OVERLAP_BM"：在ZC_area/Block/Signal标签中存在Overlap子标签并且存在Block_mode子标签
    #"OVERLAP_END"：这个在ZC_area/Block/Overlap_end中获取相关信息,这个暂时不处理
    #-----------------------------------------------------------------------------------------
    def getSignalSingsInfo( self, node, singsDic ):
        "get signal sings infomation"
        _signalParserDic = self.FileParser["Block"]["subNode"]["Signal"]
        
        _signalNodeList = node.xpath( _signalParserDic["path"] )
        
        #给singsDic赋初始值
        singsDic["SIGNAL"] = []
        singsDic["SIGNAL_BM_INIT"] = []
        singsDic["SIGNAL_OVERLAP"] = []
        singsDic["SIGNAL_OVERLAP_BM"] = []

        for _node in _signalNodeList:
            self.__SignalId += 1
            _id = self.__SignalId
            _abs = int( float( _node.xpath( _signalParserDic["abscissa"] )[0].text ) * 1000 )
            _variantInfo = self.getVariantInfo( _node )
            _dir = self.__DirectionDic[_node.xpath( _signalParserDic["Direction"] )[0].text]
            
            #获取BM和overlap标签
            _BM_mode_Flag = False
            _OverLap_Flag = False
            if 0 != len( _node.xpath( _signalParserDic["Block_mode"] ) ):
                _BM_mode_Flag = True
            if 0 != len( _node.xpath( _signalParserDic["Overlap"] ) ):
                _OverLap_Flag = True
            
            if ( not _BM_mode_Flag ) and ( not _OverLap_Flag ): #普通Signal
                singsDic["SIGNAL"].append( [6,
                                            _id,
                                            _abs,
                                            0,
                                            0,
                                            _variantInfo[0],
                                            _dir,
                                            _variantInfo[1]] )
            elif not _BM_mode_Flag: #SIGNAL_OVERLAP
                singsDic["SIGNAL_OVERLAP"].append( [8,
                                                    _id,
                                                    _abs,
                                                    0,
                                                    0,
                                                    _variantInfo[0],
                                                    _dir,
                                                    _variantInfo[1]] ) 
            elif not _OverLap_Flag: #SIGNAL_BM_INIT
                singsDic["SIGNAL_BM_INIT"].append( [7,
                                                    _id,
                                                    _abs,
                                                    0,
                                                    0,
                                                    _variantInfo[0],
                                                    _dir,
                                                    _variantInfo[1]] )                 
            else: #SIGNAL_OVERLAP_BM
                singsDic["SIGNAL_BM_INIT"].append( [9,
                                                    _id,
                                                    _abs,
                                                    0,
                                                    0,
                                                    _variantInfo[0],
                                                    _dir,
                                                    _variantInfo[1]] )                 
            
    
    def getBeaconAndBMBeaconInfoList( self, Node, blockId ):
        "get Beacon And BM Beacon Information list"
        _BeaconInfoList = []    #[[id,type,b_id,abscissa,dir],...]
        _BMBeaconInfoList = []  #[[id,direction,VARnumber,VARSectionID_0,VariantRank_0,ValidityTime_0,…,VARSectionID_15,VariantRank_15,ValidityTime_15],...]
        
        _beaconParserDic = self.FileParser["Block"]["subNode"]["Beacon"]
        #先获取Beacon信息
        _beaconNodeList = Node.xpath( _beaconParserDic["path"] )
        
        for _node in _beaconNodeList:
            _Id = int( _node.xpath( _beaconParserDic["Id"] )[0].text )
            _Abscissa = int( float( _node.xpath( _beaconParserDic["Abscissa"] )[0].text ) * 1000 )
            
            _BMInfo = self.getBMVariantInfoList( _node )
            if None != _BMInfo:
                _BeaconInfoList.append( [_Id, 4, blockId, _Abscissa, _BMInfo[0]] ) #type = 4,dir = -1
                _BMBeaconInfoList .append( [_Id] + _BMInfo )
            else:
                _BeaconInfoList.append( [_Id, 3, blockId, _Abscissa, -1] ) #type = 3,dir = -1
                
        return _BeaconInfoList, _BMBeaconInfoList
        
    #---------------------------------------------------------------------------------
    #获取BM信标的变量信息状态，当该信标为BM信标时返回列表：
    #[direction,VARnumber,VARSectionID_0,VariantRank_0,ValidityTime_0,...,VARSectionID_15,VariantRank_15,ValidityTime_15]
    #反之返回None
    #---------------------------------------------------------------------------------
    def getBMVariantInfoList( self, node ):
        "get BM Variant Information List"
        _BMbeaconParserDic = self.FileParser["Block"]["subNode"]["Beacon"]["BMBeacon"]
        _retList = []
        
        #判断是否是BM信标
        try:
#            print node, _BMbeaconParserDic["direction"]
            _direction = node.xpath( _BMbeaconParserDic["direction"] )[0].text
#            print _direction, len( _direction )
        except IndexError, e:
            return None
            
        _variantInfo = self.getBMModeVariant( node )
        _tmpList = [-1, -1, -1] * 16
        for _index in _variantInfo:
            _tmpList[( _index - 1 ) * 3 ] = _variantInfo[_index][0]
            _tmpList[( _index - 1 ) * 3 + 1] = _variantInfo[_index][1]
            _tmpList[( _index - 1 ) * 3 + 2] = _variantInfo[_index][2]
                            
        if "Up" == _direction: #0表示up方向
            _retList.append( 0 )
                
        elif "Down" == _direction: #1表示down方向
            _retList.append( 1 )
                
        else:
            print "getBMVariantInfoList Error:", _direction
            return None
            
        _retList.append( max( _variantInfo.keys() ) ) #不能用长度，因为里面可能有跳跃的点
        _retList += _tmpList
#        print _retList
        return _retList

    
    #---------------------------------------------
    #返回BM信标中每个索引值的变量代表的变量的{index:[sectionID,VariantRank,validateTime]}
    #---------------------------------------------
    def getBMModeVariant( self, node ):
        "get BM mode variant"
        _retDic = {}
        _BMbeaconParserDic = self.FileParser["Block"]["subNode"]["Beacon"]["BMBeacon"]
        
        _BMVariantNodeList = node.xpath( _BMbeaconParserDic["BMVariant"]["path"] )
        
        for _variant in _BMVariantNodeList:
#            print _variant, _variant.xpath( _BMbeaconParserDic["BMVariant"]["Index"] )
            _index = int( _variant.xpath( _BMbeaconParserDic["BMVariant"]["Index"] )[0].text )
            
            _varaintinfo = self.getVariantInfo( _variant )
            
            if None == _varaintinfo:
                print "getBMModeVariant error!"
                return None
            else:
                _retDic[_index] = [_varaintinfo[1], _varaintinfo[0], 1175] #time设置成1175
        
        
        return _retDic
        
    def getNextBlockInfoList( self, blockNode ):
        "get Next block information list"
        #[nun,nunidx,nunSecid,nur,nuridx,nurSecid,ndn,ndnidx,ndnSecid,ndr,ndridx,ndrSecid]
        _NextBlockInfoList = []
        
        #存储当前的block下面的Next Block信息
        _UpBlockInfoList = []
        _DownBlockInfoList = []
        
        _NextBlockNodeList = blockNode.xpath( self.FileParser["Block"]["subNode"]["Next_block"]["path"] )
        
        for _node in _NextBlockNodeList:
            _id = int( _node.xpath( self.FileParser["Block"]["subNode"]["Next_block"]["Id"] )[0].text )
            _direction = _node.xpath( self.FileParser["Block"]["subNode"]["Next_block"]["Direction"] )[0].text
            if "Up" == _direction:
                _tmpVariantInfo = self.getVariantInfo( _node )
                if None != _tmpVariantInfo:
                    _UpBlockInfoList.append( [_id] + _tmpVariantInfo )
                else:
                    _UpBlockInfoList.append( [_id, -1, -1] )
                    
            elif "Down" == _direction:
                _tmpVariantInfo = self.getVariantInfo( _node )
                if None != _tmpVariantInfo:
                    _DownBlockInfoList.append( [_id] + _tmpVariantInfo )
                else:
                    _DownBlockInfoList.append( [_id, -1, -1] )                              
            else:
                print "getNextBlockInfoList Error direction:", _direction
                return None
            
        #整合Next block Info
        if 0 == len( _UpBlockInfoList ):
            _NextBlockInfoList = [-1, -1, -1, -1, -1, -1]

        elif 1 == len( _UpBlockInfoList ):
            _NextBlockInfoList = _UpBlockInfoList[0] + [ -1, -1, -1]       
        
        elif 2 == len( _UpBlockInfoList ):
            _NextBlockInfoList = _UpBlockInfoList[0] + _UpBlockInfoList[1]
        
        else:
            print "getNextBlockInfoList Error _UpBlockInfoList:", _UpBlockInfoList
            return None
        
        if 0 == len( _DownBlockInfoList ):
            _NextBlockInfoList += [-1, -1, -1, -1, -1, -1]

        elif 1 == len( _DownBlockInfoList ):
            _NextBlockInfoList += _DownBlockInfoList[0] + [ -1, -1, -1]       
        
        elif 2 == len( _DownBlockInfoList ):
            _NextBlockInfoList += _DownBlockInfoList[0] + _DownBlockInfoList[1]
        
        else:
            print "getNextBlockInfoList Error _DownBlockInfoList:", _DownBlockInfoList
            return None        
        
#        print _NextBlockInfoList
        return _NextBlockInfoList
        
    #-----------------------------------------------------------------
    #当在节点下存在variant的时候，将返回一个列表：[index,lineSectionId]
    #反之，返回None
    #-----------------------------------------------------------------
    def getVariantInfo( self, Node ):
        "get variant index"
        _variantNodeList = Node.xpath( variantParser["path"] )
        
        if 0 == len( _variantNodeList ):
            return None
        else:
            _lineSectionId = int( _variantNodeList[0].xpath( variantParser["sectionId"] )[0].text )
            _index = int( _variantNodeList[0].xpath( variantParser["Index"] )[0].text )
            return [_index, _lineSectionId]
        
    #-----------------------------------------------------------------
    #当在节点下存在CBIvariant的时候，将返回一个列表：[index,CBI_ID]
    #反之，返回None
    #-----------------------------------------------------------------
    def getCBIVariantInfo( self, Node ):
        "get CBI Variant index"
        _CBIVariantNodeList = Node.xpath( CBIVariantParser["path"] )
        
        if 0 == len( _CBIVariantNodeList ):
            return None
        else:
            _CBI_Id = int( _CBIVariantNodeList[0].xpath( CBIVariantParser["CBI_id"] )[0].text )
            _index = int( _CBIVariantNodeList[0].xpath( CBIVariantParser["Index_on_CBI"] )[0].text )
            return [_index, _CBI_Id]
    
    def getZCID( self, pathNode, pathString ):
        "get ZC ID"
        _tmpNode = pathNode.xpath( pathString )[0]
        return int( _tmpNode.text )

if __name__ == '__main__':
    CCdata = CCDataBaseXmlParser()
    CCdata.loadXMLFile( r"../Bcode_CC_OFFLINE_VN_Build20111223/原始地图" )
    print CCdata.getBlocks()
#    print CCdata.getZCToCBIDic()
#    print CCdata.getCBIToZCDic()
#    print CCdata.getZCVariantDicInfo()
#    print CCdata.getCBIVariantDicInfo()
#    print CCdata.getBMBeaconVariantDicInfo()
    print CCdata.getCBIToZCDic()
