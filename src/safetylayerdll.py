# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     safetylayerdll_new.py
# Description:  安全层协议SACEM动态链接库接口类     
# Author:       YanLi
# Version:      0.0.1
# Created:      2012-12-26
# Company:      CASCO
# LastChange:   create 2012-12-26
# History:      LC, VIOM, ZC
# update:       ouyangmin add code for fsfb2
#----------------------------------------------------------------------------
from ctypes import *
from lxml import etree
from base import commlib
from base.caseprocess import CaseParser

# @brief 定义编码码字
class codeWord( Structure ):
    """
    Codeword
    """
    _fields_ = [( "CdwH", c_int32 ), \
               ( "CdwL", c_int32 )]
    
# @brief 应用给SACEM协议的发送数据_LC TSR消息
class GM_SACEM_Shb_App2Trans_TSR_Base( Structure ):
    """
    Application Safety Data
    """   
    _fields_ = [( "TSR_Value", codeWord * 12003 )]  
    
# @brief 应用给SACEM协议的发送数据_LC TSR消息
class GM_SACEM_Shb_App2Trans_TSR( Structure ):
    """
    Application Safety Data
    """
    _fields_ = [( "shb_app2trans_1", POINTER( GM_SACEM_Shb_App2Trans_TSR_Base ) ), \
                ( "shb_app2trans_2", POINTER( GM_SACEM_Shb_App2Trans_TSR_Base ) )] 

# @brief 应用给SACEM协议的发送数据
class GM_SACEM_Shb_App2Trans_Other_Base( Structure ):
    """
    Application Safety Data
    """   
    _fields_ = [( "Other_Value", codeWord * 12003 )]
    
class GM_SACEM_Shb_App2Trans_Other( Structure ):
    """
    Application Safety Data
    """   
    _fields_ = [( "shb_app2trans_1", POINTER( GM_SACEM_Shb_App2Trans_Other_Base ) ), \
                ( "shb_app2trans_2", POINTER( GM_SACEM_Shb_App2Trans_Other_Base ) )]   
    

# @brief 应用给SACEM协议的发送数据
class GM_SACEM_Shb_App2Recv_Other_Base( Structure ):
    """
    Application Safety Data
    """   
    _fields_ = [( "Other_Value", c_int32 * 256 )]
    
       
# @brief LC,ZC,VIOM设备---应用给协议的接收消息
class GM_SACEM_Shb_App2Recv_Type( Structure ):     #rename GM_SACEM_Shb_App2Recv_Type_LC
    """
    LC---SACEM Message
    """      
    _fields_ = [( "shb_app2recv_1", POINTER( GM_SACEM_Shb_App2Recv_Other_Base ) ), \
                ( "shb_app2recv_2", POINTER( GM_SACEM_Shb_App2Recv_Other_Base ) ), \
                ( "app2recv_checksum_1", c_int32 ), \
                ( "app2recv_checksum_2", c_int32 )]    
 
class  GM_SACEM_Shb_Recv2App_Other_Base( Structure ):
    """
    SACEM Message
    """
    _fields_ = [( "recv2app_value", codeWord * 256 )]       
  
        
# @brief  LC,ZC,VIOM设备---接收消息返回给应用的值
class GM_SACEM_Shb_Recv2App_Type( Structure ):    #rename GM_SACEM_Shb_Recv2App_Type_LC
    """
    LC,ZC,VIOM---Application Safety data
    """
    _fields_ = [( "shb_recv2app_1", POINTER( GM_SACEM_Shb_Recv2App_Other_Base ) ), \
                ( "shb_recv2app_2", POINTER( GM_SACEM_Shb_Recv2App_Other_Base ) )]
    

    
# @brief SACEM接口类
class GM_SACEM_Dll:
    """
    SACEM 接口类
    """
    #SACEM动态链接库的实例
    sacemDll = None
    
    #SACEM设备字典
    #例子‘ZC’:{'mode':string, 'dllFile':string, 'cnfFile':string, 'EOA':[msgId, varNum]}
    __device = None
    
    #当前实例化的设备名
    __deviceName = None
    
    #SACEM的设备列表结构
    sacemDeviceListParser = {
                    'Device':{
                              'path':r'/Devices/Device',
                              'attr':['@name', '@mode']
                              },
                    'DllFile':{
                               'path':r'.//DllFile',
                               'attr':['@path']
                               },
                    'CnfFile':{
                               'path':r'.//CnfFile',
                               'attr':['@path']                               
                               },
                    'Msg':{
                           'path':r'.//Msg',
                           'attr':['@name', '@id', '@varNum']                             
                           }
                    }    
    # @param deviceName: 调用SACEM的设备名称，如'ZC'
    def __init__( self, deviceName , path ):
        "Create SACEM DLL"
        self.__deviceName = deviceName
        #导入设备里列表
        self.ImportDevice( path )
#        print self.__device
        
        self.sacemDll = CDLL( self.__device[self.__deviceName]['dllFile'] )
        
    # @note: 导入设备列表xml
    # @param devicelistfile: sacem_devicelist.xml路径
    def ImportDevice( self, devicelistfile ):
        "导入SACEM支持的设备列表"
        self.__device = {}
        _tree = etree.parse( devicelistfile )
        _deviceroot = _tree.xpath( self.sacemDeviceListParser['Device']['path'] )
        for _device in _deviceroot:
            #获取device脚本的基本信息
            #设备名
            _deviceName = _device.xpath( self.sacemDeviceListParser['Device']['attr'][0] )[0]
            #将设备名作为key，创建字典
            self.__device[_deviceName] = {}
            #模式：NoVital，VCP，NISAL
            _deviceMode = _device.xpath( self.sacemDeviceListParser['Device']['attr'][1] )[0]
            self.__device[_deviceName]['mode'] = _deviceMode
            #dll路径
            _dllFileNode = _device.find( 'DllFile' )
            _dllFile = _dllFileNode.xpath( self.sacemDeviceListParser['DllFile']['attr'][0] )[0]
            self.__device[_deviceName]['dllFile'] = _dllFile
            #cnf路径
            _cnfFileNode = _device.find( 'CnfFile' )
            _cnfFile = _cnfFileNode.xpath( self.sacemDeviceListParser['CnfFile']['attr'][0] )[0]
            self.__device[_deviceName]['cnfFile'] = _cnfFile
            #MsgId,Varnum
            _msgNodes = _device.findall( 'Msg' )
            for _msgNode in _msgNodes:
                _msgName = _msgNode.xpath( self.sacemDeviceListParser['Msg']['attr'][0] )[0]            
                self.__device[_deviceName][_msgName] = []
                _msgId = _msgNode.xpath( self.sacemDeviceListParser['Msg']['attr'][1] )[0]
                _msgVarNum = _msgNode.xpath( self.sacemDeviceListParser['Msg']['attr'][2] )[0] 
                self.__device[_deviceName][_msgName].append( int( _msgId ) )
                self.__device[_deviceName][_msgName].append( int( _msgVarNum ) )
