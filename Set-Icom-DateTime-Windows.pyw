#!/usr/bin/env python3

# Copyright (c) 2024 Stewart Wilkinson (G0LGS)

# Set Date/Time on Icom 7100/7300/9700 radio
#
# This script sets the time slightly wrong because you cannot set seconds, only minutes.
# I prefer to set time a little incorrectly rather than to wait for up to 59 seconds

# You will need to install the following libs:
#    pyserial

import sys
import platform

if platform.system() != 'Windows':
    print("Sorry: This Version only works in Windows - Use 'Set-Icom-DateTime.py' for use in Linux")
    input("Press Enter to Exit...")
    sys.exit(1)

# Default Values (pass command line options or edit here to suit)
# Set Radio Model (7100/7300/9700)
radio="7300"
# Radio address (7100= 0x88, 7300 = 0x94, 9700 = 0xA2).
radiociv="0x94"
# Radio serial speed
baud = 115200

# Serial port of your radios serial interface (i.e com3)
serialport = "com5"

# Import libraries we'll need to use
import os
import getopt
import time
import serial
import struct
import ctypes

# Set to True for LocalTime instead of default GMT
UseLocalTime=False

# Supported Radios and Baud Rates
Radios="7100 7300 9700"
Bauds=[4800,9600,19200,38400,57600,115200]

# Address for the 'controller' (this script) - change only if you have a conflict with one of your radios
myciv="0xc0"

# **** Nothing below should need to be changed ****
debug=False

IsPYW=False
if ".pyw" in sys.argv[0]:
    IsPYW=True

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
        if debug: print( "Waiting for sync...." + ''.join("{:02x}".format(x) for x in s) )
        s = ser.read()
        # Timeout?
        if len(s) == 0:
            break;

    if ser.read() == b'\xFE':
        if debug: print( "Synced, packet info :")
        i = 0
        rxdata = []
        while s != b'\xFD':
            s = ser.read()
            if  i == 0 :
                if debug: print( "TO: " + ''.join(format(x, '02x') for x in s) )
            elif i == 1:
                if debug: print( "FROM: " + ''.join(format(x, '02x') for x in s) )
            else:
                rxdata.append(s)
                if debug: print( "Data: " + ''.join(format(x, '02x') for x in s) )
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
                if debug:
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

def Usage():
    print ( "Usage: " + sys.argv[0] + "--radio <Radio_Model> --address <Radio_CIV_Address> --port <Serial_Port> --baud <Baud_Rate> --localtime")

