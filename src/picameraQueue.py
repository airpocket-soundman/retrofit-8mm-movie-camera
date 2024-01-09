import cv2
import os
import time
import datetime
import RPi.GPIO as GPIO
import sys
import numpy as np

sensor              = 0     #0:IMX219   1:OV5647
camera              = 0
timingPin           = 16
shutterDelay        = 0.00  #sec
imgNum              = 0
stillNum            = 0
fileNum             = 1
recFlag             = False
size                = 3     #0:320x240      1:640x480       2:800x600   3:1280x720
setFPS              = 0     #0:16   1:24    2:32    3:48    4:64    5:90
recFPS              = 16
maxSec              = 30
maxFrame            = recFPS * maxSec
timeLog             = []
imgMem              = []
recStopThreshold    = 0.1   #sec
maxFrame            = 64
filePath = "/home/zero2/Workspace/"


def timingPinWasPushed(gpio_pin):
    global timeLog, switch
    if len(timeLog) < maxFrame:
        timeLog.append(time.time())
        imgRec()
    #if len(timeLog) > 1:
    #    print(str(timeLog(-1) - timeLog(-2)))
    #print("pushed")
    #rec60Frame()

GPIO.setmode(GPIO.BCM)
GPIO.setup(timingPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(timingPin, GPIO.RISING, callback = timingPinWasPushed, bouncetime = 5)

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

#os.system('v4l2-ctl -d /dev/video0 -c h264_profile=4')
#os.system("v4l2-ctl -d /dev/video0 -p 90)


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
    os.system('v4l2-ctl -d /dev/video0 -c brightness=60')
    os.system('v4l2-ctl -d /dev/video0 -c contrast=0')                     #min=-100 max=100 default=0
    os.system('v4l2-ctl -d /dev/video0 -c saturation=0')                  #same
    os.system('v4l2-ctl -d /dev/video0 -c auto_exposure=1')                 #0:Auto mode 1:Manual mode
    os.system('v4l2-ctl -d /dev/video0 -c exposure_time_absolute=50')       #min=1 max=10000 default=1000
    os.system('v4l2-ctl -d /dev/video0 -c exposure_dynamic_framerate=0')    #False=0 True=1 default=0
    os.system('v4l2-ctl -d /dev/video0 -c red_balance=1000')                # min=1 max=7999 step=1 default=1000
    os.system('v4l2-ctl -d /dev/video0 -c blue_balance=1000')
#    os.system('v4l2-ctl -d /dev/video0 -c auto_exposure_bias=12')           #0: -4000   ....    12:0    ....    24:4000
    os.system('v4l2-ctl -d /dev/video0 -c white_balance_auto_preset=1')     #0: Manual	1: Auto	2: Incandescent 3: Fluorescent 4: Fluorescent H
    				                                                        #5: Horizon	6: Daylight 7: Flash    8: Cloudy   9: Shade    10: Greyworld
#    os.system('v4l2-ctl -d /dev/video0 -c iso_sensitivity_auto=1')          #0: Manual	1: Auto
#    os.system('v4l2-ctl -d /dev/video0 -c iso_sensitivity=0')               #0: 0   1: 100000   2: 200000   3: 400000   4: 800000
    os.system('v4l2-ctl -d /dev/video0 -c rotate=180')

else:
    print("camera type unknown")



def movieSave():
    global imgNum,timeLog,codec,imgMem, stillNum
    print(imgNum)
    print(len(timeLog))
    print(len(imgMem))
    if len(timeLog) > 1:
        resultFPS =1/((timeLog[-1] - timeLog[0])/(len(timeLog)-1))
    else:
        cv2.imwrite(str(stillNum) + "sample.jpg",imgMem[0])
        resultFPS = "ND"
        stillNum += 1
    today = datetime.datetime.now()
    fileName = filePath + today.strftime("%Y%m%d_%H%M%S") + ".mp4"
    video = cv2.VideoWriter(fileName, codec, recFPS, (WIDTH, HEIGHT))

    if not video.isOpened():
        print("can't be opened")
        sys.exit()

    startTime = time.time()
    for i in range(0, imgNum):
        print(str(i) + "/" + str(imgNum))
        cv2.imwrite(str(i) + ".jpg",imgMem[i])
        img = imgMem[i]
        video.write(img)
    print(time.time() - startTime)
    video.release()
    print("result FPS = " + str(resultFPS))
    imgNum = 0
    imgMem.clear()
    timeLog.clear()

   
def imgRec():
    global capture, imgNum, frame, imgMem
    time.sleep(shutterDelay)
    ret, frame = capture.read()
#    _, _ =capture.read()    
    if ret is False:
        raise IOError
    imgMem.append(frame)
    imgNum += 1 

timeStart = time.time()

if capture.isOpened() is False:
    raise IOError

print("ok")


while(True):

    time.sleep(1.0)  
    if imgNum >0:  
        if time.time() - timeLog[-1] >= recStopThreshold:
            movieSave()
            print("time over")
            #for i in range(4):
            #    _, _ = capture.read()

capture.release()
cv2.destroyAllWindows()   
