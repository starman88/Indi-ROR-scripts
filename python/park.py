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

# assign roof_open_switch to read on GPIO 8, other wire attached to ground
roof_open_switch = Button(99)
# assign roof_closed_switch to read on GPIO 10, other wire attached to ground
roof_closed_switch = Button(99)
# assign motor_relay to relay #1 on the relay hat
motor_relay = 4
# assign hat_stack to 0, which is the first relay hat (you can have multiple hats stacked up)
hat_stack = 0
# assign relay on/off in english
relay_on = 1
relay_off = 0

# pulse the motor relay on, then off again to start the Aleko close cycle
def pulse_motor():    
    libioplus.setRelayCh(hat_stack,motor_relay,relay_on)
    time.sleep(0.7)
    libioplus.setRelayCh(hat_stack,motor_relay,relay_off)

# If roof is already closed then print message and quit.
if roof_closed_switch.is_pressed:
    print("roof is already parked")
    sys.exit(0)

# If roof neither fully open or closed then print message quit
if roof_closed_switch.value == 0 and roof_open_switch.value == 0:
    print("roof is partially open, cycle manually")
    sys.exit(0)

# If roof is fully open then trigger the motor to close, wait for closed confirmation,
# print message, update file, exit.

if roof_open_switch.is_pressed:
    pulse_motor()

#monitor the roof movement    
roof_open_switch.wait_for_release()   
print("roof is moving...")
    
roof_closed_switch.wait_for_press()
print("roof is parked")

#update INDI Dome Scripting Gateway status file
coordinates = open('/tmp/indi-status', 'w')
coordinates.truncate()
coordinates.write('1 0 0')
coordinates.close()
print ("file updated")

sys.exit(0)
