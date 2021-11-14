#!/usr/bin/env python

import os
import time
import logging
import json
ADAFRUIT = 0
if ADAFRUIT:
    import Adafruit_PCA9685 # for PC simulation

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class Servos():

    def __init__(self):
        if ADAFRUIT:
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
        return self.sc[leg][joint].id

    def setServoRaw(self, leg, joint, pwm):
        # raw pwm values
        if pwm < self.sc[leg][joint].min_pwm:
            pwm = self.sc[leg][joint].min_pwm
        elif pwm > self.sc[leg][joint].max_pwm:
            pwm = self.sc[leg][joint].max_pwm
        self.pwm.set_pwm(self.sc[leg][joint].id, 0, pwm)
        self.pwms[getChannel(leg, joint)] = pwm

    def setServoAngle(self, leg, joint, angle):
        # angle
        pwm = int(angle*(self.sc[leg][joint].max_pwm-self.sc[leg][joint].min_pwm)/self.sc[leg][joint].angle_range+self.sc[leg][joint].min_pwm)
        if pwm < self.sc[leg][joint].min_pwm:
            pwm = self.sc[leg][joint].min_pwm
        elif pwm > self.sc[leg][joint].max_pwm:
            pwm = self.sc[leg][joint].max_pwm
        self.pwm.set_pwm(self.sc[leg][joint].id, 0, pwm)
        self.pwms[getChannel(leg, joint)] = pwm
        self.angles[getChannel(leg, joint)] = angle

    def close(self):
        for i in range(11):
            self.pwm.set_pwm(i, 0, 4096)

class Actuation():

    QUIT = 0
    IDLE = 1
    SET  = 2
    CTR  = 3
    RST  = 4
    MOV  = 5

    def __init__(self):
        self.mode = self.IDLE
        self.swipe = 0
        self.swipe_sign = 1
        self.MAX_SWIPE = 200 # max swipe angle
        #self.min_pwms = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #self.max_pwms = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #self.range_angles = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.servos = Servos()
        self.leg = ""
        self.joint = ""

    def printServos(self):
        try:
            print("Active leg: "+self.leg)
            print("Active joint: "+self.joint)
            print("PWMs: ")
            print(self.servos.pwms)
            print("Angles: ")
            print(self.servos.angles)
            print("Min PWM: "+self.servos.sc[self.leg][self.joint].min_pwm)
            print("Max PWM: "+self.servos.sc[self.leg][self.joint].max_pwm)
            print("\n")
        except:
            pass

    def setMode(self, mode):
        if(mode == "b" or mode == "q"):
            self.mode = self.QUIT
        elif(mode == "s"):
            self.mode = self.SET
        elif(mode == "c" or mode == "a"):
            self.mode = self.CTR
        elif(mode == "r"):
            self.mode = self.RST
        elif(mode == "m"):
            self.mode = self.MOV
        elif(mode == "i"):
            self.mode = self.IDLE
        else:
            print("Unknown mode")

    def swipeServo(self):
        if self.swipe >= self.MAX_SWIPE:
            self.swipe_sign = -1
            time.sleep(1)
        if self.swipe <= 0:
            self.swipe_sign = 1
            time.sleep(1)
        self.swipe += self.swipe_sign
        self.setServo(1, self.swipe)
        print("swipe: "+str(self.swipe)+"  ", end = "\r")
        #self.printServos()

    def close(self):
        self.servos.close()
        logger.debug("Bye")

# Run this if standalone (test purpose)
if __name__ == '__main__':
    message = ""
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    cls()
    try:
        logger.info("Started main")
        a = Actuation()
        while a.mode != a.QUIT:
            print("b: back (quit), s: select, r: reset, c: control raw, a: control angle, m: swipe")
            mode = input("Set your choice: ")
            a.setMode(mode)
            if mode == "b" or mode == "q":
                a.close()
                break
            elif mode == "s":
                while a.mode == a.SET:
                    cls()
                    print(message)
                    print("\n*** select mode ***\n")
                    a.printServos()
                    command = input('Select leg to be selected ("fl", "rl", "fr", "rr" or "b" to go back): ')
                    if command == "b" or command == "q": break
                    else:
                        try:
                            if(command == "fl" or command == "fr" or command == "rl" or command == "rr"):
                                a.leg = command
                        except:
                            message = "Wrong selection !!"
                    command = input('Select joint to be selected ("k nee", "h ip", "r oll" or "b" to go back): ')
                    if command == "b" or command == "q": break
                    else:
                        try:
                            if(command == "k" or command == "h" or command == "r"):
                                a.joint = command
                                cls()
                                a.setMode("i")
                        except:
                            message = "Wrong selection !!"
            elif mode == "r":
                while a.mode == a.RST:
                    cls()
                    print(message)
                    print("\n*** reset mode ***\n")
                    
            elif mode == "c":
                while a.mode == a.CTR:
                    cls()
                    print(message)
                    print("\n*** control mode (raw PWM) ***\n")
                    a.printServos()
                    command = input('Select servo PWM (or "b" to go back): ')
                    if command == "b" or command == "q": break
                    else:
                        try:
                            a.servos.setServoRaw(self.leg, self.joint, int(command))
                        except:
                            message = "Wrong selection !!"
            elif mode == "a":
                command = 0
                while a.mode == a.CTR:
                    cls()
                    print(message)
                    print("\n*** control mode (angle) ***\n")
                    a.printServos()
                    print("Last angle: "+str(command)+"°")
                    command = input('Select servo angle (or "b" to go back): ')
                    if command == "b" or command == "q": break
                    else:
                        try:
                            a.servos.setServoAngle(self.leg, self.joint, int(command))
                        except:
                            message = "Wrong selection !!"
            elif mode == "m":
                try:
                    while True:
                        a.swipeServo()
                        time.sleep(0.01)
                except KeyboardInterrupt:
                    mode = "b"
    except KeyboardInterrupt:
        # Signal termination 
        logger.info("Keyboard interrupt. Terminate thread")
        a.close()
