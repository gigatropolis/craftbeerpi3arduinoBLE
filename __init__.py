
# -*- coding: utf-8 -*-
import os, sys, threading, time
from modules import cbpi, app
from modules.core.hardware import SensorActive
from modules.core.props import Property
from bluepy import btle
import struct
import threading

PeripheralConnection = None
PeripheralAddrName = ""
lock_periphal = threading.Lock()
lock_CharRead = threading.Lock()

class BLESensorBase(SensorActive):

    def InitPeripheralConnection(self, address):

        global PeripheralConnection
        global PeripheralAddrName
        global lock_periphal
        global lock_CharRead

        lock_periphal.acquire()
        print "PRE: PeripheralAddrName = %s" %(PeripheralAddrName)

        if not PeripheralAddrName or not PeripheralConnection:

            print "connecting...."
            PeripheralAddrName = address
            try:
                print "PeripheralAddrName=%s" % (PeripheralAddrName)
                PeripheralConnection = btle.Peripheral(address)
                print "PeripheralConnection=%s" % (str(PeripheralConnection))
            except:
                print "Couldn't connect"
            finally:
               lock_periphal.release()

    @classmethod
    def init_global(cls):
        '''
        Called one at the startup for all sensors
        :return: 
        '''
        #cls['PeripheralConnection'] = None
        #self['PeripheralAddrName'] = ""

 
@cbpi.sensor
class ArduinoBLE_Temperature(BLESensorBase):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, default_value="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, default_value="run blelisten.py: '1101....'")
    CharTemp = Property.Text("Characteristic Temperature", configurable=True, default_value="run blelisten.py '2204...'")

    def get_unit(self):
        '''
        :return: Unit of the sensor as string. Should not be longer than 3 characters
        '''
        return "°C" if self.get_config_parameter("unit", "C") == "C" else "°F"

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return: 
        '''
        pass

    def execute(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        self.InitPeripheralConnection(self.PeripheralAddress)
        self.Peripheral = PeripheralConnection

        print "temp.Peripheral = ", self.Peripheral
        while self.is_running():

            self.sleep(5)
            lock_CharRead.acquire()
            ch = self.Peripheral.getCharacteristics()
            temp = 0
            
            for c in ch:

                if str(c.uuid) == self.CharTemp:          
                    if c.supportsRead():
                        s1 = c.read()
                        temp = struct.unpack("<HH", s1)[0] /100.0
                        if (self.get_unit() == "C"):
                            self.data_received(temp)
                        else:
                            f = 9.0 / 5.0 * temp + 32.0
                            self.data_received(round(f, 2))
                    break
 
            lock_CharRead.release()
            self.sleep(5)


@cbpi.sensor
class ArduinoBLE_Excel_Xaxis(BLESensorBase):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, default_value="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, default_value="run blelisten.py: '1101....'")
    CharExcel_X = Property.Text("Characteristic Excel_X", configurable=True, default_value="run blelisten.py '2201...'")

    def get_unit(self):
        return "°"

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return: 
        '''
        pass

    def execute(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        self.sleep(0.1)
        self.InitPeripheralConnection(self.PeripheralAddress)
        self.Peripheral = PeripheralConnection

        print "X.Peripheral = ", self.Peripheral
        while self.is_running():

            self.sleep(5)
            lock_CharRead.acquire()
            ch = self.Peripheral.getCharacteristics()
            temp = 0
            
            for c in ch:
                 if str(c.uuid) == self.CharExcel_X:
                    if c.supportsRead():
                        s1 = c.read()
                        excelX = struct.unpack("<HH", s1)[0]
                        self.data_received(excelX)
                    break
                    
            lock_CharRead.release()
            self.sleep(5)

@cbpi.sensor
class ArduinoBLE_Humidity(BLESensorBase):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, default_value="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, default_value="run blelisten.py: '1101....'")
    CharHum = Property.Text("Characteristic Humidity", configurable=True, default_value="run blelisten.py '2205...'")

    def get_unit(self):
        return "%"

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return: 
        '''
        pass

    def execute(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        self.sleep(0.2)
        self.InitPeripheralConnection(self.PeripheralAddress)
        self.Peripheral = PeripheralConnection

        print "hum.Peripheral = ", self.Peripheral
        while self.is_running():

            self.sleep(5)
            lock_CharRead.acquire()
            ch = self.Peripheral.getCharacteristics()
            temp = 0
            
            for c in ch:
                if str(c.uuid) == self.CharHum:
                    if c.supportsRead():
                        s1 = c.read()
                        hum = struct.unpack("<HH", s1)[0] /100.0
                        self.data_received(hum)
                    break
                    
            lock_CharRead.release()
            self.sleep(5)

@cbpi.sensor
class ArduinoBLE_Pressure(BLESensorBase):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, default_value="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, default_value="run blelisten.py: '1101....'")
    CharPress = Property.Text("Characteristic Pressure", configurable=True, default_value="run blelisten.py '2206...'")

    def get_unit(self):
        return "kPa"

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return: 
        '''
        pass

    def execute(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        self.sleep(0.3)
        self.InitPeripheralConnection(self.PeripheralAddress)
        self.Peripheral = PeripheralConnection

        print "press.Peripheral = ", self.Peripheral
        while self.is_running():

            lock_CharRead.acquire()
            ch = self.Peripheral.getCharacteristics()
            temp = 0
            
            for c in ch:
                #print(str(c.uuid))

                if str(c.uuid) == self.CharPress:
                    if c.supportsRead():
                        s1 = c.read()
                        pressure = struct.unpack("<HH", s1)[0] /100.0
                        self.data_received(pressure)
                    break
                    
            lock_CharRead.release()
            self.sleep(5)
