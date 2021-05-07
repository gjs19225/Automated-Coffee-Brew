
import sys
sys.path.append("../")
import RPi.GPIO as GPIO
import time
import pigpio as pg
import threading
from threading import Thread

# This program utilizes the digital output value of a Passive Infared Sensor (PIR)
# to actuate the brewing of a coffee pot via two DC motors. The duration of the
# program is finite for a fixed interval of time.

GPIO.setmode(GPIO.BCM)
cannotDetectMotionLed = 15
canDetectMotionLed = 25
motionDetLed = 7
pirPin = 17
resetButton = 23
pulseWidth = .05
canDetectMotion = True
count = 0
GPIO.setup(cannotDetectMotionLed, GPIO.OUT)
GPIO.setup(canDetectMotionLed, GPIO.OUT)
GPIO.setup(motionDetLed, GPIO.OUT)
GPIO.setup(pirPin,GPIO.IN)
GPIO.setup(resetButton, GPIO.IN)
GPIO.setup(4, GPIO.OUT)  # DC motors
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
oldResetButtonValue = GPIO.input(resetButton)
newResetButtonValue = GPIO.input(resetButton)
canProgramRun = True

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
   global count
   global canProgramRun

   while(canDetectMotion == True and canProgramRun == True):
       # Detect motion until the sensor turns on
       if (GPIO.input(pirPin) == 1): # Motion detected
          print("Motion detected")
          canDetectMotion = False
          GPIO.output(motionDetLed, GPIO.HIGH)
          for i in range(20):
             GPIO.output(5,GPIO.LOW) # Perform a wave drive with the DC motors
             GPIO.output(6,GPIO.HIGH)
             GPIO.output(4,GPIO.HIGH)
             time.sleep(pulseWidth)
             GPIO.output(5,GPIO.HIGH)
             GPIO.output(6,GPIO.HIGH)
             GPIO.output(4,GPIO.HIGH)
             time.sleep(pulseWidth)
             GPIO.output(5,GPIO.HIGH)
             GPIO.output(6,GPIO.LOW)
             GPIO.output(4, GPIO.HIGH)
             time.sleep(pulseWidth)
             GPIO.output(5,GPIO.LOW)
             GPIO.output(6,GPIO.LOW)
             GPIO.output(4, GPIO.HIGH)
             time.sleep(pulseWidth)
             GPIO.output(16, GPIO.HIGH)
             GPIO.output(20, GPIO.HIGH)
             GPIO.output(21, GPIO.HIGH)
             time.sleep(pulseWidth)
             GPIO.output(16, GPIO.HIGH)
             GPIO.output(20, GPIO.HIGH)
             GPIO.output(21, GPIO.HIGH)
             time.sleep(pulseWidth)
             GPIO.output(16,GPIO.HIGH)
             GPIO.output(20, GPIO.LOW)
             GPIO.output(21, GPIO.HIGH)
             time.sleep(pulseWidth)
             GPIO.output(16, GPIO.LOW)
             GPIO.output(20, GPIO.LOW)
             GPIO.output(21,GPIO.HIGH)
             time.sleep(pulseWidth)
             print(i)

# Function: Terminates the program within a set period of time.
# Precondition: Function is started in a thread.
# Postcondition: Program terminates approcimately in a minute and ten seconds.
#
# Used as a safety net in case the auto startup script results in an
# infinte loop.
def countTracker():
   global count
   global canProgramRun

   while True:
      print("count: ", count)
      if (count > 70):
         canProgramRun = False
      time.sleep(2)

# Entry point to program
GPIO.output(cannotDetectMotionLed, 0)
GPIO.output(canDetectMotionLed, 1)

countTrackerThr = Thread(target=countTracker, args=(), daemon=True)
countTrackerThr.start()

resetButtonThr = Thread(target=resetButtonToggle, args=(), daemon=True)
resetButtonThr.start()

motionDetectThr = Thread(target=motionDetection, args=(), daemon=True)
motionDetectThr.start()

isMotionLoopStarted = False
while canProgramRun == True:
   count += 1
   if (not motionDetectThr.is_alive()):
      motionDetectThr = Thread(target=motionDetection, args=(), daemon=True)
      motionDetectThr.start()
   print("count: ", count)
   time.sleep(1)

# Indicate to the user that the program is no longer running
GPIO.output(cannotDetectMotionLed, 0)
GPIO.output(canDetectMotionLed, 0)
