"""
Server side code to access all files stored on the server and to generate graphical data from those files
"""
import socket
import argparse
import os
import re
import csv
path = os.getcwd()


class data_visualisation:
    def __init__(self,results):
        self.IP_address=results.IP_address
        self.flag=results.flag
        self.filename=results.filename
        self.all=results.all
        self.sonic=results.sonic
        self.temp=results.temp
        self.light=results.light
        self.accl=results.accl
        self.imu=results.imu
        self.sonic_time=[]
        self.sonic_data=[]
        self.light_time=[]
        self.light_data=[]
        self.temp_time=[]
        self.temp_data=[]
        self.accl_time=[]
        self.accl_data_x=[]
        self.accl_data_y=[]
        self.accl_data_z=[]
        self.GyroMag_time=[]
        self.Gyro_data_x=[]
        self.Gyro_data_y=[]
        self.Gyro_data_z=[]
        self.Mag_data_x=[]
        self.Mag_data_y=[]
        self.Mag_data_z=[]
        self.headers=[]
        
    def plot_data(self,time,data,sensor,unit,value):
        #do plotting
        
        import numpy as np
        import matplotlib.pyplot as plt
        
        
        import random
        if sensor=="Ultrasonic Sensor":
            data=[a for a in data if a<500]
        s=input("Please enter Y if save plot of sensor : "+sensor)
        N=len(data)
        if N>=1000:
            ind = np.arange(1000)
            x=np.random.choice(data, 1000)
            plt.figure()  
            plt.plot(ind, x,'ro--', linewidth=1, markersize=1)
            
            plt.ylabel(value+" in "+unit)
            plt.xlabel("Time")
            plt.title(self.filename.split(' ')[0]+ "  "+sensor)
            #plt.xlim((xmin,xmax))
            #plt.ylim((ymin,ymax))
            #plt.xticks(ind , time, rotation='vertical')
            if s=="Y":
                plt.savefig(self.filename.split(' ')[0]+sensor+".png")
            plt.show()
        elif N>500 and N<1000:
            ind = np.arange(750)
            x=np.random.choice(data, 750)
            plt.figure()  
            plt.plot(ind, x,'ro--', linewidth=1, markersize=1)
            
            plt.ylabel(value+" in "+unit)
            plt.xlabel("Time")
            plt.title(self.filename.split(' ')[0]+ "  "+sensor)
            #plt.xlim((xmin,xmax))
            #plt.ylim((ymin,ymax))
            #plt.xticks(ind , time, rotation='vertical')
            if s=="Y":
                plt.savefig(self.filename.split(' ')[0]+sensor+".png")
            plt.show()
        elif N<500:
            ind = np.arange(N)
            x=np.random.choice(data, N)
            plt.figure()  
            plt.plot(ind, x,'ro--', linewidth=1, markersize=1)
            
            plt.ylabel(value+" in "+unit)
            plt.xlabel("Time")
            plt.title(self.filename.split(' ')[0]+ "  "+sensor)
            #plt.xlim((xmin,xmax))
            #plt.ylim((ymin,ymax))
            #plt.xticks(ind , time, rotation='vertical')
            if s=="Y":
                plt.savefig(self.filename.split(' ')[0]+sensor+".png")
            plt.show()
        
            
    def plot_data_1(self,time,data_x,data_y,data_z,sensor,unit,value):
        #do plotting
        
        import numpy as np
        import matplotlib.pyplot as plt
        import random
        
        
        s=input("Please enter Y if save plot of sensor : "+sensor)
        
        N=len(time)
        if N>=1000:
            x=np.random.choice(data_x, 1000)
            y=np.random.choice(data_y, 1000)
            z=np.random.choice(data_z, 1000)
            ind = np.arange(1000)
            plt.figure()  
            plt.plot(ind, x,'ro--', linewidth=1, markersize=1)
            plt.plot(ind, y,'g+--', linewidth=1, markersize=1)
            plt.plot(ind, z,'b*--', linewidth=1, markersize=1)
            plt.ylabel(value+" in "+unit)
            plt.xlabel("Time")
            plt.title(self.filename.split(' ')[0]+ "  "+sensor)
            
            #plt.xticks(ind , time, rotation='vertical')
            if s=="Y":
                plt.savefig(self.filename.split(' ')[0]+sensor+".png")
            plt.show()
        elif N>500 and N<1000:
            x=np.random.choice(data_x, 750)
            y=np.random.choice(data_y, 750)
            z=np.random.choice(data_z, 750)
            ind = np.arange(75)
            plt.figure()  
            plt.plot(ind, x,'ro--', linewidth=1, markersize=1)
            plt.plot(ind, y,'g+--', linewidth=1, markersize=1)
            plt.plot(ind, z,'b*--', linewidth=1, markersize=1)
            plt.ylabel(value+" in "+unit)
            plt.xlabel("Time")
            plt.title(self.filename.split(' ')[0]+ "  "+sensor)
            if s=="Y":
                plt.savefig(self.filename.split(' ')[0]+sensor+".png")
            plt.show()
        elif N<500:
            x=np.random.choice(data_x, N)
            y=np.random.choice(data_y, N)
            z=np.random.choice(data_z, N)
            ind = np.arange(N)
            plt.figure()  
            plt.plot(ind, x,'ro--', linewidth=1, markersize=1)
            plt.plot(ind, y,'g+--', linewidth=1, markersize=1)
            plt.plot(ind, z,'b*--', linewidth=1, markersize=1)
            plt.ylabel(value+" in "+unit)
            plt.xlabel("Time")
            plt.title(self.filename.split(' ')[0]+ "  "+sensor)
            if s=="Y":
                plt.savefig(self.filename.split(' ')[0]+sensor+".png")
            plt.show()
        
    def extract_data(self):
        #extract data to be plotted in to two lists
        csvfile=open(self.filename)
        reader = csv.DictReader(csvfile)
        self.headers = reader.fieldnames
        final_dict = { col_name: [] for col_name in self.headers }
        
        for row in reader:
            for col_name in self.headers:
                a=row[col_name]
                if a!='':
                    final_dict[col_name].append(a)
        self.sonic_time=final_dict[self.headers[0]]
        self.sonic_data=final_dict[self.headers[1]]
        self.sonic_data=[float(a) for a in self.sonic_data]
        
        self.light_time=final_dict[self.headers[2]]
        self.light_data=final_dict[self.headers[3]]
        self.light_data=[float(a) for a in self.light_data]
        
        self.temp_time=final_dict[self.headers[4]]
        self.temp_data=final_dict[self.headers[5]]
        self.temp_data=[float(a) for a in self.temp_data]
        
        self.accl_time=final_dict[self.headers[6]]
        self.accl_data_x=final_dict[self.headers[7]]
        self.accl_data_x=[float(a) for a in self.accl_data_x]
        
        self.accl_data_y=final_dict[self.headers[8]]
        self.accl_data_y=[float(a) for a in self.accl_data_y]
        
        self.accl_data_z=final_dict[self.headers[9]]
        self.accl_data_z=[float(a) for a in self.accl_data_z]
        
        self.GyroMag_time=final_dict[self.headers[10]]
        self.Gyro_data_x=final_dict[self.headers[11]]
        self.Gyro_data_x=[float(a) for a in self.Gyro_data_x]
        
        self.Gyro_data_y=final_dict[self.headers[12]]
        self.Gyro_data_y=[float(a) for a in self.Gyro_data_y]
        
        self.Gyro_data_z=final_dict[self.headers[13]]
        self.Gyro_data_z=[float(a) for a in self.Gyro_data_z]
    
        self.Mag_data_x=final_dict[self.headers[14]]
        self.Mag_data_x=[float(a) for a in self.Mag_data_x]
        
        self.Mag_data_y=final_dict[self.headers[15]]
        self.Mag_data_y=[float(a) for a in self.Mag_data_y]
        
        self.Mag_data_z=final_dict[self.headers[16]]
        self.Mag_data_z=[float(a) for a in self.Mag_data_z]
    
    def selectsensor(self):
        if self.all:
            self.plot_data(self.sonic_time,self.sonic_data,"Ultrasonic Sensor","cm","Distance")
            self.plot_data(self.light_time,self.light_data,"Light Sensor","..","Light Level")
            self.plot_data(self.temp_time,self.temp_data,"Temperature Sensor","Celcius","Temperature")
            self.plot_data_1(self.accl_time,self.accl_data_x,self.accl_data_y,self.accl_data_z,"3 Axis Accelerometer","m/s^2","Acceleration")

            self.plot_data_1(self.GyroMag_time,self.Gyro_data_x,self.Gyro_data_y,self.Gyro_data_z,"9- DoF IMU Gyroscope","deg/s","Rotation")
            self.plot_data_1(self.GyroMag_time,self.Mag_data_x,self.Mag_data_y,self.Mag_data_z,"9- DoF IMU Magnetometer","Gauss","Magnetic field")

        elif self.sonic:
            self.plot_data(self.sonic_time,self.sonic_data,"Ultrasonic Sensor","cm","Distance")
        elif self.light:
            self.plot_data(self.light_time,self.light_data,"Light Sensor","..","Light Level")
        elif self.temp:
            self.plot_data(self.temp_time,self.temp_data,"Temperature Sensor","Celcius","Temperature")
        elif self.accl:
            self.plot_data_1(self.accl_time,self.accl_data_x,self.accl_data_y,self.accl_data_z,"3 Axis Accelerometer","m/s^2","Acceleration")

        elif self.imu:
            self.plot_data_1(self.GyroMag_time,self.Gyro_data_x,self.Gyro_data_y,self.Gyro_data_z,"9- DoF IMU Gyroscope","deg/s","Rotation")
            self.plot_data_1(self.GyroMag_time,self.Mag_data_x,self.Mag_data_y,self.Mag_data_z,"9- DoF IMU Magnetometer","Gauss","Magnetic field")

            

