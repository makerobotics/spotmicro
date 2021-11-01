#!/usr/bin/env python

import time
import logging
import configparser
from threading import Thread
import Adafruit_PCA9685
#import RPi.GPIO as GPIO
import sense
import data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class control(Thread):

    TRACE = 1

    def __init__(self, sensors):
        Thread.__init__(self)
        self.tracefile = None
        self.traceline = 0
        self.traceData = {}
        self.lastFrameTimestamp = time.time()
        self.cycleTime = 0
        self._running = True
        #self.initTrace()
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(60)
        
    def initTrace(self):
        if(self.TRACE == 1):
            self.tracefile = open("trace.csv","w+")
            header = "timestamp;"
            for k, v in self.traceData.iteritems():
                header += k+";"
            header += "\r\n"
            self.tracefile.write(header)
            
    def writeTrace(self):
        if (self.TRACE == 1):
            if self.traceline == 0:
                self.initTrace()
                self.traceline = 1
            filestring = str(time.time())+";"
            displaystring = ""
            for k, v in self.traceData.iteritems():
                displaystring += k+": "+str(v)+", "
                filestring += str(v)+";"
            filestring += "\r\n"
            #logger.debug(displaystring)
            self.tracefile.write(filestring)

    def terminate(self): 
        self._running = False
        
    def idleTask(self):
        pass
        #print("."),

    def close(self):
        logger.debug("Closing control thread")
        if self.TRACE == 1 and self.tracefile != None:
            self.tracefile.close()

    def runCommand(self, cmd):
        logger.info("Control thread received command: " + cmd)
        data = cmd.split(';')
        if(data[0] == "SERVO"):
            self.pwm.set_pwm(channel, 0, pwm)
        elif(data[0] == "RESET"):
            for ch in Range(12):
                self.pwm.set_pwm(ch, 0, 0)

    def run(self):
        logger.debug('Control thread running')
        while self._running: 
            time.sleep(0.05)
            ### Wait for command (call of runCommand by rpibot.py)
            self.idleTask()
        self.close() 
        logger.debug('Control thread terminating')

    def stop(self, reason):
        logger.info("Stopped by "+reason)

# Run this if standalone (test purpose)
if __name__ == '__main__':

    try:
        logger.info("Started main")
        s = sense.sense()
        s.start()
        c = control(s) 
        c.start()
        time.sleep(2)
        c.stop("Test")
    except KeyboardInterrupt:
        # Signal termination 
        logger.info("Keyboard interrupt. Terminate thread")
    finally:
        c.terminate()
        s.terminate()
        logger.debug("Thread terminated")

        # Wait for actual termination (if needed)  
        c.join()
        s.join()
        logger.debug("Thread finished")
