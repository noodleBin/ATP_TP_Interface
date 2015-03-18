#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     databaseparse.py
# Description:  解析项目数据文件   
# Author:       OUYANG Min
# Version:      0.0.3
# Created:      date
# Company:      CASCO
# LastChange:   2011-04-06 创建文件
# History: 
# update：2011-07-20
#更新了返回的距离单位 统一为 毫米  
# update：2011-09-14
# 现在偏移将根据文件读取，不是固定不变的，add by xiongkunpeng  
#----------------------------------------------------------------------------

import types
from xmlparser import XmlParser 
import struct
import os

#format 用于表示返回列表的格式，S-字符串,N-数字,SL-字符串列表,NL字符串列表
BJFS_DB = {'Lines':{'Line':{'path':'.//Lines/Line',
                            'atr':['Name', 'ID']
                            },
                    'format':['S', 'N']
                    },
            'Depots':{'Depot':{'path':'.//Depots/Depot',
                                'atr':['Name', 'ID']},
                      'Line_ID':{'path':'.//Line_ID',
                                'atr':[]},
                      'Track_ID_List':{'path':'.//Track_ID_List',
                                        'atr':[]},
                      'format':['S', 'N', 'N', 'NL']
                    },
            'Mainlines':{'Mainline':{'path':'.//Mainlines/Mainline',
                                     'atr':['Name', 'ID']},
                        'Line_ID':{'path':'.//Line_ID',
                                    'atr':[]},
                        'Track_ID_List':{'path':'.//Track_ID_List',
                                        'atr':[]},
                        'format':['S', 'N', 'N', 'NL']
                    },
            'Tracks':{'Track':{'path':'.//Tracks/Track',
                                'atr':['Name', 'ID']},
                      'Track_Type':{'path':'.//Track_Type',
                                    'atr':[]},
                      'Kp_Begin':{'path':'.//Kp_Begin',
                                  'atr':['Value']},
                      'Kp_End':{'path':'.//Kp_End',
                                'atr':['Value']},
                      'format':['s', 'N', 'S', 'N', 'N']
                      },
            'Blocks':{'Block':{'path':'.//Blocks/Block',
                                'atr':['Name', 'ID']},
                      'format':['S', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N']
                    },
            'Beacons':{'Beacon':{'path':'.//Beacons/Beacon',
                                'atr':['Name', 'ID']},
                        'Kp':{'path':'.//Kp',
                              'atr':['Value']},
                        'format':['S', 'N', 'N', 'N', 'S', 'S', 'S', 'S', 'N']
                    },
            'Points':{},
            'Switchs':{},
            'Overlaps':{},
            'Signals':{},
            'ESPs':{},
            'Stations':{},
            'Platforms':{}
        }

class DataBaseXml(XmlParser):
    """
    database xmlfile parser
    """
    
    
    def __init__(self):
        XmlParser.__init__(self)
    
    #根据返回数据类型设置数据
    def setType(self, format, data):
        _r = data
        for _i, _d in enumerate(format):
            if _d == 'N':
                _r[_i] = int(_r[_i])
            elif _d == 'NL':
                _r[_i] = [int(rr) for rr in _r[_i]]
        return _r
                

    
    # 把元素加到一个列表中
    def addList(self, *item):
        "add item into list"
        _r = []
        for _i in item:
            if type(_i) == types.ListType:
                _r += _i
            else:
                _r += [_i]
        return _r

    def getLines(self):
        "get lines list (line_name, line_id)"
        return [self.setType(BJFS_DB['Lines']['format'], _d) \
                for _d in self.getAttrListManyElement(BJFS_DB['Lines']['Line']['path'], BJFS_DB['Lines']['Line']['atr'])]
    
    def getDepots(self):
        "get depots trackList (depot_name, depot_id, line_id, trackList)"
        _depots = []
        _curDic = BJFS_DB['Depots']
        _node = self.getElementByName(_curDic['Depot']['path']) 
        #depot_name depot_id
        _depot = self.getAttrListOneNode(_node, _curDic['Depot']['atr'])  
        #print '_depot ', _depot
        _lineNode = self.getNodeInNode(_node, _curDic['Line_ID']['path'])
        _line_id = self.getNodeText(_lineNode)
        #print '_line_id ', _line_id
        _trackNode = self.getNodeInNode(_node, _curDic['Track_ID_List']['path'])
        _trackList = self.getTextListNode(_trackNode)
        #print '_trackList ', _trackList
        _depots.append(self.setType(_curDic['format'], _depot + [_line_id] + [_trackList]))
        return _depots
    
    def getMainlines(self):
        "get mainlines trackList (mainline_name,mainline_id,line_id,trackList)"
        _mainlines = []
        _curDic = BJFS_DB['Mainlines']
        _node = self.getElementByName(_curDic['Mainline']['path'])
        #mainline_name mainline_id
        _mainline = self.getAttrListOneNode(_node, _curDic['Mainline']['atr'])  
        _lineNode = self.getNodeInNode(_node, _curDic['Line_ID']['path'])
        _line_id = self.getNodeText(_lineNode)
        _trackNode = self.getNodeInNode(_node, _curDic['Track_ID_List']['path'])
        _trackList = self.getTextListNode(_trackNode)
        _mainlines.append(self.setType(_curDic['format'], _mainline + [_line_id] + [_trackList]))
        return _mainlines
    
    def getTracks(self):
        "get trackList (track_name,track_id,track_type,kp_begin,kp_end,)"
        _tracks = []
        _curDic = BJFS_DB['Tracks']
        _node = self.getAllElementByName(_curDic['Track']['path'])
        for _n in _node:
            _trackNameId = self.getAttrListOneNode(_n, _curDic['Track']['atr']) 
            _trackType = self.getNodeText(self.getNodeInNode(_n, _curDic['Track_Type']['path']))
            _kpBV = self.getAttrListOneNode(\
                    self.getNodeInNode(_n, _curDic['Kp_Begin']['path']), _curDic['Kp_Begin']['atr'])
            _kpEV = self.getAttrListOneNode(\
                    self.getNodeInNode(_n, _curDic['Kp_End']['path']), _curDic['Kp_End']['atr'])
            _tracks.append(self.setType(_curDic['format'], self.addList(_trackNameId, _trackType, _kpBV, _kpEV)))
        return _tracks

    def getBlocks(self):
        "get blocks (block_name,block_id,track_id,sdd,point_id,kp_begin,kp_end,nun,ndn,nur,ndr)"
        #nun Next_Up_Normal_Block_ID
        #ndn Next_Down_Normal_Block_ID
        #nur Next_Up_Reverse_Block_ID
        #ndr Next_Down_Reverse_Block_ID
        _blocks = []
        _curDic = BJFS_DB['Blocks']
        _node = self.getAllElementByName(_curDic['Block']['path'])
        for _n in _node:
            _blockNameId = self.getAttrListOneNode(_n, _curDic['Block']['atr']) 
            _text = self.getTextListNode(_n)
            # 只需要_text的一部分
            _blocks.append(self.setType(_curDic['format'], _blockNameId + _text[0:9]))
        return _blocks

    def getBeacons(self):
        "get beacons (beacon_name,beacon_id,track_id,kp,type,direction,cbtc,bm,tid)"
        _beacons = []
        _curDic = BJFS_DB['Beacons']
        _nodes = self.getAllElementByName(_curDic['Beacon']['path'])
        for _n in _nodes:
            _beaconNameId = self.getAttrListOneNode(_n, _curDic['Beacon']['atr'])
            _kp = self.getAttrListOneNode(self.getNodeInNode(_n, _curDic['Kp']['path']), _curDic['Kp']['atr'])
            _text = self.getTextListNode(_n)
            #替换kp的值
            _text[1] = _kp[0]
            _beacons.append(self.setType(_curDic['format'], _beaconNameId + _text))
        return _beacons

#在atpBinary各个字段的开始位置，对应ATP代码中的struct格式和设备个数
#offset数值为atpText文件中，该设备开始的字段索引
#按照0816的数据版本修改
ATP_MAP_FILE = {'setting':{'offset':0,
        'format':'!705*2i',
        'num':1},
        'zc':{'offset':705 * 8,
            'format':'!4i',
            'num':17},
        'block':{'offset':739 * 8,
            'format':'!50i',
            'num':3001},
        'sing':{'offset':22761 * 8,
            'format':'!16i',
            'num':20001},
        'beacon':{'offset':162768 * 8,
            'format':'!18i',
            'num':7001},
        'mtib':{'offset':189777 * 8,
            'format':'!14i',
            'num':501},
        'bm_beacon':{'offset':193284 * 8,
            'format':'!102i',
            'num':501},
        'psd':{'offset':218835 * 8,
            'format':'!56i',
            'num':501}
        }

class DataTrackMap():
    """
    load atpTrackMap
    """
    #in atpTrackMap
    #distance uint ms
    #direction 0-up 1-down

    fileBin = None
    fileTxt = None

    def __init__(self):
        "init method"
        pass
     
    def loadTrackMapFile(self, fileBinName, atptxtfile):
        "open trackMap binary file"
        self.fileBin = open(fileBinName, 'rb')
        self.fileTxt = open( atptxtfile, 'r' )
        _filelines = self.fileTxt.readlines()
        #获取偏移量
        _offest = 0
        for _line in _filelines:
            if 'g_ATPSettings' in _line:
                _offest += 1
            else:
                break
        #重新计算ATP_MAP_FILE
        _fileoffset = 0
        ATP_MAP_FILE['setting']['offset'] = 0
        ATP_MAP_FILE['setting']['format'] = '!' + str(_offest * 2) + 'i'
#        print ATP_MAP_FILE['setting']['format']
        _fileoffset += struct.calcsize(ATP_MAP_FILE['setting']['format']) * \
                        ATP_MAP_FILE['setting']['num']
        #后续的format不用改，只该偏移
        ATP_MAP_FILE['zc']['offset'] = _fileoffset  
        _fileoffset += struct.calcsize(ATP_MAP_FILE['zc']['format']) * \
                        ATP_MAP_FILE['zc']['num']
        ATP_MAP_FILE['block']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize(ATP_MAP_FILE['block']['format']) * \
                        ATP_MAP_FILE['block']['num'] 
        ATP_MAP_FILE['sing']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize(ATP_MAP_FILE['sing']['format']) * \
                        ATP_MAP_FILE['sing']['num'] 
        ATP_MAP_FILE['beacon']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize(ATP_MAP_FILE['beacon']['format']) * \
                        ATP_MAP_FILE['beacon']['num'] 
        ATP_MAP_FILE['mtib']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize(ATP_MAP_FILE['mtib']['format']) * \
                        ATP_MAP_FILE['mtib']['num'] 
        ATP_MAP_FILE['bm_beacon']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize(ATP_MAP_FILE['bm_beacon']['format']) * \
                        ATP_MAP_FILE['bm_beacon']['num'] 
        ATP_MAP_FILE['psd']['offset'] = _fileoffset 
    
    def closeTrackMapFile(self):
        "close trackMap"
        self.fileBin.close()
        self.fileTxt.close()
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 根据设备类型获取atpTrackMap中的数据
    #
    # @Param dataType
    # @Param index 用于过滤数据的下标
    # @Param 过滤的关键值元组
    # @Returns 设备数据列表
    # --------------------------------------------------------------------------
    def getDeviceData(self, dataType, index, mask):
        "get device data by dataType"
        _dev = []
        if dataType in ATP_MAP_FILE:
            _offset = ATP_MAP_FILE[dataType]['offset']
            self.fileBin.seek(_offset, os.SEEK_SET)
            _cont = self.fileBin.read(ATP_MAP_FILE[dataType]['num'] * struct.calcsize(ATP_MAP_FILE[dataType]['format']))
            for _i in range(ATP_MAP_FILE[dataType]['num']):
                _of = _i * struct.calcsize(ATP_MAP_FILE[dataType]['format'])
                _d = struct.unpack(ATP_MAP_FILE[dataType]['format'], \
                        _cont[_of : _of + struct.calcsize(ATP_MAP_FILE[dataType]['format'])])
                #过滤掉签名
                _tmp = [_dd for _dd in _d if _d.index(_dd) % 2 == 0]
                #过滤无效数据
                if _tmp[index] not in mask:
                    _dev.append(_tmp)
        return _dev

    def getZCs(self):
        "get ZCs (lc_id,version)"
        #过滤LC_id为0,-1的数据
        return self.getDeviceData('zc', 0, (0, -1))
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 提取block字段特定的数据
    #
    # @Returns blocks的数据列表
    # --------------------------------------------------------------------------
    def getBlocks(self):
        "get blocks"
        #在trackMap中的原始数据(id,length,sectionId(一直为0),zcId,ATBZone,\
        #        MAXgradientACCE_up,MAXgradientACCE_down,\
        #        BlockStartGradientAccel_up,BlockStartGradientAccel_down,\
        #        Grip_up,Grip_down,\
        #        SINGindex_up,SINGindex_down,\
        #        singularity_nb,nun,nunidx,nur,\
        #        nuridx,ndn,ndnidx,ndr,ndridx)"
        #提取后返回的数据(id,length,sectionId,SINGindex_up,SINGindex_down,singularity_nb,\
        #                    nun,nunidx,nunSecid,nur,nuridx,nurSecid,ndn,ndnidx,ndnSecid,ndr,ndridx,ndrSecid)
        #nun       Next_Up_Normal_Block_ID
        #nunidx    Next_Up_Normal_Block_Variant_Index
        #ndn       Next_Down_Normal_Block_ID
        #ndnidx    Next_Down_Normal_Block_Variant_Index
        #nur       Next_Up_Reverse_Block_ID
        #nuridx    Next_Up_Reverse_Block_Variant_Index
        #ndr       Next_Down_Reverse_Block_ID
        #ndridx    Next_Down_Reverse_Block_Variant_Index
        #过滤length为0,-1的数据
        #length为毫米
        return [[_d[0], _d[1], 0, _d[-15], _d[-14], _d[-13], _d[-12], _d[-11], _d[-10], _d[-9], _d[-8], _d[-7], _d[-6], _d[-5], _d[-4], _d[-3], _d[-2], _d[-1]]\
                 for _d in self.getDeviceData('block', 1, (0, -1))]

    def getSings(self):
        "get sing (type,id,abscissa,PERcomputedEnergy_up,PERcomputedEnergy_downAttribute,Attribute,Orientation,Section id)"
        #不过滤子项
        return self.getDeviceData('sing', 1, ()) 
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 提取beacon字段的特定数据
    #
    # @Returns beacon数据列表
    # --------------------------------------------------------------------------
    def getBeacons(self):
        "get Beacons"
        #原始数据(id,type,PositionToleranceID,blockid,abscissa,MTIBindex,BMbeaconIndex,BeaconID_up,BeaconID_down)"
        #返回的数据(id,type,b_id,abscissa,dir)
        #过滤id为0,-1数据
        #abscissa毫米
        _b = [ [_d[0], _d[1], _d[3], _d[4], 0] for _d in self.getDeviceData('beacon', 0, (0, -1))]
        _bm = self.getBMBeacons()
        _bmi = [_bi[0] for _bi in _bm]
        _dir = None
        for _bb in _b:
            if _bb[1] == 4:     #BM
                try:
                    _dir = _bm[_bmi.index(_bb[0])][1]                    
                except ValueError:
                    print 'can not find Beacon_id in BM_Beacons'
                if _dir is not None:
                    _bb[-1] = _dir
                else:
                    _bb[-1] = -1
            else:
                _bb[-1] = 2
        return _b

    def getMTIBs(self):
        "get MTIB (pair_id,beaconMaxdis_up,beaconMaxdis_down,beaconMindis_up,beaconMin_down,caliMax,caliMin)"
        #过滤pair_id为0,-1的数据
        return self.getDeviceData('mtib', 0, (0, -1))
    
    def getBMBeacons(self):
        "get BM_Beacons (id,direction,VARnumber,\
                VARSectionID_0,VariantRank_0,ValidityTime_0\
                ...\
                VARSectionID_15,VariantRank_15,ValidityTime_15\
                )"
        #过滤id为0,-1的数据
        return self.getDeviceData('bm_beacon', 0, (0, -1))
    
    def getPsds(self):
        "get psds (PSDID,\
    Side,\
    NUMERIC_32 SectionID;\
    NUMERIC_32 VariantRank;\
    NUMERIC_32 ManageTypeID;\
    NUMERIC_32 SubsystemTypeID;\
    NUMERIC_32 SubsystemID;\
    NUMERIC_32 LOGID;\
    NUMERIC_32 DoorOpeningCode;\
    NUMERIC_32 DoorClosingCode;\
    NUMERIC_32 DoorNoActionCode;\
    \
    /* FSFB2_LOCAL */\
    NUMERIC_32 FLapplicationAddress;\
    NUMERIC_32 FLSourceIDchannel1;\
    NUMERIC_32 FLSourceIDchannel2;\
    NUMERIC_32 FLsequINITconsChannel1;\
    NUMERIC_32 FLsequINITconsChannel2;\
    NUMERIC_32 FLdataverChannel1;\
    NUMERIC_32 FLdataverChannel2;\
    NUMERIC_32 FLdataverNUM;\
    \
    /* FSFB2_REMOTE */\
    NUMERIC_32 FRapplicationAddress;\
    NUMERIC_32 FR_subnet_address;\
    NUMERIC_32 FRsourceIDchannel1;\
    NUMERIC_32 FRsourceIDchannel2;\
    NUMERIC_32 FRsequINITconsChannel1;\
    NUMERIC_32 FRsequINITconsChannel2;\
    NUMERIC_32 FRdataverChannel1;\
    NUMERIC_32 FRdataverChannel2;\
    NUMERIC_32 FRdataverNUM;)"\
        #过滤psdid为0,-1的数据
        return self.getDeviceData('psd', 0, (0, -1)) 
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 显示BM_Beacons的信息
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def displayBMBeacons(self):
        print 'BM_Beacons info'
        for _b in self.getBMBeacons():
            print _b

#在ccnvBinary各个字段的开始位置，对应ccnv代码中的struct格式和设备个数
#offset数值为ccnvText文件中，该设备开始的字段索引
#offset在程序中计算，这里CCNV的部分是没有签名的
CCNV_MAP_FILE = {'setting':{'offset':0,
        'format':'!705*2i',
        'num':1},
        'zc':{'offset':0,
            'format':'!2i',
            'num':17},
        'block':{'offset':0,
            'format':'!25i',
            'num':3001},
        'sing':{'offset':0,
            'format':'!8i',
            'num':20001},
        'beacon':{'offset':0,
            'format':'!9i',
            'num':7001},
        'mtib':{'offset':0,
            'format':'!7i',
            'num':501},
        'bm_beacon':{'offset':0,
            'format':'!51i',
            'num':501},
        'psd':{'offset':0,
            'format':'!28i',
            'num':501},
        'ssa':{'offset':0,
            'format':'!7i',
            'num':101},
        'ssp':{'offset':0,
            'format':'!4i',
            'num':501},
        'vpez':{'offset':0,
            'format':'!4i',
            'num':101},
        'signals':{'offset':0,
            'format':'!2i',
            'num':1001}
        }


class DataCCNVTrackMap():
    """
    load ccnvTrackMap
    """
    #in ccnvTrackMap
    #distance uint ms
    #direction 0-up 1-down

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

    fileBin = None
    fileTxt = None
    filelines = None

    def __init__( self ):
        "init method"
        pass
     
    def loadTrackMapFile( self, fileBinName, atptxtfile ):
        "open trackMap binary file"
        self.fileBin = open( fileBinName, 'rb' )
        self.fileTxt = open( atptxtfile, 'r' )
        self.filelines = self.fileTxt.readlines()
        #获取偏移量
        _offest = 0
        for _line in self.filelines:
            if 'g_ATPSettings' in _line:
                _offest += 1
            else:
                break
        #重新计算ATP_MAP_FILE
        _fileoffset = 0
        CCNV_MAP_FILE['setting']['offset'] = 0
        CCNV_MAP_FILE['setting']['format'] = '!' + str( _offest ) + 'i'
#        print ATP_MAP_FILE['setting']['format']
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['setting']['format'] ) * \
                        CCNV_MAP_FILE['setting']['num']
