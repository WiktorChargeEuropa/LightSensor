import time
import subprocess
import logging
from yocto_api import *
from yocto_lightsensor import *

loopInterval = 0.33  # Time between measuring in seconds
debugMode = True  # Enables debug messages
minBrightness = 40

def get_light_value():
    try:
        light_value = lightsensor.get_currentValue()
        if debugMode: 
            print(f"Current light intensity: {light_value} lux")
        return light_value
    except Exception as e:
        if debugMode: 
            print(f"Error reading light value: {e}")
        return None

def try_to_connect():
    global lightsensor, sensorConnected
    try:
        lightsensor = YLightSensor.FirstLightSensor()
        if lightsensor is None:
            if debugMode: 
                print("No light sensor connected to the USB hub.")
            sensorConnected = False
        else:
            sensor_id = lightsensor.get_module().get_serialNumber()
            if debugMode: 
                print(f"Using sensor: {sensor_id}")
            sensorConnected = lightsensor.isOnline()
            if not sensorConnected:
                if debugMode: 
                    print(f"Sensor {sensor_id} is not online.")
    except Exception as e:
        if debugMode: 
            print(f"Error trying to connect to light sensor: {e}")
        sensorConnected = False

def api_init():
    errmsg = YRefParam()
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        if debugMode: 
            print(f"Cannot initialize Yoctopuce API: {errmsg.value}")

def calculate_screen_brightness(lightValue):
    return min(100, lightValue / 5 + minBrightness)

def set_brightness(value):
    try:
        # Get the connected displays
        # output = subprocess.check_output("DISPLAY=:0 xrandr --query | grep ' connected'", shell=True).decode().strip().split('\n')
        for line in output:
            # Split the output line to get the display name
            display_name = line.split()[0]
            # Set the brightness using xrandr with DISPLAY=:0
            command = f"sudo ddcutil -d -1 setvcp {value}}"
            subprocess.call(command, shell=True)
            if debugMode:
                print(f"Set screen brightness to {value}% on {display_name}")
    except Exception as e:
        if debugMode:
            print(f"Error setting brightness using xrandr: {e}")

sensorConnected = False

api_init()
while True:
    try:
        api_init()
        try_to_connect()
        if sensorConnected:
            screen_brightness = calculate_screen_brightness(get_light_value())
            set_brightness(screen_brightness)
        else:
            if debugMode: 
                print("Waiting for the sensor to connect...")
    except Exception as e:
        if debugMode:
            print(f"Error in main loop: {e}")

    time.sleep(loopInterval)
