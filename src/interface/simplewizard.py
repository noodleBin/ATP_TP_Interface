#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     simplewizard.py
# Description:  用于生成新用例的向导界面 
# Author:       Xiongkunpeng
# Version:      0.0.1
# Created:      2011-11-22
# Company:      CASCO
# LastChange:   create 2011-11-22
# History:          
#----------------------------------------------------------------------------
import  wx
import  wx.wizard as wiz
import simplepanel
from base.caseprocess import CaseEdit
from autoAnalysis.analysisedit import AnalysisEdit
from simplepanel import *

#----------------------------------------------------------------------

class TitledPage( wiz.WizardPageSimple ):
    def __init__( self, parent, title ):
        wiz.WizardPageSimple.__init__( self, parent )
#        self.sizer = makePageTitle( self, title )


#----------------------------------------------------------------------
#向导类，生成新用例的脚本
#----------------------------------------------------------------------
class CaseWizard( wiz.Wizard ):
    def __init__( self, parent, NewFlag = True ):
        if True == NewFlag:
            wiz.Wizard.__init__( self, parent, -1, "Create New Case wizard" )
        else:
            wiz.Wizard.__init__( self, parent, -1, "Case Config wizard" )
        #添加向导页面
        self.__case = CaseEdit()
        
        self.CreateNew = NewFlag
        
        page1 = CaseConfigWizard( self, "Case Config Page", Create = NewFlag, CaseEditNode = self.__case )
        page2 = RouteConfigWizard( self, "Route Config Page", CaseEditNode = self.__case )
        page3 = SceConfigWizard( self, "Scenario Config Page", CaseEditNode = self.__case )
        page4 = ZCSceConfigWizard( self, "ZC Scenario Config Page", CaseEditNode = self.__case )
        page5 = CISceConfigWizard( self, "CI Scenario Config Page", CaseEditNode = self.__case ) 
        page6 = BeaconConfigWizard( self, "Beacon Config Page", CaseEditNode = self.__case )
        page7 = ViomTSRConfigWizard( self, "Viom TSR Config Page", CaseEditNode = self.__case )
        
        self.page1 = page1
        self.page2 = page2
        self.page3 = page3
                
        self.FitToPage( page1 )
        
        # Set the initial order of the pages
        page1.SetNext( page2 )
        page2.SetPrev( page1 )
        page2.SetNext( page3 )
        page3.SetPrev( page2 )
        page3.SetNext( page4 )
        page4.SetPrev( page3 )
        page4.SetNext( page5 )
        page5.SetPrev( page4 )
        page5.SetNext( page6 )
        page6.SetPrev( page5 )
        page6.SetNext( page7 )
        page7.SetPrev( page6 )

        self.GetPageAreaSizer().Add( page1 )
#        if wizard.RunWizard( page1 ):
#            wx.MessageBox( "Wizard completed successfully", "That's all folks!" )
#        else:
#            wx.MessageBox( "Wizard was cancelled", "That's all folks!" )
        
        #保定向导相关设置
        self.Bind( wiz.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged )
        self.Bind( wiz.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging )        
        self.Bind( wiz.EVT_WIZARD_CANCEL, self.OnWizCancel )
        self.Bind( wiz.EVT_WIZARD_FINISHED, self.OnWizFinished )

    def StartWizard( self ):
        "start wizard."
        return self.RunWizard( self.page1 )
    
    def OnWizPageChanged( self, evt ):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()
        if page != self.page1:
            page.UpLoadData() #其余页面要根据配置更新相关数据
        if page == self.page2:
            self.page3.CloseTransformFrame()
            
#        self.log.write( "OnWizPageChanged: %s, %s\n" % ( dir, page.__class__ ) )


    def OnWizPageChanging( self, evt ):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()
#        self.log.write( "OnWizPageChanging: %s, %s\n" % ( dir, page.__class__ ) )
        if page == self.page1:
            #进行开辟用例处理，失败则不能进行到下一步骤
            if page.EndThisPanel() not in [0, 1]: 
                evt.Veto()
            else:
                print "create success"

    def OnWizCancel( self, evt ):
        page = evt.GetPage()