class data_extraction:
    def __init__(self,results):
        self.IP_address=results.IP_address
        self.flag=results.flag
        self.filename=results.filename
        self.all=results.all
        self.sonic=results.sonic
        self.temp=results.temp
        self.light=results.light
        self.accl=results.accl
        self.imu=results.imu
        print(self.IP_address,
        self.flag,
        self.filename,
        self.all,
        self.sonic,
        self.temp,
        self.light,
        self.accl,
        self.imu)
    def single_file_transfer(self,filename):
        #send filename request
        self.s.send(self.filename.encode(encoding='utf_8'))
        #recieve a reply on status of file 
        data = self.s.recv(22)
        data=repr(data.decode(encoding='utf_8'))
        data=re.sub("'","",data)
        print (data)
        # check if no file is returned or found
        if data == "None":
            print ("No files found")
            return
       
        path = os.getcwd()
        os.chdir(path)
        #copy file from server to client    
        with open(self.filename, 'wb') as f:
            print ('file opened')
            while True:
                #print('receiving data...')
                data = self.s.recv(1024)
                if not data:
                    f.close()
                    print ('file close()')
                    break
                # write data to a file
                f.write(data)

        print('Successfully get the file')
        self.s.close()
        print('connection closed')

    def multipule_file_transfer(self,filename):
        #send request for multiple files
        self.s.send(self.filename.encode(encoding='utf_8'))
        print('gfyfytfc')
        #recieve a reply on status of files
        data = self.s.recv(1024)
        data=repr(data.decode(encoding='utf_8'))
        data=re.sub("'","",data)
        print('hi')
        #if no file is found
        if data == "None":
            print ("No files found")
            return
        #iterate over list and obtain all files from server
        data= data.split(",")
        print(data)
        del data[0]
        for i in data:
            self.filename=i
            TCP_PORT = 1234
            BUFFER_SIZE = 1024
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.IP_address, TCP_PORT))
            self.single_file_transfer(self.filename)
        self.s.close() 
    
    def open_TCP_connection(self):
        #open TCP connection with server
        TCP_PORT = 1234
        BUFFER_SIZE = 16384
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.IP_address, TCP_PORT))
        #based on filename send request for file transfer
        if self.filename is not "None":
            self.single_file_transfer(self.filename)
        else:
            self.multipule_file_transfer(self.filename)
            
    def check_if_file_is_present(self):
        #check if file is already present with the client
        global path
        l=os.listdir(path)
        #if file not present, establish a TCP connection
        if self.filename not in l:
            self.open_TCP_connection()
            return False
        else:
            print ('File already exists in this directory')
            return True        

