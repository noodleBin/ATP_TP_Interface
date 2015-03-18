#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     basedevice.py
# Description:  基础设备类      
# Author:       OUYANG Min
# Version:      0.0.2
# Created:      2011-04-12
# Company:      CASCO
# LastChange:   update 2011-07-16
# History:      添加变量、消息导入方法
#               update 2011-07-18
#               修改变量和消息导入
#               update 2011-07-19
#               添加导入默认脚本方法
#               update 2011-07-22
#               添加导入车辆路径方法
#               update 2011-07-29
#               pack,unpack添加异常处理
#               update 2011-07-29 add by xiongkunpeng
#               添加逻辑处理函数部分
#               update 2011-08-09 add by xiongkunpeng
#               使得checkrule能够支持float类型的变量，并且添加用户自己写的rule的导入计算
#               update: 2011-08-09 add by xiongkunpeng
#               添加用户rule脚本支持
#----------------------------------------------------------------------------
from xmlparser import XmlParser
from lxml import etree
import struct
import Queue
import excepthandle
import commlib
from xmldeal import XMLDeal

class BaseDevice( object ):
    """
    base device class
    """
    __deviceName = None
    __deviceId = None
    
    #数据字典 key,value
    __data = None
    
    #初始化时导入变量字典
    __var = None
    #消息格式字典
    __msg = None
    
    #队列大小
    maxQueueSize = 1024
    inQ = None
    outQ = None

    #对象实例后缀 object
    obj = '_o'
    
    #每个对象实例用元组存贮 (objN,objB)

    #对象实例索引index的位置 设备ID用着索引
    objN = 0
    #对象实例object的位置
    objB = 1
    
    #变量和消息文件的元素名称和属性列表
    importFileParser = {
            'var': {'path':'.//Var',
                'attr':['Name', 'Type', 'IO', 'Value'],
                'type':{'int':int,
                    'string':str,
                    'float':float}
                },
            'msg': {'id':{'path':'.//Msg',
                                'attr':['Name', 'Id', 'Pack']},
                    'item':{'path':'.//Item',
                            'attr':['Index', 'Format', 'Name']
                            }
                    } 
        }


    #基本格式scenario存放列表
    #[[block, abs, delay_cycle,[[var_key, value]...]]...]
    defScenario = None
    #时间脚本scenario格式
    #[[loophour, delay_cycle,[[var_key, value]...]]...]
    TimeScenario = None
    
    #逻辑格式scenario存放列表
    #{rule ID:{'left':{},'right':{},'type':"exp",'operator':'AND'},
    # rule ID:{'exps':[{},{}],'type':"exp",'operator':'AND'},...}
    ruleScenario = None
    
    #保存逻辑中需要延时修改的值的列表
    #[[name,value,delay],...]
    rulechangelist = None
    ParserValuetype = {'int':int,
                    'string':str,
                    'float':float}
    ruleSceParser = {
            'rule':{
                    'path':r'/Rules/Rule',
                    'attr':['@id', '@type', '@operator']
                    },
            'exp':{'path':r'.//exp',
                   'attr':['@type', '@value']
                   },
            'lexp':{'path':r'.//lexp',
                   'attr':['@type', '@value']
                   },
            'rexp':{'path':r'.//rexp',
                   'attr':['@type', '@value']
                   },
            'reaction':{'path':r'.//Reaction',
                        'attr':['@name', '@value', '@delay']
                        }                    
            }
        
    defSceParser = {
            'pos':{'path':'.//Position',
                    'attr':['Block_id', 'Abscissa', 'Delay']
                  },
            'set':{'path':'.//Set',
                    'attr':['Name', 'Value']
                },
            'time':{'path':'.//Time',
                    'attr':['Loophour']}
            }

    def __init__( self, name, id ):
        " device class init "
        self.__deviceName = name
        self.__deviceId = id
        self.__data = {}
        self.__var = {}
        self.__msg = {}
        self.inQ = Queue.Queue( self.maxQueueSize )
        self.outQ = Queue.Queue( self.maxQueueSize )
        self.defScenario = []
        self.TimeScenario = []
        self.ruleScenario = {}
        self.rulechangelist = []
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 导入设备使用的关键变量
    # 添加到__data字典 格式 key(Name):value
    # 添加到__var字典 格式 key(Name):[Type,IO,Value]
    #
    # @Param varintFile
    #
    # @Returns
    # --------------------------------------------------------------------------
    def importVarint( self, varintFile ):
        " import device varint"
        _f = XmlParser()
        _f.loadXmlFile( varintFile )
        _var = _f.getAttrListManyElement( self.importFileParser['var']['path'],
                self.importFileParser['var']['attr'] )
        for _v in _var:
            #添加到__data
            #若变量的类型是基本类型,则赋初值,不是则赋值None
            if _v[1] in self.importFileParser['var']['type']:
                self.addDataKeyValue( _v[0], \
                        self.importFileParser['var']['type'][_v[1]]( _v[3] ) )
            else:
                self.addDataKeyValue( _v[0], None )
            #添加到__var
            self.__var[_v[0]] = _v[1:]
        _f.closeXmlFile()

    # --------------------------------------------------------------------------
    ##
    # @Brief 解析消息定义文件，获得消息字典
    # 消息字典格式，例子
    # __msg = {Id:
    #            {
    #             'name':'AA',
    #             'format':'!HHH',
    #             'len':6,
    #             'a',0,
    #             'b',1,
    #             'c',2
    #            }
    #   }
    #
    # @Param msgFile
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def importMsg( self, msgFile ):
        " import device msg format setting"
        _f = XmlParser()
        _f .loadXmlFile( msgFile )
        #获得所有Msg节点
        _msgNdoe = _f.getAllElementByName( self.importFileParser['msg']['id']['path'] )
        for _mn in _msgNdoe:
            #获得msg节点的所有属性
            _ma = _f.getAttrListOneNode( _mn, self.importFileParser['msg']['id']['attr'] )
            #msg type(msg id)做为key
            self.__msg[int( _ma[1] )] = {}
            
            #消息类型
            self.__msg[int( _ma[1] )]['name'] = _ma[0]
            #消息打包格式头
            self.__msg[int( _ma[1] )]['format'] = _ma[2]
            #获得该msg下的所有Item的属性
            _ia = [_f.getAttrListOneNode( _item, self.importFileParser['msg']['item']['attr'] ) \
                    for _item in _f.getNodeListInNode( _mn, self.importFileParser['msg']['item']['path'] )]
            for _ii in _ia:
                #消息格式
                self.__msg[int( _ma[1] )]['format'] += _ii[1]
                #消息子项的偏移
                self.__msg[int( _ma[1] )][_ii[2]] = int( _ii[0] )
            #消息的长度
            self.__msg[int( _ma[1] )]['len'] = struct.calcsize( self.__msg[int( _ma[1] )]['format'] )
    
    
    def importDefSce( self, sceFile ):
        "import default format scenario"
        self.defScenario = []
        self.TimeScenario = []        
        self.defScenario, \
        self.TimeScenario = XMLDeal.importDefSce( sceFile,
                                                  ReadDes = False )        

    # --------------------------------------------------------------------------
    ##
    # @Brief 获取逻辑跑车脚本，放入ruleScenario中
    #{rule ID:{'left':{},'right':{},'type':"exp",'operator':'AND'},
    # rule ID:{'exps':[{},{}],'type':"exp",'operator':'AND'},...}
    #'left':{'type':'Variant','value':'name'}
    #'left':{'type':'exp','value':'AND','left':{},'right':{}}
    #'left':{'type':'exp','value':'AND',exps:[{},{}....]}
    # @Returns var dict
    # --------------------------------------------------------------------------
    def importRuleDic( self, LogsceFile ):
        "get lofScenario dict"
        self.ruleScenario = {}
        _tree = etree.parse( LogsceFile )
        #获取rule个数
        _Logroot = _tree.xpath( self.ruleSceParser['rule']['path'] )
        for _rule in _Logroot:
            #获取rule脚本的基本信息
            #print _rule
            _tmprule = {} 
            _ID = _rule.xpath( self.ruleSceParser['rule']['attr'][0] )[0]
            _type = _rule.xpath( self.ruleSceParser['rule']['attr'][1] )[0]
            _operator = _rule.xpath( self.ruleSceParser['rule']['attr'][2] )[0]
            _tmprule['type'] = _type
            _tmprule['operator'] = _operator

            if _type == 'exp': #左右形式
                #解码左右表达式
                _leftexp = _rule.xpath( self.ruleSceParser['lexp']['path'] )[0]
                _leftexp = _rule.find( 'lexp' )
                #print self.ruleSceParser['lexp']['path']
                #_rightexp = _rule.xpath(self.ruleSceParser['rexp']['path'])[0]
                #print _rightexp
                _rightexp = _rule.find( 'rexp' )
                #print self.ruleSceParser['rexp']['path']
                _tmprule['left'] = self.expnoderead( _leftexp, 'lexp' )
                #print 'left',_tmprule['left'] 
                _tmprule['right'] = self.expnoderead( _rightexp, 'rexp' )  
                #print 'right',_tmprule['right']              
            elif _type == 'Mexp':
                _exps = _rule.xpath( self.ruleSceParser['exp']['path'] )
                _tmprule['exps'] = self.Mexpnoderead( _exps )
            #获取reaction
            _renode = _rule.xpath( self.ruleSceParser['reaction']['path'] )
            _reaction = []
            for _r in _renode:
                _name = _r.xpath( self.ruleSceParser['reaction']['attr'][0] )[0]
                _value = _r.xpath( self.ruleSceParser['reaction']['attr'][1] )[0]
                _delay = _r.xpath( self.ruleSceParser['reaction']['attr'][2] )[0]
                _reaction.append( [_name, _value, _delay] )
            _tmprule['reaction'] = _reaction
            self.ruleScenario[_ID] = _tmprule
        
            
    #---------------------------------------------------------------------------
    #@从xml的exp的node节点中获取其中内容，该函数存在递归调用
    #'left':{'type':'Variant','value':'name'}
    #'left':{'type':'exp','value':'AND','left':{},'right':{}}
    #'left':{'type':'exp','value':'AND',exps:[{},{}....]}
    #---------------------------------------------------------------------------  
    def expnoderead( self, expnode, nodename ):
        "get sub node exp"
        _return_rule = {}#返回字典
        _type = expnode.xpath( self.ruleSceParser[nodename]['attr'][0] )[0]
        #print _type
        _value = expnode.xpath( self.ruleSceParser[nodename]['attr'][1] )[0]
        #判断type以查看是否结束
        if 'Variant' == _type or 'Const' == _type:
            #print _type
            _return_rule['type'] = _type
            _return_rule['value'] = _value
        elif 'exp' == _type:
            _return_rule['type'] = _type
            _return_rule['value'] = _value
            #_leftnode = expnode.xpath(self.ruleSceParser['lexp']['path'])[0]
            _leftnode = expnode.find( 'lexp' )
            #_rightnode = expnode.xpath(self.ruleSceParser['rexp']['path'])[0]
            _rightnode = expnode.find( 'rexp' )
            _return_rule['left'] = self.expnoderead( _leftnode, 'lexp' )
            #print 'left',_return_rule['left']
            _return_rule['right'] = self.expnoderead( _rightnode, 'rexp' )
            #print 'right',_return_rule['right']
        elif 'Mexp' == _type:
            _return_rule['type'] = _type
            _return_rule['value'] = _value
            _tmpMexps = self.Mexpnoderead( expnode )
            _return_rule['exps'] = _tmpMexps
        else:
            _return_rule = None
        #print  _return_rule   
        return _return_rule
            
    #---------------------------------------------------------------------------
    #@从xml的exps的node节点中获取其中内容，该函数存在递归调用
    #'left':{'type':'Variant','value':'name'}
    #'left':{'type':'exp','value':'AND','left':{},'right':{}}
    #'left':{'type':'exp','value':'AND',exps:[{},{}....]}
    #--------------------------------------------------------------------------- 
    def Mexpnoderead( self, Mexpnode ):
        "get exps"
        _tmpexp = []
        for _exp in Mexpnode:
            _tmpexp.append( self.expnoderead( _exp, 'exp' ) )
        return _tmpexp                    
        
    #---------------------------------------------------------------------------
    #根据ruleScenario中的规则，查看__data中的值，如果规则成立，则根据规则进行值的修改
    #change_list = [name="IN_RM_PB1" value="1"  delay="0"]
    #返回，是否修改，修改了返回True，反之，返回False
    #--------------------------------------------------------------------------- 
    def checkRule( self ):
        "change __data througt rules"
        _retchange = False
        for _rulekey in self.ruleScenario:
            _rule = self.ruleScenario[_rulekey]
            if self.getcurRuleValue( _rule ):
                #触发值的改变
                _change_item = _rule['reaction'] #获取需要该值的列表
                for _item in _change_item:
                    if 0 == int( _item[2] ):
                        _name = _item[0]
                        _value = self.ParserValuetype[self.getVarDic()[_item[0]][0]]( _item[1] ) #根据类型进行转换
                        self.addDataKeyValue( _name, _value )
                        _retchange = True
                    else: #需要延时的，将其压入全局列表
                        self.rulechangelist.append( [_item[0], _item[1], int( _item[2] )] )
        
        #查看延时修改的值，将到时间的值进行修改
        _changed_index = []
        for _index, _change in enumerate( self.rulechangelist ):
            if 0 == _change[2]:#延时到了
                _name = _change[0]                
                try:
                    _value = self.importFileParser['var']['type'][self.getVarDic()[_change[0]][0]]( _change[1] ) #根据类型进行转换
