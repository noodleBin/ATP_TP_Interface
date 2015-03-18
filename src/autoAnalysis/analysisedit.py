#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     analysisedit.py
# Description:  本文件用于画各种需要使用的    
# Author:       Xiong KunPeng
# Version:      0.0.1
# Created:      2012-12-13
# Company:      CASCO
# LastChange:   create 2012-12-13
# History:      create 2012-12-13 By XiongKunpeng
#----------------------------------------------------------------------------
from base.xmldeal import XMLDeal
from varCombine import VarComb
from base import commlib
from expressionparser import ExpressionParser
import copy
import time

#-------------------------------------------------------------------------------------——
#本类用于处理自动分析脚本的编辑
#---------------------------------------------------------------------------------------
class AnalysisEdit( object ):
    '''
    analysis edit
    '''
    #分析脚本的两个字典，都是带描述的,具体格式如下
    #变量字典，存储在脚本中申明的变量以及源，包括以下几种可能
    #Type = 0：format过来的数据，存储格式：VarName:["0",Name,Attr,Des]
    #Type = 1: const数据，存储格式：VarName:["1",Name,Attr,Des]
    #Type = 2: Map数据，存储格式：VarName:["2",Name,Attr,Des],其中Attr是一个按照格式书写的string，是需要解析的
    #Type = 3: 用户自定义数据，存储格式：VarName:["3", Name, RuleDic,Des]
    #RuleDic是一个规则字典，具体形式如下：
    #双目形式：{"Type":"BOP","Value":"OR","exp1":RuleDic,"exp2":RuleDic}
    #单目形式：{"Type":"UOP","Value":"NOT","exp1":RuleDic}
    #最终表现形式：
    #{"Type"："Variant","Value":"EBRD"}
    #{"Type"："ConstInt","Value":"1"}
    #{"Type"："ConstFloat","Value":"1.6"}
    #{"Type"："ConstStr","Value":"abc"}
    #{"Type"："RULEBASE","Value":RuleId}
    __VariantsDic = None
    #规则检查字典：
    #{TestCaseName:[TCDic,Des],...}
    #TCDic:{"Pos":PosList,"Time":TimeList,"OP":OPList}
    #PosList:[start,end,Des],其中start和end为int类型
    #TimeList：[start,end,Des],其中start和end为int类型
    #OPList:[OneOPDic,...]
    #OneOPDic:有两种形式
    #一种是自定义的{"condition":conList,"result":[ResList,...],"Type":"UserDef","Value":""}
    #一种是从库里面取的{"condition":conList,"result":[ResList,...],"Type":"CommDef","Value":CommId}
    #conList：[RuleDic,Des]
    #ResList:[RuleDic,Des]
    #每个TC下面支持多个OP,每个condition下面支持多个result
    #以上信息除了声明为int，float类型的，其余最终形式都是exp
    __AnalysisRuleDic = None
    
    #通用Rule文件
    __BaseRule = None
    __BaseConst = None
    __CommOP = None
    
    
    #记录编辑文件的路径
    __analysisFilePath = None
    
    def __init__( self ):
        "pass"

    
    # after initialization, call the function first
    def iniAnalysisEdit( self, analysispath, formatpath, usrdefpath ):
        self.varComb = VarComb( formatpath, usrdefpath )
        self.varComb.bldTotlDict()
        
        self.__BaseConst = self.varComb.usrDefInput.ConstDict
        self.__BaseRule = self.varComb.usrDefInput.UsrDefDict
        self.__analysisFilePath = analysispath
        self.loadAnalysisfile( analysispath )
        
    
    def getCommOPNameList( self ):
        "get Comm OP Name List"
        _tmp = self.__CommOP.keys()
        _tmp.sort()
        return _tmp
    
    #--------------------------------------------------------------------------------------
    #{"condition":conList,"result":[ResList,...],"Type":"CommDef","Value":CommId}
    #--------------------------------------------------------------------------------------
    def getCommContentByName( self, Name ):
        "get CommContent By Name"
        if self.__CommOP.has_key( Name ):
            return self.__CommOP[Name]
        else:
            print "getCommContentByName Error", Name
            return None
        
    #----------------------------------------------------------------------------------
    #导入分析脚本
    #----------------------------------------------------------------------------------
    def loadAnalysisfile( self, analysispath ):
        "load analysis file"
