#!/usr/bin/python3

# Copyright (c) 2024 Stewart Wilkinson (G0LGS)
# Ver: 1.0.8 13/04/2024

# Set Date/Time on Icom 7100/7300/7610/9700 radio

# Notes:
# Although the CAT control info for Icom radios show only setting Hours/Mins my 7300 and 9700
# allow setting the seconds too, but only show the Hours/Mins when reading the time
# This code assumes that other radios will work the same

# The get_date and get_time Functions below are incomplete are only here for my own Testing

# You will need the following libs:
#    pyserial

import sys
import platform

if platform.system() != 'Linux':
    print("Sorry: This Version only works in Linux - Use 'Set-Icom-DateTime-Windows.pyw' for Windows")
    input("Press Enter to exit...")
    sys.exit(1)

MIN_PYTHON = (3, 6)
if not sys.version_info >= MIN_PYTHON:
    print("This script requires Python V3.6 or later")
    input("Press Enter to exit...")
    sys.exit(1)

# Default Values (pass command line options or edit here to suit)
# Set Radio Model
radio="9700"
# Radio address (7100= 0x88, 7300 = 0x94, 7610 = 0x98 , 9700 = 0xA2).
radiociv="0xA2"
# Radio serial speed
baud = 115200
# Serial port of your radios serial interface (often /dev/ttyUSB0)
serialport = "/dev/ttyUSB0"

# You can set a serial port by id so that it always connect to the correct radio, which is
# usefeul if you have more than one usb serial port connected
#serialport="/dev/serial/by-id/usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge_Controller_IC-9700_12345678_A-if00-port0"
#serialport="/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_IC-7300_87654321-if00-port0"

# Set to True for LocalTime instead of default GMT
UseLocalTime=False

# Address for the 'controller' (this script) - change only if you have a conflict with one of your radios
myciv="0xc0"

# **** Nothing below should need to be changed **** #

# Supported Radios, Default CIVs, Baud Rates
Radios=[7100,7300,7610,9700]
RadioCIV= { 7100: "0x88", 7300: "0x94", 7610: "0x98", 9700: "0xA2" }
Bauds=[4800,9600,19200,38400,57600,115200]
#
Debug=False
Quiet=False
ExactMin = False

# Import libraries we'll need to use
import os
import getopt
import time
import serial
import struct
import logging
from logging.handlers import SysLogHandler
from pathlib import Path

def sendcmd(ser,cmd):
    count = 0
    if Debug: print ( "\tSending: ", cmd )

    while(count < len(cmd)):
        senddata = int(bytes(cmd[count], 'UTF-8'), 16)
        ser.write(struct.pack('>B', senddata))
        count = count +1

def GetResp(ser):
    s = ''
    while s != b'\xFE':
        if Debug: print( "\tWaiting for sync...." + ''.join("{:02x}".format(x) for x in s) )
        s = ser.read()
        # Timeout?
        if len(s) == 0:
            break;

    if ser.read() == b'\xFE':
        if Debug: print( "\tSynced, packet info :")
        i = 0
        rxdata = []
        while s != b'\xFD':
            s = ser.read()
            if  i == 0 :
                if Debug: print( "\tTo:   0x" + ''.join(format(x, '02x') for x in s) )
            elif i == 1:
                if Debug: print( "\tFrom: 0x" + ''.join(format(x, '02x') for x in s) )
            else:
                rxdata.append(s)
                if Debug: print( "\tData: 0x" + ''.join(format(x, '02x') for x in s) )
            i +=1

        rxdata.pop()
        return rxdata

# check for Ack
def CheckAck(ser):
    timeout = time.time() + 3
    AckOk=0
    while AckOk==0:
        dat = GetResp(ser)

        if dat is None:
            # Do nothing
            if Debug: print( "\tTimeout.." )
            time.sleep(0.1)

        else:
            if dat[0] == b'\xfb':
                if Debug:
                    print( "\tGot Ack: " +dat[0].hex() )
                AckOk=1

        if time.time() > timeout:
            break

    return AckOk