#        print _fileoffset, _offest
        #后续的format不用改，只该偏移
        CCNV_MAP_FILE['zc']['offset'] = _fileoffset  
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['zc']['format'] ) * \
                        CCNV_MAP_FILE['zc']['num']
        CCNV_MAP_FILE['block']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['block']['format'] ) * \
                        CCNV_MAP_FILE['block']['num'] 
        CCNV_MAP_FILE['sing']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['sing']['format'] ) * \
                        CCNV_MAP_FILE['sing']['num'] 
        CCNV_MAP_FILE['beacon']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['beacon']['format'] ) * \
                        CCNV_MAP_FILE['beacon']['num'] 
        CCNV_MAP_FILE['mtib']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['mtib']['format'] ) * \
                        CCNV_MAP_FILE['mtib']['num'] 
        CCNV_MAP_FILE['bm_beacon']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['bm_beacon']['format'] ) * \
                        CCNV_MAP_FILE['bm_beacon']['num'] 
        CCNV_MAP_FILE['psd']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['psd']['format'] ) * \
                        CCNV_MAP_FILE['psd']['num'] 
        CCNV_MAP_FILE['ssa']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['ssa']['format'] ) * \
                        CCNV_MAP_FILE['ssa']['num'] 
        CCNV_MAP_FILE['ssp']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['ssp']['format'] ) * \
                        CCNV_MAP_FILE['ssp']['num'] 
        CCNV_MAP_FILE['vpez']['offset'] = _fileoffset 
        _fileoffset += struct.calcsize( CCNV_MAP_FILE['vpez']['format'] ) * \
                        CCNV_MAP_FILE['vpez']['num'] 
        CCNV_MAP_FILE['signals']['offset'] = _fileoffset
        
