# kx2TimeMac.py
# D. Kingma
# With an Elecraft KX2 connected to a Mac, this script will change the KX2 time to the
# UTC time as read from your Mac clock. Install pyserial before running this script.
# Note: I'm not sure if the port.name will be the same for all radios as I only had
# one radio to try this out.

import serial
import serial.tools.list_ports
import datetime
import time

# Find the serial port that the KX2 radio is connected to
kx2_port = None
for port in serial.tools.list_ports.comports():
    if port.name == 'cu.usbserial-A10KN9Z1':
        kx2_port = port.device
        break

# If the KX2 port was not found, exit with an error message
if kx2_port is None:
    print('Error: KX2 radio not found on any serial port')
    exit()

# Open a serial connection with the KX2
ser = serial.Serial(kx2_port, 38400, timeout=1)

def get_pc_time():
    now = datetime.datetime.utcnow()
    # Get current PC time as HHMMSS
    time_str = now.strftime("%H%M%S")
    pcSec = int(time_str[-2:])
    pcMin = int(time_str[-4:-2])
    pcHrs = int(time_str[-6:-4])
    return pcSec, pcMin, pcHrs

def get_kx2_time():
    ser.write(b"DB01;DB;")
    byte_read = ser.readline()
    time_read = byte_read.decode()
    kx2Sec = int(time_read[-3:-1])
    kx2Min = int(time_read[-6:-4])
    kx2Hrs = int(time_read[-9:-7])
    return kx2Sec, kx2Min, kx2Hrs

def create_up_dn_string(pcTime, kx2Time):
    diff = pcTime - kx2Time
    upDnStr = ""
    if diff > 0:
        for i in range(1, diff+1, 1):
            upDnStr = upDnStr + "UP;"
    else:
        for i in range(1, abs(diff)+ 1, 1):
            upDnStr = upDnStr + "DN;"
    return upDnStr


# get the current KX2 and PC times
kx2Sec, kx2Min, kx2Hrs = get_kx2_time()
pcSec, pcMin, pcHrs = get_pc_time()

# change to the time menu
ser.write(b"MN073;")
time.sleep(0.1)

if pcSec != kx2Sec:
    sendStr = "SWT20;" + create_up_dn_string(pcSec, kx2Sec)
    ser.write(sendStr.encode())
if pcMin != kx2Min:
    sendStr = "SWT27;" + create_up_dn_string(pcMin, kx2Min)
    ser.write(sendStr.encode())
if pcHrs != kx2Hrs:
    sendStr = "SWT19;" + create_up_dn_string(pcHrs, kx2Hrs)
    ser.write(sendStr.encode())
time.sleep(0.1)

# close time menu
ser.write(b"MN255;")
time.sleep(1)

# get the current KX2 and PC times
kx2Sec, kx2Min, kx2Hrs = get_kx2_time()
pcSec, pcMin, pcHrs = get_pc_time()

print(f"KX2 Time: {kx2Hrs:02d}:{kx2Min:02d}:{kx2Sec:02d}")
print(f" PC Time: {pcHrs:02d}:{pcMin:02d}:{pcSec:02d}")

# close serial port
ser.close()