def show_frequency(data):
    vals = [data[i].hex() for i in range (0, len(data))]
    cmd = ''.join(vals)
    print( f"Frequency: {cmd[10:11]},{cmd[11:12]}{cmd[8:9]}{cmd[9:10]},{cmd[6:7]}{cmd[7:8]}{cmd[4:5]}.{cmd[5:6]}{cmd[2:3]}" )

def get_frequency(ser):
    Res=None
    if Debug: print ( "Trying to Read Frequency" )

    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x03", "0xFD" ]
    sendcmd(ser,cmd)

    # Listen for Response (with Timeout)
    timeout = time.time() + 3
    CmdOk=0
    while CmdOk==0:
        dat = GetResp(ser)

        if dat is None:
            # Do nothing
            if Debug: print( "\tTimeout.." )
            time.sleep(0.1)

        elif len(dat) > 2:

            if dat[0] == b'\x03':
                if Debug:
                    print( "\tGot (03) :")
                    show_frequency(dat)
                CmdOk=1

            # Ack
            elif dat[0] == b'\xfb':
                if Debug: print( "\tGot (FB) :")
                CmdOk=1

            else:
                print ( "\tUnexpected response (" +dat[0].hex() + ")")
                vals = [dat[i].hex() for i in range (0, len(dat))]
                cmd = ';'.join(vals)
                print (cmd)

        if time.time() > timeout:
            break

    if CmdOk:
        if Debug: print( f"Got response from {radio} OK")
        Res=dat

    return Res

# 7100 Time / Date Functions
def ic7100_get_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x20", "0xFD" ]
    sendcmd(ser,cmd)
    CheckAck(ser)

def ic7100_set_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x20" ]
    cmd.append("0x"+year[0:2])
    cmd.append("0x"+year[2:])
    cmd.append("0x"+month)
    cmd.append("0x"+day)
    cmd.append("0xFD")
    if Debug: print ("Setting Date")
    sendcmd(ser,cmd)

def ic7100_get_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x21", "0xFD" ]
    sendcmd(ser,cmd)
    CheckAck(ser)

def ic7100_set_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x21" ]
    cmd.append("0x"+hour)
    cmd.append("0x"+minute)
    cmd.append("0x"+second)
    cmd.append("0xFD")
    if Debug: print ("Setting Time")
    sendcmd(ser,cmd)

# 7300 Time / Date Functions
def ic7300_get_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x94", "0xFD" ]
    sendcmd(ser,cmd)
    CheckAck(ser)

def ic7300_set_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x94" ]
    cmd.append("0x"+year[0:2])
    cmd.append("0x"+year[2:])
    cmd.append("0x"+month)
    cmd.append("0x"+day)
    cmd.append("0xFD")
    if Debug: print ("Setting Date")
    sendcmd(ser,cmd)

def ic7300_get_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x95", "0xFD" ]
    sendcmd(ser,cmd)
    CheckAck(ser)

def ic7300_set_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x00", "0x95" ]
    cmd.append("0x"+hour)
    cmd.append("0x"+minute)
    cmd.append("0x"+second)
    cmd.append("0xFD")
    if Debug: print ("Setting Time")
    sendcmd(ser,cmd)

# 7610 Time / Date Functions
def ic7610_get_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x58", "0xFD" ]
    sendcmd(ser,cmd)
    CheckAck(ser)

def ic7610_set_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x58" ]
    cmd.append("0x"+year[0:2])
    cmd.append("0x"+year[2:])
    cmd.append("0x"+month)
    cmd.append("0x"+day)
    cmd.append("0xFD")
    if Debug: print ("Setting Date")
    sendcmd(ser,cmd)

def ic7610_get_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x59", "0xFD" ]
    sendcmd(ser,cmd)
    CheckAck(ser)