#        self.log.write( "OnWizCancel: %s\n" % page.__class__ )

        # Show how to prevent cancelling of the wizard.  The
        # other events can be Veto'd too.
        if True == self.CreateNew and False == self.page1.createFlag: #对已经创建的进行删除
            CaseParser.delEditCaseStep()
            
#        if page is self.page1:
#            wx.MessageBox( "Cancelling on the first page has been prevented.", "Sorry" )
#            evt.Veto()


    def OnWizFinished( self, evt ):
#        self.log.write( "OnWizFinished\n" )
        #保存数据
        self.__case.saveTrainRouteList()
        self.__case.saveExpectSpeedListToXML()
        self.__case.SaveScenarioDicToXML()
        self.__case.saveZCVariantIni()
        self.__case.saveZCVariantSce()
        self.__case.saveCIVariantSce()
        self.__case.saveBMBeaconDic()
        self.__case.saveBeaconMsgSetting()
        self.__case.saveVIOMSettingToXML()
        self.__case.saveTSRSetting()
        CaseParser.SaveEditCaseConfig()



#----------------------------------------------------------------------
#向导类，生成新用例分析的脚本
#----------------------------------------------------------------------
class AnalysisWizard( wiz.Wizard ):
    def __init__( self, parent, NewFlag = True ):
        if True == NewFlag:
            wiz.Wizard.__init__( self, parent, -1, "Create New Analysis wizard" )
        else:
            wiz.Wizard.__init__( self, parent, -1, "Analysis Config wizard" )
        #添加向导页面
        self.__analysis = AnalysisEdit()
        
        self.CreateNew = NewFlag
        
        page1 = AnalysisVarConfigWizard( self, "Variant Config Page", Create = NewFlag, AnalysisEditNode = self.__analysis )
        
        page2 = AnalysisRuleConfigWizard( self, "Rule Config Page", AnalysisEditNode = self.__analysis )
        self.page1 = page1
        self.page2 = page2
                
        self.FitToPage( page1 )
        
        # Set the initial order of the pages
        page1.SetNext( page2 )
        page2.SetPrev( page1 )


        self.GetPageAreaSizer().Add( page1 )

        
        #保定向导相关设置
        self.Bind( wiz.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged )
        self.Bind( wiz.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging )        
        self.Bind( wiz.EVT_WIZARD_CANCEL, self.OnWizCancel )
        self.Bind( wiz.EVT_WIZARD_FINISHED, self.OnWizFinished )

    def StartWizard( self ):
        "start wizard."
        return self.RunWizard( self.page1 )
    
    def OnWizPageChanged( self, evt ):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()
        page.UpdateView() #更新相关数据


    def OnWizPageChanging( self, evt ):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()
#        self.log.write( "OnWizPageChanging: %s, %s\n" % ( dir, page.__class__ ) )
#        if page == self.page1:
            #进行开辟用例处理，失败则不能进行到下一步骤
#            if page.EndThisPanel() not in [0, 1]: 
#                evt.Veto()
#            else:
#                print "create success"

    def OnWizCancel( self, evt ):
        page = evt.GetPage()
#        self.log.write( "OnWizCancel: %s\n" % page.__class__ )

        # Show how to prevent cancelling of the wizard.  The
        # other events can be Veto'd too.
        if True == self.CreateNew and False == self.page1.createFlag: #对已经创建的进行删除
            CaseParser.delEditCaseStep()
            
#        if page is self.page1:
#            wx.MessageBox( "Cancelling on the first page has been prevented.", "Sorry" )
#            evt.Veto()


    def OnWizFinished( self, evt ):
        "on wiz finshed"
#        self.log.write( "OnWizFinished\n" )
        #保存数据
        _content = self.__analysis.checkIfValidAnalysisDic()
        if True != _content:
            print _content
            wx.MessageBox( _content, "Error" )
            evt.Veto()
        else:
            self.__analysis.saveAnalysisFile()
        

if __name__ == '__main__':
    pass