#        print self.__device

    # @note: 初始化SACEM和VSN
    def SACEM_Init_Dll( self, path = None ):
        "SACEM Initialization"
        _path = path if None != path else self.__device[self.__deviceName]['cnfFile']
        ret1 = self.sacemDll.SACEMDll_Init( _path )
        ret2 = self.sacemDll.GM_VSN_Init();
        
        if ( True == ret1 ) and ( True == ret2 ):
            return True
        else:
            return False
        
    # @note: 计算Checksum函数
    # @param TxShbBuf: 待计算的应用数据，不含Src和Dest，类型为列表
    # @return: 双通道Checksum
    def SACEM_Tx_Msg_Dll( self, msgid, SrcSSTy, SrcSSID, \
                         DestSSTy, DestSSID, TxShbBuf ):
        "SACEM Message Packing"
        #计算源节点和目标节点
        Src = SrcSSTy
        Src = ( Src << 8 ) & 0xff00
        Src = Src + ( SrcSSID & 0x00ff )
        Dest = DestSSTy
        Dest = ( Dest << 8 ) & 0xff00
        Dest = Dest + ( DestSSID & 0x00ff )

        Other_Base_1 = GM_SACEM_Shb_App2Trans_Other_Base()
        Other_Base_2 = GM_SACEM_Shb_App2Trans_Other_Base()
        TxBuf = GM_SACEM_Shb_App2Trans_Other()            
        #给TxBuf赋值
        TxBuf.shb_app2trans_1 = pointer( Other_Base_1 )
        TxBuf.shb_app2trans_2 = pointer( Other_Base_2 )
        Other_Base_1.Other_Value[0].CdwH = Src
        Other_Base_1.Other_Value[1].CdwH = Dest
        Other_Base_2.Other_Value[0].CdwH = Src
        Other_Base_2.Other_Value[1].CdwH = Dest 
        
        #print "---", msgid, Src , Dest
        if self.__deviceName == 'ci':
            if self.__device[self.__deviceName]['CCVariant_Request'][0] == msgid:
                #CIVariant_Report_CI2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['CCVariant_Request'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['CCVariant_Request'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0;
                    Other_Base_2.Other_Value[_c].CdwL = 0;
            elif self.__device[self.__deviceName]['CIVariant_Report'][0] == msgid:
                #CIVariant_Report_CI2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['CIVariant_Report'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['CIVariant_Report'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0;
                    Other_Base_2.Other_Value[_c].CdwL = 0;            
            else:
                print "not found ci msg"
        elif self.__deviceName == 'lc':                
            if self.__device[self.__deviceName]['DateSynReport'][0] == msgid:
                #DateSyn_LC2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['DateSynReport'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['DateSynReport'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0
                    Other_Base_2.Other_Value[_c].CdwL = 0 
            elif self.__device[self.__deviceName]['CCVersion_Authorization'][0] == msgid:
                #CCVersion_Authorization_LC2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['CCVersion_Authorization'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['CCVersion_Authorization'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0
                    Other_Base_2.Other_Value[_c].CdwL = 0  
            elif self.__device[self.__deviceName]['TSR1'][0] == msgid:
                #CCVersion_Authorization_LC2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['TSR1'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['TSR1'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0
                    Other_Base_2.Other_Value[_c].CdwL = 0 
            elif self.__device[self.__deviceName]['TSR2'][0] == msgid:
                #CCVersion_Authorization_LC2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['TSR2'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['TSR2'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0
                    Other_Base_2.Other_Value[_c].CdwL = 0 
            else:
                print "not found lc msg"
        elif self.__deviceName == 'zc':                
            if self.__device[self.__deviceName]['EOA'][0] == msgid:
                #EOA_ZC2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['EOA'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['EOA'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0
                    Other_Base_2.Other_Value[_c].CdwL = 0   
            elif self.__device[self.__deviceName]['Variants'][0] == msgid:
                #Variants_ZC2CC
                for _c in range( 0, self.__device[self.__deviceName]['Variants'][1] ):
                    Other_Base_1.Other_Value[_c ].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c ].CdwH = TxShbBuf[_c]
                    Other_Base_1.Other_Value[_c].CdwL = 0
                    Other_Base_2.Other_Value[_c].CdwL = 0             
            else:
                print "not found zc msg"    
        elif self.__deviceName == 'viom':                
            if self.__device[self.__deviceName]['VitalInput'][0] == msgid:
                #VitalInput_VIOM2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['VitalInput'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['VitalInput'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0
                    Other_Base_2.Other_Value[_c].CdwL = 0    
            else:
                print "not found viom msg"
        elif self.__deviceName == 'datp':                
            if self.__device[self.__deviceName]['Msg_DATP2ATP'][0] == msgid:
                #VitalInput_VIOM2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['Msg_DATP2ATP'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['Msg_DATP2ATP'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0
                    Other_Base_2.Other_Value[_c].CdwL = 0    
            else:
                print "not found viom msg"
      
                                        
        CheckSum_1 = c_int32()
        CheckSum_2 = c_int32()
        
#        print "----", msgid, Src, Dest
#        for _c in range(0, 40):
#            print TxBuf.shb_app2trans_1[_c].CdwH, TxBuf.shb_app2trans_1[_c].CdwL, \
#                TxBuf.shb_app2trans_2[_c].CdwH, TxBuf.shb_app2trans_2[_c].CdwL
#        print msgid,Src, Destm pointer(Txbuf), pointer(CheckSum_1), 
        ret = self.sacemDll.SACEMDll_Packing( msgid, Src, Dest, pointer( TxBuf ), \
                                             pointer( CheckSum_1 ), pointer( CheckSum_2 ) )
        #print "checksum " , CheckSum_1.value , CheckSum_2.value
        if False == ret:
            print "sacem send failed", msgid
            return None
        else:
#            print CheckSum_1.value, CheckSum_2.value
            cks1_1, cks1_2, cks1_3 = self.transform_Ito3Byte( CheckSum_1.value )
            cks2_1, cks2_2, cks2_3 = self.transform_Ito3Byte( CheckSum_2.value )
#            cks1_1, cks1_2, cks1_3 = self.transform_Ito3Byte(10290608)
#            cks2_1, cks2_2, cks2_3 = self.transform_Ito3Byte(3965632)
#            print cks1_1, cks1_2, cks1_3, cks2_1, cks2_2, cks2_3
            return cks1_1, cks1_2, cks1_3, cks2_1, cks2_2, cks2_3
        
    # @note: 校验Checksum函数
    # @param RxShbBuf: 待解包的消息， 类型为列表，结构为Application data + Checksum1 + Checksum2 
    # @return: 码字CodeWord， 类型为GM_SACEM_Shb_Recv2App_Type， 
    def SACEM_Rx_Msg_Dll( self, msgid, SrcSSTy, SrcSSID, DestSSTy, DestSSID,
                         RxShbBuf ):
        "SACEM Message Unpacking"
        #计算源节点和目标节点
        Src = SrcSSTy
        Src = ( Src << 8 ) & 0xff00
        Src = Src + ( SrcSSID & 0x00ff )
        Dest = DestSSTy
        Dest = ( Dest << 8 ) & 0xff00
        Dest = Dest + ( DestSSID & 0x00ff )
        
        #print "src, Dest", Src, Dest
        rxBuff = GM_SACEM_Shb_App2Recv_Type()
        Other_Base_1 = GM_SACEM_Shb_App2Recv_Other_Base()
        Other_Base_2 = GM_SACEM_Shb_App2Recv_Other_Base()         
        #给rxBuff赋值
        rxBuff.shb_app2recv_1 = pointer( Other_Base_1 )
        rxBuff.shb_app2recv_2 = pointer( Other_Base_2 )
        Other_Base_1.Other_Value[0] = Src
        Other_Base_2.Other_Value[0] = Src
        Other_Base_1.Other_Value[1] = Dest
        Other_Base_2.Other_Value[1] = Dest
        reVal = GM_SACEM_Shb_Recv2App_Type()
        reVal_Base_1 = GM_SACEM_Shb_Recv2App_Other_Base()
        reVal_Base_2 = GM_SACEM_Shb_Recv2App_Other_Base()
        reVal.shb_recv2app_1 = pointer( reVal_Base_1 )
        reVal.shb_recv2app_2 = pointer( reVal_Base_2 )
        