#        print CCNV_MAP_FILE

        
    def closeTrackMapFile( self ):
        "close trackMap"
        self.fileBin.close()
        self.fileTxt.close()
        self.filelines = None
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 根据设备类型获取atpTrackMap中的数据
    #
    # @Param dataType
    # @Param index 用于过滤数据的下标
    # @Param 过滤的关键值元组
    # @Returns 设备数据列表
    # --------------------------------------------------------------------------
    def getDeviceData( self, dataType, index, mask ):
        "get device data by dataType"
        _dev = []
        if dataType in CCNV_MAP_FILE:
            _offset = CCNV_MAP_FILE[dataType]['offset']
            self.fileBin.seek( _offset, os.SEEK_SET )
            _cont = self.fileBin.read( CCNV_MAP_FILE[dataType]['num'] * struct.calcsize( CCNV_MAP_FILE[dataType]['format'] ) )
            for _i in range( CCNV_MAP_FILE[dataType]['num'] ):
                _of = _i * struct.calcsize( CCNV_MAP_FILE[dataType]['format'] )
                _d = struct.unpack( CCNV_MAP_FILE[dataType]['format'], \
                        _cont[_of : _of + struct.calcsize( CCNV_MAP_FILE[dataType]['format'] )] )
                #CCNV不需要过滤签名
