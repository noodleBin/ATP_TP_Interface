#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     xmlparser.py
# Description:  用lxml.etree进行xml文件解析      
# Author:       OUYANG Min
# Version:      0.0.2
# Created:      2011-03-08
# Company:      CASCO
# LastChange:   2011-03-08
# History:      create --- 2011-03-08
#               Add Save XML and set xml value  
#----------------------------------------------------------------------------

from lxml import etree

class XmlParser( object ):
    """
    xml file parser
    """
    
    # xml tree root node
    rootNode = None
    # xml file
    #__file = None

    def __init__( self ):
        "init do nothing"
        pass

    def loadXmlFile( self, filename ):
        "load xml file"
        #self.__file = open(filename)
        #_tree = etree.parse(self.__file)
        _tree = etree.parse( filename )
#        _tree.getroot
        self.rootNode = _tree.getroot() 
       
    def getRootAttrList( self, attriList ):
        "get root attrlist"
        return [self.getNodeAttr( self.rootNode, _a ) for _a in attriList]
    
    def closeXmlFile( self ):
        "close xml file"
        pass
        #self.__file.close()
    
    def getAllElementByName( self, path ):
        "get all element by name findall"
        return self.rootNode.findall( path )

    def getElementByName( self, path ):
        "get first element by name find"
        return self.rootNode.find( path )

    def getNodeAttr( self, node, attr ):
        "get attributes by name"
        return node.get( attr ) 

    def getNodeText( self, node ):
        "get element text"
        return node.text

    def getNodeTag( self, node ):
        "get element tag"
        return node.tag
    
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 获得一个节点的多个属性
    #
    # @Param node
    # @Param attriList
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def getAttrListOneNode( self, node, attriList ):
        #print 'node attriList ', node, attriList
        return [self.getNodeAttr( node, _a ) for _a in attriList]

    # --------------------------------------------------------------------------
    ##
    # @Brief 获得一个元素的多个属性
    #
    # @Param path
    # @Param attriList
    #
    # @Returns 属性列表
    # --------------------------------------------------------------------------
    def getAttrListOneElement( self, path, attriList ):
        "get attributes of one element"
        _node = self.getElementByName( path )
        return self.getAttrListOneNode( _node, attriList )
    
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 获得多个节点的多个属性
    #
    # @Param node
    # @Param attriList
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def getAttrListManyNode( self, nodeList, attriList ):
        return [[self.getNodeAttr( _n, _a ) for _a in attriList] for _n in nodeList]

    # --------------------------------------------------------------------------
    ##
    # @Brief 获得多个元素的多个属性
    #
    # @Param path
    # @Param attriList
    #
    # @Returns 属性列表
    # --------------------------------------------------------------------------
    def getAttrListManyElement( self, path, attriList ):
        "get attributes of many element"
        _nodeList = self.getAllElementByName( path )
        return self.getAttrListManyNode( _nodeList, attriList )

    
    # --------------------------------------------------------------------------
    ##
    # @Brief 获得一个元素的子元素的值
    #
    # @Param node
    #
    # @Returns 
    # --------------------------------------------------------------------------
    def getTextListNode( self, node ):
        #当前node节点的text不返回
        return [self.getNodeText( _n ) for _n in node.iter()][1:]

    # --------------------------------------------------------------------------
    ##
    # @Brief 获得一个元素的子元素的值
    #
    # @Param path
    #
    # @Returns 元素值的列表
    # --------------------------------------------------------------------------
    def getTextListElement( self, path ):
        "get text of many element"
        _node = self.getElementByName( path )
        return self.getTextListNode( _node )

    # --------------------------------------------------------------------------
    ##
    # @Brief 在当前的节点中，通过路径查找子节点
    #
    # @Param rootNode
    # @Param path
    #
    # @Returns 节点
    # --------------------------------------------------------------------------
    def getNodeInNode( self, rootNode, path ):
        return rootNode.find( path )

    # --------------------------------------------------------------------------
    ##
    # @Brief 在当前节点中，通过路径查找子节点列表
    #
    # @Param rootNode
    # @Param path
    #
    # @Returns 节点列表
    # --------------------------------------------------------------------------
    def getNodeListInNode( self, rootNode, path ):
        return rootNode.findall( path )

    # --------------------------------------------------------------------------
    ##
    # @Brief 在当前节点中，设置节点的属性值
    #
    # @Param rootNode
    # @Param attr
    # @Param value 变量值
    # --------------------------------------------------------------------------
    def setNodeAttrValue( self, rootNode, attr, value ):
        rootNode.set( attr, value )
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 在当前节点中，设置节点的多个属性值
    #
    # @Param rootNode
    # @Param attr
    # @Param value 变量值，
    # --------------------------------------------------------------------------
    def setNodeMutiAttrValue( self, rootNode, attr, value ):
        for _i in range( attr ):
            rootNode.set( attr( _i ), value( value ) )

    # --------------------------------------------------------------------------
    ##
    # @Brief 在当前节点下，添加一个节点，并设置节点的多个属性值
    #
    # @Param rootNode
    # @Para  NodeName
    # @Param attr
    # @Param value 变量值
    # @return 创建的新新节点
    # --------------------------------------------------------------------------
    def addNewNode( self, rootNode, NodeName, attr, value ):
        _Node = etree.SubElement( rootNode, NodeName )
        for _i in range( attr ):
            _Node.set( attr( _i ), value( value ) )
        return _Node

    # --------------------------------------------------------------------------
    ##
    # @Brief 生成新根节点，添加一个节点，并设置节点的多个属性值
    #
    # @Param RootName
    # @Param attr
    # @Param value 变量值
    # @return 创建的新新节点
    # --------------------------------------------------------------------------
    def createRoot( self, RootName, attr, value ):
        _root = etree.Element( RootName )
        for _i in range( attr ):
            _root.set( attr( _i ), value( value ) )
        return _root    

    # --------------------------------------------------------------------------
    ##
    # @Brief 将xml存入
    #
    # @Param root
    # @Param path
    # --------------------------------------------------------------------------
    def saveXml( self, root, path ):
        strXML = etree.tostring( root, pretty_print = True, encoding = "utf-8" )
        _file = open( path, 'w' )
        #写入头
        _file.write( r'''<?xml version="1.0" encoding="utf-8"?>''' ) 
        _file.write( "\n" ) 
        #写入数据
        _file.write( strXML ) #保存数据
        _file.close()
        
    # --------------------------------------------------------------------------
    ##
    # @Brief 删除符合要求的节点，根据属性值，找到第一个匹配的属性，并删除
    #
    # @Param parent
    # @Param attr
    # @Param value
    # --------------------------------------------------------------------------
    def removeNodeByAttr( self, parent, attr, value ):
        _child = parent.getchildren()
        _elememt = None
        for _c in _child:
            _find = True
            for _i in range( attr ):
                if value[_i] != _c.get( attr[_i] ):
                    _find = False
                    break
            if True == _find:
                _elememt = _c
                break
        if None != _elememt:
            parent.remove( _elememt )
        else:
            print "removeNodeByAttr: Can't find the element!"
          
        
if __name__ == '__main__':
    x = XmlParser()
    #x.loadXmlFile(r'./varint.xml')
    x.loadXmlFile( r'./message.xml' )
    print x.getAllElementByName( r'.//Msg' )
    x.closeXmlFile()
