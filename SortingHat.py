#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SortingHat.py : simulates a Harry Potter style sorting hat, but with good distribution across the 4 houses
# Intention: Used as a way to divvy a lot of people up into 4 teams with a good distribution across teams.
#    Note: the good distribution assertion here is based on the usage of many people using the device in
#          single powered on session. Everytime the device is reset, state is lost, breaking the distribution.
#          The original intent was to set the sample size to 3 x the number of houses (4) which will give 
#          repetition in the selections and make it appear like a distribution isn't being forced.
# Author: Flint Weiss
#


import sys
import RPi.GPIO as GPIO
import time
import collections, random

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message, text
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT
from max7219.led import device as led_device, matrix as led_matrix


GPIO.setmode(GPIO.BCM)

# Light up button:
# GPIO 5 is power
# GPIO 21 will read ground/LOW when button pressed
LIGHT_PIN = 5
BUTTON_PIN = 21
GPIO.setup(LIGHT_PIN,  GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# create matrix device
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=1, block_orientation=0, rotate=0)
print("Created LED device")

# this should be more parameterized and dynamic; currently hardcoded
# there are 4 houses to be selected into. We want selection to be randomized but we 
# also want a fairly even distribution along with the appearance of randomization.
# So the approach is to create a base list, with the 4 houses listed 3 times. 
# this will give us a normalized distribution across 12 selections which should be
# a good mix of seeming randomness across a lot of presses. If there are fewer 
# people expected to press the button at once (I'm expecting about 120 per session)
# you could reduce the series to 2x or 1x the number of houses. 

houseList = ["1", "2", "3", "4", "1", "2", "3", "4", "1", "2", "3", "4"]
pickList = []

#==========================================================================================================
# handles the buttonPush even which will pick a team and display the number on the display
def buttonPush(channel):

    # try to get rid of the duplicate button press events since bouncetime isn't really working
#    GPIO.remove_event_detect(BUTTON_PIN)
    print 'PUSHED!'
    
    # turn off the button light
    buttonLightOff()
	
    # start the "thinking activity"
    displayOff()
    time.sleep(0.5)
    displayOn()
    time.sleep(0.5)
    displayOff()
	
    # pick a house
    myPick = pickTeam()

    # print to display
    flashChar(myPick, 3) # add a little flash
    printChar(myPick)    # but then let it stay

    # signal ready for next press
    buttonLightOn()
#    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, buttonPush, bouncetime=2000)

#==========================================================================================================
# pickTeam
def pickTeam():
   global pickList
   
   if not pickList:
      # rebuild pickList by pre-randomizing the list
      print ("refresh pick list...")
      pickList = random.sample(houseList, k=len(houseList))
   
   # pick a house by removing one from list
   myPick = pickList.pop()
   print ("Pick:", myPick )
   return myPick
	
#==========================================================================================================
# helper function to display a character by flashing it on the display
def flashChar(character, numTimes):
   for i in range(numTimes):
      displayOff() # not sure if this is needed
      time.sleep(0.25)
      printChar(character)
      time.sleep(0.25)


	
#==========================================================================================================
# printChar - print a single character to the display
#    note: this doesn't actually ensure a single character but it probably should. So in name only. ;-> 
def printChar(character):
   #print(character)
   #show_message(device, character, fill="white", font=proportional(LCD_FONT) scroll_delay=0.04)
   # show_message(device, character, fill="white", font=proportional(LCD_FONT)) 
   with canvas(device) as draw:
      text(draw, (0,0), character, fill="white", font=proportional(LCD_FONT))
	
#==========================================================================================================
# scroll message to the display
def scrollMessage(msg):
    print(msg)
    show_message(device, msg, fill="white", font=proportional(LCD_FONT), scroll_delay=0.04)

#==========================================================================================================
# turn on the light in the button
def buttonLightOn():
    GPIO.output(LIGHT_PIN, GPIO.HIGH)

#==========================================================================================================
# turn off the light in the button
def buttonLightOff():
    GPIO.output(LIGHT_PIN, GPIO.LOW)

#==========================================================================================================
# this effectively turns on all the LEDs in the display by printing a big square.
#    not to be confused with turning on the display to enable printing.
def displayOn():
    #print("display on")
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="white")


#==========================================================================================================
def displayOff():
    #print("display off")
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="black", fill="black")

#----------------------------------------------------------------------------------------------------------
# main execution section

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, buttonPush, bouncetime=2000)

scrollMessage("Sorting Hat")

displayOn()
buttonLightOn()
time.sleep(0.5)
displayOff()
buttonLightOff()
time.sleep(0.5)


#hang around, waiting for buttn presses
while(True):
   time.sleep(0.25) 

# Cleanup on exit. Only for development b/c real usage will just power down the pi
GPIO.cleanup()
