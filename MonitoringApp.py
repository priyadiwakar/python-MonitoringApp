import socket
from socketserver import ThreadingMixIn
import os
import re
import csv
import RPi.GPIO as gpio
from threading import Thread
import time
import spidev
import sys
import smbus
import datetime
from itertools import zip_longest

#path for all recording files
#setup global path variable
path=os.getcwd()
#setup global recording dictionaries
d_sonic={'sonic':[],'time_sonic':[]}
d_imu={'xmag':[],'ymag':[],'zmag':[],'xgyro':[],'ygyro':[],'zgyro':[],'time_imu':[]}
d_light={'light':[],'time_light':[]}
d_temp={'temp':[],'time_temp':[]}
d_accl={'xaccl':[],'yaccl':[],'zaccl':[],'time_accl':[]}


#assigning pin values for each sensor
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

ECHO = 24
trig = 23
light_channel = 2
temp_channel  = 0
LED = 4
bz=18
# LED pin mapping.
red = 17
green = 27
blue = 22
status=0
status1=0
bn=16



#setup GPIO pins
gpio.setup(ECHO, gpio.IN)
gpio.setup(trig, gpio.OUT, initial=gpio.LOW)
gpio.setup(LED, gpio.OUT, initial=gpio.LOW)
gpio.setup(red, gpio.OUT)
gpio.setup(green, gpio.OUT)
gpio.setup(blue, gpio.OUT)
gpio.setup(bn, gpio.IN, pull_up_down=gpio.PUD_UP)

#open spi ports
spi = spidev.SpiDev()
spi.open(0, 0)  # open spi port 0, device (CS) 0
spi.max_speed_hz=1000000

#setup i2c 
DEVICE_BUS = 1
DEVICE_ADDR_A = 0x18
DEVICE_ADDR_G = 0x6B
DEVICE_ADDR_M = 0x1E
bus = smbus.SMBus(DEVICE_BUS)

bus.write_byte_data(DEVICE_ADDR_A, 0x20, 0x27)
bus.write_byte_data(DEVICE_ADDR_A, 0x23, 0x00)

bus.write_byte_data(DEVICE_ADDR_G, 0x10, 0x70)
bus.write_byte_data(DEVICE_ADDR_G, 0x11, 0x58)


bus.write_byte_data(DEVICE_ADDR_M, 0x20, 0x80)
bus.write_byte_data(DEVICE_ADDR_M, 0x21, 0x60)
bus.write_byte_data(DEVICE_ADDR_M, 0x22, 0x00)

RED = gpio.PWM(red, 500)
GREEN = gpio.PWM(green, 500)
BLUE = gpio.PWM(blue, 500)
RED.start(0)
GREEN.start(0)
BLUE.start(0)


#Setup all helper functions for each sensor threads
def buzzer(rn):

    
    gpio.setup(bz, gpio.OUT)
    pwm=gpio.PWM(bz, rn) # set frequency to 100
    for i in range(100, rn):
        pwm.start(50)# initialize PWM at 0% (aka off)
        
        pwm.ChangeFrequency(i)
    print("***Frequency:{} Hz ***".format(rn))
    pwm.stop()					# Stop the buzzer
	

def rgb(minimum, maximum, value):
    if(value ==0):
        r = 238
        g = 130
        b = 238
        RED.ChangeFrequency(500)
        GREEN.ChangeFrequency(500)
        BLUE.ChangeFrequency(500)
        setColor(r,g,b)         
        return r, g, b

    elif(value ==50):
        r = 255
        g = 0
        b = 0
        RED.ChangeFrequency(500)
        GREEN.ChangeFrequency(500)
        BLUE.ChangeFrequency(500)
        setColor(r,g,b)
        return r, g, b

    elif(value <0):
        r = 238
        g = 130
        b = 238
        RED.ChangeFrequency(2)
        GREEN.ChangeFrequency(2)
        BLUE.ChangeFrequency(2)
        setColor(r,g,b)         
        return r, g, b

    elif(value >50):
        r = 255
        g = 0
        b = 0
        RED.ChangeFrequency(2)
        GREEN.ChangeFrequency(2)
        BLUE.ChangeFrequency(2)
        return r, g, b

    elif (value>0 and value<50):
