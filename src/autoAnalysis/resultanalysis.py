#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     resultanalysis.py
# Description:  结果分析模块    
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2012-12-04
# Company:      CASCO
# LastChange:   update 2012-12-04
# History:      2012-12-04 创建本文件
#               
#----------------------------------------------------------------------------
from base.xmlparser import XmlParser
import math
from base import simdata
import os
from inputHandle import OMAPInput, UsrDefInput
from base.xmldeal import XMLDeal
from expressionparser import ExpressionParser

class ResultAnalysis( object ):
    """
    Result Analysis class
    """
    
    #导入的数据实例
    __OMAPDataControl = None
    __UserDefDataControl = None

    #分析脚本相关字典
    #变量字典，存储在脚本中申明的变量以及源，包括以下几种可能
    #Type = 0：format过来的数据，存储格式：VarName:["0",Name]
    #Type = 1: const数据，存储格式：VarName:["1",Name]
    #Type = 2: Map数据，存储格式：VarName:["2",Name,Attr],其中Attr是一个按照格式书写的string，是需要解析的
    #Type = 3: 用户自定义数据，存储格式：VarName:["3",RuleDic]
    #RuleDic是一个规则字典，具体形式如下：
    #双目形式：{"Type":"BOP","Value":"OR","exp1":RuleDic,"exp2":RuleDic}
    #单目形式：{"Type":"UOP","Value":"NOT","exp1":RuleDic}
    #最终表现形式：
    #{"Type"："Variant","Value":"EBRD"}
    #{"Type"："ConstInt","Value":"1"}
    #{"Type"："ConstFloat","Value":"1.6"}
    #{"Type"："ConstStr","Value":"abc"}
    #{"Type"："RULEBASE","Value":RuleId}
    __VariantsDic = None #在字典中未定义的变量，自动认为是在format中定义的变量
    #规则检查字典：
    #{TestCaseName:{"Pos":[start,end],"Time":[start,end],
    #                "OP":[{"condition":RuleDic,"result":[RuleDic,...],"Type":"UserDef"},...]},...}
    #OP有两种形式一种是自定义的{"condition":RuleDic,"result":[RuleDic,...],"Type":"UserDef","Value":""}
    #一种是从库里面取的{"condition":RuleDic,"result":[RuleDic,...],"Type":"CommDef","Value":""}
    #每个TC下面支持多个OP,每个condition下面支持多个result
    #规则中有一类Type = "RULEBASE",这时，规则将到规则库中去寻找 (通过ID进行查询)
    __AnalysisRuleDic = None

    #记录当前分析的周期
    CurCycle = None
    
