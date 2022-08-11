# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

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

totalTime=0
speech=0
silence=0
numberStudents = 4

studentStatus = [None]*numberStudents

studentTime = [None]*numberStudents

studentRecentTime =[None]*numberStudents

studentPercentage = [None]*numberStudents

def initStudents():
        global studentStatus
        global studentTime
        global studentRecentTime
        global studentPercentage

        for i in range(0,numberStudents):
                studentStatus[i]= "LowAlert"
                studentTime[i]= 600
                studentPercentage[i]=100/numberStudents
                studentRecentTime[i]=300

initStudents()


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

led=Matrix(driver,width=32,height=8,coord_map=coords)
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

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
                for column in range(startingColumn+1,endingColumn+7):
                        for row in range(1,7):
                                led.set(column,row,(0,0,200))
                for row in range(1,7):
                        led.set(startingColumn+1,row,(200,200,0))
                        led.set(startingColumn+6,row,(200,200,0))
                for column in range(startingColumn+1,endingColumn+7):
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
        1+1

if dev:
        showStudentStatus()
        Mic_tuning= Tuning(dev)
        totalTime = totalTime + 1
        while True:
                if totalTime % 30 == 0:
                        recomputePercentages()
                        showStudentStatus()
                try:
                        if Mic_tuning.is_voice():
                                speech=speech+1
                                doa=Mic_tuning.direction
                                student=int(round((doa/360)*4,0))
                                if student == numberStudents:
                                        student=0
                                studentTime[student]=studentTime[student]+1
                                studentRecentTime[student]=studentRecentTime[student]+1
                        else:
                                silence=silence+1
                        time.sleep(0.1)
                        totalTime=totalTime+1
                except KeyboardInterrupt:
                        break




