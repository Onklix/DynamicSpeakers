######################################
# Author: Jonas Strand Gjersvik      #
# For: Automation Group 9            #
# Project Name:                      #
#   Dynamic Room Correction for      #
#          Home Speakers             #
# Last updated 23/05/2024            #
######################################


from time import sleep
import numpy as np
import math
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)#step pin for left motor
GPIO.setup(13, GPIO.OUT)#direction pin for left motor
GPIO.setup(15, GPIO.OUT)#direction pin for right motor
GPIO.setup(16, GPIO.OUT)#step pin for right motor

#coordinate class for storing positions and calculating angles and distances necessary to pass correct arguments to rotate_stepper
class coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.Rx = 1.235
        self.Lx = -1.235

    def getcoords(self):
        return f"( {self.x} , {self.y} )" #simply returns the coordinate in a visually pleasing manner
    
    def getdist(self, other):
        #calculates the distance between two points using the pythogorean theorem
        distance = np.sqrt(self.y**2 + (self.x-other.x)**2)
        return distance
        
    def getangle(self, other):
        sin_theta = self.y/self.getdist(other)
        theta = np.arcsin(sin_theta)
        theta = math.degrees(theta)
        if self.x > self.Rx and other.x == 1.235:
            return (180-theta)
        elif self.x < self.Lx and other.x == -1.235:
            return (180-theta)
        else:
            return theta

#function that rotates the speakers through GPIO
def rotate_stepper(speaker, steps):
    #set speaker pins
    if speaker == 'left':
        dir = 13
        step = 11
        if steps > 0:
            direction = 'CW'
        else:
            direction = 'CCW'
    else:
        dir = 16
        step = 15
        if steps < 0:
            direction = 'CW'
        else:
            direction = 'CCW'
    if direction == 'CW':
        GPIO.output(dir, GPIO.HIGH)
    else:
        GPIO.output(dir, GPIO.LOW)
    for i in range(abs(steps)):
        GPIO.output(step, GPIO.HIGH)
        sleep(0.005)
        GPIO.output(step, GPIO.LOW)
        sleep(0.005)
    print(f"rotated {speaker}")


#initiating values for the speaker position
sR_angle_old = 90
sL_angle_old = 90
sR_steps = 0
sL_steps = 0
origo = coordinate(0,0)
Rspeaker = coordinate(1.235,0)
Lspeaker = coordinate(-1.235,0)
motorsteps = 200
degree_per_step = 360/motorsteps

#continuous loop that takes an input position and rotates the speakers towards it
while True:
    xin = input("x: ")
    yin = input("y: ")
    listening_pos = coordinate(int(xin),int(yin))
    print("dist R/L")
    print(listening_pos.getdist(Rspeaker))
    print(listening_pos.getdist(Lspeaker))
    print("angle R/L")
    print(listening_pos.getangle(Rspeaker))
    print(listening_pos.getangle(Lspeaker))
    print(listening_pos.getcoords())
    print(f"Distance from right speaker: {listening_pos.getdist(Rspeaker)} meters")
    print(f"Distance from left speaker:  {listening_pos.getdist(Lspeaker)} meters")

    sR_angle_new = listening_pos.getangle(Rspeaker)
    sL_angle_new = listening_pos.getangle(Lspeaker)
    
    print(f"New angle R: {sR_angle_new}. New angle L {sL_angle_new}.")
    print(f"Change in angle for speaker R: {sR_angle_old-sR_angle_new}")
    print(f"Change in angle for speaker L: {sL_angle_old-sL_angle_new}")
    sR_steps = (sR_angle_old - sR_angle_new)/degree_per_step
    sL_steps = (sL_angle_old - sL_angle_new)/degree_per_step
    print(sR_steps, sL_steps)

    rotate_stepper('right', sR_steps)
    rotate_stepper('left', sL_steps)

    sR_angle_old = sR_angle_old - (degree_per_step * sR_steps)
    sL_angle_old = sL_angle_old - (degree_per_step * sL_steps)

    quitter = input("Quit? Y/n: ")
    if quitter.upper() == "Y":
        GPIO.cleanup()
        break