if __name__ == "__main__":
    #Argument Parsing    
    parser = argparse.ArgumentParser(description='Example with non-optional arguments')
    
    parser.add_argument('IP_address', action="store", type=str, 
                        help='Provide the IP address of the server')
    parser.add_argument('flag', action="store" , type=int, 
                        help='for text data eneter 0 or for graph data enter 1')
    
    parser.add_argument('-filename', action='store', default="None", type=str,
                        help='filename of data to be generated/ defaults to all files available')

    parser.add_argument('-all', action='store_true', default=False,
                        help='All Sensor data/graphs will be returned',
                        )
    parser.add_argument('-sonic', action='store_true', default=False,
                        help='Ultrasonic Sensor data/graphs will be returned',
                        )
    parser.add_argument('-temp', action='store_true', default=False, 
                        help='Temperature Sensor data/graphs will be returned',
                        )
    parser.add_argument('-light', action='store_true', default=False,
                        help='Light sensor data/graphs will be returned',
                        )
    parser.add_argument('-accl', action='store_true', default=False,
                        help='Accelerometer data/graphs will be returned',
                        )
    parser.add_argument('-imu', action='store_true', default=False, 
                        help='IMU data/graphs will be returned',
                        )
  

    #based on flag status create an object and call the required methods
    results = parser.parse_args()
    if results.flag == 0:
        obj = data_extraction(results)
        obj.check_if_file_is_present()
    elif results.flag == 1:
        obj = data_extraction(results)
        f=obj.check_if_file_is_present()
        if f:
            plotobj=data_visualisation(results)
            plotobj.extract_data()
            plotobj.selectsensor()
            
        
    else:
        print ('please enter flag value as 0 or 1')
    
