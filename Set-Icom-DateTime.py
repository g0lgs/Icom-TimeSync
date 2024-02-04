#!/usr/bin/env python3

# based on that from https://github.com/Kurgan-/icom-set-time

# You will need pyserial

# This script sets the time slightly wrong because you cannot set seconds, only minutes.

radio="7300"			# Set Radio Model
civaddress="0x94"		# Radio address (7300 = 0x94, 9700 = 0xA2).
baudrate = 115200		# Radio serial speed
serialport = "/dev/ic7300"  # Serial port of your radios serial interface. See comment below

# you can set a serial port by id so that it always connect to the correct radio, usefeul if you have more than
# one usb serial port connected (I have 8 of them)
#serialport = "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_IC-7300_03005669-if00-port0"

#Import libraries we'll need to use
import time
import serial
import struct

if not radio in ['7300', '9700']:
	print ("Unknown radio ".radio)
	exit

# Get time in GMT. If you want local time change to "t = time.localtime()"
t = time.gmtime()

# extract strings for year, day, month, hour, minute
# with a leading zero if needed
year = str(t.tm_year)
month = str(t.tm_mon).rjust(2,'0')
day = str(t.tm_mday).rjust(2,'0')
hour = str(t.tm_hour).rjust(2,'0')
minute = str(t.tm_min).rjust(2,'0')

# set date
if radio == "7300":
    command = ["0xFE", "0xFE", civaddress, "0xE0", "0x1A", "0x05", "0x00" ]
    command.append("0x94")
if radio == "9700":
    command = ["0xFE", "0xFE", civaddress, "0xE0", "0x1A", "0x05", "0x01" ]
    command.append("0x79")

command.append("0x"+year[0:2])
command.append("0x"+year[2:])
command.append("0x"+month)
command.append("0x"+day)
command.append("0xFD")

ser = serial.Serial(serialport, baudrate)
count = 0
while(count < 13):
    senddata = int(bytes(command[count], 'UTF-8'), 16)
    ser.write(struct.pack('>B', senddata))
    count = count +1
ser.close()

# set time
# you CANNOT set seconds, so unless you want to wait for the minute mark
# you'll end up with a time that is set incorrectly by less than one minute
# I prefer to set time incorrectly than to wait for up to 59 seconds

if radio == "7300":
    command = ["0xFE", "0xFE", civaddress, "0xE0", "0x1A", "0x05", "0x00" ]
    command.append("0x95")
if radio == "9700":
    command = ["0xFE", "0xFE", civaddress, "0xE0", "0x1A", "0x05", "0x01" ]
    command.append("0x80")

command.append("0x"+hour)
command.append("0x"+minute)
command.append("0xFD")

ser = serial.Serial(serialport, baudrate)
count = 0
while(count < 11):
    senddata = int(bytes(command[count], 'UTF-8'), 16)
    ser.write(struct.pack('>B', senddata))
    count = count +1
ser.close()

