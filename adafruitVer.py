import re
import time
from Adafruit_IO import Client, Feed
import serial
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
RELAIS_1_GPIO = 21
GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
GPIO.output(RELAIS_1_GPIO, GPIO.LOW) # on

DHT_READ_TIMEOUT = 1
DHT_DATA_PIN = 26
ADAFRUIT_IO_KEY = 'aio_Suyn56lYQOeL8qSBXjKhZ7beh7hM'
ADAFRUIT_IO_USERNAME = 'zaid_kid'
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
temperature_feed = aio.feeds('temperature')
Humadity_feed = aio.feeds('humadit')
indicator_feed = aio.feeds('checkindicator')
soil_feed = aio.feeds('soil')

port = serial.Serial("/dev/rfcomm0", baudrate=115200)

def ternOnPumb():
    StartTime = time.time()
    GPIO.output(RELAIS_1_GPIO, GPIO.HIGH) # out
    while True:
        data=sensor()
        if(float(data[1])<1800):
            StopTime = time.time()
            GPIO.output(RELAIS_1_GPIO, GPIO.LOW) # on
            print(StartTime-StopTime)
            return (StartTime-StopTime)


def sensor():
     print("DIGITAL LOGIC -- > SENDING...")
     port.write(1)
     count =0
     arr=[]
     while(count <3):
         sensor= port.readline()
         if sensor:
             sensor =sensor.decode('utf-8')
             print(sensor)
             arr.append(sensor.rstrip("\n\r"))
             count=count+1
     return arr

def cloudSer(arr):
    aio.send(temperature_feed.key, str(arr[0]))
    aio.send(Humadity_feed.key, str(arr[2]))
    temp=float(arr[1])
    aio.send(soil_feed.key,str((temp/100)))
        
while True:
    data=sensor()
    print(data[1])
    cloudSer(data)
    if(float(data[1])>1800):
        ternOnPumb()
    time.sleep(10)

   
       
