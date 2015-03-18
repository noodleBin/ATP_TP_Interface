#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     expressionparser.py
# Description:  解析表达式模块    
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2012-12-06
# Company:      CASCO
# LastChange:   update 2012-12-06
# History:      2012-12-06 创建本文件
#               
#----------------------------------------------------------------------------
"""
<支持的双目操作符 包括 OR AND GE GT LE LT EQ XOR XNOR ADD SUB MUL DIV POW MOD -->
<支持的单目操作符 包括 NOT FLOOR CEIL-->
"""
#同或和异或暂时不支持

signable = ["&", "|", "+", "-", "*", "/", "%", "(", ")", \
            "<", "=", ">", "!", "#", "@", "$", "[", "]" ]

signs = ["||", "&&", ">=", ">", "<=", "<", "==", "^",
         "+", "-", "*", "/", "%", "!", "#", "@", "$"]

singsToLabelDic = {"||":"OR", "&&":"AND", ">=":"GE",
                   ">":"GT", "<=":"LE", "<":"LT", "==":"EQ",
                   "^":"XOR", "+":"ADD",
                   "-":"SUB", "*":"MUL", "/":"DIV",
                   "%":"MOD", "!":"NOT", "#":"FLOOR",
                   "@":"CEIL", "$":"POW"
                   }

handleDic = {"floor":"#", "ceil":"@", "pow":"$" }#用于实现函数名称的转换

priorities = {"[":1, "]":1, "(":1, ")":1,
              "#":1, "@":1, "$":1,
              "!":2, "*":3, "/":3, "%":3,
              "+":4, "-":4, ">":6, ">=":6,
              "<":6, "<=":6, "==":7, "&&":11, "||":12 }

class ExpressionParser( object ):
    """
    Expression Parser class
    """

    #逻辑显示转换
    # NOT FLOOR CEIL 
    # OR AND GE GT LE LT EQ XOR XNOR ADD SUB MUL DIV POW MOD
    __SignTransDic = {"NOT":"!",
                      "FLOOR":"floor",
                      "CEIL":"ceil",
                      "OR":"||",
                      "AND":"&&",
                      "GE":">=",
                      "GT":">",
                      "LE":"<=",
                      "LT":"<",
                      "EQ":"==",
                      "XOR":"Xor",
                      "XNOR":"Xnor",
                      "ADD":"+",
                      "SUB":"-",
                      "MUL":"*",
                      "DIV":"/",
                      "POW":"pow",
                      "MOD":"%"}
    
    __BaseRuleDic = None

    def __init__( self ):
        "init"
        pass
    
    #---------------------------------------------------------------
    #判断常量的类型,有四种类型
    #1：整型，2：浮点，3：字符串，4：变量无[k-1],5:变量有[k-1],6:baseRule
    #返回：1:{"Type":"ConstInt","Value":str}
    #返回：2:{"Type":"ConstFloat","Value":str}
    #返回：3:{"Type":"ConstStr","Value":str}
    #返回：4:{"Type":"Variant","Value":str}
    #返回：5:{"Type":"Variant","Value":str#..}
    #返回：6:{"Type":"RULEBASE","Value":去除RULEBASE_后的str}
    #---------------------------------------------------------------
    @classmethod
    def getVarDic( self, Str ):
        "get Variant Type"
        try:
            int( Str )
            return {"Type":"ConstInt", "Value":Str }
        except:
            try:
                float( Str )
                return {"Type":"ConstFloat", "Value":Str }
            except:
                if "RULEBASE_" == Str[0:10]:
                    return {"Type":"RULEBASE", "Value":Str[10:] }            
                elif len( Str ) > 2 and "\"" == Str[0] and "\"" == Str[-1]:
                    return {"Type":"ConstStr", "Value":Str[1:-1] }
                elif "[" in Str and "]" == Str[-1]:#其他情况不防护
                    _index1 = Str.find( "[" )
                    _index2 = Str[_index1:].find( "k" ) + _index1#从[后面开始搜索
                    return { "Type":"Variant",
                            "Value":( Str[:_index1] + "#" + Str[_index2 + 1:-1] ) }
                else:
                    return {"Type":"Variant", "Value":Str }
        
    #---------------------------------------------------------------
    #将后缀表达式，转换为RuleDic(形式参见resultanalysis中的描述)
    #---------------------------------------------------------------        
    @classmethod
    def transSuffixExpToRuleDic( self, SuffixExplist ):
        "transform suffix expression into rule dic"
        _rev = [] 
        for _tmp in SuffixExplist: #为防止修改，进行一次赋值
            _rev.append( _tmp )
            
        if 1 == len( _rev ):
            return self.getVarDic( _rev[0] )
        #遍历SuffixExplist
        while len( _rev ) > 1:            
            #寻找操作符
            _findIndex = None
            _sign = None
            for _i, _tmp in enumerate( _rev ):
                if _tmp in signs:
                    _findIndex = _i
                    _sign = _tmp
                    break