#        self.__BaseConst, self.__BaseRule = XMLDeal.importAnalysisVar( r"./config/usrData.xml",
#                                                                       ReadDes = True )
        
        self.__CommOP = XMLDeal.importCommRule( commlib.getCurFileDir() + "/autoAnalysis/config/userRequirementRules.xml",
                                                self.__BaseRule,
                                                ReadDes = True )
        self.__VariantsDic, self.__AnalysisRuleDic = XMLDeal.importAnalysisDic( analysispath,
                                                                                BaseRule = self.__BaseRule,
                                                                                CommOP = self.__CommOP,
                                                                                ReadDes = True )
    
    #---------------------------------------------------------------------------------
    #获取BaseRule中的一个变量的内容
    #[RuleDic,Des],其中
    #---------------------------------------------------------------------------------
    def getUsrDefVarContentByName( self, Name ):
        "get user define variant content by name"
        return [ExpressionParser.transRuleDicToString( self.__BaseRule[Name][0] ),
                self.__BaseRule[Name][1]]
    
    
    #--------------------------------------------------------------------------------
    #将__VariantsDic中的相关信息转换为可显示的
    #--------------------------------------------------------------------------------
    def transVarContentListToDisplay( self, contentList ):
        "transform variant content list into display"
        _rev = None
        #['OMAPFMT', 'CONST', 'USRDEF', 'MAP']
        if "0" == contentList[0]:# 'OMAPFMT'
            _rev = ["OMAPFMT"] + contentList[1:]
        elif "1" == contentList[0]:# 'CONST'
            _rev = ["CONST"] + contentList[1:]
        elif "2" == contentList[0]:# 'MAP'
            _rev = ["MAP"] + contentList[1:]
        elif "3" == contentList[0]:# 'USRDEF'
            _rev = ["USRDEF"] + \
                    [contentList[1]] + \
                    [ExpressionParser.transRuleDicToString( contentList[2] )] + \
                    [contentList[-1]]
        return _rev
    
    #---------------------------------------------------------------------------------
    #获取编辑变量时的源字典
    #包括format，map，const，usrdef几种类型
    #---------------------------------------------------------------------------------
    def getSrcVarNameDic( self ):
        "get source Variant Name Dic"
        return self.varComb.getTotlDict()
    
    #---------------------------------------------------------------------------------
    #显示列表中包含__VariantsDic的项去除掉
    #Type为需要去除的变量列表的类型
    #---------------------------------------------------------------------------------
    def getVarListWithoutSelected( self, Type ):
        "get variant list without selected variant"
        _rev = []
        for _v in  self.getSrcVarNameDic()[Type]:
            if not self.__VariantsDic.has_key( _v ):
                _rev.append( _v )
        return _rev
    
    #---------------------------------------------------------------------------------
    #获取__VariantsDic中的所有变量的名称的列表
    #---------------------------------------------------------------------------------
    def getVarNameList( self ):
        "get Variant Name list"
        _tmpList = self.__VariantsDic.keys()
        _tmpList.sort()
        return _tmpList
    
    #---------------------------------------------------------------------------------
    #添加一个变量至__VariantsDic中
    #---------------------------------------------------------------------------------
    def addOneVar( self, Name, Type, Attr, Des ):
        "add one Var"
        _tp = self.varComb.tp2num( Type )
        
        if not self.__VariantsDic.has_key( Name ):
            if  "3" == _tp:#自定义类型
                self.__VariantsDic[Name] = [_tp, Name] + self.__BaseRule[Name]
            else:
                self.__VariantsDic[Name] = [_tp, Name, Attr, Des]
        
        
    #---------------------------------------------------------------------------
    #获取库里面OP的所有ID号
    #---------------------------------------------------------------------------
    
    
    
    #---------------------------------------------------------------------------------
    #删除__VariantsDic中的一个变量
    #---------------------------------------------------------------------------------
    def delOneVar( self, Name ):
        "delete one Var"   
        if self.__VariantsDic.has_key( Name ):
            self.__VariantsDic.pop( Name )
        else:
            self.printError( Name )
        
    #---------------------------------------------------------------------------------
    #修改__VariantsDic中的一个变量
    #---------------------------------------------------------------------------------
    def modOneVar( self, Name, Type, Attr, Des ):
        "modify one Var"         
        _tp = self.varComb.tp2num( Type )
        if self.__VariantsDic.has_key( Name ):