#        minimum, maximum = float(minimum), float(maximum)
#        ratio = 2 * (value-minimum) / (maximum - minimum)
#        b = int(max(0, 255*(1 - ratio)))
#        r = int(max(0, 255*(ratio - 1)))
#        g = 255 - b - r
        if value>0 and value<=10:
            r=75
            g=0
            b=130
        elif value>10 and value<=20:
            r=0
            g=0
            b=255
        elif value>20 and value<=30:
            r=0
            g=255
            b=0
        elif value>30 and value<=40:
            r=255
            g=255
            b=0
        elif value>40 and value<50:
            r=255
            g=127
            b=0

            
        RED.ChangeFrequency(500)
        GREEN.ChangeFrequency(500)
        BLUE.ChangeFrequency(500)
        setColor(r,g,b)
        return r, g, b


# Set a color by giving R, G, and B values of 0-255.
def setColor(r, g, b):

    # Convert 0-255 range to 0-100.
    #rgb = [(x / 255.0) * 100 for x in rgb]
    RED.ChangeDutyCycle(((255-r) / 255.0)*100)#green
    GREEN.ChangeDutyCycle(((255-g) / 255.0)*100)
    BLUE.ChangeDutyCycle(((255-b) / 255.0)*100)

    

def ReadChannel(channel):
    try:
        response = spi.xfer2([1,(8+channel)<<4,0])   #1000 0000    Start byte 00000001, channel selection: end byte
    #    print(response)
        data = ((response[1]&3) << 8) + response[2]         #011
    #    print(data)
        return data
    except:
        print("Stopped")
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
#def ConvertVolts(data, places):
#    volts = (data * 3.3) / float(1023)
#    volts = round(volts, places)
#    return volts

def ConvertTemp(data,places):
 
    temp = ((data * 330)/float(1023))-50
    temp = round(temp,places)
    return temp

def stopthreads():
    SPILight.terminate()
    SPITemp.terminate()
    sonic.terminate()
    accl.terminate()
    GyroMag.terminate()

    
    
def startthreads(mode,flag):
    global SPILight
    global SPITemp
    global sonic
    global accl
    global GyroMag
    if flag==1:
        RED.start(0)
        GREEN.start(0)
        BLUE.start(0)

        print(mode)
        SPILight = SPIDeviceLight(mode)
        SpiThreadLight = Thread(target=SPILight.run) 
        SpiThreadLight.start()
        
        SPITemp = SPIDeviceTemp(mode)
        SpiThreadTemp = Thread(target=SPITemp.run) 
        SpiThreadTemp.start()
    
        sonic = Sonic(mode)
        sonicThread = Thread(target=sonic.run)
        sonicThread.start()
    
        accl = i2c_Accel(mode)
        acclThread = Thread(target=accl.run)
        acclThread.start()
        
        
        GyroMag = i2c_GyMag(mode)
        GMThread = Thread(target=GyroMag.run)
        GMThread.start()
    elif flag==0:
        SPILight.terminate()
        SPITemp.terminate()
        sonic.terminate()
        accl.terminate()
        GyroMag.terminate()
        RED.stop()
        GREEN.stop()
        BLUE.stop()

