#!/usr/bin/python
#
# Park script for INDI Dome Scripting Gateway
# Based on github.com/fenriques/indi/blob/master/libindi/drivers/dome/dome_script.txt
# 
#
# The default folder is /usr/share/indi/scripts. 
# Exit code: 0 for success, 1 for failure
#

from gpiozero import Button
import time
import libioplus
import sys

# assign roof_open_switch to read on GPIO pin 13, other wire attached to ground
roof_open_switch = Button(13)
# assign roof_closed_switch to read on GPIO pin 21, other wire attached to ground
roof_closed_switch = Button(21)
# assign motor_relay to relay #4 on the Sequent Microsystems home automation 8 relay hat
motor_relay = 4
# assign hat_stack to 0, which is the first relay hat (you can have multiple hats stacked up)
hat_stack = 0
# assign relay on/off in english
relay_on = 1
relay_off = 0
# assign opto_channel to optocoupler #1 on the Sequent Microsystems home automation 8 relay hat
opto_channel = 1

# pulse the motor relay on, then off again to start the Aleko AR900 motor cycle
def pulse_motor():    
    libioplus.setRelayCh(hat_stack,motor_relay,relay_on)
    time.sleep(0.7)
    libioplus.setRelayCh(hat_stack,motor_relay,relay_off)

# determine if the mount is parked by checking if the beam detector is finding the reflection, return 'true' or 'false'
def mount_parked () :
    if libioplus.getOptoCh(hat_stack, opto_channel) == 1:
        return True
    else:
        return False

# If roof is already closed then print message and quit.
if roof_closed_switch.is_pressed:
    print("roof is already closed")
    sys.exit(0)

# If roof neither fully open or closed then print message quit
if roof_closed_switch.value == 0 and roof_open_switch.value == 0:
    print("roof is partially open, cycle manually")
    sys.exit(0)

# If mount is not parked then print a message and keep checking for one minute. If mount parks then print message and continue otherwise print fail message and quit.
if not mount_parked:
    print("mount is not parked")
    for x in range(6):
        print('waiting for mount to park...')
        time.sleep(10)
        if mount_parked:
            break
if mount_parked:
    print("mount is parked")
else:
    print('mount not parked, unable to close roof')
    print('quitting')
    sys.exit(0)

# If roof is fully open then trigger the motor to close, wait for closed confirmation,
# print message, update file, exit.

if roof_open_switch.is_pressed:
    pulse_motor()

# monitor the roof movement    
roof_open_switch.wait_for_release()   
print("roof is moving...")
    
roof_closed_switch.wait_for_press()
print("roof is parked")

# update INDI Dome Scripting Gateway status file
coordinates = open('/tmp/indi-status', 'w')
coordinates.truncate()
coordinates.write('1 0 0')
coordinates.close()
print ("file updated")

sys.exit(0)
