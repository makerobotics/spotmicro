#!/usr/bin/env python

import os
import time
import logging
import json
ADAFRUIT = 1
if ADAFRUIT:
    import Adafruit_PCA9685 # for PC simulation

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
    MOV  = 5

    def __init__(self):
        if ADAFRUIT:
            self.pwm = Adafruit_PCA9685.PCA9685()
            self.pwm.set_pwm_freq(60)
        self.mode = self.IDLE
        self.actives = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.pwms = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.min_pwms = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.max_pwms = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.range_angles = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.swipe = 0
        self.swipe_sign = 1
        self.MAX_SWIPE = 200 # max swipe angle
        self.servos = self.readJSONConfig()

    def readJSONConfig(self):
        # Opening JSON file
        f = open('config.json',)
        # returns JSON object as a dictionary
        data = json.load(f)
        # Closing file
        f.close()

        self.min_pwms[0] = data["FL"]["knee"]["min_pwm"]
        self.max_pwms[0] = data["FL"]["knee"]["max_pwm"]
        self.range_angles[0] = data["FL"]["knee"]["angle_range"]
        self.min_pwms[1] = data["FL"]["hip"]["min_pwm"]
        self.max_pwms[1] = data["FL"]["hip"]["max_pwm"]
        self.range_angles[1] = data["FL"]["hip"]["angle_range"]
        self.min_pwms[2] = data["FL"]["rolling"]["min_pwm"]
        self.max_pwms[2] = data["FL"]["rolling"]["max_pwm"]
        self.range_angles[2] = data["FL"]["rolling"]["angle_range"]

        self.min_pwms[3] = data["RL"]["knee"]["min_pwm"]
        self.max_pwms[3] = data["RL"]["knee"]["max_pwm"]
        self.range_angles[3] = data["RL"]["knee"]["angle_range"]
        self.min_pwms[4] = data["RL"]["hip"]["min_pwm"]
        self.max_pwms[4] = data["RL"]["hip"]["max_pwm"]
        self.range_angles[4] = data["RL"]["hip"]["angle_range"]
        self.min_pwms[5] = data["RL"]["rolling"]["min_pwm"]
        self.max_pwms[5] = data["RL"]["rolling"]["max_pwm"]
        self.range_angles[5] = data["RL"]["rolling"]["angle_range"]

        self.min_pwms[6] = data["FR"]["knee"]["min_pwm"]
        self.max_pwms[6] = data["FR"]["knee"]["max_pwm"]
        self.range_angles[6] = data["FR"]["knee"]["angle_range"]
        self.min_pwms[7] = data["FR"]["hip"]["min_pwm"]
        self.max_pwms[7] = data["FR"]["hip"]["max_pwm"]
        self.range_angles[7] = data["FR"]["hip"]["angle_range"]
        self.min_pwms[8] = data["FR"]["rolling"]["min_pwm"]
        self.max_pwms[8] = data["FR"]["rolling"]["max_pwm"]
        self.range_angles[8] = data["FR"]["rolling"]["angle_range"]

        self.min_pwms[9] = data["RR"]["knee"]["min_pwm"]
        self.max_pwms[9] = data["RR"]["knee"]["max_pwm"]
        self.range_angles[9] = data["RR"]["knee"]["angle_range"]
        self.min_pwms[10] = data["RR"]["hip"]["min_pwm"]
        self.max_pwms[10] = data["RR"]["hip"]["max_pwm"]
        self.range_angles[10] = data["RR"]["hip"]["angle_range"]
        self.min_pwms[11] = data["RR"]["rolling"]["min_pwm"]
        self.max_pwms[11] = data["RR"]["rolling"]["max_pwm"]
        self.range_angles[11] = data["RR"]["rolling"]["angle_range"]

        return data

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

    def setServo(self, unit, pwm):
        index = 0
        for i in self.actives:
            if i == 1:
                if unit == 0:
                    # raw pwm values
                    if pwm<self.min_pwms[index]:
                        pwm = self.min_pwms[index]
                    elif pwm>self.max_pwms[index]:
                        pwm = self.max_pwms[index]
                    self.pwms[index] = pwm
                    self.pwm.set_pwm(index, 0, pwm)
                else:
                    # angle
                    p = int(pwm*(self.max_pwms[index]-self.min_pwms[index])/self.range_angles[index]+self.min_pwms[index])
                    if p<self.min_pwms[index]:
                        p = self.min_pwms[index]
                    elif p>self.max_pwms[index]:
                        p = self.max_pwms[index]
                    self.pwms[index] = p
                    self.pwm.set_pwm(index, 0, p)
            index += 1

    def selectServo(self, servo, active):
        self.actives[servo] = active

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

    def printServos(self):
        print("Actives: ")
        print(self.actives)
        print("PWMs: ")
        print(self.pwms)
        print("\nMin PWMs: ")
        print(self.min_pwms)
        print("Max PWMs: ")
        print(self.max_pwms)
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
            print("b: back (quit), s: select, r: reset, c: control raw, a: control angle, m: swipe")
            mode = input("Set your choice: ")
            a.setMode(mode)
            if mode == "b" or mode == "q":
                for i in range(11):
                    a.pwm.set_pwm(i, 0, 4096)
                a.close()
                break
            elif mode == "s":
                while a.mode == a.SET:
                    cls()
                    print("\n*** select mode ***\n")
                    a.printServos()
                    servo = input('Select servo channel to be set (or "b" to go back): ')
                    if servo == "b" or servo == "q": break
                    else:
                        try:
                            a.selectServo(int(servo), 1)
                            cls()
                            a.setMode("i")
                        except:
                            print("Wrong selection !!")
            elif mode == "r":
                while a.mode == a.RST:
                    cls()
                    print("\n*** reset mode ***\n")
                    a.printServos()
                    servo = input('Select servo channel to be reset (or "b" to go back): ')
                    if servo == "b" or servo == "q": break
                    else:
                        try:
                            a.selectServo(int(servo), 0)
                            a.setMode("i")
                        except:
                            print("Wrong selection !!") # todo: show to user
            elif mode == "c":
                while a.mode == a.CTR:
                    cls()
                    print("\n*** control mode (raw PWM) ***\n")
                    a.printServos()
                    pwm = input('Select servo PWM (or "b" to go back): ')
                    if pwm == "b" or pwm == "q": break
                    else:
                        try:
                            a.setServo(0, int(pwm))
                        except:
                            print("Wrong selection !!")
            elif mode == "a":
                pwm = 0
                while a.mode == a.CTR:
                    cls()
                    print("\n*** control mode (angle) ***\n")
                    a.printServos()
                    print("Last angle: "+str(pwm)+"°")
                    pwm = input('Select servo angle (or "b" to go back): ')
                    if pwm == "b" or pwm == "q": break
                    else:
                        try:
                            a.setServo(1, int(pwm))
                        except:
                            print("Wrong selection !!")
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
