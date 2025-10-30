
# Icom-TimeSync

These are python based scripts to set the Date & Time on Icom CAT controlled Radios, such as:
IC-7100, IC-7300, IC-7610 and IC-9700 

Inspired by https://github.com/Kurgan-/icom-set-time

# Installation and Configuration

If you want to use these scripts in Windows then look below for 'Windows Installation Procedure'

# Linux Installation

> [!NOTE]
> I really should fathom out a better way of dealing with a python virtual env, but this seems to work

Downlaod the code from GitHub:

```
cd ~
mkdir -p ~/git
git clone https://github.com/g0lgs/Icom-TimeSync.git ~/git/Icom-TimeSync
cd ~/git/Icom-7300-TimeSync
```

## Setting up Python Virtual Env
```
sudo apt install python3 python3-venv
sudo python3 -m venv /opt/Icom-TimeSync/
sudo /opt/Icom-TimeSync/bin/pip install --upgrade pip
sudo /opt/Icom-TimeSync/bin/pip install -r requirements.txt
```

## Installing Icom-TimeSync

Now change the first line of the 'Set-Icom-DateTime.py' Script from:

	#!/usr/bin/python3
to:

	#/opt/Icom-TimeSync/bin/python3

Now you can place a copy of the script for each radio in /usr/local/bin

i.e
```
cd ~/git/Icom-7300-TimeSync

sudo cp Set-Icom-DateTime.py /usr/local/bin/Set-Icom7100-DateTime.py
sudo cp Set-Icom-DateTime.py /usr/local/bin/Set-Icom7300-DateTime.py
sudo cp Set-Icom-DateTime.py /usr/local/bin/Set-Icom7610-DateTime.py
sudo cp Set-Icom-DateTime.py /usr/local/bin/Set-Icom9700-DateTime.py

sudo chmod +x /usr/local/bin/Set-Icom7100-DateTime.py
sudo chmod +x /usr/local/bin/Set-Icom7300-DateTime.py
sudo chmod +x /usr/local/bin/Set-Icom7610-DateTime.py
sudo chmod +x /usr/local/bin/Set-Icom9700-DateTime.py
```

Then edit the following lines in each script:
```
radio="7100"
radiociv="0x88"
baud = 115200					# Baud Rate
serialport = "/dev/ttyUSB0"		# Serial port of your radios serial interface.
UseLocalTime=False
```
Ensure that all the lines are aligned to the left (i.e no extra spaces or TABs have been entered) as this will break it!

Instead of /dev/ttyUSB0 etc you can set a serial port by id so that it always connect to the correct radio which is usefeul if you have more than one 
usb serial port connected (or see [udev](./using-udev-to-run-the-script-automatically) about using udev)

	serialport = "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_IC-7300_12345678-if00-port0"
or
	serialport = "/dev/serial/by-id/usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge_Controller_IC-9700_12345678_A-if00-port0"

You can now run each script directly like:
```
	/usr/local/bin/Set-Icom7300-DateTime.py
```

# Alternative to Editing the Script for each radio

Instead of editing the script for each radio it also takes parameters for each of the options, you can use long or short options like:
```
./Set-Icom-DateTime.py --radio 9700 --civ 0xA2 --port /dev/ttyUSB0 --baud 115200 --localtime

./Set-Icom-DateTime.py --radio 9700 --civ 0xA2 --port /dev/ttyUSB0 --baud 115200 --gmt

./Set-Icom-DateTime.py -r 9700 -c 0xA2 -p /dev/ttyUSB0 -b 115200 -l

./Set-Icom-DateTime.py -r 9700 -c 0xA2 -p /dev/ttyUSB0 -b 115200 -g
```
> [!NOTE]
> If you use the -c or --civ option (for when you have changed the default in the radio) it must follow the -r or --radio option

> The script will default to GMT (unless you have changed it) so the optional -l or --localtime option allows you to use local time

> The -g or --gmt options will revert to use GMT time even if you set 'UseLocalTime=True' in the script.

# Using udev to run the script automatically

For the serial port you can use a udev rule to create a symlink that always points to the correct radio and
if you wish run the script to set the Date/Time each time the radio is connected.

You will need to find the appropriate information for each of your radios, using a combination of the commands:
```
	lsusb

    udevadm info -p $(udevadm info -q path -n ttyUSB0)

    udevadm info -a -n ttyUSB0
```
Look for the following:

	ATTRS{idVendor}
	ATTRS{idProduct}
	ATTRS{serial}

create a udev rule in /etc/udev/rules.d/

	I use '99-hamlib.rules' but you can use something else as long as it is a .rules

```
	sudo nano /etc/udev/rules.d/99-hamlib.rules
```

Enter the information found above like:

```
# IC 7300
ACTION=="add", KERNEL=="ttyUSB?" SUBSYSTEM=="tty", \
ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", ATTRS{serial}=="IC-7300 12345678", SYMLINK+="ic7300"
RUN{program}+="/usr/local/bin/Set-Icom7300-DateTime.py"
```
or:
```
# IC 7300
ACTION=="add", KERNEL=="ttyUSB?" SUBSYSTEM=="tty", \
ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", ATTRS{serial}=="IC-7300 12345678", SYMLINK+="ic7300"
RUN{program}+="/usr/local/bin/Set-Icom-DateTime.py --radio 7300 --baud 115200 --port /dev/ic7300"
```
This will run the script when the Radio is connected or the Computer is started with the Radio connected.

Multiple RUN{program}+="" values may be used if you want to run other programs too (with some restrictions)

After editing udev rules use
```
sudo udevadm control --reload
```
You should then disconnect and re-connect the radios USB to check that it works.