#    #导入autoAnalysis的节点
#    autoAnalysisNode = {"Vars":{"path":".//Var",
#                                "attr":['Type', 'Id', 'Attr', 'Des'] },
#                        "Rules":{"path":".//Rules",
#                                 "attr":['TC', 'Des'] },
#                        "Lexp":{"path":".//lexp",
#                                "attr":["Type", "Value"]},
#                        "Rexp":{"path":".//rexp",
#                                "attr":["Type", "Value"]},
#                        "Exp": {"path":".//exp",
#                                "attr":["Type", "Value"]},
#                        "Pos":{"path":".//Pos",
#                                "attr":["Start", "End" , "Des"]},
#                        "Time":{"path":".//Time",
#                                "attr":["Begin", "End" , "Des"]},
#                        "PreCon":{"path":".//Precondition",
#                                  "attr":["Type", "Value" , "Des"]},
#                        "Result":{"path":".//Result",
#                                  "attr":["Type", "Value" , "Des"]},
#                        "OP":{"path":".//Op",
#                                  "attr":["Type", "Value"]},
#                        "Rule":{"path":".//Rule",
#                                  "attr":["Name", "Type", "Value"]},
#                        "ReqOP":{"path":".//Op",
#                                  "attr":["Name"]}
#                        }
    
    #用于打印时的标准字符串
    __PrintHead = "#############################################################################\n"
    __PrintInterval = "-----------------------------------------------------------------------------\n"
    #基本规则单元字典
    __BaseRuleDic = None #基本单元库,RuleDic
    
    #通用的需求规则库字典
    __CommRuleDic = None #由OP构成的字典,OP
    
    #Log文件的路径
    __saveLogPath = None
    
    def __init__( self ):
        "init"
        self.__BaseRuleDic = {}
        self.__CommRuleDic = {}
        self.CurCycle = 0

    #------------------------------------------------------------------------------------
    #初始化自动分析脚本
    #本文件将导入所有自动分析需要计算的配置文件
    #kwargs["PathType"]:有两种，"OnlyDir":一种是给定地图路径，脚本路径的，"All"一种是给出所有文件的加载路径的
    #------------------------------------------------------------------------------------
    def AnalysisInit( self, *args, **kwargs ):
        "Analysis initial"
        if "All" == kwargs["InitType"]:
            _binpath = kwargs["binpath"]
            _txtpath = kwargs["txtpath"]
            _trainroutepath = kwargs["trainroutepath"]
            _analysispath = kwargs["analysispath"]
            self.__saveLogPath = kwargs["saveLogPath"]
            _omaplogpath = kwargs["omaplogpath"]
        elif "OnlyDir" == kwargs["InitType"]:
            _mappath = kwargs["mappath"]
            _scriptpath = kwargs["scenariopath"]
            _logpath = kwargs["logpath"]
            _binpath = os.path.join( _mappath, "atpCpu1Binary.txt" )
            _txtpath = os.path.join( _mappath, "atpText.txt" )
            
            _scenariopath1 = os.path.join( _scriptpath, "scenario" )
            _scenariopath2 = os.path.join( _scriptpath, "autoanalysis" )
            _logpath1 = os.path.join( _logpath, "analysislog" )
            
            _trainroutepath = os.path.join( _scenariopath1, "train_route.xml" )
            _analysispath = os.path.join( _scenariopath2, "autoAnalysis.xml" )
            self.__saveLogPath = os.path.join( _logpath1, "analysisResult.log" )
            _omaplogpath = None
        else:
            print "AnalysisInit Error!", kwargs["InitType"]
            return None        
            
        #导入分析的数据
        self.__OMAPDataControl = OMAPInput()
        
        self.__OMAPDataControl.importEnuDic( r'./TPConfig/Enumerate.xml' )
        self.__OMAPDataControl.importFormat( r'./TPconfig/OMAPFormat.xml' )
        self.__OMAPDataControl.LoadZipOMAPData( _omaplogpath )
        
        self.__UserDefDataControl = UsrDefInput()
        self.__UserDefDataControl.loadUsrDefDat( r'./autoAnalysis/config/usrData.xml', ReadDes = False )
        self.__BaseRuleDic = self.__UserDefDataControl.getUsrDict()
        #simdata 的导入
        simdata.MapData.loadMapData( _binpath, _txtpath )
        simdata.TrainRoute.loadTrainData( _trainroutepath )
        #自动分析脚本的导入
#        self.importBaseRuleDic( "./config/baseRules.xml" ) #baserule从usrdata中获取
        self.importCommRuleDic( "./autoAnalysis/config/userRequirementRules.xml" )
        self.importAnalysisfile( _analysispath )

    #--------------------------------------------------------------
    #开始自动分析
    #--------------------------------------------------------------
    def startAnalysis( self ):
        "start analysis"
        _logfile = open( self.__saveLogPath, "w" )
        _AnalysisLogDic = self.RunAnalysis()
        print _AnalysisLogDic
        _printLog = self.printAnalysisResult( _AnalysisLogDic ) #以后存文件
        
        print _printLog
        
        _logfile.write( _printLog )
        _logfile.close()
        
    #--------------------------------------------------------------
    #运行自动分析
    #--------------------------------------------------------------
    def RunAnalysis( self ):
        "run analysis"
