# Copyright (c) 2022 yasuhiro yamashita
# Released under the MIT license.
# see http://open source.org/licenses/MIT
#
# ============================
# spring loaded digital camera
#
# controler program ver.1.1.0
# ============================




import cv2
import os
import time
import datetime
import RPi.GPIO as GPIO
import sys
import numpy as np

timingPin           = 12 
ledRPin             = 20
ledGPin             = 26
shutdownPin         = 16
dip1Pin             = 2
dip2Pin             = 3
dip3Pin             = 4
dip4Pin             = 14
dip5Pin             = 15
dip6Pin             = 0

sensor              = 0     #0:IMX219   1:OV5647
camera              = 0
shutterDelay        = 0.00  #sec
stillNum            = 1
filmNum             = 1
cutNum              = 1
frameNum            = 0
recFlag             = False
size                = 3     #0:320x240      1:640x480       2:800x600   3:1280x720
setFPS              = 0     #0:16   1:24    2:32    3:48    4:64    5:90
timeLog             = []
imgMem              = []
recStopThreshold    = 0.1   #sec  *detect rec button release
maxFrame_color      = 160
maxFrame_mono       = 160
maxFrame            = maxFrame_color    #frame
filmLength          = 1600   
filmRemainLength    = filmLength
recFPS              = 16
jpgOutput           = False
filePath = "/home/zero2/Workspace/"

color_effects       = 0

def timingPinWasPushed(gpio_pin):
    global timeLog, switch, flimLength, frameNum
    if (len(imgMem) <= maxFrame and frameNum <= filmLength):
#        print(len(imgMem))
        timeLog.append(time.time())
        frameNum += 1
        imgRec()
    elif frameNum > filmLength:
        GPIO.output(ledRPin, True)
        GPIO.output(ledGPin, True)

def shutdownPinWasPushed(gpio_pin):
    global ledGPin, ledRPin, dip1Pin, filmNum, cutNum, frameNum, maxFrame
    print("DIP 1 = " + str(GPIO.input(dip1Pin)))

    if GPIO.input(dip1Pin) == 0:
        frameNum = 0
        filmNum += 1
        cutNum = 1
        color_effects = GPIO.input(dip5Pin)
        os.system('v4l2-ctl -d /dev/video0 -c color_effects=' + str(color_effects))
        if color_effects == 1:
            maxFrame = maxFrame_mono
            print('Black & White film set')
        elif color_effects == 0:
            maxFrame = maxFrame_color
            print('Color film set')

        if GPIO.input(dip4Pin) == 1:
            exposure_time_absolute = 30
        elif GPIO.input(dip4Pin) == 0:
            exposure_time_absolute = 100
        os.system('v4l2-ctl -d /dev/video0 -c exposure_time_absolute=' + str(exposure_time_absolute))
        print('exposure_time_absolute set to ' + str(exposure_time_absolute))


