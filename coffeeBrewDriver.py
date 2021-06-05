
import sys
sys.path.append("../")
import RPi.GPIO as GPIO
import time
import pigpio as pg
import threading
from threading import Thread

# This program utilizes the digital output value of a Passive Infared Sensor (PIR)
# to actuate the brewing of a coffee pot via two DC motors. The two DC motors are
# connected to a L293 H-bridge chip so that their directions can be reversed. The
# two DC motors are connected together with a wire thread that tightens when
# the motors are driven through a square-wave drive, allowing for the brewing button
# on the coffee machine to be activated.
#
# Technical documentaion of the motion controlled coffee brewer can be found in the
# README.md file of this repository.

GPIO.setmode(GPIO.BCM)
cannotDetectMotionLed = 15
canDetectMotionLed = 25
motionDetLed = 7
pirPin = 17
resetButton = 23
pulseWidth = .05
canDetectMotion = True

GPIO.setup(cannotDetectMotionLed, GPIO.OUT)
GPIO.setup(canDetectMotionLed, GPIO.OUT)
GPIO.setup(motionDetLed, GPIO.OUT)
GPIO.setup(pirPin,GPIO.IN)
GPIO.setup(resetButton, GPIO.IN)
GPIO.setup(4, GPIO.OUT)

# DC motor 1
GPIO.setup(5, GPIO.OUT) # Sends output signal to input port of H-bridge chip
GPIO.setup(6, GPIO.OUT)
GPIO.setup(4,GPIO.HIGH) # Enable port on H-bridge

# DC motor 2
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.HIGH) # Enable port on H-bridge

oldResetButtonValue = GPIO.input(resetButton)
newResetButtonValue = GPIO.input(resetButton)

# Function: Allows the motion sensor to detect movement after the reset
#           switch changes in state.
# Precodition: Function is started in a thread.
def resetButtonToggle():
   global resetButton
   global oldResetButtonValue
   global newResetButtonValue
   global canDetectMotion
   global canDetectMotionLed
   global cannotDetectMotionLed
   while True:
      newResetButtonValue = GPIO.input(resetButton)
      if (oldResetButtonValue != newResetButtonValue):
         oldResetButtonValue = newResetButtonValue
         canDetectMotion = True

      if (canDetectMotion == False):
         GPIO.output(cannotDetectMotionLed, 1)
         GPIO.output(canDetectMotionLed, 0)
      else:
         GPIO.output(cannotDetectMotionLed, 0)
         GPIO.output(canDetectMotionLed, 1)
      time.sleep(.2)

# Function: Actuates DC motors when motion is detected.
# Precondition: The function is started in a thread.
def motionDetection():
   global motionDetLed
   global pulseWidth
   global canDetectMotion

   while(canDetectMotion == True):
       # Detect motion until the sensor turns on
       if (GPIO.input(pirPin) == 1): # Motion detected
          canDetectMotion = False
          GPIO.output(motionDetLed, GPIO.HIGH)
          # Perform a square-wave drive with the DC motors
          for i in range(20):
             GPIO.output(5, 0) # Move motor 1 clockwise
             GPIO.output(6, 1)
             GPIO.output(16, 1) # Move motor 2 counter-clockwise
             GPIO.output(20, 0)
             time.sleep(pulseWidth) # Sleep for 50 miliseconds
             GPIO.output(5, 0) # Stop motor movement
             GPIO.output(6, 0)
             GPIO.output(16, 0)
             GPIO.output(20, 0)
             time.sleep(pulseWidth)
             GPIO.output(5, 0)
             GPIO.output(6, 1)
             GPIO.output(16, 1)
             GPIO.output(20, 0)
             time.sleep(pulseWidth)
             GPIO.output(5, 0)
             GPIO.output(6, 0)
             GPIO.output(16, 0)
             GPIO.output(20, 0)
             time.sleep(pulseWidth)
          # Reverse the motors in case of any wire thread entanglement
          for i in range(10):
             # Perform a square-wave drive with the DC motors
             GPIO.output(5, 1)
             GPIO.output(6, 0)
             GPIO.output(16, 0)
             GPIO.output(20, 1)
             time.sleep(pulseWidth)
             GPIO.output(5, 0)
             GPIO.output(6, 0)
             GPIO.output(16, 0)
             GPIO.output(20, 0)
             time.sleep(pulseWidth)
             GPIO.output(5, 1)
             GPIO.output(6, 0)
             GPIO.output(16, 0)
             GPIO.output(20, 1)
             time.sleep(pulseWidth)
             GPIO.output(5, 0)
             GPIO.output(6, 0)
             GPIO.output(16, 0)
             GPIO.output(20, 0)
             time.sleep(pulseWidth)


# Entry point to program
GPIO.output(cannotDetectMotionLed, 0)
GPIO.output(canDetectMotionLed, 1)

resetButtonThr = Thread(target=resetButtonToggle, args=(), daemon=True)
resetButtonThr.start()

motionDetectThr = Thread(target=motionDetection, args=(), daemon=True)
motionDetectThr.start()

while True:
   if (not motionDetectThr.is_alive()):
      motionDetectThr = Thread(target=motionDetection, args=(), daemon=True)
      motionDetectThr.start()
   time.sleep(1)

# Indicate to the user that the program is no longer running
GPIO.output(cannotDetectMotionLed, 0)
GPIO.output(canDetectMotionLed, 0)
