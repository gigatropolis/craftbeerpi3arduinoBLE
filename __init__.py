
import os, sys, threading, time
from modules import cbpi, app
from modules.core.hardware import SensorActive
from modules.core.props import Property
from bluepy import btle
import struct

@cbpi.sensor
class ArduinoTemperatureBLE(SensorActive):

    service_uuid = "00001101-0000-1000-8000-00805f9b34fb"
    char1_uuid = '00002101-0000-1000-8000-00805f9b34fb'
    char2_uuid = '00002102-0000-1000-8000-00805f9b34fb'
    charTemp_uuid = '00002104-0000-1000-8000-00805f9b34fb'

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, default_value="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, default_value="run blelisten.py: '1101....'")
    PeripheralAddress = Property.Text("Characteristic Address", configurable=True, default_value="run blelisten.py '2204...'")

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
        self.Peripheral = btle.Peripheral(ArduinoTemperatureBLE.PeripheralAddress)

        while self.is_running():

            ch = self.Peripheral.getCharacteristics()
            temp = 0
            for c in ch:
                #print(str(c.uuid))

                if str(c.uuid) == ArduinoTemperatureBLE.char1_uuid:
                    if c.supportsRead():
                        s1 = c.read()
                        temp = struct.unpack("<B", s1[0])[0] /100.0
                        if (self.get_unit() == "C"):
                            self.data_received(temp)
                        else:
                            self.data_received(9.0 / 5.0 * temp + 32.0)
 
                    self.sleep(5)

    @classmethod
    def init_global(cls):
        '''
        Called one at the startup for all sensors
        :return: 
        '''