#        _PassLogDic = [] #pass记录表，用于记录分析过程中pass的关键点:包括周期，以及对应的条件和需求等等
#        _FailLogDic = [] #fail记录表，用于记录分析过程中fail的关键点:包括周期，以及对应的条件和需求等等
        _AnalysisLogDic = {} #用于记录分析每个步骤的pass，fail内容具体格式如下：
        #{RuleKey:RuleListLog,...}
        #RuleListLog = [OPListLog,...] 多个OPlog
        #OPListLog = [[cycleNum,[resultLog,...]] #这里只记录满足条件时的周期号以及result的状态
        #resultLog为满足condition条件时的结果校验值
        for _RuleKey in self.__AnalysisRuleDic:
            _RuleCheck = self.__AnalysisRuleDic[_RuleKey]
            _AnalysisLogDic[_RuleKey] = []
            #先计算需要进行分析的起始和结束周期
            [_start, _End] = self.__OMAPDataControl.ifOmapCycleNo( _RuleCheck["Time"][0],
                                                                   _RuleCheck["Time"][1],
                                                                   _RuleCheck["Pos"][0],
                                                                   _RuleCheck["Pos"][1] ) #这个函数由数据准备提供
            
            #按照OP进行逐个分析
            for _conIndex, _condition in enumerate( _RuleCheck["OP"] ):
                
                if "CommDef" == _condition["Type"]:#不是自定义的条件要从库里面取
                    _condition = self.getCommRuleDic()[_condition["Value"]]
                    
                #遍历周期
                _tempOPList = []
                for _cycle in range( _start + 2, _End - 2 ): #首位偏移掉两个周期以避免出现越界的情况
                    #第几个周期分析
                    self.CurCycle = _cycle
#                    print "------------", _condition
#                    print self.CurCycle, self.getValueFromOMAP( "ValidTrainKinematic", _cycle ), \
#                        self.getValueFromOMAP( "LocalizationState", _cycle ), self.getValueFromOMAP( "LocalizationFault", _cycle ), self.getValueFromOMAP( "PointCrossed", _cycle )
                    if self.getRuleValueInCurCycle( _condition["condition"] ): #满足条件
                        _tempresultList = []
                        _tempOneOP = [self.CurCycle]
                        for _result in _condition["result"]:
#                            print "tst", _result
                            _tempresultList.append( self.getRuleValueInCurCycle( _result ) )
                        _tempOneOP.append( _tempresultList )
                        _tempOPList.append( _tempOneOP )
                
                _AnalysisLogDic[_RuleKey].append( _tempOPList )
        
        return _AnalysisLogDic
                            
    #---------------------------------------------------------------
    #自动分析结果打印
    #主要基于RunAnalysis获得的结果进行关键信息的打印
    #AnalysisLogDic = {} #用于记录分析每个步骤的pass，fail内容具体格式如下：
    #{RuleKey:RuleListLog,...}
    #RuleListLog = [OPListLog,...] 多个OPlog
    #OPListLog = [[cycleNum,[resultLog,...]]] #这里只记录满足条件时的周期号以及result的状态
    #resultLog为满足condition条件时的结果校验值    
    #---------------------------------------------------------------
    def printAnalysisResult( self, AnalysisLogDic ):
        "print Analysis Result"
        _revStr = ""
        #遍历所有的分析结果，按照TC遍历
        for _TCKey in AnalysisLogDic:
            _TmpAnalysisDic = self.getAnalysisRuleDic()[_TCKey]
            #打印TC头
            _revStr += self.__PrintHead
            _revStr += "TCName: " + _TCKey + "\n"
            _revStr += "StartTime(cycle): " + \
                        str( _TmpAnalysisDic["Time"][0] ) + " " + \
                        ", EndTime(cycle): " + \
                        str( _TmpAnalysisDic["Time"][1] ) + "\n"
            _revStr += "StartPos(mm): " + \
                        str( _TmpAnalysisDic["Pos"][0] ) + " " + \
                        ", EndPos(mm): " + \
                        str( _TmpAnalysisDic["Pos"][1] ) + "\n"
            _revStr += self.__PrintHead
            
            _revStr += "Start OP Check:\n"
            #遍历各个OP并打印结果