class interrupt(Thread):
    """
    Button detection
    """
    def __init__(self):
      Thread.__init__(self)
    def run(self):
        global status
        global status1
        gpio.setup(bn, gpio.IN, pull_up_down=gpio.PUD_UP)

        while True:
            try:
                print ("Press 2 sec for Recording Mode and 5 sec for Only Recording Mode")
                gpio.wait_for_edge(bn, gpio.FALLING)
                
                start = time.time()
                time.sleep(0.2)
                
                while gpio.input(bn) == gpio.LOW:
                    time.sleep(0.01)
                l = time.time() - start
                
                if l >1.5 and l<2.5:
                    
                    print("2 sec")
                    status= not status
                    
                    if status==1:
                        mode=1
                        startthreads(mode,0)
                        time.sleep(5)
                        print("Recording data..")
                        
                        gpio.output(LED,status)
                        startthreads(mode,1)
                    else:
                        mode=0
                        startthreads(mode,0)
                        time.sleep(5)
                        gpio.output(LED,status)
                        print("Stopped Recording data..")

                        #for recording
                        global d_sonic
                        global d_light
                        global d_temp
                        global d_accl
                        global d_imu
                        strg=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')[:-3]
                        myList=[]
                        myList.append(d_sonic['time_sonic'])
                        myList.append(d_sonic['sonic'])
                        myList.append(d_light['time_light'])
                        myList.append(d_light['light'])
                        myList.append(d_temp['time_temp'])
                        myList.append(d_temp['temp'])
                        myList.append(d_accl['time_accl'])
                        myList.append(d_accl['xaccl'])
                        myList.append(d_accl['yaccl'])
                        myList.append(d_accl['zaccl'])
                        myList.append(d_imu['time_imu'])
                        myList.append(d_imu['xgyro'])
                        myList.append(d_imu['ygyro'])
                        myList.append(d_imu['zgyro'])
                        myList.append(d_imu['xmag'])
                        myList.append(d_imu['ymag'])
                        myList.append(d_imu['zmag'])
                        global path
                        os.chdir(path+"/recorded_data")
                        with open(strg+".csv",'w') as f:
                            writer = csv.writer(f)
                            schema = ['time_sonic','sonic','time_light','light','time_temp','temp','time_accl','xaccl','yaccl','zaccl','time_imu','xgyro','ygyro','zgyro','xmag','ymag','zmag']
                            writer.writerow([g for g in schema])
                            for values in zip_longest(*myList):
                                writer.writerow(values)
                        d_sonic={'sonic':[],'time_sonic':[]}
                        d_imu={'xmag':[],'ymag':[],'zmag':[],'xgyro':[],'ygyro':[],'zgyro':[],'time_imu':[]}
                        d_light={'light':[],'time_light':[]}
                        d_temp={'temp':[],'time_temp':[]}
                        d_accl={'xaccl':[],'yaccl':[],'zaccl':[],'time_accl':[]}
                        #end of recording code
                        startthreads(mode,1)
                        
                  
                        
                elif l>4 and l<6:
                    
                    print("5 sec")
                    status1= not status1
                    if status1==1:
                        mode=2
                        startthreads(mode,0)
                        time.sleep(5)
                        print("Recording data..")
                        
                        startthreads(mode,1)
                        R = gpio.PWM(LED, 2)
                        r=100
                        R.start(50)
                        R.ChangeDutyCycle(((255-r) / 255.0)*100)
                        
                    else:
                        R.stop()
                        mode=0
                        startthreads(mode,0)
                        time.sleep(5)
                        print("Stopped Recording data..")
                        #for recording
                        global d_sonic
                        global d_light
                        global d_temp
                        global d_accl
                        global d_imu
                        strg=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')[:-3]
                        myList=[]
                        myList.append(d_sonic['time_sonic'])
                        myList.append(d_sonic['sonic'])
                        myList.append(d_light['time_light'])
                        myList.append(d_light['light'])
                        myList.append(d_temp['time_temp'])
                        myList.append(d_temp['temp'])
                        myList.append(d_accl['time_accl'])
                        myList.append(d_accl['xaccl'])
                        myList.append(d_accl['yaccl'])
                        myList.append(d_accl['zaccl'])
                        myList.append(d_imu['time_imu'])
                        myList.append(d_imu['xgyro'])
                        myList.append(d_imu['ygyro'])
                        myList.append(d_imu['zgyro'])
                        myList.append(d_imu['xmag'])
                        myList.append(d_imu['ymag'])
                        myList.append(d_imu['zmag'])
                        global path
                        os.chdir(path+"/recorded_data")
                        with open(strg+".csv",'w') as f:
                            writer = csv.writer(f)
                            schema = ['time_sonic','sonic','time_light','light','time_temp','temp','time_accl','xaccl','yaccl','zaccl','time_imu','xgyro','ygyro','zgyro','xmag','ymag','zmag']
                            writer.writerow([g for g in schema])
                            for values in zip_longest(*myList):
                                writer.writerow(values)
                        d_sonic={'sonic':[],'time_sonic':[]}
                        d_imu={'xmag':[],'ymag':[],'zmag':[],'xgyro':[],'ygyro':[],'zgyro':[],'time_imu':[]}
                        d_light={'light':[],'time_light':[]}
                        d_temp={'temp':[],'time_temp':[]}
                        d_accl={'xaccl':[],'yaccl':[],'zaccl':[],'time_accl':[]}
                        #end of recording code
                        startthreads(mode,1)
    
            except KeyboardInterrupt:
                sys.exit(0)
                print("Stopped")