#        print "RxShbBuf" , RxShbBuf
#        print self.__device[self.__deviceName]['Protection_Report'][1]
        if self.__deviceName == 'ci':
            if self.__device[self.__deviceName]['CIVariant_Request'][0] == msgid:
                #CIVariant_Request_CC2CI
                for _c in range( 0, ( self.__device[self.__deviceName]['CIVariant_Request'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2] = RxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2] = RxShbBuf[_c]
                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['CIVariant_Request'][1] - 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CIVariant_Request'][1] - 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CIVariant_Request'][1] )] )    
                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['CIVariant_Request'][1] + 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CIVariant_Request'][1] + 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CIVariant_Request'][1] + 3 )] )
            elif self.__device[self.__deviceName]['CCVariant_Report'][0] == msgid: 
                #CCVariant_Report_CC2CI
                for _c in range( 0, ( self.__device[self.__deviceName]['CCVariant_Report'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2] = RxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2] = RxShbBuf[_c]                   
                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVariant_Report'][1] - 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVariant_Report'][1] - 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVariant_Report'][1] )] )    
                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVariant_Report'][1] + 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVariant_Report'][1] + 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVariant_Report'][1] + 3 )] )
            else:
                return None        
        elif self.__deviceName == 'lc':
            if self.__device[self.__deviceName]['CCVersion_Report'][0] == msgid:
                #CCVersion_Report_CC2LC
                for _c in range( 0, ( self.__device[self.__deviceName]['CCVersion_Report'][1] - 1 ) ):
                    Other_Base_1.Other_Value[_c + 1] = RxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 1] = RxShbBuf[_c]
                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersion_Report'][1] - 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersion_Report'][1] )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersion_Report'][1] + 1 )] )
                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersion_Report'][1] + 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersion_Report'][1] + 3 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersion_Report'][1] + 4 )] )
            else:
                return None 
        elif self.__deviceName == 'zc':
            if self.__device[self.__deviceName]['LocReport'][0] == msgid:
                #LocReport_CC2ZC
                for _c in range( 0, ( self.__device[self.__deviceName]['LocReport'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2] = RxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2] = RxShbBuf[_c]
                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] - 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] - 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] )] )
                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] + 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] + 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] + 3 )] )
            else:
                return None 
        elif self.__deviceName == 'viom':
            if self.__device[self.__deviceName]['VitalOutput'][0] == msgid:
                #VitalOutput_CC2VIOM
                for _c in range( 0, ( self.__device[self.__deviceName]['VitalOutput'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2] = RxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2] = RxShbBuf[_c]
                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['VitalOutput'][1] - 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['VitalOutput'][1] - 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['VitalOutput'][1] )] )
                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['VitalOutput'][1] + 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['VitalOutput'][1] + 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['VitalOutput'][1] + 3 )] )
            else:
                return None
        elif self.__deviceName == 'datp':
            if self.__device[self.__deviceName]['Msg_DATP2ATP'][0] == msgid:
                #Msg_DATP2ATP_CC2DATP
                for _c in range( 0, ( self.__device[self.__deviceName]['Msg_DATP2ATP'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2] = RxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2] = RxShbBuf[_c]
                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_DATP2ATP'][1] - 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_DATP2ATP'][1] - 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_DATP2ATP'][1] )] )
                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_DATP2ATP'][1] + 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_DATP2ATP'][1] + 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_DATP2ATP'][1] + 3 )] )
            else:
                return None       
        else:
            return None
        #print "rxBuff.app2recv_checksum_1", rxBuff.app2recv_checksum_1 
        #print "rxBuff.app2recv_checksum_2", rxBuff.app2recv_checksum_2
        #print "rxbuff", rxBuff.shb_app2recv_1[1]
        #print "RxShbBuf", RxShbBuf
        ret = self.sacemDll.SACEMDll_Unpacking( msgid, Src, Dest, pointer( rxBuff ), pointer( reVal ) )
        if False == ret:
            print 'sacem recv failed ', msgid, "SrcSSTy:", SrcSSTy, SrcSSID, DestSSTy, DestSSID
            return None
        else:
            return reVal
        
    # @note: 计算校核字函数
    # @return: 双通道接收、发送四个校核字
    def SACEM_Get_CKW_Dll( self ):
        "SACEM Checkword Calculation"
        SACEM_TxCKW1 = c_int32()
        SACEM_TxCKW2 = c_int32()
        SACEM_RxCKW1 = c_int32()
        SACEM_RxCKW2 = c_int32()
        
        ret = self.sacemDll.SACEMDll_Get_CKW( pointer( SACEM_TxCKW1 ), pointer( SACEM_TxCKW2 ), \
                                             pointer( SACEM_RxCKW1 ), pointer( SACEM_RxCKW2 ) )
        if False == ret:
            return None
        else:
            return SACEM_TxCKW1.value, SACEM_TxCKW2.value, \
                   SACEM_RxCKW1.value, SACEM_RxCKW2.value     
        
    #@note: 将3个Byte转化成1个checksum
    #@param _B1,_B2,_B3: 3个Byte，_B1为最高位，_B3为低位
    #@return: 32位数
    def transfor_3BytetoI( self, _B1, _B2, _B3 ):
        "get checksum from 3 bytes"
        return _B1 * 256 * 256 + _B2 * 256 + _B3
    
    #@note: 将一个checksum转化为3个byte
    #@return: _B1,_B2,_B3,3个Byte，_B1为最高位，_B3为低位
    def transform_Ito3Byte( self, _checksum ):
        "get 3 bytes from checksum"
        _B3 = _checksum % 256
        _B2 = ( ( _checksum - _B3 ) / 256 ) % 256
        _B1 = ( ( _checksum - _B3 - _B2 * 256 ) / 256 / 256 ) % 256
        return _B1, _B2, _B3
    
    # @note: 获取VSN 
    # @param _channel: 1 --- 通道1； 2 --- 通道2
    def GM_VSN_Get( self, _channel ):
        "获取VSN"
        _vsn0 = c_int32()
        _vsn1 = c_int32()
        _vsn2 = c_int32()
        
        self.sacemDll.GM_VSN_Get( pointer( _vsn0 ), pointer( _vsn1 ), pointer( _vsn2 ) )
        if 1 == _channel:
            return _vsn1.value
        elif 2 == _channel:
            return _vsn2.value
        else:
            return None   
        
    # @note: 获取VSN掩码
    # @param _channel: 1 --- 通道1； 2 --- 通道2
    def GM_VSN_M_get( self, _channel ):
        "获取VSN掩码"
        _vsn_m_1 = c_int32()
        _vsn_m_2 = c_int32()
        
        self.sacemDll.GM_VSN_M0102_Get( pointer( _vsn_m_1 ), pointer( _vsn_m_2 ) )
        if 1 == _channel:
            return _vsn_m_1.value
        elif 2 == _channel:
            return _vsn_m_2.value
        else:
            return None

    # @note: 更新VSN, 每周期执行一次
    def GM_VSN_Update( self ):
        "更新VSN"
        self.sacemDll.GM_VSN_Update()
    


# @brief fsfb2

# @brief codeWord for 2 channel
class CodeWord2Chanel( Structure ):
    """
    Codeword for 2 channel
    """
    _fields_ = [( "CH1_H", c_int32 ), \
               ( "CH1_L", c_int32 ), \
               ( "CH2_H", c_int32 ), \
               ( "CH2_L", c_int32 )]

# @brief structure for the Application layer and fsfb2 layer
class GM_FSFB2_SHB_BUF_Node( Structure ):
    """
    brief structure for the Application layer and fsfb2 layer
    """
    _pack_ = 1 
    _fields_ = [( "Index", c_int32 ), \
               ( "FSFB2_SubAppID", c_uint8 ), \
               ( "FSFB2_LocalNodeID", c_uint16 ), \
               ( "VSN0", c_uint32 ), \
               ( "VSN1", c_uint32 ), \
               ( "VSN2", c_uint32 ), \
               ( "SHB_NETTX_1", c_uint32 * 256 ), \
               ( "SHB_NETTX_2", c_uint32 * 256 ), \
               ( "SHB_MASC_INCL_1", c_uint32 ), \
               ( "SHB_MASC_INCL_2", c_uint32 ), \
               ( "SHB_CKW_1", c_uint32 ), \
               ( "SHB_CKW_2", c_uint32 ), \
               ( "SHB_NETRX", c_uint8 * 256 ), \
               ( "SHB_NETRX_1", c_uint32 * 256 ), \
               ( "SHB_NETRX_2", c_uint32 * 256 )]