def main(argv):
    global year
    global month
    global day
    global hour
    global minute
    global radio
    global radiociv
    global baud
    global serialport
    global UseLocalTime
    global debug

    NoPrompt=False

    try:
        opts, args = getopt.getopt(argv,"?hr:c:p:b:ldn",["help","debug","radio=","civ=","port=","baud=","localtime","noprompt"])

    except getopt.GetoptError as Err:
        if IsPYW:
            ctypes.windll.user32.MessageBoxW(0, str(Err), "Icom TimeSync " +radio, 16)
        else:
            print( Err )
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-?", "-h", "--help"):
            Usage()
            sys.exit()

        elif opt in ("-n", "--noprompt"):
            NoPrompt=True

        elif opt in ("-d", "--debug"):
            debug=True

        elif opt in ("-l", "--localtime"):
            UseLocalTime=True

        elif opt in ("-r", "--radio"):
            radio = arg
            if ( radio not in Radios ):
                if IsPYW:
                    ctypes.windll.user32.MessageBoxW(0, f'Sorry Radio ({radio}) is not valid (acceptable are {Radios})', "Icom TimeSync " +radio, 16)
                else:
                    print ( f'Sorry Radio ({radio}) is not valid (acceptable are {Radios})' )
                sys.exit()

        elif opt in ("-c", "--civ"):
            radiociv = arg
            try:
                civ = int(radiociv, 16)
            except ValueError:
                if IsPYW:
                    ctypes.windll.user32.MessageBoxW(0, f'Sorry CIV Address ({radiociv}) is not valid Hex', "Icom TimeSync " +radio, 16)
                else:
                    print ( f'Sorry CIV Address ({radiociv}) is not valid Hex' )
                sys.exit()
            else:
                if civ > 255:
                    if IsPYW:
                        ctypes.windll.user32.MessageBoxW(0, f'Sorry CIV Address ({radiociv}) is out of range (0x00 to 0xff)', "Icom TimeSync " +radio, 16)
                    else:
                        print ( f'Sorry CIV Address ({radiociv}) is out of range (0x00 to 0xff)' )
                    sys.exit()
                if civ == int(myciv, 16):
                    if IsPYW:
                        ctypes.windll.user32.MessageBoxW(0, f'Sorry CIV Address ({radiociv}) is reserved (controller)', "Icom TimeSync " +radio, 16)
                    else:
                        print ( f'Sorry CIV Address ({radiociv}) is reserved (controller)' )
                    sys.exit()

        elif opt in ("-p", "--port"):
            serialport = arg

        elif opt in ("-b", "--baud"):
            baud = arg
            try:
                baud=int(baud)

            except ValueError:
                if IsPYW:
                    ctypes.windll.user32.MessageBoxW(0, f'Sorry Baud-rate ({baud}) is not valid number', "Icom TimeSync " +radio, 16)
                else:
                    print ( f'Sorry Baud-rate ({baud}) is not valid number' )
                sys.exit()

            else:
                if baud not in Bauds:
                    if IsPYW:
                        ctypes.windll.user32.MessageBoxW(0, f'Sorry Baud-rate ({baud}) is not valid (acceptable rates are {Bauds})', "Icom TimeSync " +radio, 16)
                    else:
                        print ( f'Sorry Baud-rate ({baud}) is not valid (acceptable rates are {Bauds})' )
                    sys.exit()

    # Additional Checks (in case Script Defaults have been broken)
    if radio not in Radios:
        if IsPYW:
            ctypes.windll.user32.MessageBoxW(0, f'Sorry Radio ({radio}) is not valid (acceptable are {Radios})', "Icom TimeSync " +radio, 16)
        else:
            print ( f'Sorry Radio ({radio}) is not valid (acceptable are {Radios})' )
        sys.exit(1)

    if baud not in Bauds:
        if IsPYW:
            ctypes.windll.user32.MessageBoxW(0, f'', "Icom TimeSync " +radio, 16)
        else:
            print ( f'Sorry Baud-rate ({baud}) is not valid (acceptable rates are {Bauds})' )
        sys.exit()

    try:
        civ = int(radiociv, 16)
    except ValueError:
        if IsPYW:
            ctypes.windll.user32.MessageBoxW(0, f'', "Icom TimeSync " +radio, 16)
        else:
            print ( f'Sorry CIV Address ({radiociv}) is not valid Hex' )
        sys.exit()
    else:
        if civ > 255:
            if IsPYW:
                ctypes.windll.user32.MessageBoxW(0, f'', "Icom TimeSync " +radio, 16)
            else:
                print ( f'Sorry CIV Address ({radiociv}) is out of range (0x00 to 0xff)' )
            sys.exit()
        if civ == int(myciv, 16):
            if IsPYW:
                ctypes.windll.user32.MessageBoxW(0, f'', "Icom TimeSync " +radio, 16)
            else:
                print ( f'Sorry CIV Address ({radiociv}) is reserved (controller)' )
            sys.exit()

    if NoPrompt==False:
        res = ctypes.windll.user32.MessageBoxW(0, "Are you ready to set Date/Time on " + radio, "Icom TimeSync " + radio, 36)
        if res == 7: # No Button
            sys.exit(1)

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

    try:
        ser = serial.Serial(port=serialport, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=0, rtscts=0)

    except serial.SerialException as serErr:
        if IsPYW:
            ctypes.windll.user32.MessageBoxW(0, str(serErr) + "\n\n(The port may already be in use)", "Icom TimeSync", 16)
        else:
            print( str(serErr) + "\n(The port may already be in use)" )
        sys.exit(1)

    print ("Testing radio communications")
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
        print( "Ok - Got response from " + radio )
    else:
        ser.close()
        if IsPYW:
            ctypes.windll.user32.MessageBoxW(0, "No/Unexpected response from " + radio + " on " + serialport, "Icom TimeSync " + radio, 17)
        else:
            print( "No/Unexpected response from " + radio + " on " + serialport )
        sys.exit(2)

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
        if IsPYW:
            ctypes.windll.user32.MessageBoxW(0, "Sucessfully set DateTime on " + radio, "Icom TimeSync " + radio, 64)
        else:
            print( "Sucessfully set DateTime on " + radio)
    else:
        if IsPYW:
            ctypes.windll.user32.MessageBoxW(0, "No/Unexpected response from " + radio + " on " + serialport, "Icom TimeSync " + radio, 16)
        else:
            print( "No/Unexpected response from " + radio + " on " + serialport )

    sys.exit(ExitCode)

if __name__ == "__main__":
    try:
        main(sys.argv[1:])

    except KeyboardInterrupt:
        sys.stderr.write( "Interrupted\n" )
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
