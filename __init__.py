
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
lock_Data = threading.Lock()


class BLE_ReadSensorValues(threading.Thread):
    def __init__(self, peripheral, loopDelay):
        threading.Thread.__init__(self)
        self.peripheral = peripheral
        self.loopDelay = loopDelay
        self.delegate = SensorDelegate(0)
        peripheral.setDelegate(self.delegate)
        self.running = True

    def run(self):
        global PeripheralAddrName
        tryCount = 0
        print("starting thread... ", str(self))

        while self.running:

            if not PeripheralAddrName or not self.peripheral:
                print("Thread Not Connected", PeripheralAddrName, self.peripheral)            
                self.sleep(5)
            else:
                try:
                    if self.peripheral.waitForNotifications(self.loopDelay):
                        tryCount = 0
                        continue
                except Exception as e:
                    print("waitForNotifications:: ", str(e))

                tryCount += 1
                if tryCount > 10:
                    print("No Data Received")
                    tryCount = 0
    
    def ReadRawData(self, handle):
        data, ok = self.delegate.ReadRawData(handle)

        if not ok:
            print("BLE_ReadSensorValues::ReadRawData: no data returned for handle ", handle) 

        return data


class SensorDelegate(btle.DefaultDelegate):
    def __init__(self,params):
        btle.DefaultDelegate.__init__(self)
        self.handles = dict()

    def handleNotification(self,cHandle,data):
        global lock_Data
        #print("handling notification...")
        print("handle=",cHandle, data)

        lock_Data.acquire()
        try:
            self.handles[cHandle] = data
        finally:
            lock_Data.release()

    def ReadRawData(self, handle):
        print("ReadRawData")
        if handle in self.handles:
            #lock_Data.acquire()
            try:
                return self.handles[handle], True
            except Exception as e:
                print("Can't Read Raw Data: ", str(e))
            finally:
                pass#lock_Data.release()
        
        #print("no handle ",  handle)
        return b"", False

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
                self.sensorThread = BLE_ReadSensorValues(PeripheralConnection, 4)
                self.sensorThread.start()
            except Exception as e:
                self.sensorThread = ""
                print("Couldn't connect::", str(e))
            finally:
               lock_periphal.release()

    def enable_notify(self, peripheral,  chara_uuid):
        setup_data = b"\x01\x00"
        notify = peripheral.getCharacteristics(uuid=chara_uuid)[0]
        notify_handle = notify.getHandle() + 1
        peripheral.writeCharacteristic(notify_handle, setup_data, withResponse=True)
        return notify, notify.getHandle()

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
        self.sleep(0.1)
        self.characteristicName = self.GetCharacteristic()
        self.Characteristic, self.handle = self.enable_notify(self.Peripheral, self.characteristicName)
        print( "self.characteristicName, handle = ", self.characteristicName, self.Characteristic.getHandle() )

        while self.is_running():

            rawData = self.sensorThread.ReadRawData(self.handle)
            if rawData:
                data = self.UnpackData(rawData)
                self.data_received(data)
               
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
        print("Init_Global", cls)

 
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

    def UnpackData(self, data):
        val = struct.unpack("<HH", data)[0] / 100.0
        #if self.get_unit() == "°F":
        val = 9.0 / 5.0 * val + 32.0
        return round(val, 2)

    def get_unit(self):
        return self.SensorUnits

    def GetCharacteristic(self):
        return self.Characteristic

    def GetService(self):
        return self.ServiceAddress

    def GetPeripheral(self):
        return self.PeripheralAddress
