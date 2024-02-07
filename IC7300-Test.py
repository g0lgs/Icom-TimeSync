#!/usr/bin/python3

# By Stewart G0LGS
# Feb-2024

# Set Date/Time on Icom 7300/9700 radio
# This script sets the time slightly wrong because you cannot set seconds, only minutes.
# I prefer to set time a little incorrectly rather than to wait for up to 59 seconds

# You will need the following libs:
#    pyserial

# Set Radio Model
radio="7300"
# Radio address (7300 = 0x94, 9700 = 0xA2).
radiociv="0x94"
# Radio serial speed
baudrate = 115200
# Serial port of your radios serial interface.
serialport = "/dev/ttyUSB0"

# **** Nothing below should need to be changed ****
myciv="0xc0"
debug=1

# Import libraries we'll need to use
import os
import sys
import time
import serial
import struct

def sendcmd(ser,cmd):
    count = 0
    while(count < len(cmd)):
        senddata = int(bytes(cmd[count], 'UTF-8'), 16)
        ser.write(struct.pack('>B', senddata))
        count = count +1

def getresp(ser):
    s = ''
    while s != b'\xFE':
        if debug : print( "waiting for sync...." + ''.join("{:02x}".format(x) for x in s) )
        s = ser.read()
        # Timeout?
        if len(s) == 0:
            break;

    if ser.read() == b'\xfe':
        if debug : print( "synced, packet info :")
        i = 0
        rxdata = []
        while s != b'\xFD':
            s = ser.read()
            if  i == 0 :
                if debug : print( "TO: " + ''.join(format(x, '02x') for x in s) )
            elif i == 1:
                if debug : print( "FROM: " + ''.join(format(x, '02x') for x in s) )
            else:
                rxdata.append(s)
                if debug>1 : print( "Data: " + ''.join(format(x, '02x') for x in s) )
            i +=1

        rxdata.pop()
        return rxdata

def get_frequency(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x03", "0xFD" ]
    sendcmd(ser,cmd)

def show_frequency(data):
    vals = [data[i].hex() for i in range (0, len(data))]
    cmd = ''.join(vals)
    print( "Frequency: " + cmd[10:11]+"."+cmd[11:12]+cmd[8:9]+cmd[9:10] + "." + cmd[6:7]+ cmd[7:8] + cmd[4:5] + "." + cmd[5:6]+ cmd[2:3] )

# 7300 Time / Date Functions
def ic7300_get_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x94", "0xFD" ]
    sendcmd(ser,cmd)

def ic7300_set_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x94" ]
    cmd.append("0x"+year[0:2])
    cmd.append("0x"+year[2:])
    cmd.append("0x"+month)
    cmd.append("0x"+day)
    cmd.append("0xFD")

def ic7300_get_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x95", "0xFD" ]
    sendcmd(ser,cmd)

def ic7300_set_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x95" ]
    cmd.append("0x"+hour)
    cmd.append("0x"+minute)
    cmd.append("0xFD")
    sendcmd(ser,cmd)

# 9700 Time / Date Functions
def ic9700_get_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x79", "0xFD"]
    sendcmd(ser,cmd)

def ic9700_set_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x79" ]
    cmd.append("0x"+year[0:2])
    cmd.append("0x"+year[2:])
    cmd.append("0x"+month)
    cmd.append("0x"+day)
    cmd.append("0xFD")
    sendcmd(ser,cmd)

def ic9700_get_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x80", "0xFD" ]
    sendcmd(ser,cmd)

def ic9700_set_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x80" ]
    cmd.append("0x"+hour)
    cmd.append("0x"+minute)
    cmd.append("0xFD")
    sendcmd(ser,cmd)


def main():

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

    try:
        ser = serial.Serial(serialport, baudrate, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=0, rtscts=0)

    except serial.SerialException as e:
        if e.errno == 2:
            print( "No such port:", serialport )
            exit(1)
        else:
            print( "Unexpected error", e.errno )
            exit(1)

    # Try reading frequency
    get_frequency(ser)

    # Listen for Response (with Timeout)
    timeout = time.time() + 10
    RadioOk=0
    while RadioOk==0:
        dat = getresp(ser)

        if dat is None:
            # Do nothing
            time.sleep(0.1)

        elif len(dat) > 2:

            if dat[0] == b'\x03':
                if debug : print( "Got Freq (03) :")
                show_frequency(dat)
                RadioOk=1

            else:
                print ( "Unexpected response (" +dat[0].hex() + ")")
                vals = [dat[i].hex() for i in range (0, len(dat))]
                cmd = ';'.join(vals)
                print (cmd)

        if time.time() > timeout:
            break

    if RadioOk:
        if debug: print( radio +" Radio Responded Ok")
    else:
        print( "ERROR: No response from " + radio + " on " + serialport )
        ser.close()
        exit(1)

    if radio == "7300":
            ic7300_set_date(ser)
            # Todo Check return

            ic7300_set_time(ser)
            # Todo Check return

    elif radio == "9700":
            ic9700_set_date(ser)
            # Todo Check return

            ic9700_set_time(ser)
            # Todo Check return

    if debug: print( "Done")

    ser.close()

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print( 'Interrupted' )
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