#            print _rev
            
            if None != _findIndex: #找到则需要进行处理
                try:
                    if _sign in ["#", "@", "!"]:#单目
                        _tempDic = {}
                        _tempDic["Type"] = "UOP"
                        _tempDic["Value"] = singsToLabelDic[_sign]
                        if dict == type( _rev[_findIndex - 1] ): #是已经解析出来的字典
                            _tempDic["exp1"] = _rev[_findIndex - 1]
                        else:#还是数据
                            _tempDic["exp1"] = self.getVarDic( _rev[_findIndex - 1] )
                        #修改_rev
                        _rev = _rev[:_findIndex - 1] + [_tempDic] + _rev[_findIndex + 1:]
                    else:#双目运算
                        _tempDic = {}
                        _tempDic["Type"] = "BOP"
                        _tempDic["Value"] = singsToLabelDic[_sign]
                        if dict == type( _rev[_findIndex - 2] ): #是已经解析出来的字典
                            _tempDic["exp1"] = _rev[_findIndex - 2]
                        else:#还是数据
                            _tempDic["exp1"] = self.getVarDic( _rev[_findIndex - 2] )
                        if dict == type( _rev[_findIndex - 1] ): #是已经解析出来的字典
                            _tempDic["exp2"] = _rev[_findIndex - 1]
                        else:#还是数据
                            _tempDic["exp2"] = self.getVarDic( _rev[_findIndex - 1] )    
                        #修改_rev
                        _rev = _rev[:_findIndex - 2] + [_tempDic] + _rev[_findIndex + 1:] 
                except:
                    print "transSuffixExpToRuleDic error1!", _rev, _findIndex, _sign
                    return None
            else:
                print "transSuffixExpToRuleDic error2!"
                return  None
        
                           
        return _rev[0]
    
    #---------------------------------------------------------------
    #先将表达式转换为后缀表达式
    #Explist:为中缀表达式的list形如["a","+","b"]
    #注意这里floor和ceil函数将作为一个字符串进行管理形如："floor(a)",""
    #对于a[k-1]也作为整体处理
    #后续还会对其进行处理
    #---------------------------------------------------------------
    @classmethod
    def transInfixExpToSuffixExp( self, Explist ):
        "transform infix expression into suffix expression"
        #创见两个临时的堆栈
        _stack = []
        _post = []
        
        #遍历中缀表达式
        for _item in Explist:
#            print "post", _post
#            print "stack", _stack
#            print "_item", _item
            if _item not in signs and _item not in ["(", ")"]: #是变量
                _post.append( _item )
            elif "(" == _item:
                _stack.append( _item )
            elif ")" == _item: #需要将_stack中在"("之后的数据出堆栈
                #寻找"("对应的编号
                _tempindex = None
                for _i in range( len( _stack ) ): #记得搜最后的那个，而不是第一个
                    _t_item = _stack[len( _stack ) - _i - 1 ]
                    if "(" == _t_item:
                        _tempindex = len( _stack ) - _i - 1
                        break
#                print "_tempindex", _tempindex
                if None == _tempindex:
                    print "transInfixExpToSuffixExp Error!", _stack
                    return None
                else:
                    for _i in range( _tempindex , len( _stack ) ): 
                        _tmp = _stack.pop()
                        if "(" != _tmp: #"("不需要
                            _post.append( _tmp )
                    
            else:
                #判断符号优先级
                if len( _stack ) > 0:
                    #括号"("的时候不进行比较
                    if priorities[_item] <= priorities[_stack[-1]] or "(" == _stack[-1]: #值越大，优先级越低
                        _stack.append( _item )
                    else:#将_stack堆栈顶部的出栈，放入post中
                        _post.append( _stack.pop() )
                        _stack.append( _item )
                else:
                    _stack.append( _item )
        
        #扫描完将所有剩下的运算符出栈
        for _i in range( len( _stack ) ):
            _post.append( _stack.pop() )  

        return _post
    
    #-----------------------------------------------------------------------
    #对字符串表达式进行解析，转换为List形式：具体如下
    #a + b == c ->  ["a","+","b","==","c"]
    #有几种特殊情况需要注意，变量为字符串，字符串则表示为""a"",即带引号的字符串
    #对于"floor(a)"以及a[k-1]这种的先视为整体变量处理
    #这里还应该注意Int类型，浮点类型以及字符串类型的识别
    #-----------------------------------------------------------------------               
    @classmethod
    def transExpStrIntoListStr( self, expression ):
        "transform expression string into list string"
        _result = []
        _tempStr = ""
        #事先对表达式进行处理
        _tmpExp = self.replaceExpStrByFuncDic( expression )
        _tempsigns = signs + ["(", ")", "[", "]"]
        #遍历表达式字符串
        for _i, _ch in enumerate( _tmpExp ):