class SPIDeviceLight(Thread):  
    def __init__(self,m):
        self._running = True
        self.mode=m
    def terminate(self):  
        global spi
        self._running = False
        #spi.close()

    def run(self):
        global spi
        global d_light
        while self._running:
            time.sleep(1)
            try:
       
                
                # Read the light sensor data
                light_level = ReadChannel(light_channel)
        
                if self.mode==0 :
                    # Print out results
                    print("--------------------------------------------")
                    print("Light: {} ".format(light_level))
                elif self.mode==1:
                    
                    d_light['light'].append(light_level)
                    a=str(datetime.datetime.now())
                    a=a.split(".")[0]+str(round(int(a.split(".")[1])/100000))
                    d_light['time_light'].append(a)
                    
                    print("--------------------------------------------")
                    print("Light: {} ".format(light_level))
                    print("Recording")
                
                elif self.mode==2:
                    
                    d_light['light'].append(light_level)
                    a=str(datetime.datetime.now())
                    a=a.split(".")[0]+str(round(int(a.split(".")[1])/100000))
                    d_light['time_light'].append(a)
                    
                    print("Recording")
                    
                    
            
            except:
                print("Stopped")
                SPILight.terminate()
          


class SPIDeviceTemp(Thread):  
    def __init__(self,m):
        self._running = True
        self.mode=m

    def terminate(self):  
        global spi
        self._running = False
        
        #spi.close()

    def run(self):
        global spi
        global d_temp
        while self._running:
            time.sleep(2)
            try:
                
                temp_level = ReadChannel(temp_channel) 
                temp       = ConvertTemp(temp_level,2)
                
                
                if self.mode==0 : 
                    r, g, b = rgb(0, 50, temp)
                    # Print out results
                    print("--------------------------------------------")
                    print("R G B = ", r, g, b)
                    print("Temperature : {} deg C".format(temp))  
                elif self.mode==1:
                    r, g, b = rgb(0, 50, temp)
                    #record
                    
                    a=str(datetime.datetime.now())
                    a=a.split(".")[0]+str(round(int(a.split(".")[1])/100000))
                    d_temp['time_temp'].append(a)
                    d_temp['temp'].append(temp)
                    
                    # Print out results
                    print("--------------------------------------------")
                    print("R G B = ", r, g, b)
                    print("Temperature : {} deg C".format(temp))  
                    print("Recording")
                elif self.mode==2:
                    RED.ChangeDutyCycle(0)#green
                    GREEN.ChangeDutyCycle(0)
                    BLUE.ChangeDutyCycle(0)
                    RED.stop()
                    GREEN.stop()
                    BLUE.stop()
                    d_temp['temp'].append(temp)
                    a=str(datetime.datetime.now())
                    a=a.split(".")[0]+str(round(int(a.split(".")[1])/100000))
                    d_temp['time_temp'].append(a)
                    
                    print("Recording")
                    
            except :
                print("Stopped")
                SPITemp.terminate()
            


