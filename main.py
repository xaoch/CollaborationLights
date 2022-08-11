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

values=[0 for i in range(32)]

def showInMatrix(values,totalSpeech):
        column=0
        blank=(0,0,0)
        print(values)
        for rowValue in values:
                relativeTime = int((rowValue/totalSpeech)*8)
                if relativeTime<4:
                        color=(200,0,0)
                elif relativeTime<7:
                        color=(220,190,0)
                else:
                        color=(0,200,0)
                for i in range(0,8):
                        if i<relativeTime:
                                led.set(column,7-i,color)
                        else:
                                led.set(column,7-i,blank)
                column=column+1
        led.update()

if dev:
        totalSpeech=80
        speech=0
        showInMatrix(values,totalSpeech)
        Mic_tuning= Tuning(dev)
        while True:
                try:
                        if Mic_tuning.is_voice():
                                speech=speech+1
                                if totalSpeech<speech:
                                        totalSpeech=speech
                                doa=Mic_tuning.direction
                                print(doa)
                                column=int(round((doa/360)*32,0))
                                if(column==32):
                                        column=0
                                values[column]=values[column]+1
                                if column>0:
                                        values[column-1]=values[column-1]+0.5
                                if column==0:
                                        values[31]=values[31]+0.5
                                if column<31:
                                        values[column+1]=values[column+1]+0.5
                                if column==31:
                                        values[0]=values[0]+0.5
                                showInMatrix(values,totalSpeech)

                        time.sleep(0.1)
                except KeyboardInterrupt:
                        break



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
