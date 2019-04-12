import time
from bluepy.btle import Scanner, DefaultDelegate
from bluepy.btle import UUID, Peripheral
import bluepy.btle

#modify the following constants according to the config of the wearable
device_name = "Fooguier X4"	
device_addr = "none"
device_addr_type = "random"
device_char_handle = "First Name"
device_char_UUID = 0x2A8A
char_read_interval = 1	#time inverval of reading data from the wearable, in [second]

print("Program running")

#scan target device by name
class ScanDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)
		
	def handleDiscovery(self, dev, new_dev, new_dat):
		if new_dev:
			pass
		if new_dat:
			pass
			
scanner = Scanner().withDelegate(ScanDelegate())

#looking for device using device name
device_found = 0
while device_found == 0:
	
	devices = scanner.scan(0.35)	
	for ii in devices:
		print(ii.addr, ii.getValueText(9))
		if ii.getValueText(9) == device_name:
			device_addr = ii.addr
			device_found = 1

print("device found")
print("device address: ", device_addr)

#connect to device
p = Peripheral(device_addr, device_addr_type, 0)

#modify if multiple characteristics are available
ch = p.getCharacteristics(uuid = UUID(device_char_UUID))[0]

#store results in text format
result_txt = open("result.txt", "w")

#repeatedly read data from the wearable and store it into the text file
while 1:
	val = ch.read()
	print(val)
	result_txt.write(val.decode("utf-8") + "\n")
	time.sleep(char_read_interval)

result_txt.close()
p.disconnect()