# @brief structure for the Application layer and fsfb2 layer
class GM_FSFB2_SHB_BUF( Structure ):
    """
    brief structure for the Application layer and fsfb2 layer
    """
    _fields_ = [( "num", c_int32 ), \
               ( "con", GM_FSFB2_SHB_BUF_Node * 100 )]
        
#class GM_FSFB2_DLL
class GM_FSFB2_DLL( object ):
    """
    GM FSFSb2 protocol
    """
    
    #FSFB2的设备列表结构
    FSFB2DeviceListParser = {
                    'Device':{
                              'path':r'/Devices/Device',
                              'attr':['@name', '@mode']
                              },
                    'DllFile':{
                               'path':r'.//DllFile',
                               'attr':['@path']
                               },
                    'CnfFile':{
                               'path':r'.//CnfFile',
                               'attr':['@path']                               
                               },
                    'Msg':{
                           'path':r'.//Msg',
                           'attr':['@name', '@id', '@varNum']                             
                           },
                    'Var':{
                           'path':r'.//Var',
                           'attr':['@name', '@value']
                           },
                    'Node':{
                           'path':r'.//Node',
                           'attr':['@Dev_ID', '@GM_NodeID']
                           }                             
                    }    
    
    __deviceName = None
    __fsfb2Dll = None
    __sndMsg = None
    __sndMsgNum = None
    __rcvMsg = None
    __rcvMsgNum = None
    __pointGM_FSFB2_SHB_BUF = None
    __sndmsgID = None
    __rcvmsgID = None
    __fsfb2NodeNum = None
    __callBackFun = None  
    
    def __init__( self, deviceName , fun, path = None ):
        "default init"
        
        self.__deviceName = deviceName
        #导入设备里列表
#        self.ImportDevice( "./setting/deviceFSFB2.xml" )
        #from configure file
        self.importFSFB2Config( path )
        self.__sndmsgID = self.__device[deviceName]["SendMsg"][0]
        self.__GM_FSFB2_SYSCHECK_1 = self.__device[deviceName]["SYSCHECK_1"]
        self.__GM_FSFB2_SYSCHECK_2 = self.__device[deviceName]["SYSCHECK_2"]       
        self.__sndMsgNum = self.__device[deviceName]["SendMsg"][1]
        self.__rcvMsgNum = self.__device[deviceName]["RevMsg"][1]
        self.__fsfb2NodeNum = self.__device[deviceName]["NodeNum"]
#        self.__msgID = self.__device[deviceName][]
#        self.__GM_FSFB2_SYSCHECK_1 = 0xae390b5a
#        self.__GM_FSFB2_SYSCHECK_2 = 0xc103589c       
#        self.__sndMsgNum = 1
#        self.__rcvMsgNum = 4
#        self.__fsfb2NodeNum = 15        
        _callBackfun = CFUNCTYPE( c_int32, c_int16, c_uint8, POINTER( c_uint8 ), c_uint16 )
        self.__callBackFun = _callBackfun( fun )
        #self.__callBackFun = _callBackfun( self.fsfb2CallBackFun )
#        self.__fsfb2Dll = CDLL( self.__device[self.__deviceName]['dllFile'] )
        self.__fsfb2Dll = CDLL( r'./dll/fsfb2dll.dll' )
        #print 'fsfb2dll', self.__fsfb2Dll
        #set function return type for pointer
        self.__fsfb2Dll.GM_FSFB2_SHB_Get_Handle.restype = POINTER( GM_FSFB2_SHB_BUF )


    #-----------------------------------------------------------
    #导入FSFB2配置文件
    #@path:文件路径
    #数据列表:
    #-----------------------------------------------------------
    def importFSFB2Config( self, path ):
        "import FSFB2 Configure File."
        self.__device = {}
#        print path
        _tree = etree.parse( path )
        _deviceroot = _tree.xpath( self.FSFB2DeviceListParser['Device']['path'] )
        for _device in _deviceroot:
            #获取device脚本的基本信息
            #设备名
            _deviceName = _device.xpath( self.FSFB2DeviceListParser['Device']['attr'][0] )[0]
            #将设备名作为key，创建字典
            self.__device[_deviceName] = {}
            #模式：NoVital，VCP，NISAL
            _deviceMode = _device.xpath( self.FSFB2DeviceListParser['Device']['attr'][1] )[0]
            self.__device[_deviceName]['mode'] = _deviceMode
            #dll路径
            _dllFileNode = _device.find( 'DllFile' )
            _dllFile = _dllFileNode.xpath( self.FSFB2DeviceListParser['DllFile']['attr'][0] )[0]
            self.__device[_deviceName]['dllFile'] = _dllFile
            #cnf路径
#            _cnfFileNode = _device.findall( 'CnfFile' )
#            print _cnfFileNode
#            _cnfFile = []
#            for _cnfnode in _cnfFileNode:
#                _cnfFile.append( _cnfnode.xpath( self.FSFB2DeviceListParser['CnfFile']['attr'][0] )[0] )
#            
#            self.__device[_deviceName]['cnfFile'] = _cnfFile
            #MsgId,Varnum
            _msgNodes = _device.findall( 'Msg' )
            for _msgNode in _msgNodes:
                _msgName = _msgNode.xpath( self.FSFB2DeviceListParser['Msg']['attr'][0] )[0]            
                self.__device[_deviceName][_msgName] = []
                _msgId = _msgNode.xpath( self.FSFB2DeviceListParser['Msg']['attr'][1] )[0]
                _msgVarNum = _msgNode.xpath( self.FSFB2DeviceListParser['Msg']['attr'][2] )[0] 
                self.__device[_deviceName][_msgName].append( int( _msgId ) )
                self.__device[_deviceName][_msgName].append( int( _msgVarNum ) )
                
            _varNodes = _device.findall( 'Var' )
            for _varNode in _varNodes:
                _name = _varNode.xpath( self.FSFB2DeviceListParser['Var']['attr'][0] )[0]            
                _vaule = int( _varNode.xpath( self.FSFB2DeviceListParser['Var']['attr'][1] )[0] )                
                self.__device[_deviceName][_name] = _vaule
            _Nodes = _device.findall( 'Node' )
            self.__device[_deviceName]["Node"] = {}
            for _Node in _Nodes:
                _dev_Id = int( _Node.xpath( self.FSFB2DeviceListParser['Node']['attr'][0] )[0] )            
                _GM_NodeId = int( _Node.xpath( self.FSFB2DeviceListParser['Node']['attr'][1] )[0] )                
                self.__device[_deviceName]["Node"][_dev_Id] = _GM_NodeId
#        print self.__device     
    
    
    def fsfb2Init( self ):
        "GM fsfb2 init"
        
        "_msgNum 消息长度，配置文件"
        _SndMsg = CodeWord2Chanel * self.__sndMsgNum
        _RcvMsg = CodeWord2Chanel * self.__rcvMsgNum
        self.__sndMsg = _SndMsg()
        self.__rcvMsg = _RcvMsg()
#        _tmpstr = c_char * 100
#        c_p = _tmpstr()
        #print '__sndMsg', self.__sndMsg, self.__rcvMsg
        if( self.__fsfb2Dll.GM_VSN_Init() == False ):
            return None
        