#                _tmp = [_dd for _dd in _d if _d.index( _dd ) % 2 == 0]
                #过滤无效数据
                if _d[index] not in mask:
                    _dev.append( list( _d ) ) #里面的元素转换为list
        return _dev

    def getZCs( self ):
        "get ZCs (lc_id,version)"
        #过滤LC_id为0,-1的数据
        return self.getDeviceData( 'zc', 0, ( 0, -1 ) )
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 提取block字段特定的数据
    #
    # @Returns blocks的数据列表
    # --------------------------------------------------------------------------
    def getBlocks( self ):
        "get blocks"
        #在trackMap中的原始数据(id,length,sectionId(一直为0),zcId,ATBZone,\
        #        MAXgradientACCE_up,MAXgradientACCE_down,\
        #        BlockStartGradientAccel_up,BlockStartGradientAccel_down,\
        #        Grip_up,Grip_down,\
        #        SINGindex_up,SINGindex_down,\
        #        singularity_nb,nun,nunidx,nur,\
        #        nuridx,ndn,ndnidx,ndr,ndridx)"
        #提取后返回的数据(id,length,sectionId,SINGindex_up,SINGindex_down,singularity_nb,\
        #                    nun,nunidx,nunSecid,nur,nuridx,nurSecid,ndn,ndnidx,ndnSecid,ndr,ndridx,ndrSecid)
        #nun       Next_Up_Normal_Block_ID
        #nunidx    Next_Up_Normal_Block_Variant_Index
        #ndn       Next_Down_Normal_Block_ID
        #ndnidx    Next_Down_Normal_Block_Variant_Index
        #nur       Next_Up_Reverse_Block_ID
        #nuridx    Next_Up_Reverse_Block_Variant_Index
        #ndr       Next_Down_Reverse_Block_ID
        #ndridx    Next_Down_Reverse_Block_Variant_Index
        #过滤length为0,-1的数据
        #length为毫米
        return [[_d[0], _d[1], 0, _d[-15], _d[-14], _d[-13], _d[-12], _d[-11], _d[-10], _d[-9], _d[-8], _d[-7], _d[-6], _d[-5], _d[-4], _d[-3], _d[-2], _d[-1]]\
                 for _d in self.getDeviceData( 'block', 1, ( 0, -1 ) )]

    def getSings( self ):
        "get sing (type,id,abscissa,PERcomputedEnergy_up,PERcomputedEnergy_downAttribute,Attribute,Orientation,Section id)"
        #不过滤子项
        return self.getDeviceData( 'sing', 1, () ) 
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 提取beacon字段的特定数据
    #
    # @Returns beacon数据列表
    # --------------------------------------------------------------------------
    def getBeacons( self ):
        "get Beacons"
        #原始数据(id,type,PositionToleranceID,blockid,abscissa,MTIBindex,BMbeaconIndex,BeaconID_up,BeaconID_down)"
        #返回的数据(id,type,b_id,abscissa,dir)
        #过滤id为0,-1数据
        #abscissa毫米
        _b = [ [_d[0], _d[1], _d[3], _d[4], 0] for _d in self.getDeviceData( 'beacon', 0, ( 0, -1 ) )]
        _bm = self.getBMBeacons()
        _bmi = [_bi[0] for _bi in _bm]
        _dir = None
        for _bb in _b:
            if _bb[1] == 4:     #BM
                try:
                    _dir = _bm[_bmi.index( _bb[0] )][1]                    
                except ValueError:
                    print 'can not find Beacon_id in BM_Beacons'
                if _dir is not None:
                    _bb[-1] = _dir
                else:
                    _bb[-1] = -1
            else:
                _bb[-1] = 2
        return _b

    def getMTIBs( self ):
        "get MTIB (pair_id,beaconMaxdis_up,beaconMaxdis_down,beaconMindis_up,beaconMin_down,caliMax,caliMin)"
        #过滤pair_id为0,-1的数据
        return self.getDeviceData( 'mtib', 0, ( 0, -1 ) )
    
    def getBMBeacons( self ):
        "get BM_Beacons (id,direction,VARnumber,\
                VARSectionID_0,VariantRank_0,ValidityTime_0\
                ...\
                VARSectionID_15,VariantRank_15,ValidityTime_15\
                )"
        #过滤id为0,-1的数据
        return self.getDeviceData( 'bm_beacon', 0, ( 0, -1 ) )
    
    def getPsds( self ):
        "get psds (PSDID,\
    Side,\
    NUMERIC_32 SectionID;\
    NUMERIC_32 VariantRank;\
    NUMERIC_32 ManageTypeID;\
    NUMERIC_32 SubsystemTypeID;\
    NUMERIC_32 SubsystemID;\
    NUMERIC_32 LOGID;\
    NUMERIC_32 DoorOpeningCode;\
    NUMERIC_32 DoorClosingCode;\
    NUMERIC_32 DoorNoActionCode;\
    \
    /* FSFB2_LOCAL */\
    NUMERIC_32 FLapplicationAddress;\
    NUMERIC_32 FLSourceIDchannel1;\
    NUMERIC_32 FLSourceIDchannel2;\
    NUMERIC_32 FLsequINITconsChannel1;\
    NUMERIC_32 FLsequINITconsChannel2;\
    NUMERIC_32 FLdataverChannel1;\
    NUMERIC_32 FLdataverChannel2;\
    NUMERIC_32 FLdataverNUM;\
    \
    /* FSFB2_REMOTE */\
    NUMERIC_32 FRapplicationAddress;\
    NUMERIC_32 FR_subnet_address;\
    NUMERIC_32 FRsourceIDchannel1;\
    NUMERIC_32 FRsourceIDchannel2;\
    NUMERIC_32 FRsequINITconsChannel1;\
    NUMERIC_32 FRsequINITconsChannel2;\
    NUMERIC_32 FRdataverChannel1;\
    NUMERIC_32 FRdataverChannel2;\
    NUMERIC_32 FRdataverNUM;)"
        #过滤psdid为0,-1的数据
        return self.getDeviceData( 'psd', 0, ( 0, -1 ) ) 
    
    def getSSAs( self ):
        "get SSA (id,\
        Skip_speed,\
        ExistUpStartCondition,\
        Up_Min_free_distance_after_end,\
        ExistDownStartCondition,\
        Down_Min_free_distance_after_end,\
        ExistVPEZ)"
        #过滤ssa id为0,-1的数据
        return self.getDeviceData( "ssa", 0, ( 0, -1 ) )
    
    def getSSPs( self ):
        "get ssp (Performance_id,\
        ExistStopCondition,\
        ATBDrivingModeStopZoneLength,\
        Service_stopping_area_id)"
        #过滤Performance_id为0,-1的数据
        return self.getDeviceData( "ssp", 0, ( 0, -1 ) )    

    def getVPEZs( self ):
        "get vpez (Service_stopping_area_id,\
        DoorSide,\
        LeftPSDPlatformId,\
        RightPSDPlatformId )"
        #过滤Service_stopping_area_id为0,-1的数据
        return self.getDeviceData( "vpez", 0, ( 0, -1 ) )    

    def getSignals( self ):
        "get signals (No_driving_impact_in_block_mode,\
        Route_set_not_needed_distance)"
        #不过滤数据
        return self.getDeviceData( "signals", 0, () )    
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 显示BM_Beacons的信息
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def displayBMBeacons( self ):
        print 'BM_Beacons info'
        for _b in self.getBMBeacons():
            print _b

    #---------------------------------------------------------------------------
    #获取VIOM的各个码位端口
    #---------------------------------------------------------------------------
    def getVIOMPorts( self ):
        "get viom port"
        #返回字典列表
        _revDic = {} #保存,{'vital_in':{'portName':Index,...},...}