#            self.__VariantsDic[Name] = [_tp, Name, Attr, Des]
            if  "3" == _tp:#自定义类型的描述是不能改的
                self.__VariantsDic[Name] = [_tp, Name] + self.__BaseRule[Name]
            else:
                self.__VariantsDic[Name] = [_tp, Name, Attr, Des]    
    
    
    #---------------------------------------------------------------------------------
    #获取一个Var的信息
    #返回["1",Name,Attr,Des],具体形式见最上面的Var定义
    #---------------------------------------------------------------------------------
    def getVarInfoByName( self, Name ):
        "get Variant information by name"
        if self.__VariantsDic.has_key( Name ):
            return self.transVarContentListToDisplay( self.__VariantsDic[Name] )
        else:
            self.printError( Name )
    
    
    #---------------------------------------------------------------------------------
    #获取所有rule组成的name的list
    #---------------------------------------------------------------------------------
    def getRuleNameList( self ):
        "get rule name list"
        _tmpList = self.__AnalysisRuleDic.keys()
        _tmpList.sort()
        return _tmpList
        
    
    #---------------------------------------------------------------------------------------------
    #在__AnalysisRuleDic中添加一个Rule,也即对应最开始描述的TestCaseName:[TCDic,Des]
    #这里参数值提供新规则的名称,其余的由函数自行通过填写默认值完成
    #遵循以下规则：
    #列表和字典填空
    #字符串填""
    #整型和float类型填None
    #注：这里还应该进行校验，TCName的名字不能和已有的重名，重名的话应该有提示（打印，并返回打印的字符串）
    #成功返回True
    #---------------------------------------------------------------------------------------------
    def addOneRule( self, TCName ):
        "Add one Rule"
        if self.__AnalysisRuleDic.has_key( TCName ):
            self.printError( TCName )
        else:
            self.__AnalysisRuleDic[TCName] = [{"Pos": [None, None, ""], "Time": [None, None, ""], "OP": []}, ""]
            return True
        
        
    #--------------------------------------------------------------------------------
    #删除在__AnalysisRuleDic中的一个Rule,也应该校验名字的正确性
    #--------------------------------------------------------------------------------    
    def delOneRule( self, TCName ):
        "Delete one Rule"
        if self.__AnalysisRuleDic.has_key( TCName ):
            self.__AnalysisRuleDic.pop( TCName )
            return True
        else:
            self.printError( TCName )
    
    
    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则的描述
    #--------------------------------------------------------------------------------    
    def modOneRuleDes( self, TCName, Des ):
        "modify one Rule description"
        self.__AnalysisRuleDic[TCName][-1] = Des        
    

    #--------------------------------------------------------------------------------
    #获取在__AnalysisRuleDic中某条规则的描述
    #--------------------------------------------------------------------------------
    def getOneRuleDes( self, TCName ):
        "get one Rule description"
        return self.__AnalysisRuleDic[TCName][-1]  
        
    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则的分析时间
    #Timelist：[start,end,Des]
    #--------------------------------------------------------------------------------    
    def modOneRuleTime( self, TCName, Timelist ):
        "modify one Rule Time list" 
        self.__AnalysisRuleDic[TCName][0]["Time"] = Timelist


    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则的分析的开始时间
    #--------------------------------------------------------------------------------    
    def modOneRuleStartTime( self, TCName, Time ):
        "modify one Rule start Time" 
        self.__AnalysisRuleDic[TCName][0]["Time"][0] = Time        
    
    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则的分析的结束时间
    #--------------------------------------------------------------------------------    
    def modOneRuleEndTime( self, TCName, Time ):
        "modify one Rule end Time" 
        self.__AnalysisRuleDic[TCName][0]["Time"][1] = Time  

    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则的分析的结束时间
    #--------------------------------------------------------------------------------    
    def modOneRuleTimeDes( self, TCName, Des ):
        "modify one Rule Time description" 
        self.__AnalysisRuleDic[TCName][0]["Time"][2] = Des  
    
    #--------------------------------------------------------------------------------
    #获取一个Rule中的Time信息
    #返回Timelist：[start,end,Des]
    #--------------------------------------------------------------------------------
    def getOneRuleTimeInfo( self, TCName ):
        "get one rule time info"
        if self.__AnalysisRuleDic.has_key( TCName ):
            return self.__AnalysisRuleDic[TCName][0]["Time"]
        else:
            self.printError( TCName )
    
    
    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则的分析位置
    #Poslist：[start,end,Des]
    #--------------------------------------------------------------------------------    
    def modOneRulePos( self, TCName, Poslist ):
        "modify one Rule Position List"
        self.__AnalysisRuleDic[TCName][0]["Pos"] = Poslist          


    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则的分析的起始位置
    #--------------------------------------------------------------------------------    
    def modOneRuleStartPos( self, TCName, Pos ):
        "modify one Rule start Position"
        self.__AnalysisRuleDic[TCName][0]["Pos"][0] = Pos    
    
    #---------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则的分析的结束位置
    #---------------------------------------------------------------------------
    def modOneRuleEndPos( self, TCName, Pos ):
        "modify one Rule start Position"
        self.__AnalysisRuleDic[TCName][0]["Pos"][1] = Pos    
    
    #---------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则的分析的描述
    #---------------------------------------------------------------------------
    def modOneRulePosDes( self, TCName, Des ):
        "modify one Rule start Position"
        self.__AnalysisRuleDic[TCName][0]["Pos"][2] = Des        
    
    #--------------------------------------------------------------------------------
    #获取一个Rule中的Pos信息
    #返回Poslist：[start,end,Des]
    #--------------------------------------------------------------------------------
    def getOneRulePosInfo( self, TCName ):
        "get one rule position info"
        if self.__AnalysisRuleDic.has_key( TCName ):
            return self.__AnalysisRuleDic[TCName][0]["Pos"]
        else:
            self.printError( TCName )

    #--------------------------------------------------------------------------------
    #获取一条Rule中的所有OPName组成的list
    #注：这里的OPName是OPList里面OneOPDic中的Value属性,要按照OPList的顺序返回出这个列表来
    #--------------------------------------------------------------------------------
    def getOneRuleOPNameList( self, TCName ):
        "get one rule OPName List"
        if self.__AnalysisRuleDic.has_key( TCName ):
            return [_op["Value"] for _op in self.__AnalysisRuleDic[TCName][0]["OP"]]
    
    #--------------------------------------------------------------------------------
    #添加在__AnalysisRuleDic中某条规则中的OP
    #OPName：添加的OP名称
    #这里也要进行正确性分析
    #注意由于OP是一个列表，所以添加OP的时候是放在最后的
    #--------------------------------------------------------------------------------    
    def addOneRuleOP( self, TCName, OPName ):
        "add one OP in one rule"
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if not _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"].append( {"Value": OPName,
                                                                 "Type":"UserDef",
                                                                 "condition":[{}, ""],
                                                                 "result":[]} )
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )
    
    #--------------------------------------------------------------------------------
    #将某个OP转换为从库里面取
    #--------------------------------------------------------------------------------
    def changeOneRuleOPToCommOPByName( self, TCName, NewOPName, OPIndex ):
        "change One Rule OP to comm op by name"
        if self.__AnalysisRuleDic.has_key( TCName ):
            self.__AnalysisRuleDic[TCName][0]["OP"][ OPIndex ] = self.__CommOP[NewOPName]
            return True
        else:
            self.printError( TCName )        
    
    #--------------------------------------------------------------------------------
    #删除在__AnalysisRuleDic中某条规则中的OP的
    #OPName：要删除的OP名称
    #OPIndex：要删除的OP的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #这里也要进行正确性分析
    #--------------------------------------------------------------------------------    
    def delOneRuleOP( self, TCName, OPName, OPIndex ):
        "add one OP in one rule"
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"].pop( OPIndex )
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )

    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则中的OP的描述
    #OPName：要修改的OP名称
    #OPIndex：要修改的OP的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #这里也要进行正确性分析
    #--------------------------------------------------------------------------------    
    def modOneRuleOPDes( self, TCName, OPName, OPIndex, Des ):
        "modify one OP Des in one rule"          
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["Value"] = Des
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )  
    
    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则中的OP的条件的内容
    #OPName：要修改的OP名称
    #OPIndex：要修改的OP的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #这里也要进行正确性分析
    #--------------------------------------------------------------------------------
    def modOneRuleOPCondContent( self, TCName, OPName, OPIndex, RuleDic ):
        "modify one OP condition content in one rule" 
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["condition"][0] = RuleDic
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )          

    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则中的OP的条件的描述
    #OPName：要修改的OP名称
    #OPIndex：要修改的OP的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #这里也要进行正确性分析
    #--------------------------------------------------------------------------------
    def modOneRuleOPCondDes( self, TCName, OPName, OPIndex, Des ):
        "modify one OP condition Des in one rule"
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["condition"][-1] = Des
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )
    
    
    #-------------------------------------------------------------------------
    #将OP类型从CommOP转换为UsrDef OP
    #这里主要是将以前指向CommOP的字典进行深拷贝，以避免源被修改
    #-------------------------------------------------------------------------
    def changeOPTypeToUsrDef( self, TCName, OPName, OPIndex ):
        "change OP Type to UsrDef"