#        rt = self.__fsfb2Dll.GM_FSFB2_Init( self.__fsfb2NodeNum, self.__callBackFun , pointer( c_p ) )
#        print repr( c_p.value )
#        return rt
        if( self.__fsfb2Dll.GM_FSFB2_Init( self.__fsfb2NodeNum, self.__callBackFun ) <= 0 ):
            return None
        
        if( self.__fsfb2Dll.GM_Code_SNV_Init() == False ):
            return None
        
        return True


    # --------------------------------------------------------------------------
    ##
    # @Brief 预处理需要发送的FSFB2消息
    #
    # @Param msg 消息内容 消息 格式((C1_H,C1_L,C2_H,C2_L)...)
    #
    # @Returns if false return None
    # --------------------------------------------------------------------------  
    def setCodeWord2Chanel( self, msg ):
        "set message to structure"
        #
        try:
            self.__sndMsg = ( CodeWord2Chanel * len( msg ) )( *msg )
            return True
        except Exception, e:
            print "fsfb2 setCodeWord2Chanel error", e
            return None

    # --------------------------------------------------------------------------
    ##
    # @Brief 编码FSFB2消息
    #
    # @Param msg 消息内容 消息 格式((C1_H,C1_L,C2_H,C2_L)...)
    #
    # @Returns if false return None
    # --------------------------------------------------------------------------  
    def encodeFsfb2SndMsg( self, fsfb2LocalNodeID, msg ):
        "encode application message and put into fsfb2 channel"
        
        _localNodeID = c_uint16()
        _typeIndex = c_int32()
        _localNodeID = fsfb2LocalNodeID
        _codeNum = c_uint16()
        _hasNode = None
        
        if ( self.setCodeWord2Chanel( msg ) == None ):
            #print 'setCodeWord2Chanel' 
            return None
        
        if ( self.__fsfb2Dll.GM_Code_GetTypeIndex( 16 * fsfb2LocalNodeID, pointer( _typeIndex ) ) == False ):
            #print 'GM_Code_GetTypeIndex'
            return None
        
        if ( self.__fsfb2Dll.GM_Code_SINGLE2NISAL( _typeIndex, pointer( self.__sndMsg ), pointer( _codeNum ) ) == False ):
            #print 'GM_Code_SINGLE2NISAL'
            return None
        self.__pointGM_FSFB2_SHB_BUF = self.__fsfb2Dll.GM_FSFB2_SHB_Get_Handle()
    
        for i in range( self.__pointGM_FSFB2_SHB_BUF.contents.num ):
            #print "nodeID:", self.__pointGM_FSFB2_SHB_BUF.contents.con[i].FSFB2_LocalNodeID
            if  self.__device[self.__deviceName]['Node'][_localNodeID] == self.__pointGM_FSFB2_SHB_BUF.contents.con[i].FSFB2_LocalNodeID:
                _hasNode = True
                for _index in range( _codeNum.value ):
                    self.__pointGM_FSFB2_SHB_BUF.contents.con[i].SHB_NETTX_1[_index] = self.__sndMsg[_index].CH1_L
                    self.__pointGM_FSFB2_SHB_BUF.contents.con[i].SHB_NETTX_2[_index] = self.__sndMsg[_index].CH2_L
                break
        
        if ( _hasNode == True ):
            return True
        else:
            print 'can not find node nodeID:', fsfb2LocalNodeID
            return None
       
    
    # @note: 获取VSN 
    # @param _channel: 1 --- 通道1； 2 --- 通道2
    def getVSN( self ):
        "获取VSN"
        _vsn0 = c_uint32()
        _vsn1 = c_uint32()
        _vsn2 = c_uint32()
        
        self.__fsfb2Dll.GM_VSN_Get( pointer( _vsn0 ), pointer( _vsn1 ), pointer( _vsn2 ) )
        return [_vsn0.value, _vsn1.value, _vsn2.value]
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 将应用消息放入fsfb2消息通道
    #
    # @Param fsfb2LocalNodeID 节点ID
    # @Param msg 消息内容 格式((C1_H,C1_L,C2_H,C2_L)...)
    #
    # @Returns if false return None
    # --------------------------------------------------------------------------  
    def putFsfb2Msg( self, fsfb2LocalNodeID , msgTuple ):
        """
        put application message to fsfb2 channel
        """
        
        _channelSatus = c_int32()
        _localNodeID = c_uint16()
        _localNodeID = fsfb2LocalNodeID
        
        if ( self.encodeFsfb2SndMsg( fsfb2LocalNodeID, msgTuple ) == None ):
            #print 'encodeFsfb2SndMsg'
            return None
        
#        _channelSatus = self.__fsfb2Dll.GM_FSFB2_Open_Send( _localNodeID )
#        if ( _channelSatus >= 0 ):
#            #self.__fsfb2Dll.GM_FSFB2_Read_Flush()
#            _re = self.__fsfb2Dll.GM_FSFB2_Write_Flush( self.__sndmsgID, self.__GM_FSFB2_SYSCHECK_1, self.__GM_FSFB2_SYSCHECK_2 )
#            #print "fsfb2 write flush", _re
#            if ( _re <= 0 ):
#                return None            
#            _channelSatus = self.__fsfb2Dll.GM_FSFB2_Close_Send( _localNodeID )
#            #print "_channelSatus", _channelSatus
#            if( _channelSatus < 0 ):
#                return None
#        else:
#            #print "return None"
#            return None 
        
        return True
    
    
    def Open_FSFB2_Send( self, _localNodeID ):
        "open FSFB2 Send"
        _channelSatus = self.__fsfb2Dll.GM_FSFB2_Open_Send( self.__device[self.__deviceName]['Node'][_localNodeID] )
        if ( _channelSatus >= 0 ):
            return True
        else:
            return None
    
    def Close_FSFB2_Send( self, _localNodeID ):
        "Close FSFB2 Send"
        _channelSatus = self.__fsfb2Dll.GM_FSFB2_Close_Send( self.__device[self.__deviceName]['Node'][_localNodeID] )
        if ( _channelSatus >= 0 ):
            return True
        else:
            return None
            
    def Write_Flush( self ):
        return self.__fsfb2Dll.GM_FSFB2_Write_Flush( self.__sndmsgID, self.__GM_FSFB2_SYSCHECK_1, self.__GM_FSFB2_SYSCHECK_2 )
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 检验FSFB2消息
    #
    # @Param logicAddr 消息字符串
    # @Param msgstr 消息字符串
    # @Param msglen 消息字节长度
    #
    # @Returns if false return None
    # --------------------------------------------------------------------------              
    def validFsfb2Msg( self, logicAddr, msgstr, msglen ):
        "validation fsfb2 message "
        
#        print 'recv atp-ci msg', commlib.str2hexlify( msgstr ), msglen
        if( self.__fsfb2Dll.GM_FSFB2_Inter_Write( self.__device[self.__deviceName]['Node'][logicAddr], msgstr, msglen ) == False ):
            return None
        else:
            return True
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 解码FSFB2消息
    #
    # @Param fsfb2NodeID
    #
    # @Returns if false return None
    # --------------------------------------------------------------------------    
    def decodeFsfb2Msg( self, fsfb2NodeID, GMNodeId ):
        "decode fsfb2 message"
        
        _fsfb2NodeID = fsfb2NodeID
        _localNodeCfg = c_uint16( GMNodeId )
        _typeIndex = c_int32()
        _CodeNum = c_uint16()
        
        self.__pointGM_FSFB2_SHB_BUF = self.__fsfb2Dll.GM_FSFB2_SHB_Get_Handle()
        
#        print 'vsn', self.getVSN()
        
        for i in range( self.__pointGM_FSFB2_SHB_BUF.contents.num ):
            #print 'fsfb2NodeID:', _fsfb2NodeID, _localNodeCfg, self.__pointGM_FSFB2_SHB_BUF.contents.con[i].FSFB2_LocalNodeID
            if( self.__device[self.__deviceName]['Node'][_fsfb2NodeID] == self.__pointGM_FSFB2_SHB_BUF.contents.con[i].FSFB2_LocalNodeID ):
#                print 'vsn in struct', self.__pointGM_FSFB2_SHB_BUF.contents.con[i].VSN0, self.__pointGM_FSFB2_SHB_BUF.contents.con[i].VSN1, self.__pointGM_FSFB2_SHB_BUF.contents.con[i].VSN2
                for j in range( self.__rcvMsgNum ):
                    self.__rcvMsg[j].CH1_L = self.__pointGM_FSFB2_SHB_BUF.contents.con[i].SHB_NETRX_1[j]
                    self.__rcvMsg[j].CH2_L = self.__pointGM_FSFB2_SHB_BUF.contents.con[i].SHB_NETRX_2[j]
