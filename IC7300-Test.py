#!/usr/bin/python3

# By Stewart G0LGS
# 04-Feb-2024

# You will need the following libs:
#	pyserial

# This script sets the time slightly wrong because you cannot set seconds, only minutes.
# I prefer to set time a little incorrectly rather than to wait for up to 59 seconds

radio="7300"            # Set Radio Model
civaddress="0x94"        # Radio address (7300 = 0x94, 9700 = 0xA2).
baudrate = 115200        # Radio serial speed
serialport = "/dev/ic7300"  # Serial port of your radios serial interface.

debug=1

# Import libraries we'll need to use
import os
import sys
import time
import serial
import struct

def ic7300_get_frequency(ser):
    ser.write(b'\xfe\xfe\x94\x00\x03\xfd')

def ic7300_show_frequency(data):
    vals = [data[i].hex() for i in range (0, len(data))]
    cmd = ''.join(vals)
    print( "Frequency: " + cmd[10:11]+"."+cmd[11:12]+cmd[8:9]+cmd[9:10] + "." + cmd[6:7]+ cmd[7:8] + cmd[4:5] + "." + cmd[5:6]+ cmd[2:3] )

def ic7300_read(ser):
    s = ''
    while s != b'\xfe':
        if debug : print( "waiting for sync...." + ''.join("{:02x}".format(x) for x in s) )
        s = ser.read()
    if ser.read() == b'\xfe':
        if debug : print( "synced, packet info :")
        i = 0
        rxdata = []
        while s != b'\xfd':
            s = ser.read()
            if  i == 0 :
                if debug : print( "TO: " + ''.join(format(x, '02x') for x in s) )
            elif i == 1:
                if debug : print( "FROM: " + ''.join(format(x, '02x') for x in s) )
            else:
                rxdata.append(s)
                if debug : print( ''.join(format(x, '02x') for x in s) )
            i +=1
        rxdata.pop()
        return rxdata

	# Check for Timeout ?

def main():

    try:
        ser = serial.Serial(serialport, baudrate, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)

    except serial.SerialException as e:
        if e.errno == 2:
            print( "No such port:", serialport)
            exit(1)
        else:
            print( "Unexpected error", e.errno )
            exit(1)

    ic7300_get_frequency(ser)

#    s = ser.write(b'\xfe\xfe\x94\x00\x04\xfd')

    while True:
        dat = ic7300_read(ser)
        if len(dat) > 2:
            if dat[0] == b'\x00':
                ic7300_show_frequency(dat)
    #        elif dat[0] == "\x01":
    #            ic7300_show_mode(dat[1])
    #            ic7300_show_filter(dat[2])
    #        elif dat[0] == "\x02":
    #            ic7300_show_band_edge(dat)
            elif dat[0] == b'\x03':
                if debug : print( "Got frq (03) :")
                ic7300_show_frequency(dat)
    #        elif dat[0] == "\x04":
    #            ic7300_show_mode(dat[1])
    #            ic7300_show_filter(dat[2])
            elif dat[0] == b'\x06':
                    if debug : print( "set mode :")
            elif dat[0] == b'\x07':
                    if debug : print( "set vfo :")
            elif dat[0] == b'\x08':
                    if debug : print( "set mem :")
            else:
                print ( "Unknown Command (" +dat[0].hex() + ")")
                print (dat)

    ser.close()

    print( "Done")


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print( 'Interrupted' )
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