class Sonic(Thread):  
    def __init__(self,m):
        self._running = True
        self.mode=m

    def terminate(self):  
        self._running = False
    

    def run(self):
        global d_sonic
        while self._running:
            time.sleep(0.1)
            try:
                print("******%%%%%%e*"+str(self.mode)+"%%%%*******")
                gpio.output(trig, True)
                time.sleep(0.00001)
                gpio.output(trig, False)
    
                while gpio.input(ECHO)==0:               #Check whether the ECHO is LOW
                    pulse_start = time.time()              #Saves the last known time of LOW pulse
                
                while gpio.input(ECHO)==1:               #Check whether the ECHO is HIGH
                    pulse_end = time.time()                #Saves the last known time of HIGH pulse 
    
                pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable
                distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
                distance = round(distance, 2)            #Round to two decimal points
                
                if self.mode==0:
                    print("--------------------------------------------")
                    print("Distance:{} cm ".format(distance))  #Print distance with 0.5 cm calibration
                    
                    if( distance >= 5 and distance < 20):      #Check whether the distance is within range
                       x=(1900/15) *(20-distance)
                       rn=x + 100
                       buzzer(round(rn))
                       
                       
                    if( distance<5):
                        F=2000
                        gpio.setup(bz, gpio.OUT)
                        pwm=gpio.PWM(bz, F) # set frequency to 100
                        
                        
                        pwm.start(50)# initialize PWM at 0% (aka off)   
                        print("***Frequency:{} Hz ***".format(F))
                        time.sleep(0.5)
                        pwm.stop()
                        
                elif self.mode==1:
                    print("--------------------------------------------")
                    print("Distance:{} cm ".format(distance))  #Print distance with 0.5 cm calibration
                    #recording
                    
                    d_sonic['sonic'].append(distance)
                    a=str(datetime.datetime.now())
                    a=a.split(".")[0]+str(round(int(a.split(".")[1])/100000))
                    d_sonic['time_sonic'].append(a)
                    

                    if( distance >= 5 and distance < 20):      #Check whether the distance is within range
                       x=(1900/15) *(20-distance)
                       rn=x + 100
                       buzzer(round(rn))
                       
                       
                    if( distance<5):
                        F=2000
                        gpio.setup(bz, gpio.OUT)
                        pwm=gpio.PWM(bz, F) # set frequency to 100
                        
                        
                        pwm.start(50)# initialize PWM at 0% (aka off)   
                        print("***Frequency:{} Hz ***".format(F))
                        time.sleep(0.5)
                        pwm.stop()
                    print("Recording")
                elif self.mode==2:
                    
                    d_sonic['sonic'].append(distance)
                    a=str(datetime.datetime.now())
                    a=a.split(".")[0]+str(round(int(a.split(".")[1])/100000))
                    d_sonic['time_sonic'].append(a)
                    
                    print("Recording")
            except :
                print("Stopped")
                sonic.terminate()
           
            
                    
            

def read_i2cdata(addr, reg1, reg2):
    try:
        data0 = bus.read_byte_data(addr, reg1)
        data1 = bus.read_byte_data(addr, reg2)
        Accl = data1 * 256 + data0
        if Accl > 32767 :
            Accl -= 65536
        return Accl
    except :
        print("Stopped")