The script should run and log any issues to syslog which you can examine with:
```
journalctl | grep DateTime.py | tail -n 10
```
If it sets the time you should see something like:

 Feb 11 07:23:40:24 \<computername\> Set-Icom-DateTi[12361]: Set-Icom-DateTime.py:main:345 INFO DateTime set on 7300

In the event of a problem something like:

 Feb 11 07:25:19 \<computername\> Set-Icom-DateTi[11387]: Set-Icom-DateTime.py:main:262 WARNING No such port: /dev/ic9700a

If the radio is connected but not switched on then (after a short delay) the logs will show one or more messages like:

 Feb 11 08:12:05 \<computername\> Set-Icom-DateTi[3480]: Set-Icom-DateTime.py:main:311 WARNING No/Unexpected response from 7300 on /dev/ic7300

 Feb 11 08:12:05 \<computername\> systemd-udevd[3391]: ttyUSB0: Process '/usr/local/bin/Set-Icom-DateTime.py' failed with exit code 2.

 Feb 11 08:12:36 \<computername\> Set-Icom-DateTi[3565]: Set-Icom-DateTime.py:main:454 WARNING No such port: /dev/ic7300

Turn the radio on and then disconnect and re-connect its USB to try again

# Windows Installation Procedure

You will need a recent version of Python for Windows.

Please refer to the PDF for Windows 7

Go to https://www.python.org/downloads/ to download the Latest Python Version for Windows

Open the Installer

* On the Initial Screen select Customize Installation
* Ensure that the follow options are enabled:
	- pip
	- for all users
	- py launcher

(Other options may be deselected if desired)

* Click Next
* Select
	- Install Pythox X.XX for all users
	- Add Python for environment variables
* Click Install
* Click Yes (when prompted) about making changes.

* when 'Steup was sucessful' appears Click Close

When the Installation is Complete Open a command prompt

Enter the command:
```
pip3 install pyserial --user
```

(Note the --user option is required for python 3.8.1 under Windows 7, but Pyton 3.12.2 on Windows 10 or 11 work without it)

Now download the 'Set-Icom-DateTime-Windows.pyw' from this Git Repositry and save it to your desktop
(or some other location if you prefer)

After downloading open the file in your prefered Text Editor (i.e Notepad++)

Change the Settings around lines 20 to 28 to set the appropriate values for your radio

The ones you need to set are:
	
radio, radiociv, baud and serialport

```
# Set Radio Model (7100/7300/9700)
radio="9700"
# Radio address (7100= 0x88, 7300 = 0x94, 9700 = 0xA2).
radiociv="0xa2"
# Radio serial speed
baud = 115200
# Serial port of your radios serial interface (i.e com3)
serialport = "com3"
# Set to True for LocalTime instead of default GMT
UseLocalTime=False
```
Ensure that all the lines are aligned to the left (i.e no extra spaces or TABs have been entered)

Save the file

Now just double-click the File on the Desktop to set the time on the Radio

## Alternative to Editing the Script

Instead of editing the script for each radio it also takes parameters for each of the options, you can
use long or short options:

	Set-Icom-DateTime-Windows.py --radio 9700 --civ 0xA2 --port /dev/ttyUSB0 --baud 115200 --localtime --noprompt

	Set-Icom-DateTime-Windows.py -r 9700 -c 0xA2 -p /dev/ttyUSB0 -b 115200 -l -n

or
	Set-Icom-DateTime-Windows.pyw --radio 9700 --civ 0xA2 --port /dev/ttyUSB0 --baud 115200 --localtime --noprompt

	Set-Icom-DateTime-Windows.pyw -r 9700 -c 0xA2 -p /dev/ttyUSB0 -b 115200 -l -n

Without the the -n or --noprompt the script will prompt (via a pop-up dialog box) that you are ready to set the radio,
this is perhaps most useful when creating a desktop shortcut.

The script will default to GMT (unless you have changed it) the optional -l or --localtime option allows you to use the local PC Time

## Configuring Windows to auto-run the script at login

 * Right click the Desktop Icon (or where-ever you saved the the .pyw file) and select 'Copy as Path'
 * Press Windows+R, then in the box type 'shell:startup'
 * Click Ok
 * Right Click in the Window and Select New -> Shortcut then Click Browse
 * Navigate to the C:\Program Files\PythonXXX Folder and Select pythonw.exe (or python.exe for testing)
 * Add a Space and Press Ctrl-V
 * Add any of the command-line options you wish to use
 * Click Next
 * Enter a Suitable Name (i.e Set 7300 Time)

My command lines for these look like:

	"C:\Program Files\Python312\pythonw.exe" "D:\Scripts\Icom-7300-TimeSync\Set-Icom-DateTime-Windows.pyw" --radio 7300 --port com5 --civ 0x94 --baud 115200

	"C:\Program Files\Python312\pythonw.exe" "D:\Scripts\Icom-7300-TimeSync\Set-Icom-DateTime-Windows.pyw" --radio 9700 --port com3 --civ 0xa2 --baud 115200

As these may start before I have turned on the Shack PSU's or radios I do not use the '--noprompt' option, but my equivalent Desktop Shorcuts do.

If you have 2 or more radio's repeat the same process using different Short-cut names with appropriate settings for each one.

## Known Issues

In some cases the radio (this may depend on Firmware Revision in use) may not accept the seconds value when the script tries to 
set the time, if this appears to be the case then case search for _set_time function for your radio and changes the line:

	cmd.append("0x"+second)
	
to:

	#cmd.append("0x"+second)

This will mean that your radio will be up to 59 seconds behind, however that is much better than being at some random date/time.

----------
Stewart G0LGS\
Revised: Oct 2025
