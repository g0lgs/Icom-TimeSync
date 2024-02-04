
Script to set the Time on Icom 7300 and Icom 9700 Radios 
based on https://github.com/Kurgan-/icom-set-time

I suggest you place a copy of the Script for each radio in /usr/local/bin

i.e

	sudo cp Set-Icom-DateTime.py /usr/local/Set-Icom7300-DateTime.py
	sudo cp Set-Icom-DateTime.py /usr/local/Set-Icom9700-DateTime.py

	sudo chmod +x /usr/local/Set-Icom7300-DateTime.py
	sudo chmod +x /usr/local/Set-Icom9700-DateTime.py

Then edit the following lines in each script:

	radio="7300"            # Set Radio Model
	civaddress="0x94"       # Radio address (7300 = 0x94, 9700 = 0xA2).
	baudrate = 115200       # Radio serial speed
	serialport = "/dev/ttyUSB0"  # Serial port of your radios serial interface.

You can set a serial port by id so that it always connect to the correct radio, which is
usefeul if you have more than one usb serial port connected

like:

	serialport = "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_IC-7300_03011354-if00-port0"
or
	serialport = "/dev/serial/by-id/usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge_Controller_IC-9700_13001015_A-if00-port0"


You could add a udev rule to create a symlink that always points to the correct radio

Use

    sudo udevadm info -a /dev/ttyUSB0
or
    sudo udevadm info -a -n ttyUSB0

To get the inforamtion to create a udev rule in /etc/udev/rules.d/99 like:

# IC 7300
KERNEL=="ttyUSB?" SUBSYSTEMS=="usb", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", ATTRS{serial}=="IC-7300 03011354", SYMLINK+="ic7300"

or

KERNEL=="ttyUSB?" SUBSYSTEMS=="usb", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", ATTRS{serial}=="IC-7300 03011354", SYMLINK+="ic7300" RUN{program}+="/usr/local/bin/Set-Icom7300-DateTime.py &"

Which would run the script when the Radio is connected or the Computer is started with the Radio connected.

Multiple RUN{program}+="" values may be used if you want to run other programs too (with some restrictions)

-------------
Stewart G0LGS
Feb 2024