#                    print 'chL j vsn', j, hex( self.__rcvMsg[j].CH1_L ^ self.getVSN()[1] ^ 0x12340234 ), hex( self.__rcvMsg[j].CH2_L ^ self.getVSN()[2] ^ 0x43211328 )
                if( self.__fsfb2Dll.GM_Code_GetTypeIndex( _localNodeCfg, pointer( _typeIndex ) ) == True ):
                    if( self.__fsfb2Dll.GM_Code_NISAL2SINGLE( _typeIndex, pointer( self.__rcvMsg ), pointer( _CodeNum ) ) == True ):
                        return True
                    else:
                        return None
                else:
                    return None
        
        return None
      
    # --------------------------------------------------------------------------
    ##
    # @Brief 获取FSFB2消息
    #
    # @Param logicAddr 消息字符串
    # @Param msgstr 消息字符串
    # @Param msglen 消息字节长度
    #
    # @Returns msgList or None
    # --------------------------------------------------------------------------          
    def getFsfb2Msg( self, logicAddr, msgstr, msglen ):
        "validation fsfb2 message and unpack message"
        
        _logicAddr = c_int16( logicAddr )
        _appliAddr = c_int32()
        _msglen = c_uint16()
        _msgstr = c_char_p( msgstr )
        #_fsfb2NodeID = fsfb2NodeID
        #_logicAddr = logicAddr
        #print 'logicAddr,_logicAddr', logicAddr, _logicAddr
        
        _msglen = msglen
        
#        if ( self.validFsfb2Msg( _logicAddr, _msgstr, _msglen ) == None ):
#            return None
        
#        if( self.__fsfb2Dll.GM_FSFB2_Read_Flush() == True ):
            #self.__device[self.__deviceName]['Node'][logicAddr] 为收消息Nodeid与GM_CODE.bin文件对应
        if ( self.decodeFsfb2Msg( logicAddr, logicAddr ) == True ):
            return [_m.CH1_H for _m in self.__rcvMsg]
        else:
            return None
#        else:
#            return None
        

    def Read_Flush( self ):
        return self.__fsfb2Dll.GM_FSFB2_Read_Flush() 
    
    # --------------------------------------------------------------------------
    ##
    # @Brief VSN周期更新
    #
    # @Returns True
    # --------------------------------------------------------------------------          
    def vsnUpdate( self ):
        "update vsn"
        
        self.__fsfb2Dll.GM_VSN_Update()
        return True




    # --------------------------------------------------------------------------
    ##
    # @Brief FSFB2回调函数 -用于发送FSFB2消息时将生成的FSFB2消息给信号层打包
    #
    # @Param upperLevelLogicAddr int16 
    # @Param msgID uint8
    # @Param pData uint8 *
    # @Param pData uint16
    #
    # @Returns if false return None
    # -------------------------------------------------------------------------- 
    #@staticmethod     
def fsfb2CallBackFun( upperLevelLogicAddr, msgID, pData, dataSize ):
    "call back function for GM_FSFB2_Init"
                    
    print 'fsfb2CallBackFun', upperLevelLogicAddr, msgID, pData, dataSize
    return True
if __name__ == '__main__' :

#----------------------FSFB2----------------------------
#    import time     
#    fsfb2_test = GM_FSFB2_DLL( "ci", fsfb2CallBackFun, r'./setting/fsfb2_devicelist.xml' )
#    re = fsfb2_test.fsfb2Init()
#    print 'fsfb2 init re', re
#    #atp配置文件中，有效的节点60-66,49-55
#
#    re = fsfb2_test.putFsfb2Msg( 20, ( ( 1, 0, 1, 0 ), ) )
#
#    print 'fsfb2 put re', re
#    print 'get errorNO', get_errno(), get_last_error()
#    time.sleep( 10 )

#----------------------Sacem----------------------------    
    sacemdll = GM_SACEM_Dll( 'ci', r"./TPConfig/setting/sacem_devicelist_for_cc.xml" )
#    sacemdll = GM_SACEM_Dll( 'lc', r"./TPConfig/setting/sacem_devicelist_for_cc.xml" )   
#    sacemdll = GM_SACEM_Dll( 'zc', r"./TPConfig/setting/sacem_devicelist_for_cc.xml" )
#    sacemdll = GM_SACEM_Dll( 'viom', r"./TPConfig/setting/sacem_devicelist_for_cc.xml" )
#    sacemdll = GM_SACEM_Dll( 'datp',r"./TPConfig/setting/sacem_devicelist_for_cc.xml"  )  
    #SACEM初始化
    if True == sacemdll.SACEM_Init_Dll():
        print "SACEM Initializing successful!" 
    else:
        print "SACEM Initializing is failed!"
    
    #Src is CI, Dest is CC, message is Protection_Request, msgId is 3
    SrcSSTy = 60
    SrcSSID = 1
    DestSSTy = 20
    DestSSID = 1
    
    CCVariantRequestMsgId = 3
    CIVariantReportMsgId = 104
    CIVariantRequestMsgId = 4
    CCVariantReportMsgId = 103
    
    #Src is LC, Dest is CC
#    SrcSSTy = 40
#    SrcSSID = 11
#    DestSSTy = 20
#    DestSSID = 2
    
    CCVersionReportMsgId = 101
    DateSynReportMsgId = 45
    CCVersionAuthorizationMsgId = 58
    TSRMsgId = 136   

    #Src is ZC, Dest is CC
#    SrcSSTy = 30
#    SrcSSID = 1
#    DestSSTy = 20
#    DestSSID = 1
    
    LocReportMsgId = 64
    EOAMsgId = 20
    VariantsMsgId = 30
    
    #Src is VIOM, Dest is CC
#    SrcSSTy = 23
#    SrcSSID = 1
#    DestSSTy = 24
#    DestSSID = 1
    
    VitalInputMsgID = 11
    VitalOutputMsgID = 12
 
     #Src is DATP, Dest is CC
#    SrcSSTy = 24
#    SrcSSID = 1
#    DestSSTy = 24
#    DestSSID = 2
    
    Datp2CCMsgID = 21

    #application data to pack
    #CI2CC_Message
    CCVariantRequest_Msg = [0x0]
    CIVariantReport_Msg = []
    for _c in range( 0, 513 ):
        CIVariantReport_Msg.append( 0 )
    CIVariantReport_Msg.append( 128 )
    
