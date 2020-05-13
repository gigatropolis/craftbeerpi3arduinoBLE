
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

class SensorDelegate(btle.DefaultDelegate):
    def __init__(self,params):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self,cHandle,data):
        print("handling notification...")
        print("handle=",cHandle)
        raw = struct.unpack("<HH",data)[0]
        if cHandle == 12:
            data = raw
        else:
            data = raw /100.0

        print("data", data)

class BLESensorBase(SensorActive):

    def InitPeripheralConnection(self, address):

        global PeripheralConnection
        global PeripheralAddrName
        global lock_periphal
        global lock_CharRead

        lock_periphal.acquire()

        if not PeripheralAddrName or not PeripheralConnection:

            print "connecting...."
            PeripheralAddrName = address
            try:
                PeripheralConnection = btle.Peripheral(address)
                print("PeripheralConnection=%s" % (str(PeripheralConnection)))
                PeripheralConnection.setDelegate(SensorDelegate(0))
            except:
                print("Couldn't connect")
            finally:
               lock_periphal.release()

    def enable_notify(p,  chara_uuid):
        setup_data = b"\x01\x00"
        notify = p.getCharacteristics(uuid=chara_uuid)[0]
        notify_handle = notify.getHandle() + 1
        p.writeCharacteristic(notify_handle, setup_data, withResponse=True)

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
                 if str(c.uuid) == self.GetCharacteristic():
                    if c.supportsRead():
                        rawData = c.read()
                        data = self.UnpackData(rawData)
                        self.data_received(data)
                    break
                    
            lock_CharRead.release()
            self.sleep(4)

    def UnpackData(self, data):
        return struct.unpack("<HH", data)[0] /100.0

    def GetCharacteristic(self):
        return ""

    def GetService(self):
        return ""

    def GetPeripheral(self):
        return ""

    @classmethod
    def init_global(cls):
        '''
        Called one at the startup for all sensors
        :return: 
        '''
        print("Init_Global")

 
@cbpi.sensor
class BLE_UnsignedInt(BLESensorBase):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, description="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, description="run blelisten.py: '1101....'")
    Characteristic = Property.Text("Characteristic Address", configurable=True, description="run blelisten.py '2201...'")
    SensorUnits = Property.Select("Sensor Units", options=["°", "°C", "°F", "kPa", "%"], description="Units to display for sensor")

    def UnpackData(seld, data):
        return struct.unpack("<HH", data)[0]

    def get_unit(self):
        return self.SensorUnits

    def GetCharacteristic(self):
        return self.Characteristic

    def GetService(self):
        return self.ServiceAddress

    def GetPeripheral(self):
        return self.PeripheralAddress


@cbpi.sensor
class BLE_Float(BLESensorBase):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, description="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, description="run blelisten.py: '1101....'")
    Characteristic = Property.Text("Characteristic Address", configurable=True, description="run blelisten.py '2201...'")
    SensorUnits = Property.Select("Sensor Units", options=["°", "°C", "°F", "kPa", "%"], description="Units to display for sensor")

    def UnpackData(seld, data):
        val = struct.unpack("<HH", data)[0] / 100.0
        if get_unit() == "°F":
            val = 9.0 / 5.0 * val + 32.0
        return val

    def get_unit(self):
        return self.SensorUnits

    def GetCharacteristic(self):
        return self.Characteristic

    def GetService(self):
        return self.ServiceAddress

    def GetPeripheral(self):
        return self.PeripheralAddress
