"""
Smart Alarm Clock
Version 1

Written by Declan Ross

The A Team
"""
 
#Import function and LCD initilization
import RPi.GPIO as GPIO
import time
import requests     #pip install requests
import pygame

from time import strftime                   #pip install stftime
from signal import signal, SIGTERM, SIGHUP, pause   #build in?
from rpi_lcd import LCD     #pip install rpi-lcd
lcd = LCD()
pygame.init()

#For if the LCD initilization fails
def safe_exit(signum, frame):
    exit(1)
try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)
except KeyboardInterrupt:
    pass


#Pin constants
snoozeButton = 17
phoneDetector = 19
trigUltrasound = 22
echoUltrasound = 27
obstaclePin = 13
soundPin = 23
GPIO.setmode(GPIO.BCM)  

#Setup code that is executed at the beginning of the code
def setup():
    #Global variables
    global isAlarmSet           #If user is awake or asleep, indicated by a button press and getting out of bed
    global lastLCDOutput1       #These 2 variables are used to only update the LCD
    global lastLCDOutput2       #when it has a different screen sent
    
    global nextWakeupHour       #Variable for the next hour alarm to be sounded, received from the server
    global nextWakeupMinute     #Variable for the next minute alarm to be sounded, recieving 
    global nextWakeupSecond
    global nextSleepHour        #Next bedtime hour recommendation recieved from the server
    global nextSleepMinute      #Next bedtime minute recommendation recieved from the server
    global nextSleepSecond
    
    global userSleepHour        #Current sleep hour indicated by the user pressing the sleep button
    global userSleepMinute      #Current sleep minute indicated by the user pressing the minute button
    global userSleepSecond
    
    global userSnoozing         #is user snoozing? alarm sounded and button pressed
    global alarmSounding        #is alarm sounding? alarm sounding
    global snoozeTimer          #How long the snooze lasts

    global url                  #Connection URL to User Interface
    global urlSnooze
    global urlGetsUp
    global AlarmSound           #The sound played to wake the user
    global sleepID
    
    isAlarmSet = False
    lastLCDOutput1 = "a"
    lastLCDOutput2 = "a"
    isSnoozeHeldDown = False
    
    nextWakeupHour = "12"
    nextWakeupMinute = "11"
    nextWakeupSecond = "00"
    nextSleepHour = "22"
    nextSleepMinute = "00"
    nextSleepSecond = "00"
    
    userSleepHour = ""
    userSleepMinute = ""
    userSleepSecond = ""
    
    userSnoozing = False
    alarmSounding = False
    snoozeTimer = 2
    userInBed = True

    url = 'https://iot-alarm-server.onrender.com/setalarm'
    urlSnooze = 'https://iot-alarm-server.onrender.com/stopalarm'
    urlGetsUp = 'https://iot-alarm-server.onrender.com/cancelalarm'
    AlarmSound = pygame.mixer.Sound("Alarm.wav")
    sleepID = ""
    
    #for the Snooze button
    GPIO.setup(snoozeButton, GPIO.IN)
    
    #for the phone detector
    GPIO.setup(phoneDetector, GPIO.IN)
    
    #Ultrasonic
    GPIO.setup(trigUltrasound, GPIO.OUT)
    GPIO.setup(echoUltrasound, GPIO.IN)
    GPIO.setup(obstaclePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    #Beeper
    GPIO.setup(soundPin, GPIO.OUT)

    currentIteration = 0
    lastDistanceReading = 0
    #Change this to change the distance in which the sadjaskldasd
    triggerDistance = 100
    userInBed = False

    phonePresent = True

def distance():
    GPIO.output(trigUltrasound, 0)
    time.sleep(0.000002)

    GPIO.output(trigUltrasound, 1)
    time.sleep(0.00001)
    GPIO.output(trigUltrasound, 0)

    while GPIO.input(echoUltrasound) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(echoUltrasound) == 1:
        a = 1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

def updateTimeAndDisplay():
    global isAlarmSet
    global nextWakeupHour
    global nextWakeupMinute
    global nextSleepHour
    global nextSleepMinute
    
    global alarmSounding
    global userSnoozing
    global phonePresent
    
    newLCDOutput1 = ""
    newLCDOutput2 = ""
    #This function will update the time and display periodically
    #Display will only be updated with a change in time
    #print(isAlarmSet)
    currentTime = strftime("%I:%M")
    if isAlarmSet and not userSnoozing and not alarmSounding and not phonePresent:
        suggestLCDUpdate((currentTime + " Asleep"), ("PUT PHONE DOWN")
    if isAlarmSet and not userSnoozing and not alarmSounding and phonePresent:
        suggestLCDUpdate((currentTime + " Asleep"), ("Rise at " + nextWakeupHour + ":" + nextWakeupMinute))
        return
        
    if not isAlarmSet and not userSnoozing and not alarmSounding:
        suggestLCDUpdate((currentTime + " Awake"), ("Rest at " + nextSleepHour + ":" + nextSleepMinute))
        return

    if isAlarmSet and alarmSounding:
        suggestLCDUpdate((currentTime), ("WAKE UP!"))
        return
    
    if isAlarmSet and userSnoozing and not alarmSounding:
        suggestLCDUpdate((currentTime + " Snoozing"), ("Rise at " + nextWakeupHour + ":" + nextWakeupMinute))
        return
     
def suggestLCDUpdate(line1, line2):
    global lastLCDOutput1
    global lastLCDOutput2
    newLCDOutput1 = (line1)
    newLCDOutput2 = (line2)
    if (newLCDOutput1 != lastLCDOutput1) or (newLCDOutput2 != lastLCDOutput2):
        lcd.text(newLCDOutput1, 1)
        lcd.text(newLCDOutput2, 2)
        lastLCDOutput1 = newLCDOutput1
        lastLCDOutput2 = newLCDOutput2
     
def onButtonClick():
    global isAlarmSet
    global userSleepHour
    global userSleepMinute
    global userSleepSecond
    
    global alarmSounding
    global userSnoozing

    
    if alarmSounding:
         #Activated when alarm goes off and the user is snoozing
         alarmSounding = False
         userSnoozing = True
         setNewAlarm()
    else:
        if sendSleepButtonPressedPOST:            
            #If Post request returned a time
            isAlarmSet = True
            setState(isAlarmSet)
            userSleepHour = strftime("%I")
            userSleepMinute = strftime("%M")
            userSleepSecond = strftime("%S")
            print(f'Sleep time: {userSleepHour}:{userSleepMinute}:{userSleepSecond}')
        else:
            #Post did not connect properly
            print("Failed, connection not working or no alarm is set")

def setWakeupTime(nWH, nWM, nWS):
    global nextWakeupHour
    global nextWakeupMinute
    global nextWakeupSecond

    nextWakeupHour = nWH
    nextWakeupMinute = nWM
    nextWakeupSecond = nWS

def sendSleepButtonPressedPOST():
    global url
    global sleepID
    try:
        date = strftime("%Y") + "-" + strftime("%m") + "-" + strftime("%d")
        time = strftime("%H") + ":" + strftime("%M") + ":" strftime("%S")
        formattedDateTime = date + " " + time
        output = {"timeTriggered": formattedDateTime}

        #Send post request
        rawRecievedData = requests.post(url, json = output)

        #Convert to text
        textReceivedData = rawRecievedData.text

        #Remove front and end of code
        formattedData = textReceivedData.replace("{", "")
        formattedData = formattedData.replace("}}", "")

        #Seperate label and data
        formattedData = formattedData.rsplit(",")

        #Status
        instanceData = formattedData[0].rsplit(":")
        Status = instanceData[1]

        #Message
        instanceData = formattedData[1].rsplit(":")
        Message = instanceData[1]

        #ID
        instanceData = formattedData[2].rsplit(":")
        ID = instanceData[2]

        sleepID = ID
        sleepID = sleepID.replace("\"", "")
        print(sleepID)

        #Wake up time
        instanceData = formattedData[6].rsplit(":")
        WakeUpTimeHour = instanceData[1].rsplit(" ")[1]
        WakeUpTimeMinute = instanceData[2]
        WakeUpTimeSecond = instanceData[3].replace("\"", "")

        #Optimal Wake up time
        instanceData = formattedData[7].rsplit(":")
        OptimalWakeUpTimeHour = instanceData[1].rsplit(" ")[1]
        OptimalWakeUpTimeMinute = instanceData[2]
        OptimalWakeUpTimeSecond = instanceData[3].replace("\"", "")

        setWakeupTime(OptimalWakeUpTimeHour, OptimalWakeupTimeMinute, OptimalWakeUpTimeSecond)
        return True
    except:
        return False
        
def pollButton():
    #Check state of snooze button
    if (GPIO.input(snoozeButton) != True):
        while ((GPIO.input(snoozeButton)) != True):
            continue
        onButtonClick()

def checkForAlarms():
    #This function will periodically compare the current time with the
    global nextWakeupHour
    global nextWakeupMinute
    global alarmSounding
    global userSnoozing
    
    currentHour = strftime("%I")
    currentMinute = strftime("%M")
    
    if (nextWakeupHour == currentHour):
        if (nextWakeupMinute == currentMinute):
            if (isAlarmSet):
                userSnoozing = False
                alarmSounding = True
                
def setNewAlarm():
    global nextWakeupHour
    global nextWakeupMinute
    global alarmSounding
    global userSnoozing
    global snoozeTimer
    
    currentHour = strftime("%I")
    currentMinute = strftime("%M")
    
    if ((int(currentMinute) + int(snoozeTimer)) >= 60):
        nextWakeupHour = currentHour + 1
        nextWakeupMinute = 0
    nextWakeupHour = currentHour
    nextWakeupMinute = int(currentMinute) + snoozeTimer
    nextWakeupMinute = str(nextWakeupMinute)
    
def userGetsOutOfBed():
    global alarmSounding
    global userSnoozing
    if userSnoozing or alarmSounding:
        alarmSounding = False
        userSnoozing = False
        GPIO.output(soundPin, GPIO.HIGH)
        #Post user gets up
        if sendUserGetsOutOfBedDuringAlarmPOST():
            print("User got up (POST SENT)")
        else:
            print("POST failed, connection not working")
        print("User is out of bed to start the day")

def sendUserGetsOutOfBedDuringAlarmPOST():
    global urlGetsUp
    global sleepID
    try:
        date = strftime("%Y") + "-" + strftime("%m") + "-" + strftime("%d")
        time = strftime("%H") + ":" + strftime("%M") + ":" strftime("%S")
        formattedDateTime = date + " " + time
        output = {"timeCancelled": formattedDateTime, "sleepScheduleId", sleepID}

        #Send post request
        rawRecievedData = requests.post(urlGetsUp, json = output)
        return True
    except:
        return False
    return

def sendUserPressesSnoozeButtonPOST():
    global urlGetsUp
    global sleepID
    try:
        date = strftime("%Y") + "-" + strftime("%m") + "-" + strftime("%d")
        time = strftime("%H") + ":" + strftime("%M") + ":" strftime("%S")
        formattedDateTime = date + " " + time
        output = {"timeStopped": formattedDateTime, "sleepScheduleId", sleepID}

        #Send post request
        rawRecievedData = requests.post(urlSnooze, json = output)
        return True
    except:
        return False
    return

def setState(state):
    #Set this to True for asleep and False for awake
    global isAlarmSet
    isAlarmSet = state
    return

def alarmSounding():
    global AlarmSound
    if alarmSounding:
        #START NOISE
        pygame.mixer.Sound.play(AlarmSound)
        return
    else:
        pygame.mixer.stop()
        #STOP NOISE
        return

def checkBedTime():
    #Post request to get just the bedtime
    return

def checkIfUserGotUp():
    global currentIteration
    global lastDistanceReading
    global triggerDistance
    global userInBed
    currentIteration = currentIteration + 1
    time.sleep(0.05)
    if currentIteration == 10:
        a = distance()
        currentIteration = 0
        if a < triggerDistance:
            if userInBed:
                userInBed = False
                userGetsOutOfBed()

        else:
            userInBed = True

def checkForPhone():
    global phonePresent

    if (0 == GPIO.input(obstaclePin)):
        if not phonePresent:
            phonePresent = True
            phonePutDown()
    else:
        if phonePresent:
            phonePresent = False

def phonePickedUp():
    if isAlarmSet:
        print("Phone Picked Up")
        GPIO.output(soundPin, GPIO.LOW)

def phonePutDown():
    if isAlarmSet:
        print("Phone put down")
    GPIO.output(soundPin, GPIO.HIGH)

def exitFunction():
    suggestLCDUpdate("Closing", "")
    time.sleep(2)
    GPIO.output(soundPin, GPIO.HIGH)
    GPIO.cleanup()
    return
    
            
#Execute setup code
setup()
atexit.register(exitFunction)

while True:
    updateTimeAndDisplay()
    checkForPhone()
    pollButton()
    checkIfUserGotUp()
    checkForAlarms()
    checkBedTime()