#    print "222", CIVariantReport_Msg.__len__()
    
    #LC2CC_Message
    DateSynReport_Msg = [0x10351, 2]
    CCVersionAuthorization_Msg = [0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, \
                                  0x01, 0x01, 0x00, 0x00, 0x01, 0x01, 0x00, 0x01, \
                                  0x04]
    TSR_Msg = []
    for _c in range( 0, 3000 ):
        TSR_Msg += [0x01, 0x00, 0x00, 0x00]
    TSR_Msg.append( 0x4 )
    
    print "111", TSR_Msg.__len__()
    
    #ZC2CC_Message
    EOA_Msg = [0x01, 0x00, 0x0102, 0x0038, 0x01, 0x0022, 0x0033, 0x00042002, 0x00034015, \
               0x00034015, 0x00000018]
    Variants_Msg = [1, 12, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    for _c in range( 0, 224 - 12 ):
        Variants_Msg.append( 0 )
    Variants_Msg.append( 128 )
    
    #VIOM2CC_Message
    VitalInput_Msg = [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
                0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
#                0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
#                0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
                123456, 654321, 789, 987]
    
    #DATP2CC_Message
    DATP2ATP_Msg = []
    
#    Protection_Request_Send = [0x4210, 0x00002800]
#    EOA_Request_Send = [0x0011, 0x0022, 0x00, 0x3300, 0x01, 0, 1, 0, 1, 0, \
#                   1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0x00112233, 0x00112233]   
#    Variant_Request_Send = [0x0011, 0x2200, 0x00112233] 
#    Protection_Report_Send = [0x4210, 0x00, 0x00, 0x28, 0x0001, 0x01, 0x01, 0x00, 0x00, 0x01, \
#                         0x1001, 0x01, 0x03, 0x01, 0x0000, 0x00, 0x0000, 0x01, 0x01, 0x01, \
#                         0x8A, 0x01, 0x2292, 0x01, 0x00, 0x00, 0x4219, 0x01, 0x00112233]
#    EOA_Report_Send = [0x0011, 0x0022, 0x06, 0x0044, 0x0055, 0x01, 0x0022, 0x0033, 0x0044, \
#                  0x00112233, 0x00112233, 0x01]
#    Variants_Report_Send = [1, 12, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#    for _c in range( 0, 224 - 12 ):
#        Variants_Report_Send.append( 0 )
#    Variants_Report_Send.append( 128 )
    
    
    #LC_ZC message info    
#    DateSyn_Report = [0x10351, 0x2]
#    Version_Report = [0x0001, 0x0001, 0x0001, 0x0001, 0x0001, 0x00000002]
    
    
    #CC_ZC message info
#    Loc_Report = [0x01, 0x01, 0x00, 0x0000, 0x0000, 0x01, 0x02, 0x00, 0x0000, \
#                  0x0000, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x14, 0x01, 0x00, \
#                  0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x00000395, 0x00049af2]

    #ATS_2_ZC message info
#    STD_Confirmation = [0xEE, 0xFF]
#    Gama_Confirmation = [0x11, 1, 0x22]

   
    
    #发送过程
    #CI2CC
    checksum = sacemdll.SACEM_Tx_Msg_Dll( CCVariantRequestMsgId, SrcSSTy, SrcSSID, DestSSTy, DestSSID, CCVariantRequest_Msg )
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( CIVariantReportMsgId, SrcSSTy, SrcSSID, DestSSTy, DestSSID, CIVariantReport_Msg )
    #LC2CC
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( DateSynReportMsgId, SrcSSTy, SrcSSID, DestSSTy, DestSSID, DateSynReport_Msg )
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( CCVersionAuthorizationMsgId, SrcSSTy, SrcSSID, DestSSTy, DestSSID, CCVersionAuthorization_Msg )
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( TSRMsgId, SrcSSTy, SrcSSID, DestSSTy, DestSSID, TSR_Msg )
    #ZC2CC
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( EOAMsgId, SrcSSTy, SrcSSID, DestSSTy, DestSSID, EOA_Msg )
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( VariantsMsgId, SrcSSTy, SrcSSID, DestSSTy, DestSSID, Variants_Msg )
    #VIOM2CC
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( VitalInputMsgID, SrcSSTy, SrcSSID, DestSSTy, DestSSID, VitalInput_Msg )
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( VersionReportMsgId, SrcSSTy, SrcSSID, DestSSTy, DestSSID, Version_Report )
    #ats_2_zc
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( STDConfirmationMsgID, SrcSSTy, SrcSSID, DestSSTy, DestSSID, STD_Confirmation )
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( GamaConfirmationMsgID, SrcSSTy, SrcSSID, DestSSTy, DestSSID, Gama_Confirmation )

#    if ( checksum == None ):
#        print "Packing is failed!"
#    else:
#        print checksum
#        print "Packing successful!"
      
      
    #接收的消息
    
    #CC2CI_message
    CIVariantRequest_Msg = [0x128]
    CIVariantRequest_cks1 = sacemdll.transform_Ito3Byte( 6328524 )
    CIVariantRequest_cks2 = sacemdll.transform_Ito3Byte( 10711874 )
    CIVariantRequest_Msg += CIVariantRequest_cks1
    CIVariantRequest_Msg += CIVariantRequest_cks2
    
    CCVariantReport_Msg = [12]
    for _c in range( 0, 128 ):
        CCVariantReport_Msg.append( 0 )
    CCVariantReport_Msg.append( 128 )
    CCVariantReport_cks1 = sacemdll.transform_Ito3Byte( 2625834 )
    CCVariantReport_cks2 = sacemdll.transform_Ito3Byte( 5390389 )
    CCVariantReport_Msg += CCVariantReport_cks1
    CCVariantReport_Msg += CCVariantReport_cks2
    
    #CC2LC_message
    CCVersionReport_Msg = [0x0001, 0x0001, 0x0001, 0x0001, 0x0001, 0x0004, 0x0005, 0x0006, 0x0007, \
                           0x0008, 0x0009, 0x000A, 0x000B, 0x000C, 0x000D, 0x000E, 0x000F, 0x0010, \
                           0x12345678]
    CCVersionReportMsg_cks1 = sacemdll.transform_Ito3Byte( 7423556 )
    CCVersionReportMsg_cks2 = sacemdll.transform_Ito3Byte( 5063861 )
    CCVersionReport_Msg += CCVersionReportMsg_cks1
    CCVersionReport_Msg += CCVersionReportMsg_cks2
    
    #CC2ZC_message
    LocReport_Msg = [0x12, 0x1, 0x01, 0x102, 0x0001, 0x00, 0x02, 0x02, 0xC802, 0x156, \
                     0x01, 0x22, 0x01, 0x01, 0x00, 0x00, 0x00, 0x25, 0x01, 0x01, 0x01]
    for _c in range( 0, 32 ):
        LocReport_Msg.append( 1 )
    LocReport_Msg.append( 0x11223344 )
    LocReport_Msg.append( 0x00224488 )
    LocReportMsg_cks1 = sacemdll.transform_Ito3Byte( 9190579 )
    LocReportMsg_cks2 = sacemdll.transform_Ito3Byte( 9705210 )
    LocReport_Msg += LocReportMsg_cks1
    LocReport_Msg += LocReportMsg_cks2
    
    #CC2VIOM_message
    VitalOutput_Msg = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0x0, 0x0, 0x0, \
                   0x408EC886, 0x0, 0x3AF1A5A0, 1, 1, 0]
    VitalOutput_Msg_cks1 = sacemdll.transform_Ito3Byte( 3636135 )
    VitalOutput_Msg_cks2 = sacemdll.transform_Ito3Byte( 1927005 )
    VitalOutput_Msg += VitalOutput_Msg_cks1
    VitalOutput_Msg += VitalOutput_Msg_cks2
    
    #CC2DATP_message
    Msg_DATP2ATP = []
     
    #ZC2ZC Protection_Request    
#    Protection_Request_Rev = [0x4210, 0x00002800]
#    ProtectionRequest_cks1 = sacemdll.transform_Ito3Byte( 5616957 )
#    ProtectionRequest_cks2 = sacemdll.transform_Ito3Byte( 1639781 )
#    Protection_Request_Rev += ProtectionRequest_cks1
#    Protection_Request_Rev += ProtectionRequest_cks2     
    #ZC2ZC EOA_Request
#    EOA_Request_Rev = [0x0011, 0x0022, 0x00, 0x3300, 0x01, 0, 1, 0, 1, 0, \
#                   1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0x00112233, 0x00112233]       
#    EOARequest_cks1 = sacemdll.transform_Ito3Byte( 9844720 )
#    EOARequest_cks2 = sacemdll.transform_Ito3Byte( 8006813 )
#    EOA_Request_Rev += EOARequest_cks1
#    EOA_Request_Rev += EOARequest_cks2
    #ZC2ZC Variants_Request
#    Variant_Request_Rev = [0x0011, 0x2200, 0x00112233]    
#    VariantRequest_cks1 = sacemdll.transform_Ito3Byte( 10022083 )
#    VariantRequest_cks2 = sacemdll.transform_Ito3Byte( 8814627 )
#    Variant_Request_Rev += VariantRequest_cks1
#    Variant_Request_Rev += VariantRequest_cks2    
    #ZC2ZC Protection_Report消息
#    Protection_Report_Rev = [0x4210, 0x00, 0x00, 0x28, 0x0001, 0x01, 0x01, 0x00, 0x00, 0x01, \
#                         0x1001, 0x01, 0x03, 0x01, 0x0000, 0x00, 0x0000, 0x01, 0x01, 0x01, \
#                         0x8A, 0x01, 0x2292, 0x01, 0x00, 0x00, 0x4219, 0x01, 0x00112233]
#    ProtectionReport_cks1 = sacemdll.transform_Ito3Byte( 11372511 )
#    ProtectionReport_cks2 = sacemdll.transform_Ito3Byte( 4927329 )
#    print cks1,cks2
#    Protection_Report_Rev += ProtectionReport_cks1
#    Protection_Report_Rev += ProtectionReport_cks2    
    #ZC2ZC EOA_Report消息