#        _filelines = self.fileTxt.readlines()
        
        #先获取vital的变量
        #计算ATPsetting offset
        _atpBaseOffset = 0
        for _line in self.filelines:
            if 'g_ATPSettings.VIOM' in _line:
                break
            else:
                _atpBaseOffset += 1  
                  
        _revDic['vital_in'] = {}
        for _Name in self.__rs_viomsettinglist_vital_in:
            _atpOffset = _atpBaseOffset
            for _line in self.filelines[_atpBaseOffset:]:
                if 'g_ATPSettings' in _line:
                    if _Name in _line: #找到了
#                        print '---', _Name, _atpOffset
                        self.fileBin.seek( _atpOffset * 4, os.SEEK_SET )
                        _cont = self.fileBin.read( 4 )
                        _index = struct.unpack( '!i', _cont )[0]
                        _revDic['vital_in'][_Name] = _index
                        break
                else:
                    break
                _atpOffset += 1 

        _revDic['vital_out'] = {}        
        for _Name in self.__rs_viomsettinglist_vital_out:
            _atpOffset = _atpBaseOffset
            for _line in self.filelines[_atpBaseOffset:]:
                if 'g_ATPSettings' in _line:
                    if _Name in _line: #找到了
                        self.fileBin.seek( _atpOffset * 4, os.SEEK_SET )
                        _cont = self.fileBin.read( 4 )
                        _index = struct.unpack( '!i', _cont )[0]
                        _revDic['vital_out'][_Name] = _index
                        break
                else:
                    break
                _atpOffset += 1         
        
        #计算CCNVsetting offset
        _ccnvBaseOffset = CCNV_MAP_FILE['signals']['offset'] / 4 #搜索少点
