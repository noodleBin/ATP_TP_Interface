#!/usr/bin/env python
# -*- coding: utf-8 -*- 


import wx

import os
import sys
import time
import  wx.lib.buttons  as  buttons



RedRGB = (255,0,0,255)
GreenRGB = (0,255,0,255)
YellowRGB = (255,255,0,255)
GrayRGB = (192,192,192,255)
PurpleRGB = (128,0,128,255)

try:
    from agw import gradientbutton as GB
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.gradientbutton as GB

            
class MyGradientButton(wx.Panel):

    def __init__(self, parent, log):
     
        wx.Panel.__init__(self, parent)
        self.trainStatus ={
                      'initStatus':{'presetSpeedEnable':True,
                                    'currentSpeedEnable':False,
                                    'Stop':[False,RedRGB],
                                    'Run':[True,PurpleRGB]
                                    },

                      'AccStatus':{
                                   'presetSpeedEnable':False,
                                    'currentSpeedEnable':False,
                                    'Stop':[False,RedRGB],
                                    'Run':[False,YellowRGB]
                                 },
                     'RunStatus':{'presetSpeedEnable':False,
                                    'currentSpeedEnable':False,
                                    'Stop':[True,RedRGB],
                                    'Run':[False,GreenRGB]
                                    },
                      'DecStatus':{
                                    'presetSpeedEnable':False,
                                    'currentSpeedEnable':False,
                                    'Stop':[False,YellowRGB],
                                    'Run':[False,PurpleRGB]
                                 }   
                      }  
        self.currentStatus ='initStatus'
        self.lastStatus = ''
        
        self.presetMaxSpeed = 20
        self.currentSpeed = 20
        self.handles = list()
        self.log = log
        
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetBackgroundColour(wx.WHITE)
        
        self.DoLayout()
        self.BindEvents()
    def getCurrentStatus(self):
        return self.currentStatus   
    def statusChange(self,statusName):
        def updateTheView(state):
            self.handles[0].Enable(state['presetSpeedEnable'])
            self.handles[1].Enable(state['currentSpeedEnable'])
            self.handles[1].SetValue('%d'%(self.getCurrentSpeed()))
            self.handles[2].Enable(state['Stop'][0])
            self.handles[3].Enable(state['Run'][0])
            self.handles[2].SetBackgroundColour(state['Stop'][1])
            self.handles[3].SetBackgroundColour(state['Run'][1])
            self.GetSizer().Layout()
        if self.lastStatus != statusName:
            self.lastStatus = self.currentStatus
            self.currentStatus = statusName  
            state = self.trainStatus[statusName]         
            updateTheView(state)            
            return True
        else: 
            return False
        
    def getCurrentSpeed(self):
        return self.currentSpeed
    
    def setCurrentSpeed(self,speed):
        self.currentSpeed = speed
        if speed == self.presetMaxSpeed:            
            self.statusChange('RunStatus')
        elif 0 == speed:        
            self.statusChange('initStatus')
        else:
            self.handles[1].SetValue(str(speed))
            print self.handles[1].GetValue()
            self.statusChange(self.currentStatus)
            self.mainPanel.Refresh()
        
    def DoLayout(self):
        frameSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        colourSizer = wx.FlexGridSizer(3, 2, 20, 20)
        
        firstStrings = ["Preset Speed", "Current Speed"]
        secondStrings = ["Stop", "Run"]
        
        for strings in firstStrings:
            label = wx.StaticText(self.mainPanel, -1, strings)
            txtctrl = wx.TextCtrl( self.mainPanel, -1, '', size = ( 125, -1 ) )
            if strings == "Current Speed":
                txtctrl.Enable(False)
            self.handles.append(txtctrl)
            colourSizer.Add(label, 0, wx.ALIGN_CENTER|wx.EXPAND)
            colourSizer.Add(txtctrl, 0, wx.ALIGN_CENTER|wx.EXPAND)

        for strings in secondStrings:
            bt = buttons.GenButton(self.mainPanel, -1, strings)            
            bt.SetFont(wx.Font(15, wx.SWISS, wx.NORMAL, wx.BOLD, False))
            bt.SetBezelWidth(10)
            bt.SetMinSize(wx.DefaultSize)
            if strings == "Stop":
                bt.SetBackgroundColour(PurpleRGB)
                bt.Enable(False)                 
            else:
                bt.SetBackgroundColour(PurpleRGB)
            bt.SetForegroundColour(wx.WHITE)  
            colourSizer.Add(bt, flag=wx.ADJUST_MINSIZE)    
            self.handles.append(bt)
  
        mainSizer.Add(colourSizer, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
#        mainSizer.Add(testBt)

        boldFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        boldFont.SetWeight(wx.BOLD)
        
        buttonFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        buttonFont.SetWeight(wx.BOLD)
        try:
            buttonFont.SetFaceName("Tahoma")
        except:
            pass
           
        self.mainPanel.SetSizer(mainSizer)
        mainSizer.Layout()
        frameSizer.Add(self.mainPanel, 1, wx.EXPAND)
        self.SetSizer(frameSizer)
        frameSizer.Layout()
           
    def BindEvents(self): 
        self.Bind(wx.EVT_BUTTON, self.onRun,self.handles[3])
        self.Bind(wx.EVT_BUTTON, self.onStop,self.handles[2])
        

    def onRun(self,event):   
        if self.currentStatus == "initStatus":
            self.setPresetMaxSpeed()  
                      
        self.statusChange('AccStatus')

    def onStop(self,event):       
#        self.handles[3].Enable(True)
        self.statusChange('DecStatus')
       
    def setPresetMaxSpeed(self):
        text = self.handles[0].GetValue()
        speed = int(text)
        if speed>4 and speed<=20:   
            self.presetMaxSpeed = speed
            print "Preset OK"
        else:
            print "the Preset Speed is not in normal range "  
        self.handles[0].Enable(False)    

class TrainSimulator(wx.Frame):
    grad = None
    def __init__(self, parent, log):

        wx.Frame.__init__(
            self, parent, -1, "Test Frame", size=(400,250)
            )

        panel = wx.Panel(self, -1, style=0)
        
        self.grad = MyGradientButton(panel, log)
        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(self.grad, 1, wx.GROW|wx.ALL, 5)
        panel.SetSizer(bs)
        
    def getGradient(self):
        return self.grad
     
if __name__ == '__main__':
    app = wx.App(0)
    frame = TrainSimulator(None,-1)     
    frame.Show(True)
    app.MainLoop()