#                    print "rule dic1", _change, self.getVarDic()[_change[0]]
                except KeyError, e:
                    print self.rulechangelist
                    print "rule dic2", _change, self.getVarDic()[_change[0]], e
                self.addDataKeyValue( _name, _value )
                _changed_index.append( _index )
                _retchange = True
            else:
                self.rulechangelist[_index][2] -= 1 
        
        for _index in _changed_index: #将已修改的pop出来
            self.rulechangelist.pop( _index )
        
        return _retchange
                
        
    #---------------------------------------------------------------------------
    #@计算某个rule的值，成立返回true，反之返回false
    #---------------------------------------------------------------------------    
    def getcurRuleValue( self, rule ):
        "calculate rule value"
        _operator = rule['operator']
        _type = rule['type']
        if 'exp' == _type:
            #获取left和right的值
            _left = rule['left']
            _right = rule['right']
            
            if _left['type'] == 'Const':
                _leftValue = self.calculateSubExp( _left, _right['value'] )
            else:
                _leftValue = self.calculateSubExp( _left )
                
            if _right['type'] == 'Const':
                _rightValue = self.calculateSubExp( _right, _left['value'] )
            else:
                _rightValue = self.calculateSubExp( _right )
                
            #计算表达式的值
            return self.calculateValueformOp( _leftValue, _rightValue, _operator )

        elif 'Mexp' == _type:
            #获取exps
            _exps = rule['exps']
            return self.calulateExps( _exps, _operator )
            
    #---------------------------------------------------------------------------
    #@计算子表达式的值
    #{'type':'Variant','value':'name'}
    #{'type':'exp','value':'AND','left':{},'right':{}}
    #{'type':'Mexp','value':'AND',exps:[{},{}....]}
    #valuename:在变量为常数的时候使用，用来获取变量的类型
    #---------------------------------------------------------------------------
    def calculateSubExp( self, exp, valuename = '' ):
        "calculate sub expression"
        _type = exp['type']
        _value = exp['value']
        if 'Variant' == _type:
            return self.getDataValue( exp['value'] )
        elif 'Const' == _type:  #根据数值的类型进行转换
            return self.ParserValuetype[self.getVarDic()[valuename][0]]( _value )
        elif 'exp' == _type:
            _left = exp['left']
            _right = exp['right'] 
                       
            if _left['type'] == 'Const':
                _leftValue = self.calculateSubExp( _left, _right['value'] )
            else:
                _leftValue = self.calculateSubExp( _left )
                
            if _right['type'] == 'Const':
                _rightValue = self.calculateSubExp( _right, _left['value'] )
            else:
                _rightValue = self.calculateSubExp( _right )
                
            _operate = exp['value']
            return self.calculateValueformOp( _leftValue, _rightValue, _operate )

        elif 'Mexp' == _type:
            _operate = exp['value']
            _exps = exp['exps']
            return self.calulateExps( _exps, _operate )
        else:
            print 'Error Expression type!'
            
        
    #---------------------------------------------------------------------------
    #@计算多从表达式的值
    #---------------------------------------------------------------------------
    def calulateExps( self, exps, operator ):
        "calculate Muti expression"
        _rt = None
        for _exp in exps:
            if None == _rt:
                _rt = self.calculateSubExp( _exp )
            elif 'AND' == operator:
                _rt = _rt and self.calculateSubExp( _exp )
            elif 'OR' == operator:
                _rt = _rt or self.calculateSubExp( _exp )
        return _rt
                
    
    #---------------------------------------------------------------------------
    #@根据operator计算结果
    #---------------------------------------------------------------------------
    def calculateValueformOp( self, leftValue, rightValue, operator ):
        "calculator Expression Value"
        if "==" == operator:
            return ( leftValue == rightValue )
        elif "GT" == operator:     
            return ( leftValue > rightValue )
        elif "LT" == operator:     
            return ( leftValue < rightValue )
        elif "GE" == operator:     
            return ( leftValue >= rightValue ) 
        elif "LE" == operator:     
            return ( leftValue <= rightValue )
        elif "AND" == operator:     
            return ( leftValue and rightValue )
        elif "OR" == operator:     
            return ( leftValue or rightValue )
        
    # --------------------------------------------------------------------------
    ##
    # @Brief 获得设备变量字典
    #
    # @Returns var dict
    # --------------------------------------------------------------------------
    def getVarDic( self ):
        " get var dict"
        return self.__var


    # --------------------------------------------------------------------------
    ##
    # @Brief 获得设备消息字典
    #
    # @Returns msg dict
    # --------------------------------------------------------------------------
    def getMsgDic( self ):
        " get var dict"
        return self.__msg

        
    # --------------------------------------------------------------------------
    ##
    # @Brief 添加数据到字典，注意相同的key会覆盖
    #
    # @Param key
    # @Param value
    #
    # @Returns True
    # --------------------------------------------------------------------------
    def addDataKeyValue( self, key, value ):
        " add data into device data dic"
        self.__data[key] = value
        return True

    # --------------------------------------------------------------------------
    ##
    # @Brief 添加数据到__var字典，注意相同的key会覆盖
    #
    # @Param key
    # @Param value
    #
    # @Returns True
    # --------------------------------------------------------------------------
    def addVarKeyValue( self, key, value ):
        " add data into device var dic"
        self.__var[key] = value
        return True
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 添加数据到__msg字典，注意相同的key会覆盖
    #
    # @Param key
    # @Param value
    #
    # @Returns True
    # --------------------------------------------------------------------------
    def addMsgKeyValue( self, key, value ):
        " add data into device msg dic"
        self.__msg[key] = value
        return True    
    
    def getDataValue( self, key ):
        " get value by key"
        try:
            return self.__data[key]
        except KeyError, e:
            print 'KeyError', e
            return None

    def getDataKeys( self ):
        " get all keys in data"
        return self.__data.keys()

    def delDataKeyValue( self, key ):
        " del key in data"
        try:
            del self.__data[key]
            return True
        except KeyError, e:
            print 'KeyError', e 
            return None
    
    def clearDataDic( self ):
        " clear all data"
        self.__data.clear()

    def getDataDic( self ):
        " get device dataList"
        return self.__data
        
    def getDeviceName( self ):
        " get device name"
        return self.__deviceName

    def getDeviceId( self ):
        " get device id"
        return self.__deviceId
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 在字典中批量添加项目
    #
    # @Param keyList key列表
    # @Param valueList 与key列表对应的值
    #
    # @Returns True or False
    # --------------------------------------------------------------------------
    def setManyKeyValue( self, keyList, valueList ):
        " set many key and values"
        if len( keyList ) > 0 and len( keyList ) == len( valueList ):
            for _i, _a in enumerate( keyList ):
                self.addDataKeyValue( _a, valueList[_i] )
            return True
        else:
            return False
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 在数据字典中添加设备实例
    #
    # @Param key 设备类别
    # @Param deviceObjectList 设备对象列表
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def attachDeviceObject( self, key, deviceObjectList ):
        " attach device instance to device instance"
        self.addDataKeyValue( key + self.obj, \
                [( _d.getDeviceId(), _d ) for _d in deviceObjectList] )
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 获得设备实例，若有设备索引则匹配索引
    #
    # @Param deviceType
    # @Param indList
    #
    # @Returns 设备对象列表
    # --------------------------------------------------------------------------
    def getDeviceObjList( self, deviceType, indList = [] ):
        " get device instance List"
        if len( indList ):
            _lo = self.getDataValue( deviceType + self.obj )
            #return [_l[self.objB] for _l in _lo if _l[self.objN] in indList]
            return [_d[self.objB] for _l in indList for _d in _lo if _d[self.objN] == _l]

        else:
            return [_d[self.objB]for _d in self.getDataValue( deviceType + self.obj )]
    
    def getDevObjDic( self, deviceType ):
        " get device object dict"
        return [ deviceType + '.' + repr( _d.getDeviceId() ) + repr( _d.getDataDic() ) for _d in self.getDeviceObjList( deviceType )]

    # --------------------------------------------------------------------------
    ##
    # @Brief 打包应用消息
    #
    # @Param msgId
    # @Param args
    #
    # @Returns msg
    # --------------------------------------------------------------------------
    def packAppMsg( self, msgId, *args ):
        try:
            _msg = struct.pack( self.__msg[msgId]['format'], *args )
        except struct.error, e:
            print 'packAppMsg error:', e, 'msgId', msgId
            return None
        return _msg
    # --------------------------------------------------------------------------
    ##
    # @Brief 解析应用层消息
    #
    # @Param msgId
    # @Param mes 消息字符串
    #
    # @Returns 消息列表
    # --------------------------------------------------------------------------
    def unpackAppMsg( self, msgId, mes ):
        " unpack application message"
        try:
            _mes = struct.unpack( self.__msg[msgId]['format'], mes )
        except struct.error, e:
            print 'unpackAppMsg error:', e, 'MESID:', msgId
            return None
        return _mes

    #-------------------------------------------------------------
    #@默认消息处理函数
    #@将消息放入对应的变量中去
    #@根据消息Id
    #-------------------------------------------------------------
    def defaultMsgHandle( self, msgId, mes ):
        ""
    
    def deviceInit( self, *args, **kwargs ):
        " init need to do"
        #TODO 导入变量、应用消息、设备数据解析、控制脚本解析、离线数据计算等
        pass
    
    def deviceRun( self, *args, **kwargs ):
        " running need to do"
        #TODO 设备变量维护、应用消息生成等
        pass

    def deviceRunWithExceptHandle( self, *args, **kwargs ):
        " running need to do"
        #添加了异常收集设备Run函数
        try:
        	self.deviceRun()
        except ( NameError, ZeroDivisionError,
                 IndexError, KeyError,
                 IOError, AttributeError,
                 ValueError, TypeError ), e:
            print "deviceRunWithExceptHandle", "Dev Name:" , self.getDeviceName() , "ID:", str( self.getDeviceId() ), e
            excepthandle.ExceptHandleQ.put( ( 1,
                                              commlib.curTime(),
                                              "Dev Name:" + self.getDeviceName() + "ID:" + str( self.getDeviceId() ),
                                              e ) 
                                           )
        except:#其余的error
            print "deviceRunWithExceptHandle error", "Dev Name:" , self.getDeviceName() , "ID:", str( self.getDeviceId() )
            excepthandle.ExceptHandleQ.put( ( 1,
                                              commlib.curTime(),
                                              "Dev Name:" + self.getDeviceName() + "ID:" + str( self.getDeviceId() ),
                                              "deviceRunWithExceptHandle error" )             
                                           )
    
    def deviceEnd( self, *args, **kwargs ):
        " ending need to do"
        #TODO
        pass
    
    def deviceExcept( self, *args, **kwargs ):
        " when except need to do"
        #TODO 设备运行过程中的异常处理
        pass

if __name__ == '__main__':
    b = BaseDevice( 'base', 1 )
    b.importVarint( r'./varint.xml' )
    print 'var dic', b.getVarDic()
    print 'data dic', b.getDataDic()
    b.importMsg( r'./message.xml' )
    print 'msg dic', b.getMsgDic()
    b.importDefSce( r'./scenario.xml' )
    print 'scenario', b.defScenario
    print 'Timescenario', b.TimeScenario
