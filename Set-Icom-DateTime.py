#!/usr/bin/env python3

# Copyright (c) Stewart Wilkinson (G0LGS)
# Created 07-Feb-2024
# Re-worked for Windows 06/04/2024

# Set Date/Time on Icom 7100/7300/9700 radio
#
# This script sets the time slightly wrong because you cannot set seconds, only minutes.
# I prefer to set time a little incorrectly rather than to wait for up to 59 seconds

# You will need to install the following libs:
#    pyserial

# Import libraries we'll need to use
import os
import sys
import time
import serial
import struct

# Set Radio Model (7100/7300/9700)
radio="7300"
# Radio address (7100= 0x88, 7300 = 0x94, 9700 = 0xA2).
radiociv="0x94"
# Radio serial speed
baud = 115200

# Serial port of your radios serial interface
# i.e Linux /dev/ttyUSB0 or Windows com3
if os.name == 'nt':
    serialport = "com3"
    import ctypes
else:
    serialport = "/dev/ttyUSB0"
    import logging
    from logging.handlers import SysLogHandler

# Note for Linux:
# You can set a serial port by id so that it always connect to the correct radio, which is
# usefeul if you have more than one usb serial port connected
#
#serialport="/dev/serial/by-id/usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge_Controller_IC-9700_12345678_A-if00-port0"
#serialport="/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_IC-7300_87654321-if00-port0"

# Set to True for LocalTime instead of default GMT
UseLocalTime=False

# Address for the 'controller' (this script) - change only if you have a conflict with one of your radios
myciv="0xc0"

# **** Nothing below should need to be changed ****
debug=False

def sendcmd(ser,cmd):
    count = 0

    if debug:
        print ( "Sending: ", cmd )

    while(count < len(cmd)):
        senddata = int(bytes(cmd[count], 'UTF-8'), 16)
        ser.write(struct.pack('>B', senddata))
        count = count +1

def GetResp(ser):
    s = ''
    while s != b'\xFE':
        if debug : print( "Waiting for sync...." + ''.join("{:02x}".format(x) for x in s) )
        s = ser.read()
        # Timeout?
        if len(s) == 0:
            break;

    if ser.read() == b'\xFE':
        if debug : print( "Synced, packet info :")
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
                if debug : print( "Data: " + ''.join(format(x, '02x') for x in s) )
            i +=1

        rxdata.pop()
        return rxdata

# check for Ack
def CheckAck(ser):
    timeout = time.time() + 5
    AckOk=0
    while AckOk==0:
        dat = GetResp(ser)

        if dat is None:
            # Do nothing
            if debug: print( "Timeout.." )
            time.sleep(0.1)

        else:
            if dat[0] == b'\xfb':
                if debug :
                    print( "Got Ack: " +dat[0].hex() )
                AckOk=1

        if time.time() > timeout:
            break

    return AckOk

