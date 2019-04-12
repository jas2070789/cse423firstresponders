import time
from bluepy.btle import Scanner, DefaultDelegate
from bluepy.btle import UUID, Peripheral
import bluepy.btle

device_name = "Fooguier X4"
device_addr = "none"
device_char_handle = "First Name"
device_char_UUID = 0x2A8A
char_read_interval = 1	#second
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
p = Peripheral(device_addr, "random", 0)
ch = p.getCharacteristics(uuid = UUID(device_char_UUID))[0]

result_txt = open("result.txt", "w")

i = 0
while i < 10:
	val = ch.read()
	print(val)
	result_txt.write(val.decode("utf-8") + "\n")
	time.sleep(char_read_interval)
	i = i + 1

result_txt.close()
p.disconnect()