#            print "@@@", _TCKey, AnalysisLogDic[_TCKey], AnalysisLogDic[_TCKey]["OP"]
            for _index, _op in enumerate( AnalysisLogDic[_TCKey] ): 
                #打印需要进行判断的信息
                _revStr += self.__PrintInterval
                _revStr += "OP" + str( _index ) + " Rule:" + "\n"
                #这里要判断OP是自定义的还是库里面的，库里面的要进行读取转换
                _revStr += self.transSingleOPToString( self.getRealOPDic( _TmpAnalysisDic["OP"][_index] ) ) 
                _revStr += self.__PrintInterval
                
                if len( _op ) > 0: #判断是否有满足条件的周期
                    _tmpOPResult = self.handleOneOPLog( _op )
                    for _r in _tmpOPResult:
                        if _tmpOPResult[_r][0]:
                            _revStr += self.printSuccessCycle( _r )
                        else:
                            _revStr += self.printFailCycle( _r,
                                                            _tmpOPResult[_r],
                                                            _TmpAnalysisDic["OP"][_index]["result"] )
                else: #不存在满足条件的周期
                    _revStr += "There is no cycle that satisfy the condition:\n" + \
                                self.transRuleDicToString( _TmpAnalysisDic["OP"][_index]["condition"] ) + "\n" + \
                                "here. Please check the case script!!!\n"
                _revStr += self.__PrintInterval
        return _revStr
    
    #----------------------------------------------------------------
    #获取真实的OP字典，对于库里面的，要取出来
    #----------------------------------------------------------------
    def getRealOPDic( self, OPDic ):
        "get real op dic"
        if "CommDef" == OPDic["Type"]:
            return self.getCommRuleDic()[OPDic["Value"]] 
        else:
            return OPDic  
    
    #----------------------------------------------------------------
    #获取真实的Rule字典，库里面的也要取出来
    #----------------------------------------------------------------
    def getRealRuleDic( self, RuleDic ):
        "get real rule dic"
        if "RULEBASE" == RuleDic["Type"]:
            return self.getBaseRuleDic()[RuleDic["Value"]] 
        else:
            return RuleDic      
                
    #----------------------------------------------------------------
    #打印校验成功的周期
    #----------------------------------------------------------------
    def printSuccessCycle( self, cycle ):
        "print success cycle"
        return "Analysis success in cycle:" + str( cycle ) + "\n"   
    
    #----------------------------------------------------------------
    #打印校验失败的周期
    #cycleinfo:[Successflag,FailResultList]
    #resultinfo:[resultRuleDic,...]
    #----------------------------------------------------------------
    def printFailCycle( self, cycle, cycleinfo, resultinfo ):
        "print fail cycle"
        _revStr = ""
        _revStr += "Analysis fail in cycle:" + str( cycle ) + "\n" 
        for _index in cycleinfo[1]:
            _revStr += "Analysis fail in result check index:" + str( _index ) + "\n"
            _revStr += "And the result check rule is: \n" + \
                         self.transRuleDicToString( resultinfo[_index] ) + "\n"
        
        return _revStr
                    
                
    #----------------------------------------------------------------
    #检查OneOPLog中是否有成功的，和失败的，并返回对应的标签
    #OneOPLog:[[cycleNum,[resultLog,...]]]
    #返回标签的形式如下：
    #{CycleNum:[Successflag,FailResultList]}
    #当某个周期是成功的时候CycleNum:[True,[]]
    #当某个周期是失败的时候CycleNum:[False,[FailResultIndex,...]]
    #----------------------------------------------------------------
    def handleOneOPLog( self, OneOPLog ):
        "handle one OP Log"
        _revDic = {}
        for _OneCycleOPLog in OneOPLog:
            _cycle = _OneCycleOPLog[0]
            _revDic[_cycle] = []
            _resultList = _OneCycleOPLog[1]
            _failResultList = []
            for _index, _tmpresult in enumerate( _resultList ):
                if not bool( _tmpresult ):
                    _failResultList.append( _index )
            if len( _failResultList ) > 0:
                _revDic[_cycle] = [False, _failResultList] 
            else:
                _revDic[_cycle] = [True, _failResultList] 
        return _revDic       
              
    #---------------------------------------------------------------
    #将RuleDic转换为String输出，形如
    #    b == a + c
    #---------------------------------------------------------------            
    def transRuleDicToString( self, RuleDic ):
        "transform rule dic to string"
        #函数移到ExpressionParser中去了，方便其他文件调用
        return ExpressionParser.transRuleDicToString( RuleDic )
    
    #---------------------------------------------------------------
    #将OP转换为用户可识别的字符串集合，形式如下：
    #if a == 1:
    #    b = c+d
    #op:{"condition":RuleDic,"result":[RuleDic,...]}
    #---------------------------------------------------------------
    def transSingleOPToString( self, OP ):
        "transform single OP to string"
        _revStr = ""
        _conditionStr = self.transRuleDicToString( self.getRealRuleDic( OP["condition"] ) )
        _revStr += "if " + _conditionStr + "==True:\n"
        for _result in OP["result"]:
            _revStr += "    " + self.transRuleDicToString( self.getRealRuleDic( _result ) ) + "==True\n"
        
        return _revStr

    #---------------------------------------------------------------
    #获取当前进行进行分析的周期号
    #---------------------------------------------------------------
    def getCurCycle( self ):
        "get current cycle"
        return self.CurCycle
    
    #---------------------------------------------------------------
    #导入通用的计算规则
    #注意baserule中不应该有嵌套，也即baserule包含baserule
    #---------------------------------------------------------------
    def importBaseRuleDic( self, path ):
        "import Base Rule Dic"
        self.__BaseRuleDic = XMLDeal.importBaseRule( path )