#            _tempStr += _ch
            if _ch in signable: #属于逻辑符号时有两种情况，一种是_tempStr的倒数第二个也是
                if _tempStr in signable:
                    if ( _tempStr + _ch ) in _tempsigns: #由两个字符组成的操作符
                        _result.append( _tempStr + _ch )
                        _tempStr = ""
                    elif _tempStr in _tempsigns and _ch in _tempsigns:#存在单目运算符
                        _result.append( _tempStr )
                        _result.append( _ch )
                        _tempStr = ""
                    elif _tempStr in [")", "]"]:#两个特殊情况
                        _result.append( _tempStr )
                        _tempStr = _ch
                    else:
                        print "transExpStrIntoListStr Error1, unknow sign!", _tempStr + _ch
                        return None
                else:
                    if len( _tempStr ) > 0:
                        _result.append( _tempStr )
                    _tempStr = _ch
            else: #当前的不是操作数
                if _tempStr in signable:#上一个是操作数
                    if _tempStr  in _tempsigns: #由一个字符组成的操作符
                        _result.append( _tempStr )
                        _tempStr = _ch
                    else:
                        print "transExpStrIntoListStr Error2, unknow sign!", _tempStr
                        return None                                 
                else:    
                    _tempStr += _ch       
        
        #添加尾部      
        if len( _tempStr ) > 0:
            _result.append( _tempStr )
        
        #对于有"[]"的进行合并 
        
        return self.combineBracket( _result )
    
    
    #----------------------------------------------------------------------
    #将['b', '[', 'k', '-', '1', ']']->["b[k-1]"]
    #----------------------------------------------------------------------
    @classmethod
    def combineBracket( self, list ):
        "combine bracket"
        _rev = []
        _IndexList = [] #存储list中出现"["的时间
        for _i, _tmpcontent in enumerate( list ):
            if "[" == _tmpcontent:
                if "]" == list[_i + 4]:#校验是否符合要求
                    _IndexList.append( _i )
                else:
                    print "combineBracket error", list[_i - 1:_i + 4]
                    return None
        
        _offsetIndex = 0    
        for _i in _IndexList:
            _rev += list[_offsetIndex:_i - 1] + \
                    [list[_i - 1] + list[_i] + list[_i + 1] + list[_i + 2] + list[_i + 3] + list[_i + 4]]
            _offsetIndex = _i + 5
        #补上最后的字符
        _rev += list[_offsetIndex:]
        return _rev
    
    #----------------------------------------------------------------------
    #将表达式中的函数名修改为变体字符串，具体见handleDic
    #例如："a + float(b) - ceil(x)" -> "a+#(b)-@(x)"
    #----------------------------------------------------------------------
    @classmethod
    def replaceExpStrByFuncDic( self, ExpStr ):
        "replace expression string by function dic"
        #去除掉所有的空格符
        _ExpStrWithoutSpace = ""
        for _ch in ExpStr.split( " " ):
            _ExpStrWithoutSpace += _ch
        
        _tempResult = self.checkIfHasSubStr( _ExpStrWithoutSpace, ["floor", "ceil", "pow"] ) 
        while len( _tempResult ) > 0:
            #找到了位置，进行替换
            [_index, _str] = _tempResult
            if _str in ["floor", "ceil"]:
                _ExpStrWithoutSpace = _ExpStrWithoutSpace[0:_index] + \
                                        handleDic[_str] + \
                                        _ExpStrWithoutSpace[_index + len( _str ):]
            else: #"pow" "pow(a,b)"->"(a$b)"
                _commaIndex = _ExpStrWithoutSpace[_index + len( _str ):].find( "," )
                if -1 != _commaIndex:
                    _ExpStrWithoutSpace = _ExpStrWithoutSpace[0:_index] + \
                                            _ExpStrWithoutSpace[_index + len( _str ):_index + len( _str ) + _commaIndex ] + \
                                            handleDic[_str] + \
                                            _ExpStrWithoutSpace[_index + len( _str ) + _commaIndex + 1:]
                else:
                    print "replaceExpStrByFuncDic error!", _ExpStrWithoutSpace, _tempResult
            _tempResult = self.checkIfHasSubStr( _ExpStrWithoutSpace, ["floor", "ceil", "pow"] ) 
