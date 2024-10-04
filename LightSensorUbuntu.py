import time
import os
from yocto_api import *
from yocto_lightsensor import *

loopInterval = 0.33  # Time between measuring in seconds
debugMode = True  # Enables debug messages

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
    return min(100, lightValue / 5 + 25)

def set_brightness(value):
    # Path to the brightness file for the primary display
    brightness_path = "/sys/class/backlight/intel_backlight/brightness"
    max_brightness_path = "/sys/class/backlight/intel_backlight/max_brightness"

    try:
        # Read the maximum brightness
        with open(max_brightness_path, 'r') as f:
            max_brightness = int(f.read().strip())

        # Calculate the new brightness value
        new_brightness = int((value / 100) * max_brightness)

        # Set the new brightness
        with open(brightness_path, 'w') as f:
            f.write(str(new_brightness))
        
        if debugMode:
            print(f"Set screen brightness to {new_brightness} (out of {max_brightness})")
    except Exception as e:
        if debugMode:
            print(f"Error setting brightness: {e}")

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