#        print self.__BaseRuleDic

    #-------------------------------------------------------------
    #导入用户需求的判断条件库
    #-------------------------------------------------------------
    def importCommRuleDic( self, path ):
        "import common rules Dic"
        self.__CommRuleDic = XMLDeal.importCommRule( path, self.getBaseRuleDic() )         
        
    def getBaseRuleDic( self ):
        return self.__BaseRuleDic
    
    def getCommRuleDic( self ):
        return self.__CommRuleDic
    
    def importAnalysisfile( self, path ):
        "import analysis file"
        self.__VariantsDic, \
        self.__AnalysisRuleDic = XMLDeal.importAnalysisDic( path,
                                                            BaseRule = self.getBaseRuleDic(),
                                                            CommOP = self.getCommRuleDic(),
                                                            ReadDes = False )
#        print self.__VariantsDic

    def getVariantsDic( self ):
        return self.__VariantsDic
    
    def getAnalysisRuleDic( self ):
        return self.__AnalysisRuleDic
    
#    #------------------------------------------------------------------
#    #从导入的XML中提取Rules对应的数据
#    #XMlfilehandle是由XmlParser生成的XML文件句柄
#    #Node:单个rule节点
#    #------------------------------------------------------------------
#    def getRulesDic( self, XMlfilehandle, Node ):
#        "get Rules dic"
#        _ruleDic = {}
#        #读取位置和时间信息
#        _PosNode = XMlfilehandle.getNodeInNode( Node, self.autoAnalysisNode["Pos"]["path"] )
#        if None != _PosNode:
#            _attrlist = XMlfilehandle.getAttrListOneNode( _PosNode,
#                                                         self.autoAnalysisNode["Pos"]["attr"] )
#            _ruleDic["Pos"] = [int( _attrlist[0] ), int( _attrlist[1] )]
#        else:
#            _ruleDic["Pos"] = [None, None]        
#        _TimeNode = XMlfilehandle.getNodeInNode( Node, self.autoAnalysisNode["Time"]["path"] )
#        if None != _TimeNode:
#            _attrlist = XMlfilehandle.getAttrListOneNode( _TimeNode,
#                                                         self.autoAnalysisNode["Time"]["attr"] )
##            print _attrlist
#            _ruleDic["Time"] = [int( _attrlist[0] ), int( _attrlist[1] )]
#        else:
#            _ruleDic["Time"] = [None, None]
#        
#        #读取OP
#        _OPList = []
#        _OPListNode = XMlfilehandle.getNodeListInNode( Node,
#                                                   self.autoAnalysisNode["OP"]["path"] )
##        print _OPListNode
#        for _opNode in _OPListNode:
##            print _opNode, Node
#            _type, _value = XMlfilehandle.getAttrListOneNode( _opNode,
#                                                              self.autoAnalysisNode["OP"]["attr"] )
#            if "UserDef" == _type:
#                _OPList.append( self.getOPDic( XMlfilehandle, _opNode, _type, _value ) )
#            elif "CommDef" == _type:
#                #{"Type":"CommDef","Value":""}
#                if self.getCommRuleDic().has_key( _value ):
#                    _OPList.append( {"Type":"CommDef", "Value":_value} )
#                else:    
#                    print "getRulesDic Error1!", _value
#                    return None
#            else:
#                print "getRulesDic Error ! ", _type, _value
#        _ruleDic["OP"] = _OPList
#        
#        _name = XMlfilehandle.getAttrListOneNode( Node, self.autoAnalysisNode["Rules"]["attr"] )[0]
#        
#        return _name, _ruleDic
#        
#    
    #------------------------------------------------------------------
    #从导入的XML的OP的节点中获取所有的变量信息
    #XMlfilehandle是由XmlParser生成的XML文件句柄
    #------------------------------------------------------------------
    def getOPDic( self, XMlfilehandle, Node, Type, Value ):
        "get OP dic"
        return XMLDeal.parserOPDic( XMlfilehandle, Node, self.getBaseRuleDic(), Type, Value )

