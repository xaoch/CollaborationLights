# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import paho.mqtt.client as mqtt
import configparser
from bibliopixel import Matrix
from bibliopixel.layout import *
from bibliopixel.animation import MatrixCalibrationTest
from bibliopixel.drivers.PiWS281X import *
from BiblioPixelAnimations.matrix import MatrixRain
from bibliopixel.layout import Rotation

from tuning import Tuning
import usb.core
import usb.util
import time
import os
import sys

config = configparser.ConfigParser()
config.read(sys.argv[1])

ipMqttServer = config["DEFAULT"]["MQTTServerIp"]
portMqttServer = config["DEFAULT"]["MQTTServerPort"]
Mode = config["DEFAULT"]["Mode"]
numberStudents = 4

sensorName = "Microphone"
sensorStatus = "off"
dev=None
led=None
stopSignal= False

studentStatus = None
studentTime = None
studentRecentTime = None
studentSpeaking = None

def initStudents():
        global studentStatus
        global studentTime
        global studentRecentTime
        global studentSpeaking

        studentStatus = [None] * numberStudents
        studentTime = [None] * numberStudents
        studentRecentTime = [None] * numberStudents
        studentSpeaking = [None] * numberStudents

        for i in range(0,numberStudents):
                studentStatus[i]= "Middle"
                client.publish("collaborationLights/studentStatus", i + "/Middle")
                studentTime[i]= 600
                studentRecentTime[i]=300
                studentSpeaking[i]=0

def initilization():
        global dev
        global led
        driver=PiWS281X(8*32)
        coords=[]
        for i in range(8):
                before=i
                row=[]
                for j in range(32):
                        row.append(before)
                        if j%2==0:
                                before=before+15-2*i
                        else:
                                before=before+1+i*2
                coords.append(row)
        led = Matrix(driver,width=32,height=8,coord_map=coords)
        dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

def clear():
        for i in range(0,8):
                for j in range(0,32):
                        led.set(j,i,(0,0,0))

def drawShape(status,startingColumn,endingColumn):
        width = endingColumn - startingColumn
        height=8
        if status=="LowAlert":
                for column in range(startingColumn+3,startingColumn+5):
                        for row in range(3,5):
                                led.set(column,row,(200,200,0))
        elif status=="Low":
                for column in range(startingColumn+3,startingColumn+5):
                        for row in range(3,5):
                                led.set(column,row,(0,0,200))
        elif status=="Middle":
                for column in range(startingColumn+2,startingColumn+6):
                        for row in range(2,6):
                                led.set(column,row,(0,0,200))
        elif status=="High":
                for column in range(startingColumn+1,startingColumn+7):
                        for row in range(1,7):
                                led.set(column,row,(0,0,200))
        elif status=="HighAlert":
                for column in range(startingColumn+1,startingColumn+7):
                        for row in range(1,7):
                                led.set(column,row,(0,0,200))
                for row in range(1,7):
                        led.set(startingColumn+1,row,(200,200,0))
                        led.set(startingColumn+6,row,(200,200,0))
                for column in range(startingColumn+1,startingColumn+7):
                        led.set(column,1,(200,200,0))
                        led.set(column,6,(200,200,0))

def showStudentStatus():
        global studentStatus
        global studentTime
        global studentRecentTime
        for i in range(0,numberStudents):
                startingColumn = int(i*(32 / numberStudents))
                endingColumn = int((i+1)*(32 / numberStudents))
                drawShape(studentStatus[i],startingColumn,endingColumn)
        led.update()

def recomputePercentages():
        print(studentTime)
        totalSpeakingTime=0
        totalRecentSpeakingTime=0
        for i in range(1,numberStudents):
                studentTime[i]=studentTime[i]+studentSpeaking[i]
                totalSpeakingTime=totalSpeakingTime+studentTime[i]
                studentRecentTime[i]=studentRecentTime[i]+studentSpeaking[i]
                totalRecentSpeakingTime=totalRecentSpeakingTime+studentRecentTime[i]
                studentSpeaking[i]=0
        for i in range(1,numberStudents):
                percentage=studentTime[i]/totalSpeakingTime
                percentageRecent=studentRecentTime[i]/totalRecentSpeakingTime
                if percentage>0.75:
                        if studentStatus[i]!="HighAlert":
                                client.publish("collaborationLights/studentStatus", i + "/HighAlert")
                        studentStatus[i]="HighAlert"
                elif percentage>0.5:
                        if studentStatus[i]!="High":
                                client.publish("collaborationLights/studentStatus", i + "/High")
                        studentStatus[i]="High"
                elif percentage>0.25:
                        if studentStatus[i]!="Middle":
                                client.publish("collaborationLights/studentStatus", i + "/Middle")
                        studentStatus[i]="Middle"
                elif percentage>0.10:
                        if studentStatus[i]!="Low":
                                client.publish("collaborationLights/studentStatus", i + "/Low")
                        studentStatus[i]="Low"
                else:
                        if studentStatus[i]!="LowAlert":
                                client.publish("collaborationLights/studentStatus", i + "/LowAlert")
                        studentStatus[i]="LowAlert"

def update():
        client.publish("collaborationLights/heartbeat", sensorName + "," + sensorStatus)

def start_recording():
        global sensorStatus
        global stopSignal

        sensorStatus="recording"
        stopSignal=False
        update()

        totalTime = 0
        speech = 0
        silence = 0
        initStudents()

        showStudentStatus()
        Mic_tuning= Tuning(dev)
        totalTime = totalTime + 1
        while True:
                if totalTime % 300 == 0:
                    recomputePercentages()
                    clear()
                    showStudentStatus()
                if Mic_tuning.is_voice():
                    speech=speech+1
                    doa=Mic_tuning.direction
                    student=int(round((doa/360)*4,0))
                    if student == numberStudents:
                        student=0
                    studentSpeaking[student]=studentSpeaking[student]+1
                else:
                    silence=silence+1
                time.sleep(0.1)
                totalTime=totalTime+1
                if stopSignal:
                        break
                        sensorStatus="ready"

def stop_recording():
    global sensorStatus
    global stopSignal

    if (sensorStatus=="recording"):
        stopSignal=True
        print("Stoping")
    else:
        print("Not recording")
    update()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("collaborationLights/control")
    update()

def on_message(client, userdata, msg):
    global sensorStatus
    message = msg.payload.decode()
    messagePart = message.split(",")
    if (messagePart[0] in "start"):
        if (sensorStatus == "ready"):
            print("Starting")
            recordingId=messagePart[1]
            start_recording(recordingId)
        else:
            print("Not ready")
    elif (messagePart[0] in "stop"):
        if (sensorStatus== "recording"):
            stop_recording()
        else:
            print("Not recording")
    elif (messagePart[0] in "report_alive"):
        client.publish("collaborationLights/heartbeat", sensorName + "," + sensorStatus)
    elif (messagePart[0] in "rebootMicrophone"):
        print("Reboot Requested")
        if (sensorStatus=="recording"):
                stop_recording()
        os.system("sudo reboot")
    elif (messagePart[0] in "shutdownMicrophone"):
        print("Shutdown Requested")
        if (sensorStatus=="recording"):
            stop_recording()
        os.system("sudo halt")
    elif (messagePart[0] in "update"):
        print("Updating Software")
        os.system("git pull origin master")
        print("Software Updated")
        if (sensorStatus=="recording"):
            stop_recording()
        os.system("sudo reboot")


client = mqtt.Client()
sensorStatus="ready"
while(True):
    try:
        client.connect(ipMqttServer, int(portMqttServer), 60)
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_forever()
    except:
        time.sleep(1)



