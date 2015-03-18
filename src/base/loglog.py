#!/usr/bin/python
# -*- coding:utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     loglog.py
# Description:  logging module     
# Author:       OUYANG Min
# Version:      0.0.1
# Created:      2011-03-08
# Company:      CASCO
# LastChange:   2012-02-24
# History:      Created --- 2011-03-08
#               Modify for save in different path
#----------------------------------------------------------------------------
import logging
import time

class LogFactory():
    """a logger factory, create the logger and add file handel"""


    def __init__( self ):
        "open logConfig file"
        pass
    @classmethod
    def createdLogger( self, loggerName ):
        "return a logger and the name is loggerName"
        return logging.getLogger( loggerName )

class LogLog():
    """logging information"""


    __logger = None
    __fh = None
    __logName = None
    __LogFlag = None
    
    __LogLevel = logging.DEBUG  #初始设置为改级别
    
    def __init__( self ):
        "do nothing"
        pass
    
    @classmethod
    def setWholeLogLevel( cls, level ):
        "set whole log level"
        if 0 == level:
            cls.__LogLevel = logging.CRITICAL
        elif 1 == level:
            cls.__LogLevel = logging.ERROR
        elif 2 == level:
            cls.__LogLevel = logging.WARN
        elif 3 == level:
            cls.__LogLevel = logging.INFO
        elif 4 == level:
            cls.__LogLevel = logging.DEBUG
        else:
            print "not define"

    def orderLogger( self, filePath, loggerName = 'root' ):
        "order a logger from factory"
        self.__LogFlag = True
        self.__logName = loggerName
        self.__logger = logging.getLogger( loggerName )
        self.__logger.setLevel( LogLog.__LogLevel )
        #self.__logger.setLevel(logging.ERROR)
        self.__fh = logging.FileHandler( filePath, 'w' )
        formatter = logging.Formatter( "%(asctime)s - %(name)s - %(levelname)s - %(message)s" )
        self.__fh.setFormatter( formatter )
        self.__fh.setLevel( logging.DEBUG )
        self.__logger.addHandler( self.__fh )
        
          
    def setloglevel( self, level ):
        "set log level"
        if 0 == level:
            self.__logger.setLevel( logging.CRITICAL )
        elif 1 == level:
            self.__logger.setLevel( logging.ERROR )
        elif 2 == level:
            self.__logger.setLevel( logging.WARN )
        elif 3 == level:
            self.__logger.setLevel( logging.INFO )
        elif 4 == level:
            self.__logger.setLevel( logging.DEBUG )
        else:
            print "not define"
    
    def fileclose( self ):
        "close handle file"
        self.__LogFlag = False
        time.sleep( 0.1 ) #延时0.1秒
        try:
            self.__fh.flush()
            self.__fh.close()
            self.__logger.removeHandler( self.__fh )
        except:
            print "fileclose error:", self.__logName
            
    def logDebug( self, mes ):
        "log debug message"
        if self.__LogFlag == False:
            return
        if self.__logger:
            self.__logger.debug( mes )
        else:
            self.useTips()
    

    def logInfo( self, mes ):
        "log information message"
        if self.__LogFlag == False:
            return        
        if self.__logger:
            self.__logger.info( mes )
        else:
            self.useTips()
    

    def logWarn( self, mes ):
        "log warnning message"
        if self.__LogFlag == False:
            return        
        if self.__logger:
            self.__logger.warn( mes )
        else:
            self.useTips()
    

    def logError( self, mes ):
        "log error message"
        if self.__LogFlag == False:
            return
        if self.__logger:
            self.__logger.error( mes )
        else:
            self.useTips()
    

    def logCritical( self, mes ):
        "log critical  message"
        if self.__LogFlag == False:
            return
        if self.__logger:
            self.__logger.critical( mes )
        else:
            self.useTips()


    def useTips( self ):
        "tips for user"
        print 'LogLog use tips,please create logger first'
    
    # --------------------------------------------------------------------------
    ##
    # @Brief 记录日志
    # @level 4-debug,3-info,2-warn,1-error,0-critical
    # @mes 
    # --------------------------------------------------------------------------
    def logMes( self, level, mes ):
        "log message by level"
        if level == 0:
            self.logCritical( mes )
        elif level == 1:
            self.logError( mes )
        elif level == 2:
            self.logWarn( mes )
        elif level == 3:
            self.logInfo( mes )
        elif level == 4:
            self.logDebug( mes )
        else:
            self.logError( 'level is not define' )
    
    

if __name__ == '__main__':
    l = LogLog()
    l.orderLogger( "test.log", 'background' )
    l.logMes( 4, "dffdasfdsaa" )
    l.fileclose()
    l = LogLog()
    l.orderLogger( "test1.log", 'background' )
    l.logMes( 4, "dfadfafdasfadsdfa" )    
    l.fileclose()
#    l.logMes(4, "dfadfafdasfadsdf23")  
    #LogLog.orderLogger()
#    LogLog.logDebug('debug')
#    LogLog.logInfo('info')
#    LogLog.logWarn('warn')
#    LogLog.logCritical('critical')
#    LogLog.logError('error')
#    LogLog.logMes(4, 'TT')
