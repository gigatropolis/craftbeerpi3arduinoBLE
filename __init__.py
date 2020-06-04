
# -*- coding: utf-8 -*-
import os, sys, threading, time
from modules import cbpi, app
from modules.core.hardware import SensorPassive
from modules.core.props import Property
from bluepy import btle
import struct

PeripheralConnection = None
PeripheralAddrName = ""
SensorThread = None
lock_periphal = threading.Lock()
lock_SetNotify = threading.Lock()
lock_Data = threading.Lock()

def InitPeripheralConnection(cls, address):

    global PeripheralConnection
    global PeripheralAddrName
    global SensorThread
    global lock_periphal
    global lock_CharRead

    tries = 0
    #lock_periphal.acquire()
    try:
        while not PeripheralAddrName and not PeripheralConnection and tries < 10:

            print( "connecting to %s ...." % (address))
            try:
                if SensorThread:
                    print("Found  SensorThread. Killing...")
                    SensorThread.running = False
                    time.sleep(5)

                PeripheralConnection = btle.Peripheral(address)
                print("PeripheralConnection=%s" % (str(PeripheralConnection)))
                SensorThread = BLE_ReadSensorValues(PeripheralConnection, 4)
                SensorThread.start()
                PeripheralAddrName = address
                time.sleep(3)
            except Exception as e:
                if SensorThread:
                    SensorThread.running = False

                print("InitPeripheralConnection::Couldn't connect::", str(e))
                tries += 1
                print("connection attempt %d (%s)" % (tries + 1, str(cls)))
                time.sleep(1)
    finally:
        pass
        #lock_periphal.release()


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
        global PeripheralConnection
        tryCount = 0
        print("starting thread... %s" % (str(self)))

        while self.running:

            if not PeripheralAddrName or not self.peripheral or not PeripheralConnection:
                print("Thread Not Connected", PeripheralAddrName, self.peripheral)            
                
                time.sleep(5)
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
                time.sleep(5)

    def stop(self):
        self.running = False

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

        #lock_Data.acquire()
        try:
            self.handles[cHandle] = data
        finally:
            pass
            #lock_Data.release()

    def ReadRawData(self, handle):
        print("ReadRawData", handle, str(self))
        data = b""
        ok = False

        if handle in self.handles:
            lock_Data.acquire()
            try:
                data = self.handles[handle], True
                ok = True
            except Exception as e:
                print("Can't Read Raw Data: ", str(e))
            finally:
                #pass
                lock_Data.release()
        
        #print("no handle ",  handle)
        return data, ok

@cbpi.sensor
class BLESensor(SensorPassive):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, description="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, description="run blelisten.py: '1101....'")
    Characteristic = Property.Text("Characteristic Address", configurable=True, description="run blelisten.py '2201...'")
    SensorUnits = Property.Select("Sensor Units", options=["°", "°C", "F", "kPa", "%"], description="Units to display for sensor")
    DataType = Property.Select("Data Type", options = ["BLE Float", "BLE Integer", "BLE String"] )
    
    def init(self):
        global PeripheralConnection
        global SensorThread

        self.sensorThread = None
        print("init::%s" % (str(self)))

        if not SensorThread:
            print("init::No sensor thread", str(self))
            return
        
        if not PeripheralConnection:
            print("init::no PeripheralConnection", str(self))
            return

        self.peripheral = PeripheralConnection
        self.sensorThread = SensorThread

        self.characteristicName = self.Characteristic
        self.Char, self.handle = self.enable_notify(self.peripheral, self.characteristicName)
        #print( "self.characteristicName, handle = ", self.characteristicName, self.Char.getHandle() )

    def get_unit(self):
        return self.SensorUnits

    def GetCharacteristic(self):
        return str(self.Characteristic)

    def GetService(self):
        return self.ServiceAddress

    def GetPeripheral(self):
        return self.PeripheralAddress

    def enable_notify(self, peripheral,  chara_uuid):
        global lock_SetNotify
        print("enable_notify::chara_uuid=%s" % (chara_uuid))
        notify, handle = None, None
        lock_SetNotify.acquire()
        try:
            setup_data = b"\x01\x00"
            notify = peripheral.getCharacteristics(uuid=chara_uuid)[0]
            notify_handle = notify.getHandle() + 1
            peripheral.writeCharacteristic(notify_handle, setup_data, withResponse=True)
            handle = notify.getHandle()
        except Exception as e:
            print("Can't enable_notify: ", str(e))
        finally:
            lock_SetNotify.release()
            
        return notify, handle

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return: 
        '''
        pass

    def read(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        global PeripheralConnection
        global SensorThread

        #print("read()::%s" % (str(self)))

        connected = False
        if PeripheralConnection and self.PeripheralAddress:
            connected = True

        tries = 0
        while not connected and tries < 10:
            print("connection attempt %d (%s)" % (tries+1, str(self)))
            InitPeripheralConnection(None,self.PeripheralAddress)
            self.peripheral = PeripheralConnection
            if not PeripheralConnection:
                self.sleep(4)
                tries += 1
                continue

            connected = True

        if not self.sensorThread:
            print("read::no sensorThread %s" % (str(self)))
            return

        rawData, ok = self.sensorThread.ReadRawData(self.handle)
        #print(ok, "self.DataType=", self.DataType, "handle=",self.handle, "raw=", rawData)
        data = 0.0
        try:
            if rawData:
                if self.DataType == u"BLE Integer":
                    data = self.UnpackData(rawData)
                elif self.DataType == u"BLE Float":
                    data = self.UnpackDataFloat(rawData)
                else:
                    print("DataType Not Found")
                    data = self.UnpackDataFloat(rawData)
        except Exception as e:
            print("Can't unpack: ", str(e))

        #print("data=", data)
        try:
            self.data_received(round(data, 2))
        except Exception as e:
            print("Can't Send Data ", str(e))
        
    def UnpackData(self, data):
        return struct.unpack("<HH", data)[0]

    def UnpackDataFloat(self, data):
        val = struct.unpack("<HH", data)[0] / 100.0

        if self.get_unit() == "F": #"°F":
            val = 9.0 / 5.0 * val + 32.0

        #print("UnpackDataFloat=", val)
        return round(val, 2)

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
        global PeripheralConnection
        global SensorThread

        print("Init_Global", cls)
        InitPeripheralConnection(cls, 'dd:ee:d7:d2:ac:74')

        if not PeripheralConnection:
            print("Connection Not made")
 