#        print CCNV_MAP_FILE['signals']['offset'] / 4
        for _line in self.filelines[CCNV_MAP_FILE['signals']['offset'] / 4:]:
            if 'g_CCNVSettings.VIOM' in _line:
                break
            else:
                _ccnvBaseOffset += 1
#        print _ccnvBaseOffset
        #获取novital的变量
        _revDic['novital_in'] = {}
        for _Name in self.__rs_viomsettinglist_novital_in:
            _ccnvOffset = _ccnvBaseOffset
            for _line in self.filelines[_ccnvBaseOffset:]:
                
                if 'g_CCNVSettings.VIOM' in _line:
#                    print '----', _Name, _ccnvOffset
                    if _Name in _line: #找到了
#                        print '----', _Name, _ccnvOffset
                        self.fileBin.seek( _ccnvOffset * 4, os.SEEK_SET )
                        _cont = self.fileBin.read( 4 )
                        _index = struct.unpack( '!i', _cont )[0]
                        _revDic['novital_in'][_Name] = _index
                        break
                else:
                    break
                _ccnvOffset += 1 

        _revDic['novital_out'] = {}
        for _Name in self.__rs_viomsettinglist_novital_out:
            _ccnvOffset = _ccnvBaseOffset
            for _line in self.filelines[_ccnvBaseOffset:]:
                if 'g_CCNVSettings.VIOM' in _line:
                    if _Name in _line: #找到了
                        self.fileBin.seek( _ccnvOffset * 4, os.SEEK_SET )
                        _cont = self.fileBin.read( 4 )
                        _index = struct.unpack( '!i', _cont )[0]
                        _revDic['novital_out'][_Name] = _index
                        break
                else:
                    break
                _ccnvOffset += 1
        
        return _revDic
    