#    #------------------------------------------------------------------
#    #从导入的XML的Variants的节点中获取所有的变量信息
#    #XMlfilehandle是由XmlParser生成的XML文件句柄
#    #------------------------------------------------------------------
#    def getVariantDic( self, XMlfilehandle, Node ):
#        "get variant dic"
#        _VarList = XMlfilehandle.getNodeListInNode( Node, self.autoAnalysisNode["Vars"]["path"] )
#        for _var in _VarList:
#            _attrlist = XMlfilehandle.getAttrListOneNode( _var, self.autoAnalysisNode['Vars']['attr'] )
#            if "0" == _attrlist[0]: #来自omap
#                self.__VariantsDic[_attrlist[1]] = _attrlist[0:2]
#            elif "1" == _attrlist[0]: #常量
#                self.__VariantsDic[_attrlist[1]] = _attrlist[0:2]
#            elif "2" == _attrlist[0]: #MAP数据
#                self.__VariantsDic[_attrlist[1]] = _attrlist[0:3]
#            elif "3" == _attrlist[0]: #用户自定义变量
#                self.__VariantsDic[_attrlist[1]] = ["3",
#                                                    self.getRuleDic( XMlfilehandle,
#                                                                    _var.find( "VarDef" ) )
#                                                    ]
#            else:
#                print "getVariantDic Error ! ", _attrlist
    
    #-----------------------------------------------------
    #获取规则脚本字典RuleDic
    #XMlfilehandle是由XmlParser生成的XML文件句柄
    #FatherNode:XML的规则脚本的父节点
    #-----------------------------------------------------
    def getRuleDic( self, XMlfilehandle, FatherNode ):
        "get Rule dic"
        return XMLDeal.parserRuleDic( XMlfilehandle, FatherNode, self.getBaseRuleDic() )

    #-----------------------------------------------------
    #计算一个规则在某个周期的结果值
    #输入为一个RuleDic
    #-----------------------------------------------------
    def getRuleValueInCurCycle( self, ruleDic ):
        "get rule value in current cycle"
        if "ConstInt" == ruleDic["Type"]:
            return int( ruleDic["Value"] )
        elif "ConstFloat" == ruleDic["Type"]:
            return float( ruleDic["Value"] )
        elif "Variant" == ruleDic["Type"]:
            #查看是否有偏移
            _temp = ruleDic["Value"].split( "#" )
            if len( _temp ) >= 2:
                return self.getCurVariantValue( _temp[0], int( _temp[1] ) )
            else:
                return self.getCurVariantValue( _temp[0] )
        elif "ConstStr" == ruleDic["Type"]:
            return ruleDic["Value"]
        elif "BOP" == ruleDic["Type"]: #双目运算符
            #取出左右的运算符并计算结果,注：这里的string只能用于执行双目运算符的
            #双目形式：{"Type":"BOP","Value":"OR","exp1":RuleDic,"exp2":RuleDic}
            _exp1Value = self.getRuleValueInCurCycle( ruleDic["exp1"] )
            _exp2Value = self.getRuleValueInCurCycle( ruleDic["exp2"] )
            _OP = ruleDic["Value"]
            return self.calculateBOP( _exp1Value, _exp2Value, _OP ) 
        elif "UOP" == ruleDic["Type"]: #单目运算符
            #单目形式：{"Type":"UOP","Value":"NOT","exp1":RuleDic}
            _expValue = self.getRuleValueInCurCycle( ruleDic["exp1"] )
            _OP = ruleDic["Value"]
            return self.calculateUOP( _expValue, _OP )