def ic7610_set_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x59" ]
    cmd.append("0x"+hour)
    cmd.append("0x"+minute)
    cmd.append("0x"+second)
    cmd.append("0xFD")
    if Debug: print ("Setting Time")
    sendcmd(ser,cmd)

# 9700 Time / Date Functions
def ic9700_get_date(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x79", "0xFD"]
    sendcmd(ser,cmd)
    CheckAck(ser)

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
    CheckAck(ser)

def ic9700_set_time(ser):
    cmd = [ "0xFE", "0xFE", radiociv, myciv, "0x1A", "0x05", "0x01", "0x80" ]
    cmd.append("0x"+hour)
    cmd.append("0x"+minute)
    cmd.append("0x"+second)
    cmd.append("0xFD")
    sendcmd(ser,cmd)

def Usage():
    print ( "\nUsage: " + sys.argv[0] + "\t-r|--radio <Radio_Model> -c|--civ <Radio_CIV_Address> -p|--port <Serial_Port> -b|--baud <Baud_Rate> -l|--localtime -g|--gmt")
    print ( "\n\tNote: Uses default CIV address for given radio unless --civ option follows --radio\n")

def main(argv):
    global Debug
    global year
    global month
    global day
    global hour
    global minute
    global second
    global radio
    global radiociv
    global baud
    global serialport
    global UseLocalTime
    global ExactMin

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    handler = logging.handlers.SysLogHandler(facility=SysLogHandler.LOG_DAEMON, address = '/dev/log')

    formatter = logging.Formatter(
        fmt="%(filename)s:%(funcName)s:%(lineno)d %(levelname)s %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    try:
        opts, args = getopt.getopt(argv,"?hDr:c:p:b:lgq",["help","Debug","radio=","civ=","port=","baud=","localtime","gmt","quiet"])

    except getopt.GetoptError as Err:
        print (Err)
        Usage()
        sys.exit(2)

    for opt, arg in opts:

        if opt in ("-?", "-h", "--help"):
            Usage()
            sys.exit()

        elif opt in ("-D", "--Debug"):
            Debug=True

        elif opt in ("-q", "--quiet"):
            Quiet=True

        elif opt in ("-l", "--localtime"):
            UseLocalTime=True

        elif opt in ("-g", "--gmt"):
            UseLocalTime=False

        elif opt in ("-r", "--radio"):
            radio = arg
            try:
                radNo=int(radio)

            except ValueError:
                print ( f'Sorry Radio ({radio}) is not valid (acceptable are {Radios})' )
                sys.exit()

            else:
                if radNo not in Radios:
                    print ( f'Sorry Radio ({radio}) is not valid (acceptable are {Radios})' )
                    sys.exit()

                # default CIV
                radiociv=RadioCIV[radNo]

        elif opt in ("-c", "--civ"):
            radiociv = arg
            try:
                civ = int(radiociv, 16)

            except ValueError:
                print ( f'Sorry CIV Address ({radiociv}) is not valid Hex' )
                sys.exit()

            else:
                if civ > 255:
                    print ( f'Sorry CIV Address ({radiociv}) is out of range (0x00 to 0xff)' )
                    sys.exit()
                if civ == int(myciv, 16):
                    print ( f'Sorry CIV Address ({radiociv}) is reserved (controller)' )
                    sys.exit()

        elif opt in ("-p", "--port"):
            serialport = arg

        elif opt in ("-b", "--baud"):
            baud = arg
            try:
                baud=int(baud)

            except ValueError:
                print ( f'Sorry Baud-rate ({baud}) is not valid number' )
                sys.exit()

            else:
                if baud not in Bauds:
                    print ( f'Sorry Baud-rate ({baud}) is not valid (acceptable rates are {Bauds})' )
                    sys.exit()

    # Additional Checks (in case Script Defaults have been broken)
    try:
        radNo=int(radio)

    except ValueError:
        print ( f'Sorry Radio ({radio}) is not valid (acceptable are {Radios})' )
        sys.exit(1)

    else:
        if radNo not in Radios:
            sys.stderr.write( "ERROR: Unsupported radio: " + radio +"\n" )
            logger.warning( "Unsupported radio: " + radio )
            sys.exit(1)

    if baud not in Bauds:
        print ( f'Sorry Baud-rate ({baud}) is not valid (acceptable rates are {Bauds})' )
        sys.exit(1)

    try:
        civ = int(radiociv, 16)

    except ValueError:
        print ( f'Sorry CIV Address ({radiociv}) is not valid Hex' )
        sys.exit(1)
    else:
        if civ > 255:
            print ( f'Sorry CIV Address ({radiociv}) is out of range (0x00 to 0xff)' )
            sys.exit()
        if civ == int(myciv, 16):
            print ( f'Sorry CIV Address ({radiociv}) is reserved (controller)' )
            sys.exit(1)

    # Exit Code
    ExitCode=0

    # Resolve any symlink to real path
    serdev=os.path.realpath(serialport)

    try:
        ser = serial.Serial(port=serialport, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=0, rtscts=0)

    except serial.SerialException as serErr:
        if serErr.errno == 2:
            sys.stderr.write( "ERROR: No such port: " +serialport + "\n" )
            logger.warning( "No such port: " +serialport )
            sys.exit(1)
        if serErr.errno == 16:
            sys.stderr.write( "ERROR: port: " +serialport + " busy\n" )
            logger.warning( "Port: " +serialport + " busy" )
            sys.exit(1)
        else:
            sys.stderr.write( "Unexpected error: "+ str(serErr.errno) + "\n" )
            logger.warning( "Unexpected error: "+ str(serErr.errno) )
            sys.exit(1)

    except ValueError as Err:
        print (Err)
        logger.warning( Err )
        sys.exit()

    if Debug: print ("Testing radio communications")
    # Try reading frequency
    Freq = get_frequency(ser)
    if Freq == None:
        ser.close()
        if serdev in serialport:
            sys.stderr.write( f"Error: No/Unexpected response from {radio} ({radiociv}) on {serialport} at {baud} Bauds\n" )
            logger.warning( f"No/Unexpected response from {radio} ({radiociv}) on {serialport} at {baud} Bauds" )
        else:
            sys.stderr.write( f"Error: No/Unexpected response from {radio} ({radiociv}) on {serialport} ({serdev}) at {baud} Bauds\n" )
            logger.warning( f"No/Unexpected response from {radio} ({radiociv}) on {serialport} ({serdev}) at {baud} Bauds" )
        sys.exit(2)

    # Get time for system clock (defaut is GMT)
    if UseLocalTime:
        t = time.localtime()
    else:
        t = time.gmtime()

    # extract strings for year, day, month, hour, minute, second
    # with a leading zero if needed
    year = str(t.tm_year)
    month = str(t.tm_mon).rjust(2,'0')
    day = str(t.tm_mday).rjust(2,'0')
    hour = str(t.tm_hour).rjust(2,'0')
    minute = str(t.tm_min).rjust(2,'0')
    second = str(t.tm_sec).rjust(2,'0')

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

    elif radio == "7610":
            ic7610_set_date(ser)
            if not CheckAck(ser):
                ExitCode=3
            else:
                ic7610_set_time(ser)
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
        print( "Ok" )
        logger.info( "DateTime set on " + radio )
    else:
        if serdev in serialport:
            sys.stderr.write( f"Error: No/Unexpected response from {radio} ({radiociv}) on {serialport} at {baud} Bauds\n" )
            logger.warning( f"No/Unexpected response from {radio} ({radiociv}) on {serialport} at {baud} Bauds" )
        else:
            sys.stderr.write( f"Error: No/Unexpected response from {radio} ({radiociv}) on {serialport} ({serdev}) at {baud} Bauds\n" )
            logger.warning( f"No/Unexpected response from {radio} ({radiociv}) on {serialport} ({serdev}) at {baud} Bauds" )

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
