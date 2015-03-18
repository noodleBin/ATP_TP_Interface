#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     ruleprocess.py
# Description:  规则脚本的处理，主要是根据规则改值     
# Author:       Kunpeng Xiong
# Version:      0.0.1
# Created:      2011-07-19
# Company:      CASCO
# LastChange:   update 2011-07-21
# History:      2011-07-21 :add getNormalChangeItem
#----------------------------------------------------------------------------
#import simdata
#from simdata import TrainRoute
#import commlib
class RuleProcess():
    """
    rule process for device.
    """
    Valuetype = {'int':int, 'string':str, 'float':float}
    #逻辑格式scenario存放列表
    #{rule ID:{'left':{},'right':{},'type':"exp",'operator':'AND'},
    # rule ID:{'exps':[{},{}],'type':"exp",'operator':'AND'},...}
    __ruleScenario = None
    
    #保存逻辑中需要延时修改的值的列表
    #[[name,value,delay],...]
    __rulechangelist = None
    
    #规则对应的设备节点
    __devicenode = None
    
    def __init__(self, devNode, ruleSce):
        "init method"
        self.__devicenode = devNode      
        self.__ruleScenario = ruleSce
        #__rulechangelist初始化为空列表
        self.__rulechangelist = []


    #---------------------------------------------------------------------------
    #根据__ruleScenario中的规则，查看__data中的值，如果规则成立，则根据规则进行值的修改
    #change_list = [name="IN_RM_PB1" value="1"  delay="0"]
    #返回，是否修改，修改了返回True，反之，返回False
    #--------------------------------------------------------------------------- 
    def checkRule(self):
        "change __data througt rules"
        _devNode = self.__devicenode
        _retchange = False
        for _rulekey in self.__ruleScenario:
            _rule = self.__ruleScenario[_rulekey]
            if self.getcurRuleValue(_rule):
                #触发值的改变
                _change_item = _rule['reaction'] #获取需要该值的列表
                for _item in _change_item:
                    if 0 == int(_item[2]):
                        _name = _item[0]
                        _value = self.Valuetype[_devNode.getVarDic()[_item[0]][0]](_item[1]) #根据类型进行转换
                        _devNode.addDataKeyValue(_name, _value)
                        _retchange = True
                    else: #需要延时的，将其压入全局列表
                        self.__rulechangelist.append([_item[0], _item[1], int(_item[2])])
        
        #查看延时修改的值，将到时间的值进行修改
        _changed_index = []
        for _index, _change in enumerate(self.__rulechangelist):
            if 0 == _change[2]:#延时到了
                _name = _item[0]
                _value = self.Valuetype[_devNode.getVarDic()[_change[0]][0]](_change[1]) #根据类型进行转换
                _devNode.addDataKeyValue(_name, _value)
                _changed_index.append(_index)
                _retchange = True
            else:
                self.__rulechangelist[_index][2] -= 1 
        
        for _index in _changed_index: #将已修改的pop出来
            self.__rulechangelist.pop(_index)
        
        return _retchange
                
        
    #---------------------------------------------------------------------------
    #@计算某个rule的值，成立返回true，反之返回false
    #---------------------------------------------------------------------------    
    def getcurRuleValue(self, rule):
        "calculate rule value"
        _operator = rule['operator']
        _type = rule['type']
        if 'exp' == _type:
            #获取left和right的值
            _left = rule['left']
            _right = rule['right']
            
            if _left['type'] == 'Const':
                _leftValue = self.calculateSubExp(_left, _right['value'])
            else:
                _leftValue = self.calculateSubExp(_left)
                
            if _right['type'] == 'Const':
                _rightValue = self.calculateSubExp(_right, _left['value'])
            else:
                _rightValue = self.calculateSubExp(_right)
                
            #计算表达式的值
            return self.calculateValueformOp(_leftValue, _rightValue, _operator)

        elif 'Mexp' == _type:
            #获取exps
            _exps = rule['exps']
            return self.calulateExps(_exps, _operator)
            
    #---------------------------------------------------------------------------
    #@计算子表达式的值
    #{'type':'Variant','value':'name'}
    #{'type':'exp','value':'AND','left':{},'right':{}}
    #{'type':'Mexp','value':'AND',exps:[{},{}....]}
    #valuename:在变量为常数的时候使用，用来获取变量的类型
    #---------------------------------------------------------------------------
    def calculateSubExp(self, exp, valuename = ''):
        "calculate sub expression"
        _devNode = self.__devicenode
        _type = exp['type']
        _value = exp['value']
        if 'Variant' == _type:
            return _devNode.getDataValue(exp['value'])
        elif 'Const' == _type:  #根据数值的类型进行转换
            return self.Valuetype[_devNode.getVarDic()[valuename][0]](_value)
        elif 'exp' == _type:
            _left = exp['left']
            _right = exp['right'] 
                       
            if _left['type'] == 'Const':
                _leftValue = self.calculateSubExp(_left, _right['value'])
            else:
                _leftValue = self.calculateSubExp(_left)
                
            if _right['type'] == 'Const':
                _rightValue = self.calculateSubExp(_right, _left['value'])
            else:
                _rightValue = self.calculateSubExp(_right)
                
            _operate = exp['value']
            return self.calculateValueformOp(_leftValue, _rightValue, _operate)

        elif 'Mexp' == _type:
            _operate = exp['value']
            _exps = exp['exps']
            return self.calulateExps(_exps, _operate)
        else:
            print 'Error Expression type!'
            
        
    #---------------------------------------------------------------------------
    #@计算多从表达式的值
    #---------------------------------------------------------------------------
    def calulateExps(self, exps, operator):
        "calculate Muti expression"
        _rt = None
        for _exp in exps:
            if None == _rt:
                _rt = self.calculateSubExp(_exp)
            elif 'AND' == operator:
                _rt = _rt and self.calculateSubExp(_exp)
            elif 'OR' == operator:
                _rt = _rt or self.calculateSubExp(_exp)
        return _rt
                
    
    #---------------------------------------------------------------------------
    #@根据operator计算结果
    #---------------------------------------------------------------------------
    def calculateValueformOp(self, leftValue, rightValue, operator):
        "calculator Expression Value"
        if "==" == operator:
            return (leftValue == rightValue)
        elif "GT" == operator:     
            return (leftValue > rightValue)
        elif "LT" == operator:     
            return (leftValue < rightValue)
        elif "GE" == operator:     
            return (leftValue >= rightValue) 
        elif "LE" == operator:     
            return (leftValue <= rightValue)
        elif "AND" == operator:     
            return (leftValue and rightValue)
        elif "OR" == operator:     
            return (leftValue or rightValue)    
        
    
if __name__ == '__main__':
    pass