#            print _ExpStrWithoutSpace, _tempResult
        return _ExpStrWithoutSpace
        
    #----------------------------------------------------------------------
    #判断字符串中是否包含,子字符串列表中的字段
    #有的话返回最近的一个子字段的位置，以及子字段名称[index,str],反之返回空列表[]
    #----------------------------------------------------------------------
    @classmethod
    def checkIfHasSubStr( self, checkstr, strlist ):
        "check if has sub string in the check string"
        _minIndex = len( checkstr ) #初始值为一个大于字符串长度的值
        _tempStr = None
        for _i, _findstr in enumerate( strlist ):
            _findIndex = checkstr.find( _findstr )
#            print _findstr, _findIndex
            if -1 != _findIndex and _minIndex > _findIndex:
                _minIndex = _findIndex
                _tempStr = _findstr
        if -1 == _minIndex or _minIndex >= len( checkstr ):
            return []
        else:
            return [_minIndex, _tempStr]

    #---------------------------------------------------------------
    #将RuleDic转换为String输出，形如
    #    b == a + c
    #本函数由resultanalysis中提出而来
    #---------------------------------------------------------------            
    @classmethod
    def transRuleDicToString( self, RuleDic ):
        "transform rule dic to string"
        try:
            if "BOP" == RuleDic["Type"]:
                _expstr1 = self.transRuleDicToString( RuleDic["exp1"] )
                _expstr2 = self.transRuleDicToString( RuleDic["exp2"] )
                
                if "POW" == RuleDic["Value"]: 
                    return self.__SignTransDic[RuleDic["Value"]] + "(" + _expstr1 + "," + _expstr2 + ")"
                else:
                    return "(" + _expstr1 + self.__SignTransDic[RuleDic["Value"]] + _expstr2 + ")"
            elif "UOP" == RuleDic["Type"]:
                _expstr = self.transRuleDicToString( RuleDic["exp1"] )
                
                return "(" + self.__SignTransDic[RuleDic["Value"]] + _expstr + ")"
            elif "ConstStr" == RuleDic["Type"]:
                return "\"" + RuleDic["Value"] + "\""
            elif "Variant" == RuleDic["Type"]:
                _tempStr = RuleDic["Value"].split( "#" )
                if len( _tempStr ) <= 1:
                    return RuleDic["Value"]
                else:
                    _tempInt = int( _tempStr[1] )
                    if _tempInt > 0:
                        return _tempStr[0] + "[k+" + _tempStr[1] + "]"
                    else:
                        return _tempStr[0] + "[k" + _tempStr[1] + "]"
            elif RuleDic["Type"] in ["ConstInt", "ConstFloat"]:
                return RuleDic["Value"]
            elif "RULEBASE" == RuleDic["Type"]:
                #计算真实的Rule吗？不计算，只返回
    #            return self.transRuleDicToString( self.__BaseRuleDic[RuleDic["Value"]] )       
                return RuleDic["Type"] + "_" + RuleDic["Value"]
            else:
                print "TransRuleDicToString Error!", RuleDic
                return None
        except KeyError, e:
            print "transRuleDicToString", e
            return ""
    
    #-------------------------------------------------------------------------
    #将表达式字符串转换为字典
    #-------------------------------------------------------------------------         
    @classmethod
    def transStringToRuleDic( cls, ExpString ):
        "transform expression string into rule dic"
        _listStr = cls.transExpStrIntoListStr( ExpString )
#        print _listStr
        _suffixExp = cls.transInfixExpToSuffixExp( _listStr )
#        print _suffixExp
        return cls.transSuffixExpToRuleDic( _suffixExp )
     
if __name__ == '__main__':
#    a = "[1, 2, 3, 4, 5]"
#    for _i, _a in  enumerate( a ):
#        print _i, _a
#    test = ExpressionParser()
#    print ExpressionParser.replaceExpStrByFuncDic( "a+ floor(a)+ vb+ceil(fadfa)" )
#    a = ExpressionParser.transExpStrIntoListStr( "((OUT_EBRD11==0)||(!OUT_EBRD12))" )
#    print a
#    b = ExpressionParser.transInfixExpToSuffixExp( a )
#    print b
#    c = ExpressionParser.transSuffixExpToRuleDic( b )
#    print ExpressionParser.transRuleDicToString( c )
    print ExpressionParser.transStringToRuleDic( "((ValidTrainKinematic==\"FALSE\")&&(LocalizationState[k-1]==\"LOCALIZED\"))-123" )
    
