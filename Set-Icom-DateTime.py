#!/usr/bin/python3

# By Stewart G0LGS
# 04-Feb-2024

# based on https://github.com/Kurgan-/icom-set-time

# You will need pyserial

# This script sets the time slightly wrong because you cannot set seconds, only minutes.
# I prefer to set time a little incorrectly rather than to wait for up to 59 seconds

radio="7300"			# Set Radio Model
civaddress="0x94"		# Radio address (7300 = 0x94, 9700 = 0xA2).
baudrate = 115200		# Radio serial speed
serialport = "/dev/ic7300"  # Serial port of your radios serial interface.

# Import libraries we'll need to use
import time
import serial
import struct

if not radio in ['7300', '9700']:
	print ("Unsupported radio:",radio)
	exit(1)

# Get time in GMT. If you want local time change to "t = time.localtime()"
t = time.gmtime()

# extract strings for year, day, month, hour, minute
# with a leading zero if needed
year = str(t.tm_year)
month = str(t.tm_mon).rjust(2,'0')
day = str(t.tm_mday).rjust(2,'0')
hour = str(t.tm_hour).rjust(2,'0')
minute = str(t.tm_min).rjust(2,'0')

# Set Date first

if radio == "7300":
    command = ["0xFE", "0xFE", civaddress, "0xE0", "0x1A", "0x05" ]
    command.append("0x00")
    command.append("0x94")
if radio == "9700":
    command = ["0xFE", "0xFE", civaddress, "0xE0", "0x1A", "0x05" ]
    command.append("0x01")
    command.append("0x79")

command.append("0x"+year[0:2])
command.append("0x"+year[2:])
command.append("0x"+month)
command.append("0x"+day)
command.append("0xFD")

try:
	ser = serial.Serial(serialport, baudrate, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)

except serial.SerialException as e:
	if e.errno == 2:
		print( "No such port:", serialport)
		exit(1)
	else:
		print( "Unexpected error", e.errno )
		exit(1)

count = 0
while(count < 13):
    senddata = int(bytes(command[count], 'UTF-8'), 16)
    ser.write(struct.pack('>B', senddata))
    count = count +1

ser.close()

# Set Time

if radio == "7300":
    command = ["0xFE", "0xFE", civaddress, "0xE0", "0x1A", "0x05" ]
    command.append("0x00")
    command.append("0x95")
if radio == "9700":
    command = ["0xFE", "0xFE", civaddress, "0xE0", "0x1A", "0x05" ]
    command.append("0x01")
    command.append("0x80")

command.append("0x"+hour)
command.append("0x"+minute)
command.append("0xFD")

try:
	ser = serial.Serial(serialport, baudrate, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)

except serial.SerialException as e:
	if e.errno == 2:
		print( "No such port:", serialport)
		exit(1)
	else:
		print( "Unexpected error", e.errno )
		exit(1)

count = 0
while(count < 11):
    senddata = int(bytes(command[count], 'UTF-8'), 16)
    ser.write(struct.pack('>B', senddata))
    count = count +1

ser.close()

print( "Done")