if __name__ == '__main__':
    #x = DataBaseXml()
    #x.loadXmlFile('./datafile/BJFSL_SyDB_Chain1.xml')
    #print 'Lines ', x.getLines()
    #print 'Depots ', x.getDepots()
    #print 'Mainlines ', x.getMainlines()
    #print 'Tracks ', len(x.getTracks()), x.getTracks()
    #print 'Blocks ', len(x.getBlocks()), x.getBlocks()
    #x.closeXmlFile()
    #x.loadXmlFile('./datafile/BJFS_All_lines_Beacon_Layout_File_v1.0.5.xml')
    #print 'Beacons ', len(x.getBeacons()), x.getBeacons()
    #x.closeXmlFile()

    x = DataCCNVTrackMap()
    x.loadTrackMapFile( '../testmap/ccnvBinary.txt', '../testmap/ccnvText.txt' )
#    print CCNV_MAP_FILE
#    import time
#    print time.time()
    print x.getVIOMPorts()
#    print time.time()
    
#    print 'zc', x.getZCs()
#    print 'block', x.getBlocks()
#    print 'sing', x.getSings() 
    #print ZC_ini.LineSN_Sings
#    for _k in ZC_ini.LineSN_Sings:
#        print _k
#        _tmp = ZC_ini.LineSN_Sings[_k]
#        for _i in _tmp:
#            if _Sings[_i][0] in [2,6,7,8,12]:
#                print _Sings[_i]
#        print '\n'
             
#    print 'beacon', x.getBeacons()
#    x.displayBMBeacons()
    #print 'mtib',   x.getMTIBs()
    #print 'bm_beacon', x.getBMBeacons()
    #print 'psd', x.getPsds()
#    x.closeTrackMapFile()
