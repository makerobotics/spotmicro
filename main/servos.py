#!/usr/bin/env python

import os
import time
import logging
import json
SERVO = 0
if SERVO:
    import Adafruit_PCA9685 # for PC simulation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class servos():

    def __init__(self):
        if SERVO:
            self.pwm = Adafruit_PCA9685.PCA9685()
            self.pwm.set_pwm_freq(60)
        self.sc = self.readServosConfig()
        self.pwms = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.angles = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def readServosConfig(self):
        # Opening JSON file
        f = open('config.json',)
        # returns JSON object as a dictionary
        data = json.load(f)
        # Closing file
        f.close()
        return data

    def getChannel(self, leg, joint):
        return self.sc[leg][joint]["id"]

    def bound(self, leg, joint, pwm):
        if(self.sc[leg][joint]["max_angle_pwm"] > self.sc[leg][joint]["min_angle_pwm"]):
            min = self.sc[leg][joint]["min_angle_pwm"]
            max = self.sc[leg][joint]["max_angle_pwm"]
        else:
            max = self.sc[leg][joint]["min_angle_pwm"]
            min = self.sc[leg][joint]["max_angle_pwm"]
        
        if pwm < min:
            pwm = min
        elif pwm > max:
            pwm = max
        return pwm

    def setServoRaw(self, leg, joint, pwm):
        # raw pwm values
        p = self.bound(leg, joint, pwm)
        if SERVO:
            self.pwm.set_pwm(self.sc[leg][joint]["id"], 0, p)
        self.pwms[self.getChannel(leg, joint)] = p

    def setServoAngle(self, leg, joint, angle):
        factor = int( (self.sc[leg][joint]["max_angle_pwm"]-self.sc[leg][joint]["min_angle_pwm"])/(self.sc[leg][joint]["max_angle"]-self.sc[leg][joint]["min_angle"]) )
        offset = int( self.sc[leg][joint]["max_angle_pwm"] - factor*self.sc[leg][joint]["max_angle"])
        #logger.debug(str(factor) + " " + str(offset))
        pwm = int( factor * angle + offset)
        p = self.bound(leg, joint, pwm)
        if SERVO:
            self.pwm.set_pwm(self.sc[leg][joint]["id"], 0, p)
        self.pwms[self.getChannel(leg, joint)] = p
        self.angles[self.getChannel(leg, joint)] = angle
        logger.debug(leg+" "+joint+" "+str(angle) + " " + str(p))
        
    def close(self):
        if SERVO:
            for i in range(11):
                self.pwm.set_pwm(i, 0, 4096)
