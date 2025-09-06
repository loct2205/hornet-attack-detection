from ultralytics import YOLO
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import os
import glob
import time
import math
#from picamera2.encoders import H264Encoder, Quality
from picamera2 import Picamera2, Preview
from threading import Thread, Event
import threading
def saveCapture():
    global i
    global num_object
    global average_density
    while True:
        print("SaveCapture is running")
        fileName = '/home/pi4/my_project/Image/img{:03d}.jpg'.format(i)
        start_time = time.time()
        if num_object > 0:
            print("fast mode")
            density = 0
            im_num = 0
            #start_time = time.time()
            while time.time() - start_time < 120:
                fileName = '/home/pi4/my_project/Image/img{:03d}.jpg'.format(i)
                camera.capture_file(fileName)
                print("chup anh thu ", i)
                i += 1
                density += num_object
                num_object = 0
                im_num += 1
                print("density {}", density)
                print("time: ", time.time() - start_time)
                time.sleep(10)
            average_density = density / im_num
            print("average_density {}", average_density)
            #event.set()
        else:
            print("normal most")
            print("time chup anh: ", time.time() - start_time)
            im_num = 0
            camera.capture_file(fileName)
            i += 1
            time.sleep(30)
def detectImage():
    global j
    global num_object
    model = YOLO("best.pt")
    while True: 
        imName = '/home/pi4/my_project/Image/img{:03d}.jpg'.format(j)
        if os.path.exists(imName):
            time.sleep(0.5)
            start_time = time.time()
            print("\nDetectImage is running")
            try:
                #model = YOLO("best.pt")
                results = model.predict(imName)
            except Exception as e:
                print("Error:", e) #: print("Error")
            print("anh thu: {:03d}\n".format(j))
            print(imName)
            try:
                result = results[0]
                num_object = len(result.boxes)
                print("num_object {}", num_object)
                box = result.boxes[0]
                #print("Object type:",box.cls[0])
                #print("Coordinates:",box.xyxy[0])
                print("Probability:",box.conf[0])
                path = '/home/pi4/my_project/ImageDetection/img{:03d}.jpg'.format(j)
                plt.imsave(path, result.plot()[:,:,::-1])
                print("time phan tich anh: ", time.time() - start_time)
                time.sleep(0.5)
            except IndexError:
                print("Can't detect object in image")
                print("time phan tich anh: ", time.time() - start_time)
                time.sleep(0.5)
            j += 1
def warning():
    global average_density
    global limit_density
    while True:
        k = 0
        #event.wait()
        if average_density > limit_density:
            print("Warning is on")
            threadLock.acquire()
            start_time = time.time()
            #GPIO.PWM(27, 1).start(50)
            while (k < 20):
                GPIO.output(17, 1)
                GPIO.output(27, 1)
                time.sleep(0.5)
                GPIO.output(17, 0)
                GPIO.output(27, 0)
                k += 1
                time.sleep(0.5)
            #for x in rang(0, 361):
                #sinVal = math.sin(x*(math.pi/180))
                #toneVal = 2000 + sinVal*500
                #p.ChangFrequency(toneVal)
                #GPIO.output(17, 1)
                #time.sleep(0.001)
                #GPIO.output(17, 0)
            #event.clear()
            average_density = 0
            #GPIO.PWM(27, 1).stop()
            threadLock.release()
            time.sleep(1)
        else:
            time.sleep(1)
def removeImage():
    oldImName = glob.glob('/home/pi4/my_project/Image/*')
    oldImName_2 = glob.glob('/home/pi4/my_project/ImageDetection/*')
    for f in oldImName:
        os.remove(f)
    for f in oldImName_2:
        os.remove(f)
#def detectJ():
#    j = 0
#    for j in range(20):
#        a = j
#        fileName = '/home/pi4/my_project/Image/img{:03d}.jpg'.format(j)
        #if os.path.exists(fileName):
#        detectImage(fileName)

camera = Picamera2()
config = camera.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 640)}, display="lores")
camera.configure(config)
        #encoder = H264Encoder(bitrate=10000000)
camera.options["quality"] = 95
camera.start(show_preview = False)
global i
global j
global num_object
global density
global average_density
average_density = 0
num_object = 0
i = 0
j = 0
limit_density = 0.25
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
removeImage()
print("start\n")
#camera.capture_file("test-python.jpg")
#event = Event()
threadLock = threading.Lock()
thread1 = Thread(target = saveCapture)
thread2 = Thread(target = detectImage)
thread3 = Thread(target = warning)
#thread1.daemon = True
thread1.start()
thread2.start()
thread3.start()
thread1.join()
thread2.join()
thread3.join()