def get_frequency(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x03", "0xFD" ]
    sendcmd(ser,cmd)

def show_frequency(data):
    vals = [data[i].hex() for i in range (0, len(data))]
    cmd = ''.join(vals)
    print( "Frequency: " + cmd[10:11]+"."+cmd[11:12]+cmd[8:9]+cmd[9:10] + "." + cmd[6:7]+ cmd[7:8] + cmd[4:5] + "." + cmd[5:6]+ cmd[2:3] )

# 7100 Time / Date Functions
def ic7100_get_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x20", "0xFD" ]
    sendcmd(ser,cmd)

def ic7100_set_date(ser):
    global year
    global month
    global day
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x20" ]
    cmd.append("0x"+year[0:2])
    cmd.append("0x"+year[2:])
    cmd.append("0x"+month)
    cmd.append("0x"+day)
    cmd.append("0xFD")
    if debug: print ("Setting Date")
    sendcmd(ser,cmd)

def ic7100_get_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x21", "0xFD" ]
    sendcmd(ser,cmd)

def ic7100_set_time(ser):
    global hour
    global minute
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x21" ]
    cmd.append("0x"+hour)
    cmd.append("0x"+minute)
    cmd.append("0xFD")
    if debug: print ("Setting Time")
    sendcmd(ser,cmd)

# 7300 Time / Date Functions
def ic7300_get_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x94", "0xFD" ]
    sendcmd(ser,cmd)

def ic7300_set_date(ser):
    global year
    global month
    global day
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x94" ]
    cmd.append("0x"+year[0:2])
    cmd.append("0x"+year[2:])
    cmd.append("0x"+month)
    cmd.append("0x"+day)
    cmd.append("0xFD")
    if debug: print ("Setting Date")
    sendcmd(ser,cmd)

def ic7300_get_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x95", "0xFD" ]
    sendcmd(ser,cmd)

def ic7300_set_time(ser):
    global hour
    global minute
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x95" ]
    cmd.append("0x"+hour)
    cmd.append("0x"+minute)
    cmd.append("0xFD")
    if debug: print ("Setting Time")
    sendcmd(ser,cmd)

# 9700 Time / Date Functions
def ic9700_get_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x79", "0xFD"]
    sendcmd(ser,cmd)

def ic9700_set_date(ser):
    global year
    global month
    global day
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
    global hour
    global minute
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x80" ]
    cmd.append("0x"+hour)
    cmd.append("0x"+minute)
    cmd.append("0xFD")
    sendcmd(ser,cmd)


def main():
    global year
    global month
    global day
    global hour
    global minute

    if os.name != 'nt':
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.handlers.SysLogHandler(facility=SysLogHandler.LOG_DAEMON, address = '/dev/log')
        formatter = logging.Formatter(
            fmt="%(filename)s:%(funcName)s:%(lineno)d %(levelname)s %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if not radio in ['7100', '7300', '9700']:
        if os.name != 'nt':
            sys.stderr.write( "ERROR: Unsupported radio: " + radio +"\n" )
            logger.warning( "Unsupported radio: " + radio )
        else:
            ctypes.windll.user32.MessageBoxW(0, "Unsupported radio: " + radio, "Icom TimeSync", 0)
        exit(1)

    # Exit Code
    ExitCode=0

    # Get time (defaut is GMT)
    if UseLocalTime:
        t = time.localtime()
    else:
        t = time.gmtime()

    # extract strings for year, day, month, hour, minute
    # with a leading zero if needed
    year = str(t.tm_year)
    month = str(t.tm_mon).rjust(2,'0')
    day = str(t.tm_mday).rjust(2,'0')
    hour = str(t.tm_hour).rjust(2,'0')
    minute = str(t.tm_min).rjust(2,'0')

    if os.name != 'nt':
        try:
            ser = serial.Serial(port=serialport, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=0, rtscts=0)

        except serial.SerialException as serErr:
            if serErr.errno == 2:
                sys.stderr.write( "ERROR: No such port: " + serialport + "\n" )
                logger.warning( "No such port: " + serialport )
                exit(1)
            if serErr.errno == 16:
                sys.stderr.write( "ERROR: port: " + serialport + " busy\n" )
                logger.warning( "Port: " + serialport + " busy" )
                exit(1)
            else:
                sys.stderr.write( "Unexpected error: " + str(serErr.errno) + "\n" )
                logger.warning( "Unexpected error: " + str(serErr.errno) )
                exit(1)
    else:
        try:
            ser = serial.Serial(port=serialport, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=0, rtscts=0)

        except serial.SerialException as serErr:
            ctypes.windll.user32.MessageBoxW(0, str(serErr), "Icom TimeSync", 0)
            exit(1)

    if debug : print ("Testing radio communications")
    # Try reading frequency
    get_frequency(ser)

    # Listen for Response (with Timeout)
    timeout = time.time() + 5
    CmdOk=0
    while CmdOk==0:
        dat = GetResp(ser)

        if dat is None:
            # Do nothing
            if debug: print( "Timeout.." )
            time.sleep(0.1)

        elif len(dat) > 2:

            if dat[0] == b'\x03':
                if debug:
                    print( "Got (03) :")
                    show_frequency(dat)
                CmdOk=1

            # Ack
            elif dat[0] == b'\xfb':
                if debug: print( "Got (FB) :")
                CmdOk=1

            else:
                if debug: print ( "Unexpected response (" +dat[0].hex() + ")")
                vals = [dat[i].hex() for i in range (0, len(dat))]
                cmd = ';'.join(vals)
                print (cmd)

        if time.time() > timeout:
            break

    if CmdOk:
        if debug: print( radio +" Got response from radio")
    else:
        ser.close()
        if os.name != 'nt':
            sys.stderr.write( "ERROR: No/Unexpected response from " + radio + " on " + serialport + "\n" )
            logger.warning( "No/Unexpected response from " + radio + " on " + serialport )
        else:
            ctypes.windll.user32.MessageBoxW(0, "No/Unexpected response from " + radio + " on " + serialport, "Icom TimeSync", 1)
        exit(2)

    if radio == "7100":
            ic7100_set_date(ser)
            if not CheckAck(ser):
                ExitCode=3
            else:
                ic7100_set_time(ser)
                if not CheckAck(ser):
                    ExitCode=4

    elif radio == "7300":
            ic7300_set_date(ser)
            if not CheckAck(ser):
                ExitCode=3
            else:
                ic7300_set_time(ser)
                if not CheckAck(ser):
                    ExitCode=4

    elif radio == "9700":
            ic9700_set_date(ser)
            if not CheckAck(ser):
                ExitCode=3
            else:
                ic9700_set_time(ser)
                if not CheckAck(ser):
                    ExitCode=4

    ser.close()

    if ExitCode == 0:
        if os.name != 'nt':
            print('Ok')
            logger.info( "Sucessfully set DateTime on " + radio )
        else:
            ctypes.windll.user32.MessageBoxW(0, "Sucessfully set DateTime on " + radio, "Icom TimeSync", 0)
    else:
        if os.name != 'nt':
            sys.stderr.write( "ERROR: No/Unexpected reponse from Radio\n" )
            logger.warning( "No/Unexpected response from " + radio + " on " + serialport )
        else:
            ctypes.windll.user32.MessageBoxW(0, "No/Unexpected response from " + radio + " on " + serialport, "Icom TimeSync", 0)

    exit(ExitCode)

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        sys.stderr.write( "Interrupted\n" )
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
