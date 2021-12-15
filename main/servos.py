#!/usr/bin/env python

import os
import time
import logging
import json
SERVO = 0
if SERVO:
    import Adafruit_PCA9685 # for PC simulation

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class servos():

    def __init__(self):
        if SERVO:
            self.pwm = Adafruit_PCA9685.PCA9685()
            self.pwm.set_pwm_freq(60)
        self.sc = None
        self.readServosConfig()
        self.pwms = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.angles = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        logger.info("Started servo class")

    def readServosConfig(self):
        # Opening JSON file
        f = open('config.json',)
        # returns JSON object as a dictionary
        data = json.load(f)
        # Closing file
        f.close()
        self.sc = data

    def getChannel(self, leg, joint):
        return self.sc[leg][joint]["id"]

    def bound(self, leg, joint, pwm):
        if(self.sc[leg][joint]["max_pwm"] > self.sc[leg][joint]["min_pwm"]):
            min = self.sc[leg][joint]["min_pwm"]
            max = self.sc[leg][joint]["max_pwm"]
        else:
            max = self.sc[leg][joint]["min_pwm"]
            min = self.sc[leg][joint]["max_pwm"]

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
        factor = (self.sc[leg][joint]["max_angle_pwm"]-self.sc[leg][joint]["min_angle_pwm"])/(self.sc[leg][joint]["max_angle"]-self.sc[leg][joint]["min_angle"])
        offset = self.sc[leg][joint]["min_angle_pwm"] - factor * self.sc[leg][joint]["min_angle"]
        logger.debug("Factor: "+str(factor) + ", Offset: " + str(offset))
        pwm = int( factor * angle + offset)
        p = self.bound(leg, joint, pwm)
        if SERVO:
            self.pwm.set_pwm(self.sc[leg][joint]["id"], 0, p)
        self.pwms[self.getChannel(leg, joint)] = p
        self.angles[self.getChannel(leg, joint)] = angle
        logger.debug("Leg: "+leg+", Joint: "+joint+", Angle: "+str(angle) + ", PWM: " + str(p))

    def close(self):
        logger.info("Closed servos")
        if SERVO:
            for i in range(12):
                self.pwm.set_pwm(i, 0, 4096)
            time.sleep(0.5)

# Run this if standalone (test purpose)
if __name__ == '__main__':
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)

    try:
        logger.info("Started main")
        s = servos()
        s.setServoAngle("FL", "hip", 0)
        time.sleep(0.5)
        s.setServoAngle("FR", "hip", 0)
        time.sleep(0.5)
        s.setServoAngle("RL", "hip", 0)
        time.sleep(0.5)
        s.setServoAngle("RR", "hip", 0)
        time.sleep(0.5)
    except KeyboardInterrupt:
        # Signal termination
        logger.info("Keyboard interrupt. Terminate thread")
    finally:
        s.close()
        logger.debug("Thread terminated")