#    EOA_Report_Rev = [0x0011, 0x0022, 0x06, 0x0044, 0x0055, 0x01, 0x0022, 0x0033, 0x0044, \
#                  0x00112233, 0x00112233, 0x01]
#    EOAReport_cks1 = sacemdll.transform_Ito3Byte( 6324633 )
#    EOAReport_cks2 = sacemdll.transform_Ito3Byte( 2604751 )
#    EOA_Report_Rev += EOAReport_cks1
#    EOA_Report_Rev += EOAReport_cks2    
    #ZC2ZC Variants_Report消息
#    Variants_Report_Rev = [1, 12, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#    for _c in range( 0, 224 - 12 ):
#        Variants_Report_Rev.append( 0 )
#    Variants_Report_Rev.append( 128 )
#    print Variants_Report
#    VariantsReport_cks1 = sacemdll.transform_Ito3Byte( 8642833 )
#    VariantsReport_cks2 = sacemdll.transform_Ito3Byte( 4123646 )
#    print "VariantsReport_cks1" , VariantsReport_cks1
#    Variants_Report_Rev += VariantsReport_cks1
#    Variants_Report_Rev += VariantsReport_cks2
#    print Variants_Report
#    CCVersionReport = [0x0001, 0x0001, 0x0001, 0x0001, 0x0001, \
#                       0x0004, 0x0005, 0x0006, 0x0007, 0x0008, \
#                       0x0009, 0x000A, 0x000B, 0x000C, 0x000D, \
#                       0x000E, 0x000F, 0x0010, 0x12345678]
#    cks1 = sacemdll.transform_Ito3Byte( 7423556 )
#    cks2 = sacemdll.transform_Ito3Byte( 5063861 )
#    print cks1,cks2
#    CCVersionReport += cks1
#    CCVersionReport += cks2
#    print CCVersionReport

    #ZC2LC DateSynRequest
#    DateSyn_Request = [0x2]
#    DateSynRequest_cks1 = sacemdll.transform_Ito3Byte( 7266376 )
#    DateSynRequest_cks2 = sacemdll.transform_Ito3Byte( 3949171 )
#    DateSyn_Request += DateSynRequest_cks1
#    DateSyn_Request += DateSynRequest_cks2
    
    #ZC2LC VersionForZCRequest
#    Version_Request = [0x2] 
#    VersionRequest_cks1 = sacemdll.transform_Ito3Byte( 235396 )
#    VersionRequest_cks2 = sacemdll.transform_Ito3Byte( 4988914 )
#    Version_Request += VersionRequest_cks1
#    Version_Request += VersionRequest_cks2
    #ZC2CC EOA消息 
#    EOA = [0x01, 0x00, 0x0102, 0x0038, 0x01, 0x0022, 0x0033, 0x00042002, 0x00034015, \
#            0x00034015, 0x00000018]
#    EOA_cks1 = sacemdll.transform_Ito3Byte( 4739176 )
#    EOA_cks2 = sacemdll.transform_Ito3Byte( 6122918 )
#    EOA += EOA_cks1
#    EOA += EOA_cks2
     
    #ZC2CC Variants消息
#    Variants = [1, 12, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#    for _c in range( 0, 224 - 12 ):
#        Variants.append( 0 )
#    Variants.append( 128 )
#    Variants_cks1 = sacemdll.transform_Ito3Byte( 5380534 )
#    Variants_cks2 = sacemdll.transform_Ito3Byte( 4013595 )
#    Variants += Variants_cks1
#    Variants += Variants_cks2
    
    
    
    #ZC_2_ATS STDReturnCode
#    STD_Return_Code = [0x1122, 1, 0, 0xA5]
#    STDReturnCode_cks1 = sacemdll.transform_Ito3Byte( 9138665 )
#    STDReturnCode_cks2 = sacemdll.transform_Ito3Byte( 10840545 )
#    STD_Return_Code += STDReturnCode_cks1
#    STD_Return_Code += STDReturnCode_cks2
    
    #ZC_2_ATS GamaReturnCode
#    Gama_Return_Code = [0x1122, 1, 0, 0xB2]
#    GamaReturnCode_cks1 = sacemdll.transform_Ito3Byte( 7088237 )
#    GamaReturnCode_cks2 = sacemdll.transform_Ito3Byte( 7322638 )
#    Gama_Return_Code += GamaReturnCode_cks1
#    Gama_Return_Code += GamaReturnCode_cks2
#    retcdw = GM_SACEM_Shb_Recv2App_Type_LC()
    retcdw = GM_SACEM_Shb_Recv2App_Type()  
    #接收过程
    #application data to Unpack 
#    LocReport = [0x12, 0x01, 0x01, 0x0102, 0x0001, 0x00, 0x02, 0x02, \
#                 0xC802, 0x0156, 0x01, 0x22, 0x01, 0x01, 0x00, 0x00, \
#                 0x00, 0x25, 0x01, 0x01, 0x01, 0x00, 0x01, 0x00, 0x01, \
#                 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, \
#                 0x01, 0x00, 0x11223344, 0x00224488]
#    LocReportCKS1 = 8856513
#    LocReportCKS2 = 10974148
#    LocReportCKS_1 = sacemdll.transform_Ito3Byte(LocReportCKS1)
#    LocReportCKS_2 = sacemdll.transform_Ito3Byte(LocReportCKS2)
#    LocReport.extend(list(LocReportCKS_1))
#    LocReport.extend(list(LocReportCKS_2))
#    print "LCReport", LocReport
#    CCVersionReport = []
#    for _c in checksum:
#        DATP2ATP.append(_c)
#    print DATP2ATP
        
    #ZC2ZC, Src is 30, Dest is 30
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( ProtectionReportMsgId, 30, 1, \
#                                       30, 2, Protection_Report_Rev )
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( EOAReportMsgId, 30, 1, \
#                                       30, 2, EOA_Report_Rev )
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( VariantsReportMsgId, 30, 1, \
#                                       30, 2, Variants_Report_Rev )
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( ProtectionRequestMsgId, 30, 1, \
#                                       30, 2, Protection_Request_Rev )
     #CC2CI
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( CIVariantRequestMsgId, 20, 1, \
#                                       60, 1, CIVariantRequest_Msg )
    retcdw = sacemdll.SACEM_Rx_Msg_Dll( CCVariantReportMsgId, 20, 1, \
                                       60, 1, CCVariantReport_Msg )
    #CC2LC_Message
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( CCVersionReportMsgId, 20, 1, \
#                                       40, 1, CCVersionReport_Msg )
     #CC2ZC_Message
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( LocReportMsgId, 20, 1, \
#                                       30, 12, LocReport_Msg )
     #CC2VIOM_Message
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( VitalOutputMsgID, 24, 2, \
#                                       23, 1, VitalOutput_Msg )

     #ZC2ATS_Message
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( STDReturnCodeMsgID, 30, 1, \
#                                       10, 1, STD_Return_Code )
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( GamaReturnCodeMsgID, 30, 1, \
#                                       10, 1, Gama_Return_Code )
    if None == retcdw:
        print "Unpacking is failed!"
    else:
        print "Unpacking successful!"
#        for _c in range( 0, 20 ):
#            print retcdw.shb_recv2app_1
#            print retcdw.shb_recv2app_1[0].recv2app_value[_c].CdwH
#            print retcdw.shb_recv2app_2[0].recv2app_value[_c].CdwH
#            print retcdw.shb_recv2app_1[0].recv2app_value[_c].CdwL
#            print retcdw.shb_recv2app_2[0].recv2app_value[_c].CdwL
        
    #计算校核字
    CKW = sacemdll.SACEM_Get_CKW_Dll()
    if None == CKW:
        print "CKW failed!"
    else:
        print "CKW calculation successful!"
        print CKW
    