GPIO.setmode(GPIO.BCM)
GPIO.setup(timingPin,   GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(shutdownPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(dip1Pin,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(dip2Pin,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(dip3Pin,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(dip4Pin,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(dip5Pin,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(ledRPin,     GPIO.OUT)
GPIO.setup(ledGPin,     GPIO.OUT)

GPIO.add_event_detect(timingPin, GPIO.RISING, callback = timingPinWasPushed, bouncetime = 5)
GPIO.add_event_detect(shutdownPin, GPIO.FALLING, callback = shutdownPinWasPushed, bouncetime = 100)
GPIO.output(ledRPin, False)
GPIO.output(ledGPin, False)

color_effects = GPIO.input(dip5Pin)
if color_effects == 1:
    print("Black & White film set")
elif color_effects == 0:
    print("Color film set")

if GPIO.input(dip4Pin) == 1:
    exposure_time_absolute = 30
elif GPIO.input(dip4Pin) == 0:
    exposure_time_absolute = 100
print("exposure_time_absolute set to " + str(exposure_time_absolute))

#解像度パラメータ
if size == 0:
    WIDTH  = 320   #320/640/800/1024/1280/1920
    HEIGHT = 240   #240/480/600/ 576/ 720/1080
elif size == 1:
    WIDTH  = 640
    HEIGHT = 480
elif size == 2:
    WIDTH  = 800
    HEIGHT = 600
elif size == 3:
    WIDTH  = 1280
    HEIGHT = 720
else:
    WIDTH  = 640
    HEIGHT = 480

if   setFPS == 0:
    targetFPS   = 16
elif setFPS == 1:
    targetFPS   = 24
elif setFPS == 2:
    targetFPS   = 32
elif setFPS == 3:
    targetFPS   = 48
elif setFPS == 4:
    targetFPS   = 64
elif setFPS == 5:
    targetFPS   = 90
else:
    targetFPS   = 16

cycle = 1/targetFPS

#カメラ入力インスタンス定義
capture = cv2.VideoCapture(camera)
codec = cv2.VideoWriter_fourcc(*'mp4v')

if capture.isOpened() is False:
  raise IOError

#解像度変更
capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
#capture.set(cv2.CAP_PROP_EXPOSURE,-3)               #0,-1:640ms -2:320ms -3:160ms -4:80ms -5:40ms -6:20ms -7:10ms 
                                                    #-8:5ms -9:2.5ms -10:1.25ms -11:650us -12:312:us -13:150us
#capture.set(cv2.CAP_PROP_GAIN, 4)
capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
capture.set(cv2.CAP_PROP_FPS,90)


#==== for raspi spy camera ov5647
if sensor == 1:
    os.system('v4l2-ctl -d /dev/video0 -c brightness=100')               #0-100
    os.system('v4l2-ctl -d /dev/video0 -c contrast=30')                  #-100-100
    os.system('v4l2-ctl -d /dev/video0 -c saturation=0')                #-100-100    
    os.system('v4l2-ctl -d /dev/video0 -c red_balance=900')            #1-7999
    os.system('v4l2-ctl -d /dev/video0 -c blue_balance=1000')           #1-7999
    os.system('v4l2-ctl -d /dev/video0 -c sharpness=0')                 #0-100
    os.system('v4l2-ctl -d /dev/video0 -c color_effects=0')             #0:None 1:Mono 2:Sepia 3:Negative 14:Antique 15:set cb/cr
    os.system('v4l2-ctl -d /dev/video0 -c rotate=180')                  #0-360
    os.system('v4l2-ctl -d /dev/video0 -c video_bitrate_mode=0')        #0:variable 1:Constant
    os.system('v4l2-ctl -d /dev/video0 -c video_bitrate=10000000')      #25000-25000000 2500step
    os.system('v4l2-ctl -d /dev/video0 -c auto_exposure=1')             #0:auto 1:manual 
    os.system('v4l2-ctl -d /dev/video0 -c exposure_time_absolute=5000') #1-10000
    os.system('v4l2-ctl -d /dev/video0 -c auto_exposure_bias=12')        #0-24
    os.system('v4l2-ctl -d /dev/video0 -c white_balance_auto_preset=0') #0:manual 1:auto 2:Incandescent 3:fluorescent 4:fluorescent m 5:horizon
                                                                        #6:daylight 7:flash 8:cloudy 9:shade 10:grayworld
    os.system('v4l2-ctl -d /dev/video0 -c iso_sensitivity_auto=1')      #0:manual 1:auto
    os.system('v4l2-ctl -d /dev/video0 -c iso_sensitivity=4')           #0:0 1:100000 2:200000 3:400000 4:800000


#==== for raspi camera v2 imx219
elif sensor == 0:
    print("IMX219 selected")
    os.system('v4l2-ctl -d /dev/video0 -c brightness=50')
    os.system('v4l2-ctl -d /dev/video0 -c contrast=0')                     #min=-100 max=100 default=0
    os.system('v4l2-ctl -d /dev/video0 -c saturation=10')                  #same
    os.system('v4l2-ctl -d /dev/video0 -c auto_exposure=1')                 #0:Auto mode 1:Manual mode
    os.system('v4l2-ctl -d /dev/video0 -c exposure_time_absolute=' + str(exposure_time_absolute))       #min=1 max=10000 default=1000
    os.system('v4l2-ctl -d /dev/video0 -c exposure_dynamic_framerate=0')    #False=0 True=1 default=0
    os.system('v4l2-ctl -d /dev/video0 -c red_balance=1200')                # min=1 max=7999 step=1 default=1000
    os.system('v4l2-ctl -d /dev/video0 -c blue_balance=900')
#    os.system('v4l2-ctl -d /dev/video0 -c auto_exposure_bias=12')           #0: -4000   ....    12:0    ....    24:4000
    os.system('v4l2-ctl -d /dev/video0 -c white_balance_auto_preset=6')     #0: Manual	1: Auto	2: Incandescent 3: Fluorescent 4: Fluorescent H
    				                                                        #5: Horizon	6: Daylight 7: Flash    8: Cloudy   9: Shade    10: Greyworld
#    os.system('v4l2-ctl -d /dev/video0 -c iso_sensitivity_auto=1')          #0: Manual	1: Auto
#    os.system('v4l2-ctl -d /dev/video0 -c iso_sensitivity=0')               #0: 0   1: 100000   2: 200000   3: 400000   4: 800000
    os.system('v4l2-ctl -d /dev/video0 -c color_effects=' + str(color_effects))
    os.system('v4l2-ctl -d /dev/video0 -c rotate=180')


else:
    print("camera type unknown")



def movieSave():
    global timeLog, codec, imgMem, stillNum, cutNum, capture, ledGPin, ledRPin
    GPIO.output(ledGPin, False)
    GPIO.output(ledRPin, True)
    ret, frame = capture.read()
    print(len(timeLog))
    print(len(imgMem))
    if len(timeLog) > 1:
        resultFPS =1/((timeLog[-1] - timeLog[0])/(len(timeLog)-1))
    else:

        cv2.imwrite(str(stillNum) + "sample.jpg", frame)
        resultFPS = "ND"
        stillNum += 1
    today = datetime.datetime.now()
    fileName = filePath + str(filmNum) + "_" + str(cutNum) + ".mp4"
    video = cv2.VideoWriter(fileName, codec, recFPS, (WIDTH, HEIGHT))

    if not video.isOpened():
        print("can't be opened")
        sys.exit()

    startTime = time.time()
    for i in range(1, len(imgMem)):
        GPIO.output(ledRPin, False)
        print(str(i) + "/" + str(len(imgMem)))
        if jpgOutput == True:
            cv2.imwrite(str(i) + ".jpg",imgMem[i])
        img = imgMem[i]
        GPIO.output(ledRPin, True)
        video.write(img)
    video.write(frame)
    print(time.time() - startTime)
    video.release()
    print("result FPS = " + str(resultFPS))
    imgMem.clear()
    timeLog.clear()

   
def imgRec():
    global capture, frame, imgMem, ledRPin, ledGPin
    GPIO.output(ledGPin, False)
    GPIO.output(ledRPin, False)
    time.sleep(shutterDelay)
    ret, frame = capture.read()
    if ret is False:
        raise IOError
    imgMem.append(frame)
    GPIO.output(ledGPin, True)


timeStart = time.time()

if capture.isOpened() is False:
    raise IOError

print("ok")


while(True):
    GPIO.output(ledGPin, True)
    GPIO.output(ledRPin, False)
    time.sleep(1.0)  
    print(GPIO.input(timingPin))

    if len(imgMem) >0:
        if time.time() - timeLog[-1] >= recStopThreshold:
            movieSave()
            cutNum += 1
            print(str(filmNum) + "_" + str(cutNum))
            print("time over")

capture.release()
cv2.destroyAllWindows()   