class i2c_Accel(Thread):  
    def __init__(self,m):
        self._running = True
        self.mode=m

    def terminate(self):  
        self._running = False
        #bus.close()

    def run(self):
        global d_accl
        while self._running:
            time.sleep(0.1)
            try:
                
                xAccl = read_i2cdata(DEVICE_ADDR_A, 0x28, 0x29)
                yAccl = read_i2cdata(DEVICE_ADDR_A, 0x2A, 0x2B)
                zAccl = read_i2cdata(DEVICE_ADDR_A, 0x2C, 0x2D)
                conversiontoms = float(2.0/32768)*9.8
                
                
                if self.mode==0:
                    print("--------------------------------------------")
                    print ("Acceleration in X-Axis, Y-Axis, Z-Axis : \n{} m/sec^2\n{} m/sec^2\n{} m/sec^2".format(round(xAccl*conversiontoms, 3), round(yAccl*conversiontoms, 3), round(zAccl*conversiontoms, 3)))
                elif self.mode==1:
                    print("--------------------------------------------")
                    print ("Acceleration in X-Axis, Y-Axis, Z-Axis : \n{} m/sec^2\n{} m/sec^2\n{} m/sec^2".format(round(xAccl*conversiontoms, 3), round(yAccl*conversiontoms, 3), round(zAccl*conversiontoms, 3)))
                    print("Recording")
                    
                    d_accl['xaccl'].append(round(xAccl*conversiontoms, 3))
                    d_accl['yaccl'].append(round(yAccl*conversiontoms, 3))
                    d_accl['zaccl'].append(round(zAccl*conversiontoms, 3))
                    a=str(datetime.datetime.now())
                    a=a.split(".")[0]+str(round(int(a.split(".")[1])/100000))
                    d_accl['time_accl'].append(a)
                    
                
                elif self.mode==2:
                    print("Recording")
                    
                    d_accl['xaccl'].append(round(xAccl*conversiontoms, 3))
                    d_accl['yaccl'].append(round(yAccl*conversiontoms, 3))
                    d_accl['zaccl'].append(round(zAccl*conversiontoms, 3))
                    a=str(datetime.datetime.now())
                    a=a.split(".")[0]+str(round(int(a.split(".")[1])/100000))
                    d_accl['time_accl'].append(a)
                    
            
            except:
                print("Stopped")
                accl.terminate()
    
               
                
class i2c_GyMag(Thread):  
    def __init__(self,m):
        self._running = True
        self.mode=m

    def terminate(self):  
        self._running = False
        #bus.close()

    def run(self):
        global d_imu
        while self._running:
            time.sleep(0.1)
            try:
                xGyro = read_i2cdata(DEVICE_ADDR_G, 0x18, 0x19)
                yGyro = read_i2cdata(DEVICE_ADDR_G, 0x1A, 0x1B)
                zGyro = read_i2cdata(DEVICE_ADDR_G, 0x1C, 0x1D)
                gRes = 0.07 #float(2000.0 / 32768.0)
                
                
                xMag = read_i2cdata(DEVICE_ADDR_M, 0x28, 0x29)
                yMag = read_i2cdata(DEVICE_ADDR_M, 0x2A, 0x2B)
                zMag = read_i2cdata(DEVICE_ADDR_M, 0x2C, 0x2D)
                mRes=0.0058 #float(2.0/32768)
                
                
                
                if self.mode==0 :
                    print("--------------------------------------------")
                    print ("Rotation in X-Axis, Y-Axis, Z-Axis : \n{} deg/s\n{} deg/\n{} deg/sec".format(round(xGyro*gRes,2), round(yGyro*gRes,2), round(zGyro*gRes,2)))
                    
                    
                    print("--------------------------------------------")
                    print ("Magnetic Field in X-Axis, Y-Axis, Z-Axis : \n{} Gs\n{} Gs\n{} Gs".format(round(xMag*mRes,2),round(mRes*yMag,2),round(mRes*zMag,2)))
                elif self.mode==1:
                    print ("Rotation in X-Axis, Y-Axis, Z-Axis : \n{} deg/s\n{} deg/\n{} deg/sec".format(round(xGyro*gRes,2), round(yGyro*gRes,2), round(zGyro*gRes,2)))
                    
                    d_imu['xgyro'].append(round(xGyro*gRes,2))
                    d_imu['ygyro'].append(round(yGyro*gRes,2))
                    d_imu['zgyro'].append(round(zGyro*gRes,2))
                    
                    print("--------------------------------------------")
                    print ("Magnetic Field in X-Axis, Y-Axis, Z-Axis : \n{} Gs\n{} Gs\n{} Gs".format(round(xMag*mRes,2),round(mRes*yMag,2),round(mRes*zMag,2)))
                    
                    d_imu['xmag'].append(round(xMag*mRes,2))
                    d_imu['ymag'].append(round(yGyro*gRes,2))
                    d_imu['zmag'].append(round(zGyro*gRes,2))
                    a=str(datetime.datetime.now())
                    a=a.split(".")[0]+str(round(int(a.split(".")[1])/100000))
                    d_imu['time_imu'].append(a)
                    
                    print("Recording")
                elif self.mode==2:
                    
                    d_imu['xgyro'].append(round(xGyro*gRes,2))
                    d_imu['ygyro'].append(round(yGyro*gRes,2))
                    d_imu['zgyro'].append(round(zGyro*gRes,2))
                    d_imu['xmag'].append(round(xMag*mRes,2))
                    d_imu['ymag'].append(round(yGyro*gRes,2))
                    d_imu['zmag'].append(round(zGyro*gRes,2))
                    a=str(datetime.datetime.now())
                    a=a.split(".")[0]+str(round(int(a.split(".")[1])/100000))
                    d_imu['time_imu'].append(a)
                    
                    print("Recording")
    
            except:
                print("Stopped")
                GyroMag.terminate()

