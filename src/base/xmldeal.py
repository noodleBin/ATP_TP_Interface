#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     xmldeal.py
# Description:  本模块用于读入与写各种式样的xml文件,并将之进行返回
# Author:       KUNPENG XIONG
# Version:      0.0.2
# Created:      2011-12-12
# Company:      CASCO
# LastChange:   2011-12-12
# History:      Created --- 2011-12-12
#               Modify for Edit Case 2012-03-21
#----------------------------------------------------------------------------
from xmlparser import XmlParser
from lxml import etree
import os

class XMLDeal():
    """
    import all xml for platform
    """

    #各个xml文件读取的格式字典
    FileParser = {
            'rs_xml':{'nodepath':{'expectspeed': '/speed/value',
                                  'EndPos': '/speed/EB',
                                  'viom_setting_in':'/VIOM_Settings/VIOM_IN/Item',
                                  'viom_setting_out':'/VIOM_Settings/VIOM_OUT/Item'},
                      'attributes':{'expectspeed': ['@type', '@coordinate', \
                                                    '@accelerated', '@expectCoor', \
                                                    '@expectSpeed', '@dewelltime', '@description'],
                                    'EndPos': '@Endcoordinate',
                                    'viom_setting':['@Index', '@Name', '@VIOM']
                                    }
                   },
            'defSce':{'pos':{'path':'.//Position',
                             'attr':['Block_id', 'Abscissa', 'Delay', 'Description']},
                      'set':{'path':'.//Set',
                             'attr':['Name', 'Value']},
                      'time':{'path':'.//Time',
                              'attr':['Loophour', 'Description']}
                   },
            'Msg_xml':{'mesagge':{'msgSet':{'path':'.//Msg',
                                  'attr':['Name', 'Id', 'Pack']},
                                  'set':{'path':'.//Item',
                                         'attr':['Index', 'Format', 'Name', 'Description']}
                                  }
                       },
            'variant':{'path':'.//Var',
                       'attr':['Name', 'Type', 'IO', 'Value', 'Description']
                   },
            'zc_xml':{'variant':{'pos':{'path':'.//Position',
                                        'attr':['Block_id', 'Abscissa', 'Delay', 'Description']},
                                 'set':{'path':'.//Set',
                                        'attr':['LineScetionID', 'Index', 'Value']}
                                 },
                      'Ini_Parser':{'Ini_LineSection':r'/Ini_Config/LineSection',
                                    'Ini_Variant':r'.//Variant',
                                    'attr_LineSection':( '@ID' ),
                                    'attr_Variant':( '@Type', '@Index', '@EquipmentID', '@Value' )
                                    }   
                   },
            'ci_xml':{'variant':{'pos':{'path':'.//Position',
                                        'attr':['Block_id', 'Abscissa', 'Delay', 'Description']},
                                 'set':{'path':'.//Set',
                                        'attr':['CBI_ID', 'Index', 'Value']}
                                 },
                      'Ini_Parser':{"path":r'.//CBI',
                                    "attr":["ID", "VariantNum", "Value" ]
                                    }  
                   },
            'tsrSetting' : {'TSR_PARA':{'path':'.//TSR_PARA',
                                        'attr':'Value'}
                   },
            'beacon':{'path' : {'Beacon': '/BM_Beacon/Beacon',
                                    'Beacon_Msg': '/Beacon_Msg_Setting/Beacon_Msg',
                                    },
                      'attr' : {'Beacon': ( '@ID', '@direction', '@VARnumber' ),
                                'Variant': ( '@Index', '@Value', '@Description' ),
                                'Beacon_Msg': ( '@Beacon_ID', '@Beacon_Name', '@Disabled', '@Msg_Beacon_ID', '@Use_Default_Msg', '@Available', '@Check_Word_1', '@Check_Word_2' , '@deta_dis' )}
                      },
            'train_route': {'route':{'path':'.//Route', 'attr':['Block_List']},
                            'start':{'path':'.//Start', 'attr':['Block_id', 'Abscissa']},
                            'dire':{'path':'.//Direction', 'attr':['Value']},
                            'trainLen':{'path':'.//trainLen', 'attr':['Value']},
                            'Cog_dir':{'path':'.//Cog_dir', 'attr':['Value']}               
                            },
            'lastplatformconfig':{'MapLib':{'path':'.//MapLib', 'attr':['Path']},
                                  'CaseLib':{'path':'.//CaseLib', 'attr':['Path']},
                                  'CaseVersion':{'path':'.//CaseVersion', 'attr':['Path']},
                                  'LastMap':{'path':'.//LastMap', 'attr':['Path']},
                                  'LastConfig':{'path':'.//LastConfig', 'attr':['ENDType']}
                            },
            "BaseRule":{"Rule":{"path":".//Rule", "attr":["Name", "Type", "Value", "Des"]},
                        "Lexp":{"path":".//lexp", "attr":["Type", "Value"]},
                        "Rexp":{"path":".//rexp", "attr":["Type", "Value"]},
                        "Exp": {"path":".//exp", "attr":["Type", "Value"]}
                        },
            "CommOP":{"ReqOP":{"path":".//Op", "attr":["Name"]},
                      "PreCon":{"path":".//Precondition", "attr":["Type", "Value" , "Des"]},
                      "Result":{"path":".//Result", "attr":["Type", "Value" , "Des"]}
                        },
            "AnalysisVar":{"Const":{"path":".//Const", "attr":["Id", "Val", "Type", "Des" ]},
                           "Var":{"path":".//Var", "attr":["Id", "Val", "Type", "Des" ]}
                           },
            "autoAnalysis":{"Vars":{"path":".//Var", "attr":['Type', 'Id', 'Attr', 'Des']},
                            "Rules":{"path":".//Rules", "attr":['TC', 'Des'] },
                            "Pos":{"path":".//Pos", "attr":["Start", "End" , "Des"]},
                            "Time":{"path":".//Time", "attr":["Begin", "End" , "Des"]},
                            "OP":{"path":".//Op", "attr":["Type", "Value"]}
                            },
            'platformInfo':{'TestedProduct':{'path':'.//TestedProduct', 'attr':['Label', 'Version']}},
            'omapfigureconfig':{'Config':{'path':'.//Config', 'attr':['Name', "Description"]},
                                'FrameLabel':{'path':'.//FrameLabel', 'attr':['Name']},
                                'Data':{'path':'.//Data', 'attr':['Name', 'Maximum', 'Minimum', 'LineStyle', 'lineWidth', 'colR', 'colG', 'colB']}}
							
        }

    __rs_viomsettinglist_in = ["IN_ANCS1", "IN_ANCS2",
                               "IN_ACS1", "IN_ACS2",
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
        "init do nothing"
        pass

    #--------------------------------------
    #本函数将导入XX_message.xml的所有信息
    #--------------------------------------
    @classmethod
    def importDevMsg( cls, path ):
        "import message."
        _V_Message = [] #清空
        _msgparser = cls.FileParser['Msg_xml']['mesagge']
        _f = XmlParser()
        _f .loadXmlFile( path )
        #获得所有Msg节点
        _msgNdoe = _f.getAllElementByName( _msgparser['msgSet']['path'] )
        for _mn in _msgNdoe:
            #获Msg得属性
            _l = []
            _mna = _f.getAttrListOneNode( _mn, _msgparser['msgSet']['attr'] )
            _l.append( _mna[0] )
            _l.append( _mna[1] )
            _l.append( _mna[2] )
            
            #获得所有该Msg下Set节点的属性
            _seta = [_f.getAttrListOneNode( _set, _msgparser['set']['attr'] ) \
                    for _set in _f.getNodeListInNode( _mn, _msgparser['set']['path'] )]           
            _l.append( _seta )
            _V_Message.append( _l )

        return _V_Message
            
    #-----------------------------------------------
    #写入XX_message.xml
    #-----------------------------------------------
    @classmethod
    def ExportDevMsg( cls, path, msgData ):
        "export message."
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "Msg_Settings" )
        
        for _i, _d in enumerate( msgData ):
            _name = _d[0]
            _id = _d[1]
            _pack = _d[2]
            _list = _d[3]
            _Pos = etree.SubElement( _Root, "Msg" )
            _Pos.set( 'Name', _name )
            _Pos.set( 'Id', _id )
            _Pos.set( 'Pack', _pack )
            for _l in _list:
                _set = etree.SubElement( _Pos, "Item" )
                _set.set( 'Index', _l[0] )
                _set.set( 'Format', _l[1] ) 
                _set.set( 'Name', _l[2] )  
                _set.set( 'Description', _l[3] )         
        
        _file.write( '''
<!--Msg_Type是关键字，Msg_Id对应与消息的类型id PackType是消息打包方式"!"表示大端-->
<!-- Item Format：I是UINT32， 16I是UINT32的数组，其他表示参考Pythonv2.6.6 documentation -->
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()  

    #--------------------------------------
    #本函数将导入variant.xml的所有信息
    #--------------------------------------
    @classmethod
    def importVariant( cls, path ):
        "import variant."
        _f = XmlParser()
        #print "var path",path
        _f .loadXmlFile( path )
        #先初始化设备节点，到时候统一放到data中去
        _Variant = [] #[[Name,Type,IO,Value,Description],...]
        
        #获得所有Position节点
        _Nodes = _f.getAttrListManyElement( cls.FileParser['variant']['path'],
                                            cls.FileParser['variant']['attr'] )
        for _node in _Nodes:
            _Variant.append( _node )
            
        return _Variant
            
    #-----------------------------------------------
    #写入variant.xml
    #-----------------------------------------------
    @classmethod
    def ExportVariant( cls, path, variants ):
        "export variant."
        _file = open( path, 'w' )
        #创建XML根节点
        _Root = etree.Element( "Variables" )
        
        #写defScenario：[[blockid,Abs,dwelltime,[]]]
        for _V in variants:
            _var = etree.SubElement( _Root, "Var" )
            _var.set( 'Name', _V[0] )
            _var.set( 'Type', _V[1] )
            _var.set( 'IO', _V[2] )
            _var.set( 'Value', _V[3] )
            _var.set( 'Description', _V[4] )
        
        _String = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )           
        _file.write( '''<?xml version="1.0" encoding="utf-8"?>
<!--设备变量定义，包含该模拟设备的配置参数，重要的运行参数，应用消息中的关键值等-->
<!--变量的类型 int float  string complex-->
<!--Name是变量关键字-->
<!--complex类型的变量忽略value中赋值-->
<!--IO设置了变量的行为，Log 为每周期记录到日志-->
''' ) #保存数据

        _file.write( _String )
        _file.close()     
            
    
    
    #--------------------------------------------------------
    #@读取设备的默认变量控制脚本
    #path:文件路径
    #返回defScenario，TimeScenario两个字典,
    #数据格式为[[blockid,Abs,dwelltime,[]]]
    #      [[loophour,[]]]
    #--------------------------------------------------------
    @classmethod
    def importDefSce( self, path, ReadDes = False ):
        "import default format scenario"
        _f = XmlParser()
        _f .loadXmlFile( path )
        #先初始化设备节点，到时候统一放到data中去
        _defScenario = []
        _defScenarioDes = []
        _TimeScenario = []
        _TimeScenarioDes = []
        #获得所有Position节点
        _posNode = _f.getAllElementByName( self.FileParser['defSce']['pos']['path'] )
        for _pn in _posNode:
            #获Position得属性
            _l = []
            _pna = _f.getAttrListOneNode( _pn, self.FileParser['defSce']['pos']['attr'] )
            #_l.append([_pna[0], int(_pna[1]), int(_pna[2])])
            _l.append( _pna[0] )
            _l.append( _pna[1] )
            _l.append( _pna[2] )
            
            if _pna[3] != None:
                _defScenarioDes.append( _pna[3] )
            else:
                _defScenarioDes.append( "" )
                
            #获得所有该Position下Set节点的属性
            _seta = [_f.getAttrListOneNode( _set, self.FileParser['defSce']['set']['attr'] ) \
                    for _set in _f.getNodeListInNode( _pn, self.FileParser['defSce']['set']['path'] )]           
            _l.append( _seta )
            _defScenario.append( _l )
        
        #获得所有Time节点
        _timeNode = _f.getAllElementByName( self.FileParser['defSce']['time']['path'] )
        for _tn in _timeNode:
            #获Position得属性
            _l = []
            _pna = _f.getAttrListOneNode( _tn, self.FileParser['defSce']['time']['attr'] )
            #将loophour以及delay转化为int
            _l.append( int( _pna[0] ) )
            
            if _pna[1] != None:
                _TimeScenarioDes.append( _pna[1] )
            else:
                _TimeScenarioDes.append( "" )
                            
            #获得所有该Position下Set节点的属性
            _seta = [_f.getAttrListOneNode( _set, self.FileParser['defSce']['set']['attr'] ) \
                    for _set in _f.getNodeListInNode( _tn, self.FileParser['defSce']['set']['path'] )]           
            _l.append( _seta )
            _TimeScenario.append( _l )
        if False == ReadDes:    
            return _defScenario, _TimeScenario
        else:
            return _defScenario, _TimeScenario, _defScenarioDes, _TimeScenarioDes

    #-----------------------------------------------------
    #@将默认脚本数据写入文件中去
    #输入：path，文件路径
    #    defScenario：
    #    TimeScenario：
    #-----------------------------------------------------
    @classmethod
    def ExportDefSce( cls, path, defScenario, TimeScenario, defScenarioDes, TimeScenarioDes ):
        "export default scenario to xml"
        _file = open( path, 'w' )
        #创建XML根节点
        _Root = etree.Element( "Scenario" )
        
        #写defScenario：[[blockid,Abs,dwelltime,[]]]
        for _i, _d in enumerate( defScenario ):
            _blockid = _d[0]
            _abs = _d[1]
            _delay = _d[2]
            _list = _d[3]
            _Pos = etree.SubElement( _Root, "Position" )
            _Pos.set( 'Block_id', _blockid )
            _Pos.set( 'Abscissa', _abs )
            _Pos.set( 'Delay', _delay )
            _Pos.set( 'Description', defScenarioDes[_i] )
            for _l in _list:
                _set = etree.SubElement( _Pos, "Set" )
                _set.set( 'Name', _l[0] )
                _set.set( 'Value', _l[1] )
                
        #写TimeScenario：[[loophour,[]]]
        for _i, _T in enumerate( TimeScenario ):
            _loophour = _T[0]
            _list = _T[1]
            _Pos = etree.SubElement( _Root, "Time" )
            _Pos.set( 'Loophour', str( _loophour ) )
            _Pos.set( 'Description', TimeScenarioDes[_i] )
            for _l in _list:
                _set = etree.SubElement( _Pos, "Set" )
                _set.set( 'Name', _l[0] )
                _set.set( 'Value', _l[1] )                    
        
        _String = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )           
        _file.write( '''<?xml version="1.0" encoding="utf-8"?>
<!--该脚本定义了车辆位置和消息值的定义关系-->
<!--block中的abscissa的单位是毫米-->
<!--delay定义了该值过多少时间后变化,delay的刻度是100ms，既delay 1 代表100ms-->
<!--var必须是在var.xml中定义过的-->
''' ) #保存数据

        _file.write( _String )
        _file.close()     
    
    
    #---------------------------------------------------------------------------------
    #@读取RS与VIOM接口的配置文件以获知VIOM码位的与变量的对应关系
    #@读取的数据将存入字典data中：返回两个字典，dicin，dicout
    #@内容'VIOM_IN_Setting'：{'Name':Index,...}
    #@path:文件路径    
    #---------------------------------------------------------------------------------
    @classmethod
    def importVIOMSetting( self, path ):
        "载入VIOM接口配置信息"
        tree = etree.parse( path )
        #先读取VIOMIN的相关配置
        r = tree.xpath( self.FileParser['rs_xml']['nodepath']['viom_setting_in'] )
        _dic_in = {}
        for node in r:  
            _para_name = node.xpath( self.FileParser['rs_xml']['attributes']['viom_setting'][1] )[0]
            _para_index = int( node.xpath( self.FileParser['rs_xml']['attributes']['viom_setting'][0] )[0] )
            _para_VIOM = int( node.xpath( self.FileParser['rs_xml']['attributes']['viom_setting'][2] )[0] )
            _dic_in[_para_name] = [_para_index, _para_VIOM]
        
        #读取VIOMOUT的相关配置
        r = tree.xpath( self.FileParser['rs_xml']['nodepath']['viom_setting_out'] )
        _dic_out = {}
        for node in r:  
            _para_name = node.xpath( self.FileParser['rs_xml']['attributes']['viom_setting'][1] )[0]
            _para_index = int( node.xpath( self.FileParser['rs_xml']['attributes']['viom_setting'][0] )[0] )
            _para_VIOM = int( node.xpath( self.FileParser['rs_xml']['attributes']['viom_setting'][2] )[0] )
            _dic_out[_para_name] = [_para_index, _para_VIOM]
        
        #将结果添加到设备的__data中
        return _dic_in, _dic_out

    #------------------------------------------------------------
    #@写入rs_viom_setting.xml
    #------------------------------------------------------------
    @classmethod
    def ExportVIOMSetting( cls, path, dic_in, dic_out ):
        "Save viom setting."
        _viom_setting_file = open( path, 'w' )
        _viom_setting_file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _viom_setting = etree.Element( "VIOM_Settings" )
        
        _viom_in = etree.SubElement( _viom_setting, "VIOM_IN" )
        for _inName in cls.__rs_viomsettinglist_in:
            if dic_in.has_key( _inName ):
                _viom_in_item = etree.SubElement( _viom_in, "Item" )
                _viom_in_item.set( "Index", str( dic_in[_inName][0] ) )
                _viom_in_item.set( "Name", _inName )
                _viom_in_item.set( "VIOM", str( dic_in[_inName][1] ) )
                _viom_in_item.set( "Description", _inName )
        
        _viom_out = etree.SubElement( _viom_setting, "VIOM_OUT" )
        for _outName in cls.__rs_viomsettinglist_out:
            if dic_out.has_key( _outName ):
                _viom_out_item = etree.SubElement( _viom_out, "Item" )
                _viom_out_item.set( "Index", str( dic_out[_outName][0] ) )
                _viom_out_item.set( "Name", _outName )
                _viom_out_item.set( "VIOM", str( dic_out[_outName][1] ) )
                _viom_out_item.set( "Description", _outName )

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

    #------------------------------------------------------
    #读入train_route
    #------------------------------------------------------
    @classmethod
    def importTrainRoute( cls, path ):
        "import train route."
        _f = XmlParser()
        _f .loadXmlFile( path )
        #获得route节点的属性
        _route = _f.getAttrListOneElement( cls.FileParser['train_route']['route']['path'], \
                                           cls.FileParser['train_route']['route']['attr'] )
        _routeV = [int( _s ) for _s in _route[0].strip().split( ',' )]
    
        _start = _f.getAttrListOneElement( cls.FileParser['train_route']['start']['path'], \
                                           cls.FileParser['train_route']['start']['attr'] )
        _startV = [int( _s ) for _s in _start]
    
        _dire = _f.getAttrListOneElement( cls.FileParser['train_route']['dire']['path'], \
                                          cls.FileParser['train_route']['dire']['attr'] )
        _direV = int( _dire[0] )
        
        _trainLen = int( _f.getAttrListOneElement( cls.FileParser['train_route']['trainLen']['path'], \
                                                   cls.FileParser['train_route']['trainLen']['attr'] )[0] )
        
        _Cog_dir = int( _f.getAttrListOneElement( cls.FileParser['train_route']['Cog_dir']['path'], \
                                                  cls.FileParser['train_route']['Cog_dir']['attr'] )[0] )
        
        return _routeV, _startV, _direV, _trainLen, _Cog_dir

    #----------------------------------------------------------------
    #写入train_route
    #----------------------------------------------------------------
    @classmethod
    def ExportTrainRoute( cls, path, routeV, startV, direV, trainLen, Cog_dir ):
        "export train route."
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "Train" )
        
        _Route = etree.SubElement( _Root, "Route" )
        _routestr = ''
        for _r in routeV:
            _routestr += ',' + str( _r )
            
        _Route.set( 'Block_List', _routestr[1:] )
        
        _Start = etree.SubElement( _Root, "Start" )
        _Start.set( 'Block_id', str( startV[0] ) )
        _Start.set( 'Abscissa', str( startV[1] ) )
        
        _Cog_dir = etree.SubElement( _Root, "Cog_dir" )
        _Cog_dir.set( 'Value', str( Cog_dir ) )
        
        _trainLen = etree.SubElement( _Root, "trainLen" )
        _trainLen.set( 'Value', str( trainLen ) )
        
        _Direction = etree.SubElement( _Root, "Direction" )
        _Direction.set( 'Value', str( direV ) )

        _file.write( '''
<!--该脚本定义了车辆运行路径，运行方向，开始位置（车尾-->
<!--路径中间必须用“，”隔开-->
<!-- 1-up -1-down -->
<!-- Block_List应该与Direction方向一致 -->
<!-- trainLen单位:毫米 -->
<!--<trainLen  Value="2526"/>-->      
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()        
            
    #---------------------------------------------------------------------------------
    #@读取跑车脚本信息并存放在变量trainRunScenario中
    #@para：filePath，跑车脚本的存放路径
    #@path:文件路径   
    #返回值：trainRunScenario，_EB_EndPos
    #---------------------------------------------------------------------------------            
    @classmethod
    def importExpectSpeed( self, path, ReadDes = False ):
        "载入跑车脚本信息"
        #self.logMes(4, type(self).__name__ + '.' + sys._getframe().f_code.co_name)
        _trainRunScenario = []
        _trainRunScenarioDes = [] #与_trainRunScenario对应
        tree = etree.parse( path )
        r = tree.xpath( self.FileParser['rs_xml']['nodepath']['expectspeed'] )
        
        for node in r:   
            _list = []
            for p in self.FileParser['rs_xml']['attributes']['expectspeed']:  
                #print p
                _para = node.xpath( p ) 
                if p == '@description':
                    _trainRunScenarioDes.append( _para[0] if len( _para ) > 0 else "" )
                elif _para != []:
                    if p == '@type':
                        _list.append( int( _para[0] ) )                    
                    else:
                        _list.append( float( _para[0] ) )
            _trainRunScenario.append( _list )  
        #载入EB后的目标位置
        if len( tree.xpath( self.FileParser['rs_xml']['nodepath']['EndPos'] ) ) > 0: 
            _EB_EndPos = int( 1000.0 * float( tree.xpath( self.FileParser['rs_xml']['nodepath']['EndPos'] )[0]
                              .xpath( self.FileParser['rs_xml']['attributes']['EndPos'] )[0] ) )
        else:
            _EB_EndPos = None
        
        if False == ReadDes:    
            return _trainRunScenario, _EB_EndPos
        else:
            return _trainRunScenario, _EB_EndPos, _trainRunScenarioDes

    #-----------------------------------------------------
    #写入rs_expectSpeed
    #-----------------------------------------------------
    @classmethod
    def ExportExpectSpeed( cls, path, trainRunScenario, EB_EndPos, trainRunScenarioDes ):
        "export expect speed."
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "speed" )
        
        for _i, _trainRun in enumerate( trainRunScenario ):
            _value = etree.SubElement( _Root, "value" )
            if 0 == _trainRun[0]: #type 0
                _value.set( 'type', str( _trainRun[0] ) )
                _value.set( 'coordinate', str( _trainRun[1] ) )
                _value.set( 'accelerated', str( _trainRun[2] ) )
                _value.set( 'expectSpeed', str( _trainRun[3] ) )
            else: #type 1
                _value.set( 'type', str( _trainRun[0] ) )
                _value.set( 'coordinate', str( _trainRun[1] ) )
                _value.set( 'expectCoor', str( _trainRun[2] ) )
                _value.set( 'expectSpeed', str( _trainRun[3] ) )
                _value.set( 'dewelltime', str( _trainRun[4] ) )
            _value.set( 'description', trainRunScenarioDes[_i] )                    
        if None != EB_EndPos:
            _EB_EndPos = etree.SubElement( _Root, "EB" )
            _EB_EndPos.set( 'Endcoordinate', str( EB_EndPos / 1000 ) ) #mm转化为m
        
        _file.write( '''
<!--coordinate的单位是 m ，accelerated的单位是 m/s^2 ，expectSpeed的单位是 m/s-->
<!--每条value的顺序按照coordinate增加的顺序，否则可能会导致解析错误-->
<!--每条初始坐标与上条结束坐标相比，要留有一定裕量(expectSpeed=0除外)，这段路程默认匀速，否则也可能导致错误-->
<!--倒车数据示例：<value type='1' coordinate='当前位置坐标' expectCoor='当前位置坐标-x' expectSpeed='5'>-->
<!--dewelltime:以周期为单位，1表示100毫秒-->
<!--Endcoordinate:紧急制动之后的车辆的运行目的地-->  
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()  

    #------------------------------------------------------------------------------
    #@读入ci_variant_scenario.xml中的有关脚本信息，并存如变量V_secnario中
    #格式如下：[[BlockID,Absicssa,delay,[[CBI_ID,Index,value],...]],...]
    #@path:文件路径
    #返回该列表
    #------------------------------------------------------------------------------           
    @classmethod
    def importCIVarSce( self, path, ReadDes = False ):
        "import Variant format scenario"
        _V_Scenario = [] #清空
        _V_ScenarioDes = [] #清空
        _ciparser = self.FileParser['ci_xml']['variant']
        _f = XmlParser()
        _f .loadXmlFile( path )
        #获得所有Position节点
        _posNdoe = _f.getAllElementByName( _ciparser['pos']['path'] )
        for _pn in _posNdoe:
            #获Position得属性
            _l = []
            _pna = _f.getAttrListOneNode( _pn, _ciparser['pos']['attr'] )
            _l.append( _pna[0] )
            _l.append( _pna[1] )
            _l.append( _pna[2] )

            if _pna[3] != None:
                _V_ScenarioDes.append( _pna[3] )
            else:
                _V_ScenarioDes.append( "" )
            
            #获得所有该Position下Set节点的属性
            _seta = [_f.getAttrListOneNode( _set, _ciparser['set']['attr'] ) \
                    for _set in _f.getNodeListInNode( _pn, _ciparser['set']['path'] )]           
            _l.append( _seta )
            _V_Scenario.append( _l )
        if False == ReadDes:
            return _V_Scenario
        else:
            return _V_Scenario, _V_ScenarioDes

    #---------------------------------------------------------
    #写入ci_variant_scenario
    #---------------------------------------------------------
    @classmethod
    def ExportCIVarSce( self, path, V_Scenario, V_ScenarioDes ):
        "export zc variant scenario to xml"
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "Scenario" )
        
        for _i, _d in enumerate( V_Scenario ):
            _blockid = _d[0]
            _abs = _d[1]
            _delay = _d[2]
            _list = _d[3]
            _Pos = etree.SubElement( _Root, "Position" )
            _Pos.set( 'Block_id', _blockid )
            _Pos.set( 'Abscissa', _abs )
            _Pos.set( 'Delay', _delay )
            _Pos.set( 'Description', V_ScenarioDes[_i] )
            for _l in _list:
                _set = etree.SubElement( _Pos, "Set" )
                _set.set( 'CBI_ID', _l[0] )
                _set.set( 'Index', _l[1] ) 
                _set.set( 'Value', _l[2] )           
        
        _file.write( '''
<!--该脚本定义了车辆位置和ZC发送的variant的关系定义-->
<!--block中的abscissa的单位是毫米-->
<!--EOAdistance的value是各个variant改变后的值，取值为：0或1 -->
<!--delay定义了该值过多少时间后变化,delay的刻度是100ms，既delay 1 代表100ms-->
<!--脚本的LineScetionID和Index是用于定位variant的位置，且必须是在zc_variant_ini.xml中能过找到的-->
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()  
        
    #------------------------------------------------------------------------------
    #@读入zc_variant_scenario.xml中的有关脚本信息，并存如变量V_secnario中
    #格式如下：[[BlockID,Absicssa,delay,[[linesectionID,Index,value],...]],...]
    #@path:文件路径
    #返回该列表
    #------------------------------------------------------------------------------           
    @classmethod
    def importZCVarSce( self, path, ReadDes = False ):
        "import Variant format scenario"
        _V_Scenario = [] #清空
        _V_ScenarioDes = [] #清空
        _zcparser = self.FileParser['zc_xml']['variant']
        _f = XmlParser()
#        print "importZCVarSce", path
        _f .loadXmlFile( path )
        #获得所有Position节点
        _posNdoe = _f.getAllElementByName( _zcparser['pos']['path'] )
        for _pn in _posNdoe:
            #获Position得属性
            _l = []
            _pna = _f.getAttrListOneNode( _pn, _zcparser['pos']['attr'] )
            _l.append( _pna[0] )
            _l.append( _pna[1] )
            _l.append( _pna[2] )

            if _pna[3] != None:
                _V_ScenarioDes.append( _pna[3] )
            else:
                _V_ScenarioDes.append( "" )
            
            #获得所有该Position下Set节点的属性
            _seta = [_f.getAttrListOneNode( _set, _zcparser['set']['attr'] ) \
                    for _set in _f.getNodeListInNode( _pn, _zcparser['set']['path'] )]           
            _l.append( _seta )
            _V_Scenario.append( _l )
        if False == ReadDes:
            return _V_Scenario
        else:
            return _V_Scenario, _V_ScenarioDes

    #---------------------------------------------------------
    #写入zc_variant_scenario
    #---------------------------------------------------------
    @classmethod
    def ExportZCVarSce( self, path, V_Scenario, V_ScenarioDes ):
        "export zc variant scenario to xml"
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "Scenario" )
        
        for _i, _d in enumerate( V_Scenario ):
            _blockid = _d[0]
            _abs = _d[1]
            _delay = _d[2]
            _list = _d[3]
            _Pos = etree.SubElement( _Root, "Position" )
            _Pos.set( 'Block_id', _blockid )
            _Pos.set( 'Abscissa', _abs )
            _Pos.set( 'Delay', _delay )
            _Pos.set( 'Description', V_ScenarioDes[_i] )
            for _l in _list:
                _set = etree.SubElement( _Pos, "Set" )
                _set.set( 'LineScetionID', _l[0] )
                _set.set( 'Index', _l[1] ) 
                _set.set( 'Value', _l[2] )           
        
        _file.write( '''
<!--该脚本定义了车辆位置和ZC发送的variant的关系定义-->
<!--block中的abscissa的单位是毫米-->
<!--EOAdistance的value是各个variant改变后的值，取值为：0或1 -->
<!--delay定义了该值过多少时间后变化,delay的刻度是100ms，既delay 1 代表100ms-->
<!--脚本的LineScetionID和Index是用于定位variant的位置，且必须是在zc_variant_ini.xml中能过找到的-->
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()  


    #------------------------------------------------------------------------
    #读取ci_variant_ini.xml
    #------------------------------------------------------------------------
    @classmethod
    def importCIVariantIni( cls, path ):
        "get CI initialization variant"
        _VatiantIniDic = {} #清空
        _f = XmlParser()
        _f .loadXmlFile( path )
        #获得所有CBI节点
        _CBINode = _f.getAllElementByName( cls.FileParser['ci_xml']['Ini_Parser']['path'] )
        for _node in _CBINode:
            _attrList = _f.getAttrListOneNode( _node, cls.FileParser['ci_xml']['Ini_Parser']['attr'] )
            
            _Id = int( _attrList[0] )
            _VariantNum = int( _attrList[1] )
            _value = int( _attrList[2] )
            
            _variantList = [_value] * 512
            
            _VatiantIniDic[_Id] = [_VariantNum, _variantList]
        return _VatiantIniDic       

    #------------------------------------------------------------------------
    #读取zc_variant_ini.xml
    #------------------------------------------------------------------------
    @classmethod
    def importZCVariantIni( cls, path ):
        "get initialization variant"
        _Initree = etree.parse( path )
        _variant_dic = {}
        _variant_dic_len = {}
        _variant_dic_Num = {}
        _variant_type_EQID = {}
        for _node in _Initree.xpath( cls.FileParser['zc_xml']['Ini_Parser']['Ini_LineSection'] ):
            _ini_var_list = [0] * 224  #初始化变量
            _ini_type_EQID_list = [0] * 224 #存储type和equipmentID
            _key = -1    #LineSectionID
            #print self.Ini_Parser['Ini_LineSection']
            _para = _node.xpath( cls.FileParser['zc_xml']['Ini_Parser']['attr_LineSection'] )[0]
            _key = int( _para[0] )
            _maxIndex = -1
            _NumofVar = 0
            #解码Variant
            for _Linenode in _node.xpath( cls.FileParser['zc_xml']['Ini_Parser']['Ini_Variant'] ):
                #读取配置信息
                _para_index = int( _Linenode.xpath( "@Index" )[0] ) - 1 #从0开始
                #print _para_index
                _para_value = int( _Linenode.xpath( "@Value" )[0] )
                #将value存入对应的位置
                _ini_type_EQID_list[_para_index] = [_Linenode.xpath( "@Type" )[0],
                                                    _Linenode.xpath( "@EquipmentID" )[0]]
                _ini_var_list[_para_index] = _para_value
                _NumofVar = _NumofVar + 1
                if _maxIndex < _para_index + 1:  #取最大的长度
                    _maxIndex = _para_index + 1
            #将数据压入字典中
            _variant_dic[_key] = _ini_var_list
            _variant_dic_len[_key] = _maxIndex
            _variant_dic_Num[_key] = _NumofVar
            _variant_type_EQID[_key] = _ini_type_EQID_list
            
        return _variant_dic, _variant_dic_len, _variant_dic_Num, _variant_type_EQID
    
    #----------------------------------------------------------
    #写入zc_variant_ini.xml
    #----------------------------------------------------------
    @classmethod
    def ExportZCVariantIni( cls, path, variant_dic, variant_type_EQID ):
        "export variant ini."
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "Ini_Config" )
        
        for _line in variant_type_EQID:
            _LineSec = etree.SubElement( _Root, "LineSection" )
            _LineSec.set( 'ID', str( _line ) )
            for _i, _var in enumerate( variant_type_EQID[_line] ):
                if 0 != _var:
                    _variant = etree.SubElement( _LineSec, "Variant" )
                    _variant.set( 'Type', _var[0] )
                    _variant.set( 'Index', str( _i + 1 ) ) #index从1开始
                    _variant.set( 'EquipmentID', _var[1] )
                    _variant.set( 'Value', str( variant_dic[_line][_i] ) )
        
        _file.write( '''
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()  

        
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 加载TSR setting文件
    # @path:文件路径
    # @Returns _tsrItem or None
    # --------------------------------------------------------------------------
    @classmethod
    def importTSRSetting( self, path, ReadDes = False ):
        "import tsrsetting xml file"
        _f = XmlParser()
        _f.loadXmlFile( path )
        _tsrPaser = self.FileParser['tsrSetting']
        _tsrItem = {}
        _tsrItemDes = {}   
        for _item in _f.getAllElementByName( _tsrPaser['TSR_PARA']['path'] ):
            _tmp = []
            _key = None
            for _e in _item.iter():
                    if _e.tag != 'TSR_PARA':
                        if _e.tag == 'Index':
                            _key = int( _e.get( _tsrPaser['TSR_PARA']['attr'] ) )
                        elif  _e.tag == 'Intermediate_Block_ID_Of_TSR':
                            _route = _e.get( _tsrPaser['TSR_PARA']['attr'] )
                            if _route == '':
                                _tmp.append( [] )
                            else:
                                try:
                                    _tmp.append( [int( _s ) for _s in _route.strip().split( ',' )] )
                                except ValueError, e:
                                    print 'tsr list input error', e
                                    return None                    
                        else:
                            _tmp.append( int( _e.get( _tsrPaser['TSR_PARA']['attr'] ) ) )
            _tsrItem[_key] = _tmp
            _Des = _f.getAttrListOneNode( _item, ["Description"] )
            if _Des[0] != None:
                _tsrItemDes[_key] = _Des[0]
            else:
                _tsrItemDes[_key] = ""
            
        if False == ReadDes:
            return _tsrItem
        else:
            return _tsrItem, _tsrItemDes
    
    #---------------------------------------------------
    #写入lc_tsr_setting.xml
    #---------------------------------------------------
    @classmethod
    def ExportTSRSetting( cls, path, tsrItems, tsrItemDes ):
        "export TSR setting."
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "TSR" )
        
        for _TSR in tsrItems:
            _TsrItem = etree.SubElement( _Root, "TSR_PARA" )
            _TsrItem.set( "Description", tsrItemDes[_TSR] )
            _Index = etree.SubElement( _TsrItem, "Index" )
            _Index.set( 'Value', str( _TSR ) )
            
            _TSR_Speed = etree.SubElement( _TsrItem, "TSR_Speed" )
            _TSR_Speed.set( 'Value', str( tsrItems[_TSR][0] ) )            

            _First_Block_ID_Of_TSR = etree.SubElement( _TsrItem, "First_Block_ID_Of_TSR" )
            _First_Block_ID_Of_TSR.set( 'Value', str( tsrItems[_TSR][1] ) )
            
            _Start_Abscissa_On_First_Block_Of_TSR = etree.SubElement( _TsrItem, "Start_Abscissa_On_First_Block_Of_TSR" )
            _Start_Abscissa_On_First_Block_Of_TSR.set( 'Value', str( tsrItems[_TSR][2] ) )
            
            _Number_Of_Intermediate_Blocks_Of_TSR = etree.SubElement( _TsrItem, "Number_Of_Intermediate_Blocks_Of_TSR" )
            _Number_Of_Intermediate_Blocks_Of_TSR.set( 'Value', str( tsrItems[_TSR][3] ) )
            
            _Intermediate_Block_ID_Of_TSR = etree.SubElement( _TsrItem, "Intermediate_Block_ID_Of_TSR" )
            if len( tsrItems[_TSR][4] ) > 0:
                _Intermediate_Block_ID_Of_TSR.set( 'Value', ( repr( tsrItems[_TSR][4] )[1:-1] ) )
            else:
                _Intermediate_Block_ID_Of_TSR.set( 'Value', '' )
            
            _Last_Block_ID_Of_TSR = etree.SubElement( _TsrItem, "Last_Block_ID_Of_TSR" )
            _Last_Block_ID_Of_TSR.set( 'Value', str( tsrItems[_TSR][5] ) )
            
            _End_Abscissa_On_Last_Block_Of_TSR = etree.SubElement( _TsrItem, "End_Abscissa_On_Last_Block_Of_TSR" )
            _End_Abscissa_On_Last_Block_Of_TSR.set( 'Value', str( tsrItems[_TSR][6] ) )            
            
        _file.write( '''
<!--
该脚本定义了TSR的参数
<Index> TSR的索引 整数 从1开始
<TSR_Speed> TSR速度 整数 单位km/h
<First_Block_ID_Of_TSR> 开始Block ID
<Start_Abscissa_On_First_Block_Of_TSR> 开始坐标 整数 单位 米 quantum:0.5 
<Number_Of_Intermediate_Blocks_Of_TSR> TSR跨越的Block 整数
<Intermediate_Block_ID_Of_TSR> 跨越的block id list 用“，”隔开
<Last_Block_ID_Of_TSR> 结束Block ID
<End_Abscissa_On_Last_Block_Of_TSR> 终点坐标 整数 单位 米 quantum:0.5 
TSR的方向说明：
1）若TSR只在一个Block上面，根据坐标的大小确定方向，起点<终点 UP
2）跨越多个Block，Block Id的排列顺序确定了方向
-->        
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()  
        
                
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 加载BM beacons setting文件
    # @path:文件路径
    # @Returns _myBMBeacons
    # --------------------------------------------------------------------------
    @classmethod
    def importBMBeacons( self, path, ReadDes = False ):
        #print '>>> load_BM_Beacon'
        _BMBeacons = {}
        tree = etree.parse( path )
        _beaconpaser = self.FileParser['beacon']
        r = tree.xpath( _beaconpaser['path']['Beacon'] )
        for node in r:   
            _key = ''
            _sub_key = ''
            _list = []
            for p in _beaconpaser['attr']['Beacon']:  
                _para = node.xpath( p )                   
                if p[1:] == 'ID':
                    _key = str( _para[0] )
                else:
                    _list.append( str( _para[0] ) )
            _sec_list = []
            for subnode in node.xpath( 'Variant' ):
                _sublist = []
                for subp in _beaconpaser['attr']['Variant']:
                    if False == ReadDes and "@Description" == subp: #此情况不记录打开des
                        break
                    _para = subnode.xpath( subp )    
                    if len( _para ) == 0:    
                        _sublist.append( "" )
                    else:
                        _sublist.append( _para[0] )
                _sec_list.append( _sublist )


            _list.append( _sec_list )
            _BMBeacons[_key] = _list
        return _BMBeacons
    
    #-----------------------------------------------------------
    #写入bm_beacons.xml
    #-----------------------------------------------------------
    @classmethod
    def ExportBMBeacons( cls, path, BMBeacons ):
        "export bm beacons to xml"
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "BM_Beacon" )
        
        _bmList = []
        for _bm in BMBeacons:
            _bmList.append( _bm )
        _bmList.sort()
        for _bm in _bmList:
            _bmbeacon = etree.SubElement( _Root, "Beacon" )
            _bmbeacon.set( 'ID', _bm )
            _bmbeacon.set( 'direction', BMBeacons[_bm][0] )
            _bmbeacon.set( 'VARnumber', BMBeacons[_bm][1] )
            for _var in BMBeacons[_bm][2]:
                _variant = etree.SubElement( _bmbeacon, "Variant" )
                _variant.set( 'Index', _var[0] )
                _variant.set( 'Value', _var[1] )
#                print BMBeaconsDes[_bm]
                _variant.set( 'Description', _var[2] )
                
        _file.write( '''
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()          
        


    # --------------------------------------------------------------------------
    ##
    # @Brief 加载Beacon Message setting文件
    # @path:文件路径
    # @Returns True or None
    # --------------------------------------------------------------------------
    @classmethod
    def importBeaconMsgSetting( self, path ):
        #print '>>> load_Beacon_Msg_Setting'
        _BeaconMsgs = {}
        tree = etree.parse( path )
        _beaconpaser = self.FileParser['beacon']
        r = tree.xpath( _beaconpaser['path']['Beacon_Msg'] )
        for node in r:   
            _key = ''
            _sub_key = ''
            _list = []
            for p in _beaconpaser['attr']['Beacon_Msg']:  
                _para = node.xpath( p )    
                if _para != []:
                    if p[1:] == 'Beacon_ID':
                        _key = str( _para[0] )
                    else:
                        _list.append( str( _para[0] ) )   
                else:
                    _list.append( '' )
            _BeaconMsgs[_key] = _list   
        return _BeaconMsgs
    
    #----------------------------------------------------
    #写入beacon_msg_setting.xml
    #----------------------------------------------------
    @classmethod
    def ExportBeaconMsgSetting( cls, path, BeaconMsgs ):
        "export beacon msg setting"
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "Beacon_Msg_Setting" )
        
        for _beacon in BeaconMsgs:
            _bcn = etree.SubElement( _Root, "Beacon_Msg" )
            _bcn.set( 'Beacon_ID', _beacon )
            _bcn.set( 'Beacon_Name', BeaconMsgs[_beacon][0] )
            _bcn.set( 'Disabled', BeaconMsgs[_beacon][1] )
            _bcn.set( 'Msg_Beacon_ID', BeaconMsgs[_beacon][2] )
            _bcn.set( 'Use_Default_Msg', BeaconMsgs[_beacon][3] )
            _bcn.set( 'Available', BeaconMsgs[_beacon][4] )
            _bcn.set( 'Check_Word_1', BeaconMsgs[_beacon][5] )
            _bcn.set( 'Check_Word_2', BeaconMsgs[_beacon][6] )
            _bcn.set( 'deta_dis', BeaconMsgs[_beacon][7] )
                
        _file.write( '''
<!--本文件用于配置beacon的故障类型-->
<!--Beacon_Name:该值可不修改-->
<!--Disable:为1时beacon消息不发送-->
<!--Msg_Beacon_ID:不为""时beaconID需要修改为改设置的值，反之不修改-->
<!--Use_Default_Msg:0为默认值，非零值则修改-->
<!--Available:1可用，0不可用-->
<!--Check_Word_1:check1，为""时自己计算（用公式），反之取该变量附的值-->
<!--Check_Word_1:check2-->
<!--deta_dis:beacon相对于原始位置的偏移量，单位为mm-->
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()          
    
    @classmethod
    def importLPFConfig( cls, path ):
        "import last Platform Config"
        #注意中文路径在不用eclipse运行的时候会有问题
        _lastPFC = {}
        _f = XmlParser()
        _f .loadXmlFile( path )
        _lastplatformconfig = cls.FileParser['lastplatformconfig']
        _Maplib = _f.getAttrListManyElement( _lastplatformconfig['MapLib']['path'],
                                             _lastplatformconfig['MapLib']['attr'] )[0][0]
        
        _lastPFC['MapLib'] = _Maplib.decode( 'utf-8' ) #都转成utf8格式
        
        _Caselib = _f.getAttrListManyElement( _lastplatformconfig['CaseLib']['path'],
                                             _lastplatformconfig['CaseLib']['attr'] )[0][0]
        
        _lastPFC['CaseLib'] = _Caselib.decode( 'utf-8' ) #都转成utf8格式
        
        _CaseVersion = _f.getAttrListManyElement( _lastplatformconfig['CaseVersion']['path'],
                                             _lastplatformconfig['CaseVersion']['attr'] )[0][0]
                
        _lastPFC['CaseVersion'] = _CaseVersion.encode( 'utf-8' ) #都转成utf8格式        

        _LastMap = _f.getAttrListManyElement( _lastplatformconfig['LastMap']['path'],
                                             _lastplatformconfig['LastMap']['attr'] )[0][0]
        
        _lastPFC['LastMap'] = _LastMap.decode( 'utf-8' ) #都转成utf8格式 
          
        _LastConfig = _f.getAttrListManyElement( _lastplatformconfig['LastConfig']['path'],
                                             _lastplatformconfig['LastConfig']['attr'] )[0][0]
        
        _lastPFC['LastConfig'] = _LastConfig.decode( 'utf-8' ) #都转成utf8格式  
        
        return _lastPFC        

    @classmethod
    def ExportLPFConfig( cls, path, lastPFC ):
        "Export last Platform Config"
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "TPS_Settings" )
        _MapLib = etree.SubElement( _Root, "MapLib" )
        _MapLib.set( 'Path', lastPFC['MapLib'] )
        _CaseLib = etree.SubElement( _Root, "CaseLib" )
        _CaseLib.set( 'Path', lastPFC['CaseLib'] )        
        _CaseVersion = etree.SubElement( _Root, "CaseVersion" )
        _CaseVersion.set( 'Path', lastPFC['CaseVersion'] )         
        _LastMap = etree.SubElement( _Root, "LastMap" )
        _LastMap.set( 'Path', lastPFC['LastMap'] ) 
        _LastConfig = etree.SubElement( _Root, "LastConfig" )
        _LastConfig.set( 'ENDType', lastPFC['LastConfig'] ) 
        
        _file.write( '''
<!--用于存储平台最后一次配置的相关设置-->
<!--用于配置系统的脚本库，地图库以及工作路劲-->
<!--用于记录上次上传的文件的相关信息，主要是地图信息，其他配置文件还是第一次运行全部上传-->
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()        
        
    #-------------------------------------------------------------------------
    #导入用户的通用规则，根据是否读取描述有两种格式
    #1(有描述的){RuleName:[RuleDic,Des],...},2(无描述的):{RuleName:RuleDic,...}
    #RuleDic的定义见resultanalysis中的描述
    #--------------------------------------------------------------------------
    @classmethod
    def importBaseRule( cls, path, ReadDes = False ):
        "import base rule"
        _BaseRuleDic = {}
        _f = XmlParser()
        _f.loadXmlFile( path )
        
        #读取所有的BaseRule节点
        _BaseRuleList = _f.getAllElementByName( cls.FileParser["BaseRule"]["Rule"]["path"] )
        for _rule in _BaseRuleList:
            #获取节点的信息
            _tmpAttr = _f.getAttrListOneNode( _rule, cls.FileParser["BaseRule"]["Rule"]["attr"] )
            #不考虑baserule
            if True == ReadDes:
                _BaseRuleDic[_tmpAttr[0]] = [cls.parserRuleDic( _f, _rule ), _tmpAttr[-1]]     
            else:
                _BaseRuleDic[_tmpAttr[0]] = cls.parserRuleDic( _f, _rule )    
        return _BaseRuleDic
    
    #---------------------------------------------------------------------------
    #将BaseRuleDic存入xml中去
    #这里只支持有描述的rule的保存
    #BaseRuleDic:{RuleName:[RuleDic,Des],...}
    #---------------------------------------------------------------------------
    @classmethod
    def ExportBaseRule( cls, path, BaseRuleDic ):
        "export base rule"
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "Rules" )
        
        #生成各个规则的xml节点
        for _ruleName in BaseRuleDic:
            _subrule = etree.SubElement( _Root, "Rule" )
            _subrule.set( 'Name', _ruleName )
            _subrule.set( 'Type', BaseRuleDic[_ruleName][0]["Type"] )
            _subrule.set( 'Value', BaseRuleDic[_ruleName][0]["Value"] )
            _subrule.set( 'Des', BaseRuleDic[_ruleName][1] )
            cls.transRuleDicIntoXml( _subrule, BaseRuleDic[_ruleName][0] )
            
        _file.write( '''
<!--根节点为 Rules-->
<!--本文件用于存储通用的规则库，每条规则实际为一条运算表达式-->
<!-- 支持双目 “BOP”和 单目“UOP”运算-->
<!-- 支持的双目操作符 包括 OR AND GE GT LE LT EQ XOR XNOR ADD SUB MUL DIV POW MOD -->
<!-- 支持的单目操作符 包括 NOT FLOOR CEIL-->
<!-- 最终节点有四种形式：Variant:"变量",ConstInt："整型",ConstFloat:"浮点型",ConstStr:"字符型"-->    
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()            
    
    
    #-----------------------------------------------------------------
    #将RuleDic转换为XMl格式
    #-----------------------------------------------------------------
    @classmethod
    def transRuleDicIntoXml( cls, fathernode, RuleDic ):
        "transform rule dic into xml"
        if "UOP" == RuleDic["Type"]:
            _exp = etree.SubElement( fathernode, "exp" )
            _exp.set( 'Type', RuleDic["exp1"]["Type"] )
            _exp.set( 'Value', RuleDic["exp1"]["Value"] )
            if RuleDic["exp1"]["Type"] not in ["Variant", "ConstInt", "ConstFloat", "ConstStr"]:
                cls.transRuleDicIntoXml( _exp, RuleDic["exp1"] )
        elif "BOP" == RuleDic["Type"]:
            _lexp = etree.SubElement( fathernode, "lexp" )
            _lexp.set( 'Type', RuleDic["exp1"]["Type"] )
            _lexp.set( 'Value', RuleDic["exp1"]["Value"] )
            if RuleDic["exp1"]["Type"] not in ["Variant", "ConstInt", "ConstFloat", "ConstStr"]:
                cls.transRuleDicIntoXml( _lexp, RuleDic["exp1"] )
            _rexp = etree.SubElement( fathernode, "rexp" )
            _rexp.set( 'Type', RuleDic["exp2"]["Type"] )
            _rexp.set( 'Value', RuleDic["exp2"]["Value"] )
            if RuleDic["exp2"]["Type"] not in ["Variant", "ConstInt", "ConstFloat", "ConstStr"]:
                cls.transRuleDicIntoXml( _rexp, RuleDic["exp2"] )
        #对于RULEBASE不做处理
    
    #---------------------------------------------------------------------------
    #处理规则节点,本函数是由resultanalysis的getRuleDic函数搬移过来的
    #处理方式和getRuleDic一样，只是处理BaseRule里面的东西的时候做了区分，这个要引入一个变量
    #获取规则脚本字典RuleDic
    #XMlfilehandle是由XmlParser生成的XML文件句柄
    #FatherNode:XML的规则脚本的父节点
    #其中参数BaseRule是给不是导入baserule的时候用的
    #---------------------------------------------------------------------------
    @classmethod
    def parserRuleDic( cls, XMlfilehandle, FatherNode, BaseRule = {} ):
        "parser Rule Dic"
        _rulebase = {}
        _attrlist = XMlfilehandle.getAttrListOneNode( FatherNode, ["Type", "Value"] )
        _OPType = _attrlist[0]
        _OPValue = _attrlist[1]
            
        if _OPType in ["Variant", "ConstInt", "ConstFloat", "ConstStr"]:
            _rulebase["Type"] = _OPType
            _rulebase["Value"] = _OPValue
        elif "BOP" == _OPType: #双目运算
            _rulebase["Type"] = _OPType
            _rulebase["Value"] = _OPValue
            _rulebase["exp1"] = cls.parserRuleDic( XMlfilehandle,
                                                   FatherNode.find( 'lexp' ),
                                                   BaseRule = BaseRule )
            _rulebase["exp2"] = cls.parserRuleDic( XMlfilehandle,
                                                   FatherNode.find( 'rexp' ),
                                                   BaseRule = BaseRule )
        elif "UOP" == _OPType: #单目运算
            _rulebase["Type"] = _OPType
            _rulebase["Value"] = _OPValue
            _rulebase["exp1"] = cls.parserRuleDic( XMlfilehandle,
                                                   FatherNode.find( 'exp' ),
                                                   BaseRule = BaseRule )          
        elif "RULEBASE" == _OPType:
            if BaseRule.has_key( _OPValue ): #对于存在于baserule的要校验是否存在
                _rulebase["Type"] = _OPType
                _rulebase["Value"] = _OPValue
            else:
                print "parserRuleDic Error1! ", BaseRule, _OPValue
                return None
        else:
            print "parserRuleDic Error2! ", _OPType
            return None
    
        return _rulebase
        
    #---------------------------------------------------------------------------------------------------
    #导入用户定义的OP,{OPName:{"condition":Con,"result":[resultlist,...],"Type":"CommDef","Value":OPName},...}
    #根据是否读取描述有两种格式
    #1(有描述的)ConDic:[Dic,Des],resultlist:[Dic,Des]
    #2(无描述的):ConDic:Dic,resultlist:Dic
    #RuleDic的定义见resultanalysis中的描述
    #---------------------------------------------------------------------------------------------------
    @classmethod
    def importCommRule( cls, path, BaseRuleDic = {} , ReadDes = False ):
        "import Comm Rule"
        _CommRuleDic = {}
        _f = XmlParser()
        _f.loadXmlFile( path )
        
        #读取所有的op
        _OPRuleList = _f.getAllElementByName( cls.FileParser["CommOP"]["ReqOP"]["path"] )
        for _op in _OPRuleList:
            #获取节点的名称
            _Name = _f.getAttrListOneNode( _op, cls.FileParser["CommOP"]["ReqOP"]["attr"] )[0]
            _CommRuleDic[_Name] = cls.parserOPDic( _f,
                                                   _op,
                                                   BaseRuleDic,
                                                   Type = "CommDef",
                                                   Value = _Name,
                                                   ReadDes = ReadDes,
                                                   CommOPFlag = True )
        
        return _CommRuleDic
    
    #---------------------------------------------------------------------------
    #处理规则节点,本函数是由resultanalysis的getOPDic函数搬移过来的
    #处理方式和getOPDic一样，只是在处理BaseRule里面的东西了，这个要自行处理
    #获取规则脚本字典RuleDic
    #XMlfilehandle是由XmlParser生成的XML文件句柄
    #FatherNode:XML的规则脚本的父节点
    #其中参数BaseRule是给不是导入baserule的时候用的
    #---------------------------------------------------------------------------
    @classmethod
    def parserOPDic( cls, XMlfilehandle, Node, BaseRuleDic = {}, Type = "UserDef", Value = "", ReadDes = False, CommOPFlag = False ):
        "parser OP dic"
        _OPDic = {}
        _OPDic["Type"] = Type
        _OPDic["Value"] = Value
#        print Type
        if "UserDef" != Type and False == CommOPFlag:
            print "parserOPDic Error! please read from comm op rule!",
            return None
        _conditionNode = XMlfilehandle.getNodeInNode( Node, cls.FileParser["CommOP"]["PreCon"]["path"] )
        if True == ReadDes:
            _Des = XMlfilehandle.getAttrListOneNode( _conditionNode, cls.FileParser["CommOP"]["PreCon"]["attr"] )[-1]
            _OPDic["condition"] = [cls.parserRuleDic( XMlfilehandle, _conditionNode, BaseRuleDic ), _Des]
        else:
            _OPDic["condition"] = cls.parserRuleDic( XMlfilehandle, _conditionNode, BaseRuleDic )
        
        _resultNodeList = XMlfilehandle.getNodeListInNode( Node, cls.FileParser["CommOP"]["Result"]["path"] )
        _resultList = []
        for _resultNode in _resultNodeList:
            if True == ReadDes:
                _Des = XMlfilehandle.getAttrListOneNode( _resultNode, cls.FileParser["CommOP"]["Result"]["attr"] )[-1]
                _resultList.append( [cls.parserRuleDic( XMlfilehandle, _resultNode, BaseRuleDic ), _Des ] )
            else:
                _resultList.append( cls.parserRuleDic( XMlfilehandle, _resultNode, BaseRuleDic ) )
        _OPDic["result"] = _resultList
        
        return _OPDic
    
    #-------------------------------------------------------------------------
    #将带有描述的用户OP存入XML中去
    #-------------------------------------------------------------------------
    @classmethod
    def ExportCommRule( cls, path, commRule ):
        "export comm rule"
        _file = open( path, 'w' )
        _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "RequirementOP" )
        
        #生成各个规则的xml节点
        for _ruleName in commRule:
            _subop = etree.SubElement( _Root, "Op" )
            _subop.set( 'Name', _ruleName )
            _condition = etree.SubElement( _subop, "Precondition" )
            _condition.set( 'Type', commRule[_ruleName]["condition"][0]["Type"] )
            _condition.set( 'Value', commRule[_ruleName]["condition"][0]["Value"] )
            _condition.set( 'Des', commRule[_ruleName]["condition"][1] )
#            if "RULEBASE" != commRule[_ruleName]["condition"][0]["Type"]:#RULEBase不需要解析
            cls.transRuleDicIntoXml( _condition, commRule[_ruleName]["condition"][0] )
            
            for _result in commRule[_ruleName]["result"]:
                _resNode = etree.SubElement( _subop, "Result" )
                _resNode.set( 'Type', _result[0]["Type"] )
                _resNode.set( 'Value', _result[0]["Value"] )
                _resNode.set( 'Des', _result[1] )
#                if "RULEBASE" != _result[0]["Type"]:
                cls.transRuleDicIntoXml( _resNode, _result[0] )              
            
        _file.write( '''
<!--根节点为 ResultAnalysis-->
<!--包括变量 Variables 和 规则 Rules-->
<!--变量 Varibales 包括 类型 Type Id Id  属性 Attr 描述 Des-->
<!--变量 Variables 类型 Type 包括 Format 来自Omap 对应 0-->
<!--变量 Variables 类型 Type 包括 Constant 来自程序中的宏 对应 1-->
<!--变量 Variables 类型 Type 包括 Setting 来自地图中的配置数据 对应 2-->
<!--变量 Variables 类型 Type 包括 用户自定义 对应 3 -->
<!--变量 Variables 类型 Type 后续可以酌情增加-->
<!--变量 Variables Id 标示标量且唯一 -->
<!--变量 Variables 属性 Attr 随类型而改变 可为空 -->

<!--规则 Rules 支持同一个Omap记录对应的多个步骤的结果分析 -->
<!--规则 Rules 包括 地点 Position 时间 Time 操作 Op -->
<!--规则 Rules 地点 Pos 单位为毫米 包括 起始 Start 和 结束 End 不填为第一帧和最后一帧 -->
<!--规则 Rules 时间 Time 单位为100毫秒 包括 起始 Begin 和 结束 End 不填为第一帧和最后一帧 -->
<!--规则 Rules 操作 Op 中出现的变量应在 Variables中定义 若不能找到，则默认为Omap Format中的变量-->
<!--规则 Rules 操作 Op 中出现的变量应在 Variables中定义 若不能找到，则默认为Omap Format中的变量-->

<!--Op 包括 Precondition 和 Result -->
<!-- Precondition 和 Result 支持双目 “BOP”和 单目“UOP”运算-->
<!-- Precondition 和 Result 支持的双目操作符 包括 OR AND GE GT LE LT EQ XOR XNOR ADD SUB MUL DIV POW MOD -->
<!-- Precondition 和 Result 支持的单目操作符 包括 NOT FLOOR CEIL-->
<!-- Op的Type有两种，UserDef的为脚本中定义，CommDef则需要到用户的需求规则库中寻找"-->
<!-- 最终节点有三种形式：Variant:"变量",ConstInt："整型",ConstFloat:"浮点型"-->
''' )
        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()          
    
        
    #-----------------------------------------------------------------------------------
    #导入自动分析需要使用的常量以及自定义变量
    #返回值为两个字典，第一个字典为常量组成的字典{Name:[value,type,des],...}{Name:[value,type],...}
    #第二个为变量组成的字典{name：[RuleDic,des],...},{name：RuleDic,...}
    #注意这里没有考虑自定义变量从base中提取的情况
    #-----------------------------------------------------------------------------------
    @classmethod
    def importAnalysisVar( cls, path, ReadDes = False ):
        "import Analysis variants"
        _constsDic = {}
        _VarsDic = {}
        _f = XmlParser()
        _f.loadXmlFile( path )
        
        #获得所有Position节点
        _constNodes = _f.getAttrListManyElement( cls.FileParser["AnalysisVar"]["Const"]['path'],
                                                 cls.FileParser["AnalysisVar"]["Const"]['attr'] )
        for _node in _constNodes:
            #_node : [Id,Val,Type,des]
            _id = _node[0]
            _type = _node[2]
            _des = _node[3]
            if "int" == _type:
                _value = int( _node[1] )
            elif "float" == _type:
                _value = float( _node[1] )
            elif "str" == _type:
                _value = _node[1]
            if True == ReadDes:
                _constsDic[_node[0]] = [_value, _type, _des ]
            else:
                _constsDic[_node[0]] = [_value, _type]
                
        _VarNodes = _f.getNodeListInNode( _f.rootNode, cls.FileParser["AnalysisVar"]["Var"]['path'] )
        for _varnode in _VarNodes:
            #[Id,Val,Type,des]
            _tmplist = _f.getAttrListOneNode( _varnode, cls.FileParser["AnalysisVar"]["Var"]['attr'] )
            #不考虑baserule
            if True == ReadDes:
                _VarsDic[_tmplist[0]] = [cls.parserRuleDic( _f, _varnode ), _tmplist[-1]]     
            else:
                _VarsDic[_tmplist[0]] = cls.parserRuleDic( _f, _varnode )               
        return _constsDic, _VarsDic

    #--------------------------------------------------------------------------------
    #将带有Des的变量信息存储到文件中去
    #--------------------------------------------------------------------------------
    @classmethod
    def ExportAnalysisVar( cls, path, constsDic, VarsDic ):    
        "export analysis variants"
        try:
            _file = open( path, 'w' )
            _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
            #创建XML根节点
            _Root = etree.Element( "AnalysisVars" )
            
            _consts = etree.SubElement( _Root, "Constants" )
            for _const in constsDic:
                _subconst = etree.SubElement( _consts, "Const" )
                _subconst.set( "Id", _const )
                _subconst.set( "Val" , str( constsDic[_const][0] ) )
                _subconst.set( "Type" , constsDic[_const][1] )
                _subconst.set( "Des" , constsDic[_const][2] )
            
            _vars = etree.SubElement( _Root, "Variants" )
            for _var in VarsDic:
                _subvar = etree.SubElement( _vars, "Var" )
                _subvar.set( "Id", _var )      
                _subvar.set( 'Type', VarsDic[_var][0]["Type"] )
                _subvar.set( 'Value', VarsDic[_var][0]["Value"] )
                _subvar.set( 'Des', VarsDic[_var][1] )
                cls.transRuleDicIntoXml( _subvar, VarsDic[_var][0] )
                
            _file.write( '''
<!--根节点为 AnalysisVars-->
<!--包括变量 Constants 和 Variants,定义了自动分析所需的常量和变量信息-->
<!--常量有三种类型：int,float,str-->
''' )
            _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
            _file.write( _str )
            _file.close() 
            return True
        except:
            return False

    #-------------------------------------------------------------------------------
    #导入分析文件，这里将reslutanalusis中的函数importAnalysisfile导入进来
    #-------------------------------------------------------------------------------
    @classmethod
    def importAnalysisDic( cls, path, BaseRule = {}, CommOP = {}, ReadDes = False ):
        "import analysis rule and variant dic file"
        _AnalysisRuleDic = {}
        _VariantsDic = {}
        _f = XmlParser()
        _f .loadXmlFile( path ) 
        
        #先读取变量字典，获取变量的总节点
        _VariantsNode = _f.getNodeInNode( _f.rootNode, ".//Variables" )
        _VariantsDic = cls.getAnalysisVariantDic( _f, _VariantsNode, BaseRule = BaseRule, ReadDes = ReadDes )
#        print  self.__VariantsDic
        
        #后获取规则字典
        _RulesNodeList = _f.getNodeListInNode( _f.rootNode, cls.FileParser["autoAnalysis"]["Rules"]["path"] )
        for _rule in _RulesNodeList:
            _Name, _Dic = cls.getAnalysisRulesDic( _f, _rule, BaseRule = BaseRule, CommOPDic = CommOP, ReadDes = ReadDes )
            if True == ReadDes:
                _Des = _f.getAttrListOneNode( _rule, ["Des"] )[0]
                _AnalysisRuleDic[_Name] = [_Dic, _Des]
            else:
                _AnalysisRuleDic[_Name] = _Dic
        
        return _VariantsDic, _AnalysisRuleDic

    
    #------------------------------------------------------------------------
    #从导入的XML中提取Rules对应的数据
    #XMlfilehandle是由XmlParser生成的XML文件句柄
    #Node:单个rule节点
    #本函数由resultanalysis搬移过来(getRulesDic)，并添加了是否读取描述的选项
    #包含两种形式：
    #1：无描述的
    #{TestCaseName:{"Pos":[start,end],"Time":[start,end],
    #                "OP":[{"condition":RuleDic,"result":[RuleDic,...],"Type":"UserDef"},...]},...}
    #2：有描述的
    #{TestCaseName:[{"Pos":[start,end],"Time":[start,end],
    #                "OP":[{"condition":[RuleDic,Des],"result":[[RuleDic,Des],...],"Type":"UserDef"},...]},Des],...}    
    #------------------------------------------------------------------------
    @classmethod
    def getAnalysisRulesDic( cls, XMlfilehandle, Node, BaseRule = {}, CommOPDic = {}, ReadDes = False ):
        "get analysis Rules dic"
        _ruleDic = {}
        #读取位置和时间信息
        _PosNode = XMlfilehandle.getNodeInNode( Node, cls.FileParser["autoAnalysis"]["Pos"]["path"] )
        if None != _PosNode:
            _attrlist = XMlfilehandle.getAttrListOneNode( _PosNode,
                                                         cls.FileParser["autoAnalysis"]["Pos"]["attr"] )
            #转换成整型，不行则返回None
            try:
                _ruleDic["Pos"] = [int( _attrlist[0] ), int( _attrlist[1] ), _attrlist[-1]] if True == ReadDes else [int( _attrlist[0] ), int( _attrlist[1] )]
            except ValueError, e:
                _ruleDic["Pos"] = [None, None, ""] if True == ReadDes else [None, None]
        else:
            _ruleDic["Pos"] = [None, None, ""] if True == ReadDes else [None, None]
        _TimeNode = XMlfilehandle.getNodeInNode( Node, cls.FileParser["autoAnalysis"]["Time"]["path"] )
        if None != _TimeNode:
            _attrlist = XMlfilehandle.getAttrListOneNode( _TimeNode,
                                                         cls.FileParser["autoAnalysis"]["Time"]["attr"] )
#            print _attrlist
            try:
                _ruleDic["Time"] = [int( _attrlist[0] ), int( _attrlist[1] ), _attrlist[-1]] if True == ReadDes else [int( _attrlist[0] ), int( _attrlist[1] )]
            except ValueError, e:
                _ruleDic["Time"] = [None, None, ""] if True == ReadDes else [None, None]
        else:
            _ruleDic["Time"] = [None, None, ""] if True == ReadDes else [None, None]
        
        #读取OP
        _OPList = []
        _OPListNode = XMlfilehandle.getNodeListInNode( Node,
                                                       cls.FileParser["autoAnalysis"]["OP"]["path"] )
#        print _OPListNode
        for _opNode in _OPListNode:
#            print _opNode, Node
            _type, _value = XMlfilehandle.getAttrListOneNode( _opNode,
                                                              cls.FileParser["autoAnalysis"]["OP"]["attr"] )
            if "UserDef" == _type:
                _OPList.append( cls.parserOPDic( XMlfilehandle,
                                                 _opNode,
                                                 BaseRuleDic = BaseRule,
                                                 Type = _type,
                                                 Value = _value,
                                                 ReadDes = ReadDes ) 
                               )
            elif "CommDef" == _type:
                #{"Type":"CommDef","Value":""}
                if CommOPDic.has_key( _value ):
                    _OPList.append( CommOPDic[_value] )
                else:    
                    print "getRulesDic Error1!", _value
                    return None
            else:
                print "getRulesDic Error ! ", _type, _value
        _ruleDic["OP"] = _OPList
        
        _name = XMlfilehandle.getAttrListOneNode( Node, cls.FileParser["autoAnalysis"]["Rules"]["attr"] )[0]
        
        return _name, _ruleDic


    #----------------------------------------------------------------------------
    #从导入的XML的Variants的节点中获取所有的变量信息
    #XMlfilehandle是由XmlParser生成的XML文件句柄
    #本函数由resultanalysis搬移过来(getVariantDic)，并添加了是否读取描述的选项
    #无描述的变量字典，存储在脚本中申明的变量以及源，包括以下几种可能
    #Type = 0：format过来的数据，存储格式：VarName:["0",Name]
    #Type = 1: const数据，存储格式：VarName:["1",Name]
    #Type = 2: Map数据，存储格式：VarName:["2",Name,Attr],其中Attr是一个按照格式书写的string，是需要解析的
    #Type = 3: 用户自定义数据，存储格式：VarName:["3",RuleDic]
    #有描述的变量字典，存储在脚本中申明的变量以及源，包括以下几种可能
    #Type = 0：format过来的数据，存储格式：VarName:["0",Name,Attr,Des]
    #Type = 1: const数据，存储格式：VarName:["1",Name,Attr,Des]
    #Type = 2: Map数据，存储格式：VarName:["2",Name,Attr,Des],其中Attr是一个按照格式书写的string，是需要解析的
    #Type = 3: 用户自定义数据，存储格式：VarName:["3",Name,RuleDic,Des]        
    #-----------------------------------------------------------------------------
    @classmethod
    def getAnalysisVariantDic( cls, XMlfilehandle, Node, BaseRule = {}, ReadDes = False ):
        "get variant dic"
        _VariantsDic = {}
        _VarList = XMlfilehandle.getNodeListInNode( Node, cls.FileParser["autoAnalysis"]["Vars"]["path"] )
        for _var in _VarList:
            _attrlist = XMlfilehandle.getAttrListOneNode( _var, cls.FileParser["autoAnalysis"]['Vars']['attr'] )
            if "0" == _attrlist[0]: #来自omap
                _VariantsDic[_attrlist[1]] = _attrlist[0:2] if False == ReadDes else  _attrlist[0:4]
            elif "1" == _attrlist[0]: #常量
                _VariantsDic[_attrlist[1]] = _attrlist[0:2] if False == ReadDes else  _attrlist[0:4]
            elif "2" == _attrlist[0]: #MAP数据
                _VariantsDic[_attrlist[1]] = _attrlist[0:3] if False == ReadDes else  _attrlist[0:4]
            elif "3" == _attrlist[0]: #用户自定义变量
                _VariantsDic[_attrlist[1]] = ["3", cls.parserRuleDic( XMlfilehandle, _var.find( "VarDef" ), BaseRule = BaseRule )] \
                                               if False == ReadDes else  ["3", _attrlist[1], cls.parserRuleDic( XMlfilehandle, _var.find( "VarDef" ), BaseRule = BaseRule )] + [_attrlist[-1]]
            else:
                print "getVariantDic Error!", _attrlist
                return None
        return _VariantsDic

    #--------------------------------------------------------------------------------
    #导出自动分析脚本至xml文件
    #有描述的变量字典，存储在脚本中申明的变量以及源，包括以下几种可能
    #Type = 0：format过来的数据，存储格式：VarName:["0",Name,Attr,Des]
    #Type = 1: const数据，存储格式：VarName:["1",Name,Attr,Des]
    #Type = 2: Map数据，存储格式：VarName:["2",Name,Attr,Des],其中Attr是一个按照格式书写的string，是需要解析的
    #Type = 3: 用户自定义数据，存储格式：VarName:["3",Name,RuleDic,Des]       
    #--------------------------------------------------------------------------------
    @classmethod
    def ExportAnalysisDic( cls, path, VariantsDic, AnalysisRuleDic ):
        "export analysis dic"
        try:
            _file = open( path, 'w' )
            _file.write( r'<?xml version="1.0" encoding="utf-8"?>' ) #添加头
            #创建XML根节点
            _Root = etree.Element( "ResultAnalysis" )
                
            _Variants = etree.SubElement( _Root, "Variables" )
            for _variant in VariantsDic:
                _subVariant = etree.SubElement( _Variants, "Var" )
                _subVariant.set( "Type", VariantsDic[_variant][0] )
                _subVariant.set( "Id" , _variant )
                if "3" != VariantsDic[_variant][0]:
                    _subVariant.set( "Attr", VariantsDic[_variant][2] )
                else:#自定义变量
                    _subDefVar = etree.SubElement( _subVariant, "VarDef" )
                    _subDefVar.set( 'Type', VariantsDic[_variant][2]["Type"] )
                    _subDefVar.set( 'Value', VariantsDic[_variant][2]["Value"] )
    #                    if "RULEBASE" != VariantsDic[_variant][1]["Type"]: #RULEBASE不需要
                    cls.transRuleDicIntoXml( _subDefVar, VariantsDic[_variant][2] )                    
                        
                _subVariant.set( "Des" , VariantsDic[_variant][-1] )
                
            for _ruleName in AnalysisRuleDic:
                _Rule = etree.SubElement( _Root, "Rules" )
                _Rule.set( "TC", _ruleName )
                _Rule.set( "Des", AnalysisRuleDic[_ruleName][-1] )
                    
                #pos
                _pos = etree.SubElement( _Rule, "Pos" )
                _pos.set( "Start", str( AnalysisRuleDic[_ruleName][0]["Pos"][0] ) )
                _pos.set( "End", str( AnalysisRuleDic[_ruleName][0]["Pos"][1] ) )
                _pos.set( "Des", AnalysisRuleDic[_ruleName][0]["Pos"][-1] )
                    
                #Time
                _time = etree.SubElement( _Rule, "Time" )
                _time.set( "Begin", str( AnalysisRuleDic[_ruleName][0]["Time"][0] ) )
                _time.set( "End", str( AnalysisRuleDic[_ruleName][0]["Time"][1] ) )
                _time.set( "Des", AnalysisRuleDic[_ruleName][0]["Time"][-1] )                
                    
                #OPs
                for _op in AnalysisRuleDic[_ruleName][0]["OP"]:
                    _subop = etree.SubElement( _Rule, "Op" )
                    _subop.set( "Type", _op["Type"] )
                    _subop.set( "Value", _op["Value"] )
                    if "UserDef" == _op["Type"]:#从库里面来的不需要下面的步骤
                        #condition
                        _subCondition = etree.SubElement( _subop, "Precondition" )
                        _subCondition.set( "Type", _op["condition"][0]["Type"] )
                        _subCondition.set( "Value", _op["condition"][0]["Value"] )
                        _subCondition.set( "Des", _op["condition"][-1] ) 
    #                       if "RULEBASE" != _op["condition"][0]["Type"]:
                        cls.transRuleDicIntoXml( _subCondition, _op["condition"][0] ) 
                            
                        #result
                        for _result in _op["result"]:
                            _subResult = etree.SubElement( _subop, "Result" )
                            _subResult.set( "Type", _result[0]["Type"] )
                            _subResult.set( "Value", _result[0]["Value"] )
                            _subResult.set( "Des", _result[-1] )                             
                            cls.transRuleDicIntoXml( _subResult, _result[0] ) 
                    
            _file.write( '''
<!--根节点为 ResultAnalysis-->
<!--包括变量 Variables 和 规则 Rules-->
<!--变量 Varibales 包括 类型 Type Id Id  属性 Attr 描述 Des-->
<!--变量 Variables 类型 Type 包括 Format 来自Omap 对应 0-->
<!--变量 Variables 类型 Type 包括 Constant 来自程序中的宏 对应 1-->
<!--变量 Variables 类型 Type 包括 Setting 来自地图中的配置数据 对应 2-->
<!--变量 Variables 类型 Type 包括 用户自定义 对应 3 -->
<!--变量 Variables 类型 Type 后续可以酌情增加-->
<!--变量 Variables Id 标示标量且唯一 -->
<!--变量 Variables 属性 Attr 随类型而改变 可为空 -->
    
<!--规则 Rules 支持同一个Omap记录对应的多个步骤的结果分析 -->
<!--规则 Rules 包括 地点 Position 时间 Time 操作 Op -->
<!--规则 Rules 地点 Pos 单位为毫米 包括 起始 Start 和 结束 End 不填为第一帧和最后一帧 -->
<!--规则 Rules 时间 Time 单位为100毫秒 包括 起始 Begin 和 结束 End 不填为第一帧和最后一帧 -->
<!--规则 Rules 操作 Op 中出现的变量应在 Variables中定义 若不能找到，则默认为Omap Format中的变量-->
<!--规则 Rules 操作 Op 中出现的变量应在 Variables中定义 若不能找到，则默认为Omap Format中的变量-->
    
<!--Op 包括 Precondition 和 Result -->
<!-- Precondition 和 Result 支持双目 “BOP”和 单目“UOP”运算-->
<!-- Precondition 和 Result 支持的双目操作符 包括 OR AND GE GT LE LT EQ XOR XNOR ADD SUB MUL DIV POW MOD -->
<!-- Precondition 和 Result 支持的单目操作符 包括 NOT FLOOR CEIL-->
<!-- Op的Type有两种，UserDef的为脚本中定义，CommDef则需要到用户的需求规则库中寻找"-->
<!-- 最终节点有三种形式：Variant:"变量",ConstInt："整型",ConstFloat:"浮点型"-->
''' )
            _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
            _file.write( _str )
            _file.close() 
            return True
        except KeyError, e:
            return False        
        
    @classmethod
    def importPlatformInfo( cls, path ):
        "import platformInfo"
        _platInfo = {}
        _f = XmlParser()
        _f .loadXmlFile( path )
        _platformInfo = cls.FileParser['platformInfo']
        _platInfo['TestedProduct'] = _f.getAttrListManyElement( _platformInfo['TestedProduct']['path'],
                                                                _platformInfo['TestedProduct']['attr'] )[0]
        
        return _platInfo   

    
    #-------------------------------------------------------------
    #保存用户定义的画OMAP Figure的配置，格式如下：
    #{ConfigName:[{FrameLabel:{Variantlabel:VariantConfig,...}},Desription],...}
    #VariantConfig:[Max,Min,linestyle,linewidth,color,showflag]
    #-------------------------------------------------------------
    @classmethod
    def importOMAPFigureConfig( cls, path ):
        "import OMAP Figure Config"
        _OMAPFigureConfigDic = {}
        _f = XmlParser()
        _f .loadXmlFile( path )
        
        _OMAPFigureConfigParser = cls.FileParser['omapfigureconfig']
        #先获取所有的Config
        _configNodeList = _f.getNodeListInNode( _f.rootNode, _OMAPFigureConfigParser['Config']['path'] )
        for _cNode in _configNodeList:
            _config = _f.getAttrListOneNode( _cNode, _OMAPFigureConfigParser['Config']['attr'] )
            _OMAPFigureConfigDic[_config[0]] = []
            _OMAPFigureConfigDic[_config[0]].append( {} )
            _OMAPFigureConfigDic[_config[0]].append( _config[1] )
            
            #获取所有FrameLabel
            _FramelabelList = _f.getNodeListInNode( _cNode, _OMAPFigureConfigParser['FrameLabel']['path'] )
            for _frameLabel in _FramelabelList:
                _frameName = _f.getAttrListOneNode( _frameLabel, _OMAPFigureConfigParser['FrameLabel']['attr'] )[0]
                _OMAPFigureConfigDic[_config[0]][0][_frameName] = {}
                #读取Data配置
                _DataNodeList = _f.getNodeListInNode( _frameLabel, _OMAPFigureConfigParser['Data']['path'] )
                for _dNode in _DataNodeList:
                    #['Name', 'Maximum', 'Minimum', 'LineStyle', 'lineWidth', 'colR', 'colG', 'colB']
                    _dataAttrList = _f.getAttrListOneNode( _dNode, _OMAPFigureConfigParser['Data']['attr'] )
                    
                    _OMAPFigureConfigDic[_config[0]][0][_frameName][_dataAttrList[0]] = [float( _dataAttrList[1] ),
                                                                                         float( _dataAttrList[2] ),
                                                                                         _dataAttrList[3],
                                                                                         float( _dataAttrList[4] ),
                                                                                         ( float( _dataAttrList[5] ), float( _dataAttrList[6] ), float( _dataAttrList[7] ) ),
                                                                                         True ]#showflag默认为True
        
        return _OMAPFigureConfigDic   

    #--------------------------------------------------------------------
    #保存OMAPFigureConfig
    #{ConfigName:[{FrameLabel:{Variantlabel:VariantConfig,...}},Desription],...}
    #VariantConfig:[Max,Min,linestyle,linewidth,color,showflag]
    #--------------------------------------------------------------------
    @classmethod
    def ExportOMAPFigureConfig( cls, path, OMAPFigureConfigDic ):
        "Export OMAP Figure Config"
        _file = open( path, 'w' )
        _file.write( '''<?xml version="1.0" encoding="utf-8"?>
''' ) #添加头
        #创建XML根节点
        _Root = etree.Element( "Configuration" )
        
        #建立config
        for _configKey in OMAPFigureConfigDic:
            _config = etree.SubElement( _Root, "Config" )
            _config.set( 'Name', _configKey )
            _config.set( 'Description', OMAPFigureConfigDic[_configKey][1] )
            
            #frame
            for _frameKey in OMAPFigureConfigDic[_configKey][0]:
                _framelabel = etree.SubElement( _config, "FrameLabel" )
                _framelabel.set( 'Name', _frameKey )
                
                #Data
                for _dataKey in OMAPFigureConfigDic[_configKey][0][_frameKey]:
                    _data = etree.SubElement( _framelabel, "Data" )
                    _datacontent = OMAPFigureConfigDic[_configKey][0][_frameKey][_dataKey]
                    _data.set( 'Name', _dataKey )
                    _data.set( 'colR', str( _datacontent[4][0] ) )
                    _data.set( 'colG', str( _datacontent[4][1] ) )
                    _data.set( 'colB', str( _datacontent[4][2] ) )
                    _data.set( 'LineStyle', _datacontent[2] )
                    _data.set( 'lineWidth', str( _datacontent[3] ) )
                    _data.set( 'Minimum', str( _datacontent[1] ) )
                    _data.set( 'Maximum', str( _datacontent[0] ) )

        _str = etree.tostring( _Root, pretty_print = True, encoding = "utf-8" )
        _file.write( _str )
        _file.close()          
           
    
if __name__ == '__main__':
    #scenario
#    defScenario, TimeScenario, defScenarioDes, TimeScenarioDes = XMLDeal.importDefSce( r'../default case/scenario/rs_scenario.xml', ReadDes = True )
#    print defScenario, TimeScenario
#    print defScenarioDes, TimeScenarioDes 
#    XMLDeal.ExportDefSce( r'../default case/scenario/rs_scenario1.xml', defScenario, TimeScenario, defScenarioDes, TimeScenarioDes )
#    
    #viomsetting
#    dic_in, dic_out = XMLDeal.importVIOMSetting( r'../default case/scenario/rs_viom_setting.xml' )
#    print dic_in, dic_out
#    XMLDeal.ExportVIOMSetting( r'../default case/scenario/rs_viom_setting1.xml', dic_in, dic_out )
    
    #train_Route
#    routeV, startV, direV, trainLen, Cog_dir = XMLDeal.importTrainRoute( r'../default case/scenario/train_route.xml' )
#    print routeV, startV, direV, trainLen, Cog_dir
#    XMLDeal.ExportTrainRoute( r'../default case/scenario/train_route1.xml', routeV, startV, direV, trainLen, Cog_dir )

    #expectspeed
#    trainRunScenario, EB_EndPos, trainRunScenarioDes = XMLDeal.importExpectSpeed( r'../default case/scenario/rs_expectSpeed.xml', ReadDes = True )
#    print trainRunScenario, EB_EndPos, trainRunScenarioDes
#    XMLDeal.ExportExpectSpeed( r'../default case/scenario/rs_expectSpeed1.xml', trainRunScenario, EB_EndPos, trainRunScenarioDes )
    
    #beacon_msg_setting
#    myBMBeacons = XMLDeal.importBMBeacons( r'../default case/scenario/bm_beacons.xml', ReadDes = True )
#    print myBMBeacons
#    XMLDeal.ExportBMBeacons( r'../default case/scenario/bm_beacons1.xml', myBMBeacons )

    #beacon_msg_setting
#    BeaconMsgs = XMLDeal.importBeaconMsgSetting(r'../default case/scenario/beacon_msg_setting.xml')
#    print BeaconMsgs
#    XMLDeal.ExportBeaconMsgSetting( r'../default case/scenario/beacon_msg_setting1.xml', BeaconMsgs )
    
    #zc_Variant_ini.xml
#    variant_dic, variant_dic_len, variant_dic_Num, variant_type_EQID = XMLDeal.importZCVariantIni( r'../default case/scenario/zc_variant_ini.xml' )
#    print variant_dic
#    print variant_dic_len 
#    print variant_dic_Num 
#    print variant_type_EQID
#    XMLDeal.ExportZCVariantIni( r'../default case/scenario/zc_variant_ini1.xml' , variant_dic, variant_type_EQID )

    #zc_variant_scenario.xml
#    V_Scenario, V_ScenarioDes = XMLDeal.importZCVarSce( r'../default case/scenario/zc_variant_scenario.xml', ReadDes = True )
#    print V_Scenario
#    print V_ScenarioDes
#    XMLDeal.ExportZCVarSce( r'../default case/scenario/zc_variant_scenario1.xml', V_Scenario, V_ScenarioDes )

    #lc_tsr_setting
#    tsrItems, tsrItemDes = XMLDeal.importTSRSetting( r'../default case/scenario/lc_tsr_setting.xml', ReadDes = True )
#    print tsrItems
#    print tsrItemDes
#    XMLDeal.ExportTSRSetting( r'../default case/scenario/lc_tsr_setting1.xml', tsrItems, tsrItemDes )

    #variant
#    variants = XMLDeal.importVariant( r'../TPConfig/setting/rs_variant.xml' )
#    print variants
#    XMLDeal.ExportVariant( r'../TPConfig/setting/rs_variant1.xml', variants )

    #导入平台lastplatform配置文件
#    lastconfig = XMLDeal.importLPFConfig( r'../TPConfig/LastPlatformConfig.xml' )
#    print lastconfig
#    XMLDeal.ExportLPFConfig( r'../TPConfig/LastPlatformConfig1.xml', lastconfig )

    #BaseRule
#    baserule = XMLDeal.importBaseRule( r'../autoAnalysis/config/baseRules.xml', ReadDes = True )
#    print baserule
#    XMLDeal.ExportBaseRule( r'../autoAnalysis/config/baseRules1.xml', baserule )
    
    #CommRule
#    baserule = XMLDeal.importBaseRule( r'../autoAnalysis/config/baseRules.xml' )
#    commRule = XMLDeal.importCommRule( r'../autoAnalysis/config/userRequirementRules.xml', {}, ReadDes = True )
#    print commRule
#    XMLDeal.ExportCommRule( r'../autoAnalysis/config/userRequirementRules1.xml', commRule )
    
    #analysisVar
#    analysisvar = XMLDeal.importAnalysisVar( r'../autoAnalysis/config/usrData.xml', ReadDes = True )
#    print analysisvar[0]
#    print analysisvar[1]
#    XMLDeal.ExportAnalysisVar( r'../autoAnalysis/config/usrData1.xml', analysisvar[0], analysisvar[1] )
    
    #analysisfile
#    baserule = XMLDeal.importBaseRule( r'../autoAnalysis/config/baseRules.xml' )
#    commRule = XMLDeal.importCommRule( r'../autoAnalysis/config/userRequirementRules.xml', BaseRuleDic = baserule, ReadDes = True )
#    analysisContent = XMLDeal.importAnalysisDic( r'../autoAnalysis/autoAnalysis_backup.xml', BaseRule = baserule, CommOP = commRule, ReadDes = True )
#    print analysisContent[0]
#    print analysisContent[1]
#    XMLDeal.ExportAnalysisDic( r'../autoAnalysis/autoAnalysis_backup1.xml', analysisContent[0], analysisContent[1] )

    #导入OMAPFigure Config
    OMAPFigureConfigDic = XMLDeal.importOMAPFigureConfig( r'../TPConfig/OMAPFigureConfig.xml' )
    print OMAPFigureConfigDic
    XMLDeal.ExportOMAPFigureConfig( r'../TPConfig/OMAPFigureConfig1.xml', OMAPFigureConfigDic )