#            return self.calculateBOP( _expValue, _OP )
        elif "RULEBASE" == ruleDic["Type"]: #来自baserule
            _tmprule = self.getBaseRuleDic()[ruleDic["Value"]]
            return self.getRuleValueInCurCycle( _tmprule )
        
        print "getRuleValueInCurCycle unKnow Type:", ruleDic["Type"]
        return None
            
    #--------------------------------------------------------
    #单目运算
    #--------------------------------------------------------
    def calculateUOP( self, value, operator ):
        "calculate UOP"
        [_valueNum, _valueStr] = self.handleParameter( value )
        if None == _valueNum:
            print "calculateUOP ERROR1", value
            return None
                
        # NOT FLOOR CEIL                       
        try:
            if  "NOT" == operator:
                return ( not _valueNum )
            elif "FLOOR" == operator:
                return math.floor( _valueNum )
            elif "CEIL" == operator:
                return math.ceil( _valueNum )
            else:
                print "calculateUOP Error!!!", value, operator
        except:
            print "calculateUOP Error3!!!", value, operator 
            return None        

    #----------------------------------------------------------------
    #处理单双目的参数，由于参数有数字和列表两种形式，所以需要事先进行处理
    #----------------------------------------------------------------
    def handleParameter( self, value ):
        "handle Parmeter"
        if type( value ) == type( [] ):
            _valueNum = value[0]
            _valueStr = value[1]
        elif type( value ) in  [int, bool, float]:
            _valueNum = value
            _valueStr = None
        elif type( value ) == str:
            _valueNum = None
            _valueStr = value
        else:
            print "calculateBOP ERROR1", value
            return [None, None]
        return [_valueNum, _valueStr]    
    
    #---------------------------------------------------------
    #双目运算
    #---------------------------------------------------------        
    def calculateBOP( self, value1, value2, operator ):
        "calculate BOP"
        #检查参数是否带有数字和字符串两种类型
        [_value1Num, _value1Str] = self.handleParameter( value1 )
        if [None, None] == [_value1Num, _value1Str]:
            print "calculateBOP ERROR1", value1
            return None
        
        [_value2Num, _value2Str] = self.handleParameter( value2 ) 
        if [None, None] == [_value2Num, _value2Str]:
            print "calculateBOP ERROR2", value2
            return None

        # OR AND GE GT LE LT EQ XOR XNOR ADD SUB MUL DIV POW MOD
        #以上逻辑运算都是整体的，最后值都应该是bool值                       
        try:
            if  "AND" == operator:
                return bool( _value1Num and _value2Num )
            elif "OR" == operator:
                return bool( _value1Num or _value2Num )
            elif "GE" == operator:
                return ( _value1Num >= _value2Num )
            elif "GT" == operator:
                return ( _value1Num > _value2Num )
            elif "LE" == operator:
                return ( _value1Num <= _value2Num )
            elif "LT" == operator:
                return ( _value1Num < _value2Num )
            elif "EQ" == operator:
                if None not in [_value1Num , _value2Num, _value1Str , _value2Str]:
                    #有字符串的情况下,如果数字不等则需要比较字符串是否相等
                    return ( _value1Num == _value2Num ) or ( _value1Str == _value2Str ) 
                elif None not in [_value1Num , _value2Num]:
                    return ( _value1Num == _value2Num )
                elif None not in [_value1Str , _value2Str]:
                    return ( _value1Str == _value2Str )
                else:
                    print "calculateBOP ERROR4", value1, value2, operator
                    return None
            elif "XOR" == operator:
                return bool( _value1Num ^ _value2Num )
            elif "XNOR" == operator:
                return ( not ( _value1Num ^ _value2Num ) )
            elif "ADD" == operator:
                return ( _value1Num + _value2Num )
            elif "SUB" == operator:
                return ( _value1Num - _value2Num )
            elif "MUL" == operator:
                return ( _value1Num * _value2Num )
            elif "DIV" == operator:
                return ( _value1Num / _value2Num )
            elif "POW" == operator:
                return math.pow( _value1Num , _value2Num )
            elif "MOD" == operator:
                return ( _value1Num % _value2Num )
            else:
                print "calculateBOP Error!!!", value1, value2, operator
        except:
            print "calculateBOP Error3!!!", value1, value2, operator 
            return None
        
    #-----------------------------------------------------
    #获取变量在本周期的值
    #-----------------------------------------------------
    def getCurVariantValue( self, Name, offsetIndex = 0 ):
        "get Current variant value"
        #首先获取变量的类型
        if self.getVariantsDic().has_key( Name ):
            if "0" == self.getVariantsDic()[Name][0]: #来自OMAP数据
                return self.getValueFromOMAP( Name, self.getCurCycle() + offsetIndex )
            elif "1" == self.getVariantsDic()[Name][0]: #来自Const数据
                return self.getValueFromConst( Name )
            elif "2" == self.getVariantsDic()[Name][0]: #来自Map数据
                _attr = self.getVariantsDic()[Name][2]
                return self.getValueFromMap( Name, _attr )
            elif "3" == self.getVariantsDic()[Name][0]: #来自用户自定义数据
                _ruleDic = self.getVariantsDic()[Name][1]
                return self.getValueFromUserDef( Name, _ruleDic )
    
    #------------------------------------------------------
    #从OMAP数据中获取值
    #Index为周期号
    #该函数会返回两个值一个数字型，一个字符串型[数值型，字符串型]
    #------------------------------------------------------        
    def getValueFromOMAP( self, Name, Index ):
        "get Value From OMAP"
        return self.__OMAPDataControl.ifOmapData( Name, Index )

    #------------------------------------------------------
    #从常量表中获取值
    #------------------------------------------------------        
    def getValueFromConst( self, Name ):
        "get Value From Const"
        return self.__UserDefDataControl.ifMapConst( Name )

    #------------------------------------------------------
    #从地图数据中获取值
    #------------------------------------------------------        
    def getValueFromMap( self, Name, Attr ):
        "get Value From Map"
        return None
    
    #------------------------------------------------------
    #从用户定义数据中获取值
    #------------------------------------------------------        
    def getValueFromUserDef( self, Name, RuleDic ):
        "get Value From user define"
        return self.getRuleValueInCurCycle( RuleDic )    
    
