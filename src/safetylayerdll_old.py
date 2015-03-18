# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     safetylayerdll.py
# Description:  安全层协议SACEM动态链接库接口类     
# Author:       Tiantian He
# Version:      0.0.1
# Created:      2011-08-29
# Company:      CASCO
# LastChange:   create 2011-12-08
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

# @brief 应用给SACEM协议的发送数据
class GM_SACEM_Shb_App2Trans_TSR_Base( Structure ):
    """
    Application Safety Data
    """   
    _fields_ = [( "TSR_Value", codeWord * 12003 )]  

# @brief 应用给SACEM协议的发送数据
class GM_SACEM_Shb_App2Trans_Other_Base( Structure ):
    """
    Application Safety Data
    """   
    _fields_ = [( "Other_Value", codeWord * 256 )]      


# @brief 应用给SACEM协议的发送数据
class GM_SACEM_Shb_App2Recv_Other_Base( Structure ):
    """
    Application Safety Data
    """   
    _fields_ = [( "Other_Value", c_int32 * 256 )]  

# @brief 应用给SACEM协议的发送数据
class GM_SACEM_Shb_App2Trans_Other( Structure ):
    """
    Application Safety Data
    """   
    _fields_ = [( "shb_app2trans_1", POINTER( GM_SACEM_Shb_App2Trans_Other_Base ) ), \
                ( "shb_app2trans_2", POINTER( GM_SACEM_Shb_App2Trans_Other_Base ) )]   
    
# @brief 应用给SACEM协议的发送数据
class GM_SACEM_Shb_App2Trans_TSR( Structure ):
    """
    Application Safety Data
    """
    _fields_ = [( "shb_app2trans_1", POINTER( GM_SACEM_Shb_App2Trans_TSR_Base ) ), \
                ( "shb_app2trans_2", POINTER( GM_SACEM_Shb_App2Trans_TSR_Base ) )]      

# @brief 应用给SACEM协议的发送数据
class GM_SACEM_Shb_App2Trans_Type( Structure ):
    """
    Application Safety Data
    """   
    _fields_ = [( "shb_app2trans_1", codeWord * 256 ), \
                ( "shb_app2trans_2", codeWord * 256 )]    
                   
# @brief 应用给协议的接收消息
class GM_SACEM_Shb_App2Recv_Type( Structure ):
    """
    SACEM Message
    """
    _fields_ = [( "shb_app2recv_1", c_int32 * 256 ), \
                ( "shb_app2recv_2", c_int32 * 256 ), \
                ( "app2recv_checksum_1", c_int32 ), \
                ( "app2recv_checksum_2", c_int32 )]


class  GM_SACEM_Shb_Recv2App_Other_Base( Structure ):
    """
    SACEM Message
    """
    _fields_ = [( "recv2app_value", codeWord * 256 )]
    
# @brief  接收消息返回给应用的值
class GM_SACEM_Shb_Recv2App_Type( Structure ):
    """
    Application Safety data
    """
    _fields_ = [( "shb_recv2app_1", codeWord * 256 ), \
                ( "shb_recv2app_2", codeWord * 256 )]                    

# @brief LC设备----应用给SACEM协议的发送数据
class GM_SACEM_Shb_App2Trans_Type_LC( Structure ):
    """
    LC----Application Safety Data
    """
    _fields_ = [( "shb_app2trans_1", codeWord * 12024 ), \
                ( "shb_app2trans_2", codeWord * 12024 )]     

# @brief LC设备---应用给协议的接收消息
class GM_SACEM_Shb_App2Recv_Type_LC( Structure ):
    """
    LC---SACEM Message
    """      
    _fields_ = [( "shb_app2recv_1", POINTER( GM_SACEM_Shb_App2Recv_Other_Base ) ), \
                ( "shb_app2recv_2", POINTER( GM_SACEM_Shb_App2Recv_Other_Base ) ), \
                ( "app2recv_checksum_1", c_int32 ), \
                ( "app2recv_checksum_2", c_int32 )]