#        print self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["Type"]
        if "UserDef" != self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["Type"]:#只有原来不是的时候做此操作
            self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex] = copy.copy( self.__CommOP[OPName] )
            self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["Type"] = "UserDef"
    
    #--------------------------------------------------------------------------
    #修改OP的类型
    #--------------------------------------------------------------------------
    def modOneRuleOPType( self, TCName, OPName, OPIndex, Type ):
        "modify one OP condition Type in one rule"
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["Type"] = Type
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )

    #--------------------------------------------------------------------------
    #修改OP的Name
    #--------------------------------------------------------------------------
    def modOneRuleOPName( self, TCName, OPName, OPIndex, Name ):
        "modify one OP condition Type in one rule"
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["Value"] = Name
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )

    
    #--------------------------------------------------------------------------------
    #获取一个Rule中一个OP的condition信息，包括内容和描述
    #OPName：要修改的OP名称
    #OPIndex：要修改的OP的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数    
    #返回conList：[RuleDic,Des]
    #--------------------------------------------------------------------------------
    def getOneRuleOPCondInfo( self, TCName, OPName, OPIndex ):
        "get one OP condition info in one rule"  
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                return self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["condition"]
            else:
                self.printError( OPName )
        else:
            self.printError( TCName ) 
    
    #--------------------------------------------------------------------------
    #获取一条OP的所有信息
    #一种是自定义的{"condition":conList,"result":[ResList,...],"Type":"UserDef","Value":""}
    #一种是从库里面取的{"Type":"CommDef","Value":CommId}
    #--------------------------------------------------------------------------
    def getOPInfo( self, TCName, OPName, OPIndex ):
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
#            print _opName, TCName, OPName
            if _opName.__contains__( OPName ):
                return self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )         

    #--------------------------------------------------------------------------------
    #获取一个Rule中一个OP的一个result信息，包括内容和描述
    #OPName：要修改的OP名称
    #OPIndex：要修改的OP的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数   
    #ResIndex：要修改的result的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数     
    #返回ResList：[RuleDic,Des]
    #--------------------------------------------------------------------------------
    def getOneRuleOPResultInfo( self, TCName, OPName, OPIndex, ResIndex ):
        "get one OP result info in one OP of one rule"  
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                return self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["result"][ResIndex]
            else:
                self.printError( OPName )
        else:
            self.printError( TCName ) 
                    
    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则中的OP的result中的描述
    #OPName：要修改的OP名称
    #OPIndex：要修改的OP的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #ResIndex：要修改的result的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #这里也要进行正确性分析
    #--------------------------------------------------------------------------------
    def modOneRuleOPResultDes( self, TCName, OPName, OPIndex, ResIndex, Des ):
        "modify one OP result Des in one rule"
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["result"][ResIndex][-1] = Des
#                print TCName, OPName, OPIndex, ResIndex
#                print self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["result"][ResIndex], Des
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )        

    #--------------------------------------------------------------------------------
    #修改在__AnalysisRuleDic中某条规则中的OP的result中的内容
    #OPName：要修改的OP名称
    #OPIndex：要修改的OP的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #ResIndex：要修改的result的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #这里也要进行正确性分析
    #--------------------------------------------------------------------------------
    def modOneRuleOPResultContent( self, TCName, OPName, OPIndex, ResIndex, RuleDic ):
        "modify one OP result content in one rule" 
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["result"][ResIndex][0] = RuleDic
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )             


    #--------------------------------------------------------------------------------
    #添加在__AnalysisRuleDic中某条规则中的OP的一条result
    #OPName：要修改的OP名称
    #OPIndex：要修改的OP的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #添加在最后面,都用默认值
    #这里也要进行正确性分析
    #--------------------------------------------------------------------------------
    def addOneRuleOPResult( self, TCName, OPName, OPIndex ):
        "add one OP result in one rule"
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["result"].append( [{}, ""] )
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )  
         
        
    #--------------------------------------------------------------------------------
    #删除在__AnalysisRuleDic中某条规则中的OP的result
    #OPName：要修改的OP名称
    #OPIndex：要修改的OP的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #ResIndex：要修改的result的Index,由于OP是以列表的形式出现的，故而实际主要是用这个参数
    #这里也要进行正确性分析
    #--------------------------------------------------------------------------------
    def delOneRuleOPResult( self, TCName, OPName, OPIndex, ResIndex ):
        "delete one OP result in one rule" 
        if self.__AnalysisRuleDic.has_key( TCName ):
            _opName = self.getOneRuleOPNameList( TCName )
            if _opName.__contains__( OPName ):
                self.__AnalysisRuleDic[TCName][0]["OP"][OPIndex]["result"].pop( ResIndex )
                return True
            else:
                self.printError( OPName )
        else:
            self.printError( TCName )             
    
    #--------------------------------------------------------------------------------
    #error print
    #--------------------------------------------------------------------------------  
    def printError( self, TCName ):
        _str = TCName + " Not Exist or already Exist!!!"
        print _str

    #--------------------------------------------------------------------------------
    #校验保存数据的正确性，这里主要是校验数据是否符合要求
    #这里只检查RuleDic的正确性
    #--------------------------------------------------------------------------------
    def checkIfValidAnalysisDic( self ):
        "check valid of analysis dic"
        if len( self.__AnalysisRuleDic ) <= 0:
            return "No Rule!!!"
        
        try:
            for _rule in self.__AnalysisRuleDic:
                #检查OP
                if len( self.__AnalysisRuleDic[_rule][0]["OP"] ) <= 0:
                    return "NO OP in Rule: " + str( _rule )
                    
                for _op in self.__AnalysisRuleDic[_rule][0]["OP"]:
                    #校验condition
                    if "" == ExpressionParser.transRuleDicToString( _op["condition"][0] ):
                        return "NO Condition in OP: " + str( _op["Value"] ) + " in Rule: " + str( _rule )
                    #检查reslut
                    if len( _op["result"] ) <= 0:
                        return "NO result in OP: " + str( _op["Value"] ) + " in Rule: " + str( _rule )
                    for _i, _r in enumerate( _op["result"] ):
                        #校验reslut
                        if "" == ExpressionParser.transRuleDicToString( _r[0] ):
                            return "NO resultExp in result index: " + str( _i ) + " in OP: " + str( _op["Value"] ) + " in Rule: " + str( _rule )                        
        except:
            return "Unknow Error in AnalysisRuleDic!"
        
        return True
            
    
    
    #--------------------------------------------------------------------------------
    #保存编辑好的文件
    #--------------------------------------------------------------------------------
    def saveAnalysisFile( self ):
        XMLDeal.ExportAnalysisDic( self.__analysisFilePath,
                                   self.__VariantsDic,
                                   self.__AnalysisRuleDic )
    
    
if __name__ == '__main__':
    pass