#setup client thread
class ClientThread(Thread):

    def __init__(self,ip,port,sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print (" New thread started for "+ip+":"+str(port))
    def single_file_transfer(self,filename):
        global path
        BUFFER_SIZE=16384
        new_path=path+"/recorded_data"
        os.chdir(new_path)
        l=os.listdir(new_path)
        if self.filename in l:
                f = open(self.filename,'rb')
                self.sock.send("file found sending now".encode(encoding='utf_8'))
                time.sleep(3)
                while True:
                        l = f.read(BUFFER_SIZE)
                        while (l):
                                self.sock.send(l)
                                l = f.read(BUFFER_SIZE)
                        if not l:
                                f.close()
                                self.sock.close()
                                break
        else:
            strig="Given file name not found"
            print(strig)
            self.sock.send(strig.encode(encoding='utf_8'))



    def run(self):
        global path
        new_path=path+"/recorded_data"
        os.chdir(new_path)
        l=os.listdir(new_path)
        data = self.sock.recv(1024)
        self.filename=repr(data.decode('utf8'))
        #filename=re.sub("b","",filename)
        self.filename=re.sub("'","",self.filename)
        print(self.filename)
        if self.filename != "None":
               self.single_file_transfer(self.filename)
        else:
            if not not l:
                strig=''
                for i in l:
                    strig=strig+','+i
                self.sock.send(strig.encode(encoding='utf_8'))


class Server(Thread):
    def __init__(self):
        self._running = True
    def terminate(self):
        self._running = False

    def run(self):
        TCP_IP = ''
        TCP_PORT = 1234
        BUFFER_SIZE = 16384
        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpsock.bind((TCP_IP, TCP_PORT))
        threads = []

        while self._running:
            tcpsock.listen(5)
            print ("Server listening....")
            (conn, (ip,port)) = tcpsock.accept()
            print ('Got connection from ', (ip,port))
            newthread = ClientThread(ip,port,conn)
            newthread.start()
            threads.append(newthread)
        for t in threads:
            t.join()


try:
    a=0
    server=Server()
    serverThread=Thread(target=server.run)
    serverThread.start()


    SPILight = SPIDeviceLight(a)
    SpiThreadLight = Thread(target=SPILight.run) 
    SpiThreadLight.start()
    
    SPITemp = SPIDeviceTemp(a)
    SpiThreadTemp = Thread(target=SPITemp.run) 
    SpiThreadTemp.start()

    sonic = Sonic(a)
    sonicThread = Thread(target=sonic.run)
    sonicThread.start()

    accl = i2c_Accel(a)
    acclThread = Thread(target=accl.run)
    acclThread.start()
    
    
    GyroMag = i2c_GyMag(a)
    GMThread = Thread(target=GyroMag.run)
    GMThread.start()
    print(a)
    i = interrupt()
    iThread = Thread(target=i.run)
    iThread.start()

    while True:
        time.sleep(1) #One second delay
except KeyboardInterrupt:
    time.sleep(1)
    SPILight.terminate()
    SPITemp.terminate()
    sonic.terminate()
    accl.terminate()
    GyroMag.terminate()
    #server.terminate()