# @brief  LC设备---接收消息返回给应用的值
class GM_SACEM_Shb_Recv2App_Type_LC( Structure ):
    """
    LC---Application Safety data
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
    
    #NISAL码字 VIOM2ATP 64个码字
    #通道1， True
    NISAL_CODE_VIOM2ATP_1_T = ( 
                               
0x3E0432C7,
0xC82732C9,
0x0ACE32E1,
0x0DB732D1,
0xFB9432DF,
0x397D32F7,
0x995C32D3,
0x6F7F32DD,
0xAD9632F5,
0xA83832D5,
0x5E1B32DB,
0x9CF232F3,
0x3CD332D7,
0xCAF032D9,
0x081932F1,
0x3FF43301,
0xC9D7330F,
0x0B3E3327,
0xAB1F3303,
0x5D3C330D,
0x9FD53325,
0x9A7B3305,
0x6C58330B,
0xAEB13323,
0x0E903307,
0xF8B33309,
0x3A5A3321,
0x3D233311,
0xCB00331F,
0x09E93337,
0xA9C83313,
0x5FEB331D,
#0xADA832C7,
#0x839932C9,
#0x21C832E1,
#0x0E7732D1,
#0x204632DF,
#0x821732F7,
#0x66B132D3,
#0x488032DD,
#0xEAD132F5,
#0xDFFB32D5,
#0xF1CA32DB,
#0x539B32F3,
#0xB73D32D7,
#0x990C32D9,
#0x3B5D32F1,
#0x372D3301,
#0x191C330F,
#0xBB4D3327,
#0x5FEB3303,
#0x71DA330D,
#0xD38B3325,
#0xE6A13305,
#0xC890330B,
#0x6AC13323,
#0x8E673307,
#0xA0563309,
#0x02073321,
#0x2DB83311,
#0x0389331F,
#0xA1D83337,
#0x457E3313,
#0x6B4F331D
 )
    #通道1， False
    NISAL_CODE_VIOM2ATP_1_F = ( 
0xB711CD38,
0x4132CD36,
0x83DBCD1E,
0x84A2CD2E,
0x7281CD20,
0xB068CD08,
0x1049CD2C,
0xE66ACD22,
0x2483CD0A,
0x212DCD2A,
0xD70ECD24,
0x15E7CD0C,
0xB5C6CD28,
0x43E5CD26,
0x810CCD0E,
0xB6E1CCFE,
0x40C2CCF0,
0x822BCCD8,
0x220ACCFC,
0xD429CCF2,
0x16C0CCDA,
0x136ECCFA,
0xE54DCCF4,
0x27A4CCDC,
0x8785CCF8,
0x71A6CCF6,
0xB34FCCDE,
0xB436CCEE,
0x4215CCE0,
0x80FCCCC8,
0x20DDCCEC,
0xD6FECCE2,
#0x28CFCD38,
#0x06FECD36,
#0xA4AFCD1E,
#0x8B10CD2E,
#0xA521CD20,
#0x0770CD08,
#0xE3D6CD2C,
#0xCDE7CD22,
#0x6FB6CD0A,
#0x5A9CCD2A,
#0x74ADCD24,
#0xD6FCCD0C,
#0x325ACD28,
#0x1C6BCD26,
#0xBE3ACD0E,
#0xB24ACCFE,
#0x9C7BCCF0,
#0x3E2ACCD8,
#0xDA8CCCFC,
#0xF4BDCCF2,
#0x56ECCCDA,
#0x63C6CCFA,
#0x4DF7CCF4,
#0xEFA6CCDC,
#0x0B00CCF8,
#0x2531CCF6,
#0x8760CCDE,
#0xA8DFCCEE,
#0x86EECCE0,
#0x24BFCCC8,
#0xC019CCEC,
#0xEE28CCE2
 )
    #通道2，True
    NISAL_CODE_VIOM2ATP_2_T = ( 
0xADA832C7,
0x839932C9,
0x21C832E1,
0x0E7732D1,
0x204632DF,
0x821732F7,
0x66B132D3,
0x488032DD,
0xEAD132F5,
0xDFFB32D5,
0xF1CA32DB,
0x539B32F3,
0xB73D32D7,
0x990C32D9,
0x3B5D32F1,
0x372D3301,
0x191C330F,
0xBB4D3327,
0x5FEB3303,
0x71DA330D,
0xD38B3325,
0xE6A13305,
0xC890330B,
0x6AC13323,
0x8E673307,
0xA0563309,
0x02073321,
0x2DB83311,
0x0389331F,
0xA1D83337,
0x457E3313,
0x6B4F331D
#0xB711CD38,
#0x4132CD36,
#0x83DBCD1E,
#0x84A2CD2E,
#0x7281CD20,
#0xB068CD08,
#0x1049CD2C,
#0xE66ACD22,
#0x2483CD0A,
#0x212DCD2A,
#0xD70ECD24,
#0x15E7CD0C,
#0xB5C6CD28,
#0x43E5CD26,
#0x810CCD0E,
#0xB6E1CCFE,
#0x40C2CCF0,
#0x822BCCD8,
#0x220ACCFC,
#0xD429CCF2,
#0x16C0CCDA,
#0x136ECCFA,
#0xE54DCCF4,
#0x27A4CCDC,
#0x8785CCF8,
#0x71A6CCF6,
#0xB34FCCDE,
#0xB436CCEE,
#0x4215CCE0,
#0x80FCCCC8,
#0x20DDCCEC,
#0xD6FECCE2,
#0x3E0432C7,
#0xC82732C9,
#0x0ACE32E1,
#0x0DB732D1,
#0xFB9432DF,
#0x397D32F7,
#0x995C32D3,
#0x6F7F32DD,
#0xAD9632F5,
#0xA83832D5,
#0x5E1B32DB,
#0x9CF232F3,
#0x3CD332D7,
#0xCAF032D9,
#0x081932F1,
#0x3FF43301,
#0xC9D7330F,
#0x0B3E3327,
#0xAB1F3303,
#0x5D3C330D,
#0x9FD53325,
#0x9A7B3305,
#0x6C58330B,
#0xAEB13323,
#0x0E903307,
#0xF8B33309,
#0x3A5A3321,
#0x3D233311,
#0xCB00331F,
#0x09E93337,
#0xA9C83313,
#0x5FEB331D,
#0xADA832C7,
#0x839932C9,
#0x21C832E1,
#0x0E7732D1,
#0x204632DF,
#0x821732F7,
#0x66B132D3,
#0x488032DD,
#0xEAD132F5,
#0xDFFB32D5,
#0xF1CA32DB,
#0x539B32F3,
#0xB73D32D7,
#0x990C32D9,
#0x3B5D32F1,
#0x372D3301,
#0x191C330F,
#0xBB4D3327,
#0x5FEB3303,
#0x71DA330D,
#0xD38B3325,
#0xE6A13305,
#0xC890330B,
#0x6AC13323,
#0x8E673307,
#0xA0563309,
#0x02073321,
#0x2DB83311,
#0x0389331F,
#0xA1D83337,
#0x457E3313,
#0x6B4F331D
 )
  #通道2，False
    NISAL_CODE_VIOM2ATP_2_F = ( 
#0xB711CD38,
#0x4132CD36,
#0x83DBCD1E,
#0x84A2CD2E,
#0x7281CD20,
#0xB068CD08,
#0x1049CD2C,
#0xE66ACD22,
#0x2483CD0A,
#0x212DCD2A,
#0xD70ECD24,
#0x15E7CD0C,
#0xB5C6CD28,
#0x43E5CD26,
#0x810CCD0E,
#0xB6E1CCFE,
#0x40C2CCF0,
#0x822BCCD8,
#0x220ACCFC,
#0xD429CCF2,
#0x16C0CCDA,
#0x136ECCFA,
#0xE54DCCF4,
#0x27A4CCDC,
#0x8785CCF8,
#0x71A6CCF6,
#0xB34FCCDE,
#0xB436CCEE,
#0x4215CCE0,
#0x80FCCCC8,
#0x20DDCCEC,
#0xD6FECCE2,
0x28CFCD38,
0x06FECD36,
0xA4AFCD1E,
0x8B10CD2E,
0xA521CD20,
0x0770CD08,
0xE3D6CD2C,
0xCDE7CD22,
0x6FB6CD0A,
0x5A9CCD2A,
0x74ADCD24,
0xD6FCCD0C,
0x325ACD28,
0x1C6BCD26,
0xBE3ACD0E,
0xB24ACCFE,
0x9C7BCCF0,
0x3E2ACCD8,
0xDA8CCCFC,
0xF4BDCCF2,
0x56ECCCDA,
0x63C6CCFA,
0x4DF7CCF4,
0xEFA6CCDC,
0x0B00CCF8,
0x2531CCF6,
0x8760CCDE,
0xA8DFCCEE,
0x86EECCE0,
0x24BFCCC8,
0xC019CCEC,
0xEE28CCE2
 )
    #NISAL码字    ATP2VIOM 20个码字  20111107htt
    #通道1， True
    NISAL_CODE_ATP2VIOM_1_T = ( 
0x965E3375,
0x93F03355,
0x65D3335B,
0xA73A3373,
0x071B3357,
0xF1383359,
0x33D13371,
0x294C3381,
0xDF6F338F,
0x1D8633A7,
0x965E3375,
0x93F03355,
0x65D3335B,
0xA73A3373,
0x071B3357,
0xF1383359,
0x33D13371,
0x294C3381,
0xDF6F338F,
0x1D8633A7
 )
    #通道1， False
    NISAL_CODE_ATP2VIOM_1_F = ( 
0x1F4BCC8A,
0x1AE5CCAA,
0xECC6CCA4,
0x2E2FCC8C,
0x8E0ECCA8,
0x782DCCA6,
0xBAC4CC8E,
0xA059CC7E,
0x567ACC70,
0x9493CC58,
0x1F4BCC8A,
0x1AE5CCAA,
0xECC6CCA4,
0x2E2FCC8C,
0x8E0ECCA8,
0x782DCCA6,
0xBAC4CC8E,
0xA059CC7E,
0x567ACC70,
0x9493CC58
 )
    #通道2， True
    NISAL_CODE_ATP2VIOM_2_T = ( 
0xA34A3375,
0x96603355,
0xB851335B,
0x1A003373,
0xFEA63357,
0xD0973359,
0x72C63371,
0xE3853381,
0xCDB4338F,
0x6FE533A7,
0xA34A3375,
0x96603355,
0xB851335B,
0x1A003373,
0xFEA63357,
0xD0973359,
0x72C63371,
0xE3853381,
0xCDB4338F,
0x6FE533A7               
 )
    #通道2， False
    NISAL_CODE_ATP2VIOM_2_F = ( 
0x262DCC8A,
0x1307CCAA,
0x3D36CCA4,
0x9F67CC8C,
0x7BC1CCA8,
0x55F0CCA6,
0xF7A1CC8E,
0x66E2CC7E,
0x48D3CC70,
0xEA82CC58,
0x262DCC8A,
0x1307CCAA,
0x3D36CCA4,
0x9F67CC8C,
0x7BC1CCA8,
0x55F0CCA6,
0xF7A1CC8E,
0x66E2CC7E,
0x48D3CC70,
0xEA82CC58
 )    
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
    def SACEM_Init_Dll( self ):
        "SACEM Initialization"
        ret1 = self.sacemDll.SACEMDll_Init( self.__device[self.__deviceName]['cnfFile'] )
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

        if 'lc' == self.__deviceName:
            if 136 == msgid:
                TSR_Base_1 = GM_SACEM_Shb_App2Trans_TSR_Base()
                TSR_Base_2 = GM_SACEM_Shb_App2Trans_TSR_Base()
                TxBuf = GM_SACEM_Shb_App2Trans_TSR()
                TxBuf.shb_app2trans_1 = pointer( TSR_Base_1 )
                TxBuf.shb_app2trans_2 = pointer( TSR_Base_2 )  
                TSR_Base_1.TSR_Value[0].CdwH = Src
                TSR_Base_1.TSR_Value[1].CdwH = Dest
                TSR_Base_2.TSR_Value[0].CdwH = Src
                TSR_Base_2.TSR_Value[1].CdwH = Dest                                 
            else:
                Other_Base_1 = GM_SACEM_Shb_App2Trans_Other_Base()
                Other_Base_2 = GM_SACEM_Shb_App2Trans_Other_Base()
                TxBuf = GM_SACEM_Shb_App2Trans_Other()
                TxBuf.shb_app2trans_1 = pointer( Other_Base_1 )
                TxBuf.shb_app2trans_2 = pointer( Other_Base_2 )
                Other_Base_1.Other_Value[0].CdwH = Src
                Other_Base_1.Other_Value[1].CdwH = Dest
                Other_Base_2.Other_Value[0].CdwH = Src
                Other_Base_2.Other_Value[1].CdwH = Dest                                    
        else:
            TxBuf = GM_SACEM_Shb_App2Trans_Type()
            
            #给TxBuf赋值
            TxBuf.shb_app2trans_1[0].CdwH = Src
            TxBuf.shb_app2trans_1[1].CdwH = Dest
            TxBuf.shb_app2trans_2[0].CdwH = Src
            TxBuf.shb_app2trans_2[1].CdwH = Dest         
        
        
        if self.__deviceName == 'zc':
            if self.__device[self.__deviceName]['EOA'][0] == msgid:
                #EOA_ZC2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['EOA'][1] - 2 ) ):
                    TxBuf.shb_app2trans_1[_c + 2].CdwH = TxShbBuf[_c]
                    TxBuf.shb_app2trans_2[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['EOA'][1] ):
                    TxBuf.shb_app2trans_1[_c].CdwL = 0;
                    TxBuf.shb_app2trans_2[_c].CdwL = 0;
            elif self.__device[self.__deviceName]['Variants'][0] == msgid:
                #Variants_ZC2CC
                #Variants消息不含Src和Dest，需将其覆盖
                for _c in range( 0, self.__device[self.__deviceName]['Variants'][1] ):
                    TxBuf.shb_app2trans_1[_c].CdwH = TxShbBuf[_c]
                    TxBuf.shb_app2trans_2[_c].CdwH = TxShbBuf[_c]
                    TxBuf.shb_app2trans_1[_c].CdwL = 0;
                    TxBuf.shb_app2trans_2[_c].CdwL = 0;
            else:
                return None
        elif self.__deviceName == 'viom':
            if self.__device[self.__deviceName]['Msg_VIOM2ATP'][0] == msgid:
                #VIOM2ATP MSG
                #两个通道的CdwH值一样，均为64个码位 + 2个Loophour 2011-8-26
                #64个码位为NISAL， 2个Loophour和Src，Dest为NoVital 2011-8-27
                
                #64个码位+2个Loophour CdwH
                for _c in range( 0, ( self.__device[self.__deviceName]['Msg_VIOM2ATP'][1] - 2 ) ):
                    TxBuf.shb_app2trans_1[_c + 2].CdwH = TxShbBuf[_c]
                    TxBuf.shb_app2trans_2[_c + 2].CdwH = TxShbBuf[_c]
                #Src和Dest CdwL
                for _c in range( 0, 2 ):
                    TxBuf.shb_app2trans_1[_c].CdwL = 0;
                    TxBuf.shb_app2trans_2[_c].CdwL = 0;
                #64个码字 CdwL
                for _c in range( 0, 32 ):
                    #转换为NISAL码字
                    if True == TxShbBuf[_c]:
                        TxBuf.shb_app2trans_1[_c + 2].CdwL = self.NISAL_CODE_VIOM2ATP_1_T[_c]
                        TxBuf.shb_app2trans_2[_c + 2].CdwL = self.NISAL_CODE_VIOM2ATP_2_T[_c]
                    elif False == TxShbBuf[_c]:
                        TxBuf.shb_app2trans_1[_c + 2].CdwL = self.NISAL_CODE_VIOM2ATP_1_F[_c]
                        TxBuf.shb_app2trans_2[_c + 2].CdwL = self.NISAL_CODE_VIOM2ATP_2_F[_c]
                    else:
                        return None
                    #CdwL^TL
                    TxBuf.shb_app2trans_1[_c + 2].CdwL ^= self.GM_VSN_Get( 1 )
                    TxBuf.shb_app2trans_2[_c + 2].CdwL ^= self.GM_VSN_Get( 2 )
                    
                    TxBuf.shb_app2trans_1[_c + 2].CdwL ^= self.GM_VSN_M_get( 1 )
                    TxBuf.shb_app2trans_2[_c + 2].CdwL ^= self.GM_VSN_M_get( 2 )
                #Loophour CdwL
                for _c in range( ( self.__device[self.__deviceName]['Msg_VIOM2ATP'][1] - 4 ), \
                                self.__device[self.__deviceName]['Msg_VIOM2ATP'][1] ):
                    TxBuf.shb_app2trans_1[_c].CdwL = 0
                    TxBuf.shb_app2trans_2[_c].CdwL = 0
            elif 12 == msgid:
                #ATP2VIOM for Test using
                #20个NISAL码字+2个Loophour+5个变量+1个变量   20111107htt
                
                #20个码位+2个Loophour+5个变量 CdwH+1个变量CdwH
                for _c in range( 0, 28 ):
                    TxBuf.shb_app2trans_1[_c + 2].CdwH = TxShbBuf[_c]
                    TxBuf.shb_app2trans_2[_c + 2].CdwH = TxShbBuf[_c]
                #Src和Dest CdwL
                for _c in range( 0, 2 ):
                    TxBuf.shb_app2trans_1[_c].CdwL = 0;
                    TxBuf.shb_app2trans_2[_c].CdwL = 0;
                #20个码字 CdwL
                for _c in range( 0, 20 ):
                    #转换为NISAL码字
                    if True == TxShbBuf[_c]:
                        TxBuf.shb_app2trans_1[_c + 2].CdwL = self.NISAL_CODE_ATP2VIOM_1_T[_c]
                        TxBuf.shb_app2trans_2[_c + 2].CdwL = self.NISAL_CODE_ATP2VIOM_2_T[_c]
                    elif False == TxShbBuf[_c]:
                        TxBuf.shb_app2trans_1[_c + 2].CdwL = self.NISAL_CODE_ATP2VIOM_1_F[_c]
                        TxBuf.shb_app2trans_2[_c + 2].CdwL = self.NISAL_CODE_ATP2VIOM_2_F[_c]
                    else:
                        return None
                    #CdwL^TL
                    TxBuf.shb_app2trans_1[_c + 2].CdwL ^= self.GM_VSN_Get( 1 )
                    TxBuf.shb_app2trans_2[_c + 2].CdwL ^= self.GM_VSN_Get( 2 )
                    
                    TxBuf.shb_app2trans_1[_c + 2].CdwL ^= self.GM_VSN_M_get( 1 )
                    TxBuf.shb_app2trans_2[_c + 2].CdwL ^= self.GM_VSN_M_get( 2 )                
                #2个Loophour+4个变量 CdwL+2个变量CdwL
                for _c in range( 22, 30 ):
                    TxBuf.shb_app2trans_1[_c].CdwL = 0
                    TxBuf.shb_app2trans_2[_c].CdwL = 0
            else:
                return None
        elif self.__deviceName == 'lc':                
            if self.__device[self.__deviceName]['DateSynReport'][0] == msgid:
                #DateSyn_LC2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['DateSynReport'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
#                    TxBuf.shb_app2trans_1[_c + 2].CdwH = TxShbBuf[_c]
#                    TxBuf.shb_app2trans_2[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['DateSynReport'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0
                    Other_Base_2.Other_Value[_c].CdwL = 0 
#                    TxBuf.shb_app2trans_1[_c].CdwL = 0;
#                    TxBuf.shb_app2trans_2[_c].CdwL = 0;
            elif self.__device[self.__deviceName]['VersionAuthorize'][0] == msgid:
                #Version_LC2CC
                for _c in range( 0, ( self.__device[self.__deviceName]['VersionAuthorize'][1] - 2 ) ):
                    Other_Base_1.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 2].CdwH = TxShbBuf[_c]
#                    TxBuf.shb_app2trans_1[_c + 2].CdwH = TxShbBuf[_c]
#                    TxBuf.shb_app2trans_2[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['VersionAuthorize'][1] ):
                    Other_Base_1.Other_Value[_c].CdwL = 0
                    Other_Base_2.Other_Value[_c].CdwL = 0   
#                    TxBuf.shb_app2trans_1[_c].CdwL = 0;
#                    TxBuf.shb_app2trans_2[_c].CdwL = 0; 
            elif self.__device[self.__deviceName]['TSR'][0] == msgid:
                #TSR_LC2CC
                #TSR变量数太多
                for _c in range( 0, 12001 ):
                    TSR_Base_1.TSR_Value[_c + 2].CdwH = TxShbBuf[_c]
                    TSR_Base_2.TSR_Value[_c + 2].CdwH = TxShbBuf[_c]
#                    TxBuf.shb_app2trans_1[_c + 2].CdwH = TxShbBuf[_c]
#                    TxBuf.shb_app2trans_2[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, 12003 ):
                    TSR_Base_1.TSR_Value[_c].CdwL = 0
                    TSR_Base_2.TSR_Value[_c].CdwL = 0                    
#                    TxBuf.shb_app2trans_1[_c].CdwL = 0;
            else:
                return None
        elif self.__deviceName == 'datp':
            if self.__device[self.__deviceName]['Msg_DATP2ATP'][0] == msgid:
                #Msg_DATP2ATP
                for _c in range( 0, ( self.__device[self.__deviceName]['Msg_DATP2ATP'][1] - 2 ) ):
                    TxBuf.shb_app2trans_1[_c + 2].CdwH = TxShbBuf[_c]
                    TxBuf.shb_app2trans_2[_c + 2].CdwH = TxShbBuf[_c]
                for _c in range( 0, self.__device[self.__deviceName]['Msg_DATP2ATP'][1] ):
                    TxBuf.shb_app2trans_1[_c].CdwL = 0;
                    TxBuf.shb_app2trans_2[_c].CdwL = 0;
            else:
                return None            
        else:
            return None
                                        
        CheckSum_1 = c_int32()
        CheckSum_2 = c_int32()
        
#        print msgid, Src, Dest
#        for _c in range(0, 2003):
#            print TxBuf.shb_app2trans_1[_c].CdwH, TxBuf.shb_app2trans_1[_c].CdwL, \
#                TxBuf.shb_app2trans_2[_c].CdwH, TxBuf.shb_app2trans_2[_c].CdwL
        ret = self.sacemDll.SACEMDll_Packing( msgid, Src, Dest, pointer( TxBuf ), \
                                             pointer( CheckSum_1 ), pointer( CheckSum_2 ) )
        if False == ret:
            print "sacem send failed", msgid
            return None
        else:
#            print CheckSum_1.value, CheckSum_2.value
            cks1_1, cks1_2, cks1_3 = self.transform_Ito3Byte( CheckSum_1.value )
            cks2_1, cks2_2, cks2_3 = self.transform_Ito3Byte( CheckSum_2.value )
#            cks1_1, cks1_2, cks1_3 = self.transform_Ito3Byte(10290608)
#            cks2_1, cks2_2, cks2_3 = self.transform_Ito3Byte(3965632)
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
        
        if 'lc' == self.__deviceName:
            rxBuff = GM_SACEM_Shb_App2Recv_Type_LC()
            Other_Base_1 = GM_SACEM_Shb_App2Recv_Other_Base()
            Other_Base_2 = GM_SACEM_Shb_App2Recv_Other_Base()
            rxBuff.shb_app2recv_1 = pointer( Other_Base_1 )
            rxBuff.shb_app2recv_2 = pointer( Other_Base_2 )
            Other_Base_1.Other_Value[0] = Src
            Other_Base_2.Other_Value[0] = Src          
            reVal = GM_SACEM_Shb_Recv2App_Type_LC()
            reVal_Base_1 = GM_SACEM_Shb_Recv2App_Other_Base()
            reVal_Base_2 = GM_SACEM_Shb_Recv2App_Other_Base()
            reVal.shb_recv2app_1 = pointer( reVal_Base_1 )
            reVal.shb_recv2app_2 = pointer( reVal_Base_2 )
        else:
            rxBuff = GM_SACEM_Shb_App2Recv_Type()
            reVal = GM_SACEM_Shb_Recv2App_Type()            
        
            #给rxBuff赋值
            rxBuff.shb_app2recv_1[0] = Src
            rxBuff.shb_app2recv_1[1] = Dest
            rxBuff.shb_app2recv_2[0] = Src
            rxBuff.shb_app2recv_2[1] = Dest
        
        if self.__deviceName == 'zc':
            if self.__device[self.__deviceName]['LocReport'][0] == msgid:
                #LocReport_CC2ZC
                for _c in range( 0, ( self.__device[self.__deviceName]['LocReport'][1] - 2 ) ):
                    rxBuff.shb_app2recv_1[_c + 2] = RxShbBuf[_c]
                    rxBuff.shb_app2recv_2[_c + 2] = RxShbBuf[_c]
                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] - 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] - 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] )] )    
                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] + 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] + 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['LocReport'][1] + 3 )] )
#            elif msgid == 20:
#                #EOA MSG
#                for _c in range(0, 11):
#                    rxBuff.shb_app2recv_1[_c + 2] = RxShbBuf[_c]
#                    rxBuff.shb_app2recv_2[_c + 2] = RxShbBuf[_c]
#                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI(RxShbBuf[11], \
#                                                                    RxShbBuf[12], RxShbBuf[13])
#                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI(RxShbBuf[14], \
#                                                                    RxShbBuf[15], RxShbBuf[16])            
            else:
                return None
        elif self.__deviceName == 'viom':
            if self.__device[self.__deviceName]['Msg_ATP2VIOM'][0] == msgid:
                #ATP2VIOM MSG
                #上模块10个码位+下模块10个码位+2个Loophour+2个变量+2个Checksum
                #两个变量中的第二个是NISAL码字，注意！
                for _c in range( 0, ( self.__device[self.__deviceName]['Msg_ATP2VIOM'][1] - 2 ) ):
                    rxBuff.shb_app2recv_1[_c + 2] = RxShbBuf[_c]
                    rxBuff.shb_app2recv_2[_c + 2] = RxShbBuf[_c]
                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_ATP2VIOM'][1] - 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_ATP2VIOM'][1] - 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_ATP2VIOM'][1] )] )
                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_ATP2VIOM'][1] + 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_ATP2VIOM'][1] + 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_ATP2VIOM'][1] + 3 )] )
            elif self.__device[self.__deviceName]['Msg_VIOM2ATP'][0] == msgid:
                #VIOM2ATP, For test use
                for _c in range( 0, ( self.__device[self.__deviceName]['Msg_VIOM2ATP'][1] - 2 ) ):
                    rxBuff.shb_app2recv_1[_c + 2] = RxShbBuf[_c]
                    rxBuff.shb_app2recv_2[_c + 2] = RxShbBuf[_c]
                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_VIOM2ATP'][1] - 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_VIOM2ATP'][1] - 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_VIOM2ATP'][1] )] )
                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_VIOM2ATP'][1] + 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_VIOM2ATP'][1] + 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['Msg_VIOM2ATP'][1] + 3 )] )
            else:
                return None
        elif self.__deviceName == 'lc':
            if self.__device[self.__deviceName]['CCVersionReport'][0] == msgid:
                #CCVersionReport_CC2LC
                #该消息比较特殊，只有Src, 无Dest。因此需将前面写入的Dest覆盖掉
                for _c in range( 0, ( self.__device[self.__deviceName]['CCVersionReport'][1] - 1 ) ):
                    Other_Base_1.Other_Value[_c + 1] = RxShbBuf[_c]
                    Other_Base_2.Other_Value[_c + 1] = RxShbBuf[_c]
#                    rxBuff.shb_app2recv_1[_c + 1] = RxShbBuf[_c]
#                    rxBuff.shb_app2recv_2[_c + 1] = RxShbBuf[_c]
                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersionReport'][1] - 1 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersionReport'][1] )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersionReport'][1] + 1 )] )
                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI( \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersionReport'][1] + 2 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersionReport'][1] + 3 )], \
                                RxShbBuf[( self.__device[self.__deviceName]['CCVersionReport'][1] + 4 )] )
#            elif 136 == msgid:
#                #TSR for test using
#                for _c in range(0, 12001):
#                    rxBuff.shb_app2recv_1[_c + 2] = RxShbBuf[_c]
#                    rxBuff.shb_app2recv_2[_c + 2] = RxShbBuf[_c]
#                rxBuff.app2recv_checksum_1 = self.transfor_3BytetoI(RxShbBuf[12001], \
#                                                                    RxShbBuf[12002], RxShbBuf[12003])
#                rxBuff.app2recv_checksum_2 = self.transfor_3BytetoI(RxShbBuf[12004], \
#                                                                    RxShbBuf[12005], RxShbBuf[12006])
            else:
                return None
        elif self.__deviceName == 'datp':
            if self.__device[self.__deviceName]['Msg_DATP2ATP'][0] == msgid:
                #Msg_ATP2DATP
                for _c in range( 0, ( self.__device[self.__deviceName]['Msg_DATP2ATP'][1] - 2 ) ):
                    rxBuff.shb_app2recv_1[_c + 2] = RxShbBuf[_c]
                    rxBuff.shb_app2recv_2[_c + 2] = RxShbBuf[_c]
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
#    sacemdll = GM_SACEM_Dll('zc')
#    sacemdll = GM_SACEM_Dll( 'lc' )
    sacemdll = GM_SACEM_Dll( 'viom', r"./TPConfig/setting/sacem_devicelist.xml" )
#    sacemdll = GM_SACEM_Dll( 'datp' )
  
    #SACEM初始化
    if True == sacemdll.SACEM_Init_Dll():
        print "SACEM Initializing successful!" 
    else:
        print "SACEM Initializing is failed!"
    
    #Src is ZC, Dest is CC, message is EOA, msgId is 20
    SrcSSTy = 30
    SrcSSID = 1
    DestSSTy = 20
    DestSSID = 1
    
    EOAMsgId = 20
    VariantsMsgId = 30
    LocMsgId = 64
    
    DateSynReportMsgId = 45
    VersionAuthorizeMsgId = 58
    TSRMsgId = 136
    CCVersionReportMsgId = 101
    
    ATP2VIOMMsgId = 12
    VIOM2ATPMsgId = 11
    
    DATP2ATPMsgId = 10
    
    #application data to pack
#    EOA = [0x01, 0x00, 0x0102, 0x0038, 0x01, 0x0022, 0x0033, \
#           0x00042002, 0x00034015, 0x00034015, 0x00000018]
#    Variants = [1, 12, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#    for _c in range(0, 224 - 12):
#        Variants.append(0)
#    Variants.append(128)
#    print Variants
    DateSynReport = [0x87db5, 0x100]
    VersionAuthorize = [0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, \
                        0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, \
                        0x00123406]
#    TSR = [0x00, 2, int( 58930 * 262.144 ), int( 58931 * 262.144 ), \
#           0x00, 34, int( 12000 * 262.144 ), int( 10000 * 262.144 ), \
#           0x00, 17, int( 3 * 262.144 ), int( 100 * 262.144 )]
    TSR = []
    for _c in range( 0, 3000 ):
        TSR += [0x01, 0x00, 0x00, 0x00]
    TSR.append( 0x10 )
    print TSR
    print TSR.__len__()
    CCVersionReport = [0x0001, 0x0001, 0x0001, 0x0001, 0x0001, \
                       0x0004, 0x0005, 0x0006, 0x0007, 0x0008, \
                       0x0009, 0x000A, 0x000B, 0x000C, 0x000D, \
                       0x000E, 0x000F, 0x0010, 0x12345678]
    cks1 = sacemdll.transform_Ito3Byte( 7423556 )
    cks2 = sacemdll.transform_Ito3Byte( 5063861 )
    CCVersionReport += cks1
    CCVersionReport += cks2
#    print CCVersionReport
    #DATP2ATP,29个变量+src+dest
    DATP2ATP = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                21, 22, 23, 24, 25, 26, 27, 28, 29, 2]
#    
    
    
#    ATP2VIOM1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
#                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
#                 201, 198, 3597242327, 128]

    #新的ATP2VIOM消息,20个码位+2个loophour+5个变量+1个变量，20111107    
#    ATP2VIOM1 = [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, \
#                 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, \
#                 12345, 54321, 0, 0, 0, 0, 1, 0]
    
    VIOM2ATP = [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
                0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
#                0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
#                0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
                123456, 654321, 789, 987]

#    retcdw = GM_SACEM_Shb_Recv2App_Type_LC()
#    retcdw = GM_SACEM_Shb_Recv2App_Type()
    
    #发送过程
#    checksum = sacemdll.SACEM_Tx_Msg_Dll(EOAMsgId, SrcSSTy, SrcSSID, DestSSTy, DestSSID, EOA)
#    checksum = sacemdll.SACEM_Tx_Msg_Dll(VariantsMsgId, SrcSSTy, SrcSSID, DestSSTy, DestSSID, Variants)
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( DateSynReportMsgId, 40, 1, 20, 1, DateSynReport )
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( VersionAuthorizeMsgId, 40, 1, 20, 1, VersionAuthorize )
    checksum = sacemdll.SACEM_Tx_Msg_Dll( TSRMsgId, 40, 1, 20, 1, TSR )
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( CCVersionReportMsgId, 20, 1, 40, 1, CCVersionReport )
#    checksum = sacemdll.SACEM_Tx_Msg_Dll(ATP2VIOMMsgId, 24, 1, 23, 1, ATP2VIOM1)
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( VIOM2ATPMsgId, 23, 1, 24, 1, VIOM2ATP )
#    checksum = sacemdll.SACEM_Tx_Msg_Dll( DATP2ATPMsgId, 24, 2, 24, 1, DATP2ATP )
    if ( checksum == None ):
        print "Packing is failed!"
    else:
        print checksum
        print "Packing successful!"
      
#    #接收过程
    #application data to Unpack 
#    for _c in checksum:
#        EOA.append(_c)
#    print EOA

#    for _c in checksum:
#        TSR.append(_c)
#    print TSR
#
#    for _c in checksum:
#        ATP2VIOM1.append(_c)
#    print ATP2VIOM1
#    ATP2VIOM1.extend([95, 4, 1, 177, 253, 145])
    
#    for _c in checksum:
#        VIOM2ATP.append( _c )
#    print VIOM2ATP

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
#    print LocReport
#    CCVersionReport = []
#    for _c in checksum:
#        DATP2ATP.append(_c)
#    print DATP2ATP
        
    #CC2LC, Src is 20, Dest is 30
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll(LocMsgId, 20, 1, \
#                                       30, 1, LocReport)
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll(TSRMsgId, 40, 1, \
#                                       20, 1, TSR)                         
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll(EOAMsgId, SrcSSTy, SrcSSID, \
#                                       DestSSTy, DestSSID, EOA)
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll(ATP2VIOMMsgId, 24, 1, \
#                                       23, 1, ATP2VIOM1)
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( VIOM2ATPMsgId, 23, 1, 24, 1, VIOM2ATP )
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( CCVersionReportMsgId, 20, 1, 40, 1, \
#                                       CCVersionReport )
#    retcdw = sacemdll.SACEM_Rx_Msg_Dll( DATP2ATPMsgId, 24, 2, 24, 1, DATP2ATP )
#    if None == retcdw:
#        print "Unpacking is failed!"
#    else:
#        print "Unpacking successful!"
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

