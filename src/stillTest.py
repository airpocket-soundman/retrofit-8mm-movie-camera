import cv2

WIDTH = 320
HEIGHT = 240

capture = cv2.VideoCapture(0,cv2.CAP_V4L2)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

if capture.isOpened() is False:
    print("can not open video0")


ret, frame = capture.read()
print(ret)

if ret is False:
    print("can not capture")

cv2.imwrite("test.jpg", frame)

capture.release()
