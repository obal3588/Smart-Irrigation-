import RPi.GPIO as GPIO
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
from datetime import date, datetime
import smbus
import boto3
import time
import boto3
import serial
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
RELAIS_1_GPIO = 21
GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
GPIO.output(RELAIS_1_GPIO, GPIO.LOW) # on

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('Test')
# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
port = serial.Serial("/dev/rfcomm0", baudrate=115200)
# AWS IoT certificate based connection
myMQTTClient = AWSIoTMQTTClient("123afhlss456")
myMQTTClient.configureEndpoint("a3lv0r9nn5lhte-ats.iot.me-south-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/pi/aws-iot-device-sdk-python/DHT11_Python/CA.pem", "/home/pi/aws-iot-device-sdk-python/DHT11_Python/d4d486d27e-private.pem.key", "/home/pi/aws-iot-device-sdk-python/DHT11_Python/d4d486d27e-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
 
#connect and publish
myMQTTClient.connect()
myMQTTClient.publish("thing01/info", "connected", 0)
 
counter=0
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




def put( Sensor_Id , Temperature, Humidity,Soil):
    table.put_item(
        Item={
            'id':Sensor_Id,
            'Temperature':Temperature,
            'Humidity' :Humidity,
            'Soil':Soil
            }
        )
#loop and publish sensor reading
while 1:

    now = datetime.utcnow()
    now_str = now.strftime('%Y-%m-%dT%H:%M:%SZ') #e.g. 2016-04-18T06:12:25.877Z
    arr = sensor()
    if(float(arr[1])>1800):
        ternOnPumb()
    put(str(counter),arr[0],arr[1],arr[2])
    payload = '{ "timestamp": "' + now_str + '","temperature": ' + str(arr[0]) + ',"humidity": '+ str(arr[2]) +  ', "soil": '+ str(arr[1]) + ' }'
    print(payload)
    myMQTTClient.publish("thing01/data", payload, 0)
    counter=counter+1
    
    sleep(4)