if __name__ == '__main__':
    test = ResultAnalysis()
    test.AnalysisInit( InitType = "All",
                       binpath = r'config/atpCpu1Binary.txt',
                       txtpath = r'config/atpText.txt',
                       trainroutepath = r'config/train_route.xml',
                       analysispath = r"./autoAnalysis.xml",
                       saveLogPath = r"./save.log",
                       omaplogpath = r"./config" )
    test.startAnalysis()
#    test = ResultAnalysis()
#    test.importBaseRuleDic( r"./config/baseRules.xml" )
#    print test.getBaseRuleDic()
#    test.importCommRuleDic( r"./config/userRequirementRules.xml" )
#    print test.getCommRuleDic()   
#    test.importAnalysisfile( r"./autoAnalysis.xml" )
#    print test.getAnalysisRuleDic()
#    print test.getVariantsDic()
#
#    RuleDic1 = {'exp1': {'exp1': {'Type': 'Variant', 'Value': 'OUT_EBRD12'}, 'Type': 'UOP', 'Value': 'NOT'}, 'Type': 'UOP', 'Value': 'NOT'}
#    RuleDic2 = {'exp2': {'exp1': {'Type': 'Variant', 'Value': 'OUT_EBRD12'}, 'Type': 'UOP', 'Value': 'NOT'}, 'exp1': {'exp2': {'Type': 'ConstInt', 'Value': '1'}, 'exp1': {'Type': 'Variant', 'Value': 'OUT_EBRD11'}, 'Type': 'BOP', 'Value': 'EQ'}, 'Type': 'BOP', 'Value': 'OR'}
#    print test.transRuleDicToString( RuleDic2 )
#    for _tcKey in test.getAnalysisRuleDic():
#        _tmpTC = test.getAnalysisRuleDic()[_tcKey]
#        for _op in _tmpTC["OP"]:
#            print test.transSingleOPToString( _op )
