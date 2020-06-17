from bluepy import btle
import struct
import time

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
        #print("handling notification...")
        #print("handle=",cHandle)
        raw = struct.unpack("<HH",data)[0]
        if cHandle == 12:
            data = raw
        elif cHandle == 15:
            data = raw /100.0
            data = round(9.0 / 5.0 * data + 32.0, 2)
        else:
            data = raw /100.0

        print("(%d) data=" % (cHandle), data)

def enable_notify(p,  chara_uuid):
    setup_data = b"\x01\x00"
    notify = p.getCharacteristics(uuid=chara_uuid)[0]
    notify_handle = notify.getHandle() + 1
    p.writeCharacteristic(notify_handle, setup_data, withResponse=True)
    time.sleep(1)

p = btle.Peripheral('dd:ee:d7:d2:ac:74', addrType=btle.ADDR_TYPE_PUBLIC)
p.setDelegate(MyDelegate(0))

print("Connected")
time.sleep(2)

chars = [char1_uuid, charTemp_uuid, charHum_uuid, charPress_uuid]
for char in chars:
    connected = False
    while not connected:
        try:
            enable_notify(p, char)
            connected = True
        except btle.BTLEDisconnectError:
            print("disconnect error...", char)
            p.disconnect()
            time.sleep(5)
            p = None
            time.sleep(5)
            p = btle.Peripheral('dd:ee:d7:d2:ac:74', addrType=btle.ADDR_TYPE_PUBLIC)
            #raise
            #time.sleep(5)

#enable_notify(p, char1_uuid)
#enable_notify(p, charTemp_uuid)
#enable_notify(p, charHum_uuid)
#enable_notify(p, charPress_uuid)

#svc = p.getServiceByUUID( service_uuid )
#chs = svc.getCharacteristics()
#for c in chs:
#    print c.valHandle

while True:
    try:
        if p.waitForNotifications(4.5):
            continue
        print("waiting...")
        #print("Chars ", p.getCharacteristics())
        continue
    except:
        p.disconnect()

        raise

    ch = p.getCharacteristics()
    for c in ch:
        print(str(c.uuid))

        if str(c.uuid) == char1_uuid:
            if c.supportsRead():
                s1 = c.read()
                #print("reading ch1: ", s1, struct.unpack("<B", s1[0])[0])
                print("reading ch1: ", s1, struct.unpack("<HH", s1)[0])
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
