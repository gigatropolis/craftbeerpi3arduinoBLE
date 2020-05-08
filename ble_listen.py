from bluepy import btle
import struct

service_uuid = "00001101-0000-1000-8000-00805f9b34fb"
char1_uuid = '00002101-0000-1000-8000-00805f9b34fb'
char2_uuid = '00002102-0000-1000-8000-00805f9b34fb'
charTemp_uuid = '00002104-0000-1000-8000-00805f9b34fb'
charHum_uuid = '00002105-0000-1000-8000-00805f9b34fb'
charPress_uuid = '00002106-0000-1000-8000-00805f9b34fb'

class MyDelegate(btle.DefaultDelegate):
    def __init__(self,params):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self,cHandle,data):
        print("handling notification...")
        print("handle=",cHandle)
        print(struct.unpack("b",data))

p = btle.Peripheral('dd:ee:d7:d2:ac:74')
p.setDelegate(MyDelegate(0))
#svc = p.getServiceByUUID( service_uuid )

while True:
    if p.waitForNotifications(0.25):
        continue
    print("waiting...")
    #print(p.getCharacteristics())

    ch = p.getCharacteristics()
    for c in ch:
        #print(str(c.uuid))

        if str(c.uuid) == char1_uuid:
            if c.supportsRead():
                s1 = c.read()
                print("reading ch1: ", s1, struct.unpack("<B", s1[0])[0])
            else:
                print("Not Supported")

        if str(c.uuid) == char2_uuid:
            if c.supportsRead():
                s2 = c.read()
                print("reading ch2: ", s2, struct.unpack("<B", s2[0])[0])
            else:
                print("Not Supported")

        if str(c.uuid) == charTemp_uuid:
            if c.supportsRead():
                s3 = c.read()
                temperature = struct.unpack("<HH", s3)[0] / 100.0
                print("reading temp: ", s3, temperature, 9.0 / 5.0 * temperature + 32.0)
            else:
                print("Not Supported")

        if str(c.uuid) == charHum_uuid:
            if c.supportsRead():
                s4 = c.read()
                hum = struct.unpack("<HH", s4)[0] / 100.0
                print("reading humidity: ", s4, hum)
            else:
                print("Not Supported")

        if str(c.uuid) == charPress_uuid:
            if c.supportsRead():
                s5 = c.read()
                press = struct.unpack("<HH", s5)[0] / 100.0
                print("reading press: ", s5, press)
            else:
                print("Not Supported")
