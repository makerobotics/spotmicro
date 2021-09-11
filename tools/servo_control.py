#!/usr/bin/env python

import os
import time
import logging
import configparser
from threading import Thread
import Adafruit_PCA9685
#import RPi.GPIO as GPIO

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class Actuation():

    QUIT = 0
    IDLE = 1
    SET  = 2
    CTR  = 3
    RST  = 4

    def __init__(self):
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(60)
        self.readIni()
        self.mode = self.IDLE
        self.actives = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.pwms =    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.min_pwms = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.max_pwms = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def readIni(self):
        logger.info("Read ini file")
        Config = configparser.ConfigParser()
        Config.read("config.ini")
        self.min_pwms[0] = Config.getint('channel_0', 'servo_min_pwm')
        self.max_pwms[0] = Config.getint('channel_0', 'servo_max_pwm')

    def setMode(self, mode):
        if(mode == "q"):
            self.mode = self.QUIT
        elif(mode == "s"):
            self.mode = self.SET
        elif(mode == "c"):
            self.mode = self.CTR
        elif(mode == "r"):
            self.mode = self.RST
        else:
            print("Unknown mode")

    def setServo(self, pwm):
        index = 0
        for i in self.actives:
            if i == 1:
                if pwm<self.min_pwms[index]:
                    pwm = self.min_pwms[index]
                elif pwm>self.max_pwms[index]:
                    pwm = self.max_pwms[index]
                self.pwms[index] = pwm
                self.pwm.set_pwm(index, 0, pwm)
            index += 1

    def selectServo(self, servo, active):
        self.actives[servo] = active

    def printServos(self):
        print("Actives: ")
        print(self.actives)
        print("PWMs: ")
        print(self.pwms)
        print("\n")

    def close(self):
        logger.debug("Bye")

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
    cls()
    try:
        logger.info("Started main")
        a = Actuation()
        while a.mode != a.QUIT:
            print("q: quit, s: select, r: reset, c: control")
            mode = input("Set your choice: ")
            a.setMode(mode)
            if mode == "q":
                a.close()
                break
            elif mode == "s":
                while a.mode == a.SET:
                    cls()
                    print("\n*** select mode ***\n")
                    a.printServos()
                    servo = input("Servo to select (or q to go back): ")
                    if servo == "q": break
                    else:
                        try:
                            a.selectServo(int(servo), 1)
                        except:
                            print("Wrong selection !!")
            elif mode == "r":
                while a.mode == a.RST:
                    cls()
                    print("\n*** reset mode ***\n")
                    a.printServos()
                    servo = input("Servo to select (or q to go back): ")
                    if servo == "q": break
                    else:
                        try:
                            a.selectServo(int(servo), 0)
                        except:
                            print("Wrong selection !!")
            elif mode == "c":
                while a.mode == a.CTR:
                    cls()
                    print("\n*** control mode ***\n")
                    a.printServos()
                    pwm = input("Select servo PWM (or q to go back): ")
                    if pwm == "q": break
                    else:
                        try:
                            a.setServo(int(pwm))
                        except:
                            print("Wrong selection !!")
    except KeyboardInterrupt:
        # Signal termination 
        logger.info("Keyboard interrupt. Terminate thread")
        a.close()
