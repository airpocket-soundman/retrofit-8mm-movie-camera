import cv2
import os
import time
import RPi.GPIO as GPIO
import sys

imgNum = 0
shootNum = 0
shutterDelay = 0.000 #sec
shutterPin = 16
repeatNum =3
WIDTH = 320
HEIGHT = 240
timeLog = []
imgMem = [3]

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
#capture.set(cv2.CAP_PROP_GAIN, 2)
#capture.set(cv2.CAP_PROP_EXPOSURE, -5)

os.system('v4l2-ctl -d /dev/video0 -c brightness=50')                   #min=0 max=100 default=50
os.system('v4l2-ctl -d /dev/video0 -c auto_exposure=1')                 #0:auto 1:manual
os.system('v4l2-ctl -d /dev/video0 -c exposure_dynamic_framerate=0')    #0:False 1:True default=0     
os.system('v4l2-ctl -d /dev/video0 -c exposure_time_absolute=50')        #min=1 max=10000 default=1000
os.system('v4l2-ctl -d /dev/video0 -c iso_sensitivity_auto=1')          #0:manual 1:auto
os.system('v4l2-ctl -d /dev/video0 -c iso_sensitivity=4')               #0:0 1:10000 2:20000 3:40000 4:80000
os.system('v4l2-ctl -d /dev/video0 -c rotate=180')

for i in range(5):
    _, _ = capture.read()


def oneShot(gpio_pin):
    startTime = time.time()
    global imgNum,capture,timeLog,shootNum,imgMem
    #for i in range(1):
    #    _,_ = capture.read()
    for i in range(repeatNum):
        #time.sleep(shutterDelay)
        ret, imgMem[i] = capture.read()
        #timeLog.append(int((time.time()-startTime)*10000)/10)
        #ret, frame = capture.read()
        #print(ret)
        #frame=cv2.rotate(frame, cv2.ROTATE_180)
        #imgMem.append(frame)
    #print(timeLog)
    if shootNum >= 0:
        for i in range(repeatNum):
            cv2.imwrite(str(shootNum) + "-" + str(i) + ".jpg",imgMem[i])
    timeLog = []
    imgMem = []
    imgMem=[3]
    shootNum += 1


GPIO.setmode(GPIO.BCM)
GPIO.setup(shutterPin, GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(shutterPin,GPIO.RISING, callback = oneShot, bouncetime = 5)




if capture.isOpened() is False:
    print("can not open video0")

#oneShot(16)
print("ready")

while True:
    time.sleep(1)
    print(GPIO.input(shutterPin))
capture.release()

