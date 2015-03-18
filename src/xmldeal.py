#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     xmldeal.py
#Description:  本模块用于读入与写各种式样的xml文件,并将之进行返回
# Author:       KUNPENG XIONG
# Version:      0.0.2
# Created:      2011-12-12
# Company:      CASCO
# LastChange:   2011-12-12
# History:      Created --- 2011-12-12
#               Modify for Edit Case 2012-03-21
#----------------------------------------------------------------------------
from xmlparser import XmlParser

class XMLDeal():
    """
    import all xml for platform
    """

    #各个xml文件读取的格式字典
    FileParser = {'train_route': {'map':{'path':'.//Map', 'attr':['List']},
                            'Cog_dir':{'path':'.//Cog_dir', 'attr':['Value']},
                            'accel':{'path':'.//Accel', 'attr':['Positive', 'Negative']},
                            'V_max':{'path':'.//V_max', 'attr':['Value']},
                            'timer':{'path':'.//Timer', 'attr':['Big','Small']},
                            'radio':{'path':'.//Radio', 'attr':['Outer','Inner']},
                            'lineInfo':{'path':'.//LineInfo', 'attr':['LineNumber']}       
                            }}
    #各个xml文件读取的格式字典
    smartTramParser = {'smartTramInfo': {'Mode':{'path':'.//Mode', 'attr':['Value']},
                            'Stop_time':{'path':'.//Stop_time', 'attr':['Value']},
                            'Cog_dir':{'path':'.//Cog_dir', 'attr':['Value']},
                            'accel':{'path':'.//Accel', 'attr':['Positive', 'Negative']},
                            'V_max':{'path':'.//V_max', 'attr':['Value']},
                            'timer':{'path':'.//Timer', 'attr':['Big','Small']},
                            'radio':{'path':'.//Radio', 'attr':['Outer','Inner']}      
                            }}

    def __init__( self ):
        "init do nothing"
        pass
    
    #------------------------------------------------------
    #读入smartTram 信息
    #------------------------------------------------------
    @classmethod
    def importSmartTramInfo(cls, path):
        "import smartTram infomation."
        _f = XmlParser()
        _f .loadXmlFile( path )
        _Mode = _f.getAttrListOneElement( cls.smartTramParser['smartTramInfo']['Mode']['path'], \
                                                  cls.smartTramParser['smartTramInfo']['Mode']['attr'] )[0]
                                                  
        _stop_time = int( _f.getAttrListOneElement( cls.smartTramParser['smartTramInfo']['Stop_time']['path'], \
                                                  cls.smartTramParser['smartTramInfo']['Stop_time']['attr'] )[0] )
        
        _Cog_dir = float( _f.getAttrListOneElement( cls.smartTramParser['smartTramInfo']['Cog_dir']['path'], \
                                                  cls.smartTramParser['smartTramInfo']['Cog_dir']['attr'] )[0] )
        
        _accel = _f.getAttrListOneElement( cls.smartTramParser['smartTramInfo']['accel']['path'], \
                                           cls.smartTramParser['smartTramInfo']['accel']['attr'] )
        _accelV = [int( _a ) for _a in _accel]
        
        _V_max = int(_f.getAttrListOneElement( cls.smartTramParser['smartTramInfo']['V_max']['path'], \
                                           cls.smartTramParser['smartTramInfo']['V_max']['attr'] )[0])
        
        _timer = _f.getAttrListOneElement( cls.smartTramParser['smartTramInfo']['timer']['path'], \
                                   cls.smartTramParser['smartTramInfo']['timer']['attr'] )
        _timerV = [float( _t ) for _t in _timer]
        
        _radio = _f.getAttrListOneElement( cls.smartTramParser['smartTramInfo']['radio']['path'], \
                           cls.smartTramParser['smartTramInfo']['radio']['attr'] )
        _radioV = [float( _r) for _r in _radio]
        return _Mode,_stop_time,_Cog_dir,_accelV,_V_max,_timerV,_radioV

    #------------------------------------------------------
    #读入train_route
    #------------------------------------------------------
    @classmethod
    def importTrainRoute( cls, path ):
        "import train route."
        _f = XmlParser()
        _f .loadXmlFile( path )
        #获得route节点的属性
        _map = _f.getAttrListOneElement( cls.FileParser['train_route']['map']['path'], \
                                                   cls.FileParser['train_route']['map']['attr'] )
#         print'-----_map-----',_map
        _mapList = [int( _s ) for _s in _map[0].strip().split( ',' )]
#         print'-----_mapList-----',_mapList
        _Cog_dir = float( _f.getAttrListOneElement( cls.FileParser['train_route']['Cog_dir']['path'], \
                                                  cls.FileParser['train_route']['Cog_dir']['attr'] )[0] )
        
        _accel = _f.getAttrListOneElement( cls.FileParser['train_route']['accel']['path'], \
                                           cls.FileParser['train_route']['accel']['attr'] )
        _accelV = [int( _a ) for _a in _accel]
        
        _V_max = int(_f.getAttrListOneElement( cls.FileParser['train_route']['V_max']['path'], \
                                           cls.FileParser['train_route']['V_max']['attr'] )[0])
        
        _timer = _f.getAttrListOneElement( cls.FileParser['train_route']['timer']['path'], \
                                   cls.FileParser['train_route']['timer']['attr'] )
        _timerV = [float( _t ) for _t in _timer]
        
        _radio = _f.getAttrListOneElement( cls.FileParser['train_route']['radio']['path'], \
                           cls.FileParser['train_route']['radio']['attr'] )
        
        _radioV = [float( _r) for _r in _radio]
        
        _lineInfo = _f.getAttrListOneElement(cls.FileParser['train_route']['lineInfo']['path'],\
                            cls.FileParser['train_route']['lineInfo']['attr'])
        _lineList = [int( _a ) for _a in _lineInfo[0].strip().split( ',' )]
        
#         _lineId= int(_lineInfo[0])
#         _dir = int(_lineInfo[1])
#         _ssaList = [int( _s ) for _s in _lineInfo[2].strip().split( ',' )]
#         if _dir == 1:#上行线解析
#             _blockList = [int( _s ) for _s in _lineInfo[3].strip().split( ',' )]
#         else:#下行线
#             _blockList = [int( _s ) for _s in _lineInfo[3].strip().split( ',' )[::-1]]
#         print '-------_lineInfo----------',_lineInfo
#         print '-----------_blockList-------',_blockList
        return _mapList,_Cog_dir,_accelV,_V_max,_timerV,_radioV,_lineList
  
        
if __name__ == '__main__':
    #train_Route
#     _mapList,cog_dir,accel,V_max,time,radio,lineList= XMLDeal.importTrainRoute( r'./scenario/train_route.xml' )
#     print _mapList,cog_dir,accel,V_max,time,radio,lineList
    
    mode,stop_time,cog_dir,accel,V_max,time,radio= XMLDeal.importSmartTramInfo( r'./scenario/smartTram_info.xml' )
    print mode,stop_time,cog_dir,accel,V_max,time,radio