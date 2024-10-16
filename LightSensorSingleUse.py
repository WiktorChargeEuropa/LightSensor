# This application is meant for a periodic crone calls

import time
import subprocess
import logging
from yocto_api import *
from yocto_lightsensor import *

# Cycle configuration
debugMode = True    # Debug logging enable
minBrightness = 60  # Min value of screen brightness
####################################################

logging.basicConfig(level=logging.DEBUG if debugMode else logging.ERROR)

def get_light_value():
    try:
        light_value = lightsensor.get_currentValue()
        logging.debug(f"Current light intensity: {light_value} lux")
        return light_value
    except Exception as e:
        logging.error(f"Error reading light value: {e}")
        return None

def try_to_connect():
    global lightsensor, sensorConnected
    try:
        lightsensor = YLightSensor.FirstLightSensor()
        if lightsensor is None:
            logging.warning("No light sensor connected to the USB hub.")
            sensorConnected = False
        else:
            sensor_id = lightsensor.get_module().get_serialNumber()
            logging.debug(f"Using sensor: {sensor_id}")
            sensorConnected = lightsensor.isOnline()
            if not sensorConnected:
                logging.warning(f"Sensor {sensor_id} is not online.")
    except Exception as e:
        logging.error(f"Error trying to connect to light sensor: {e}")
        sensorConnected = False

def api_init():
    errmsg = YRefParam()
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        logging.error(f"Cannot initialize Yoctopuce API: {errmsg.value}")

def calculate_screen_brightness(lightValue):
    return min(100, lightValue / 10 + minBrightness)

def set_brightness(value):
    try:
        output = subprocess.check_output("DISPLAY=:0 xrandr --query | grep ' connected'", shell=True).decode().strip().split('\n')
        for line in output:
            display_name = line.split()[0]
            command = f"DISPLAY=:0 xrandr --output {display_name} --brightness {value / 100.0}"
            subprocess.call(command, shell=True)
            logging.info(f"Set screen brightness to {value}% on {display_name}")
    except Exception as e:
        logging.error(f"Error setting brightness using xrandr: {e}")

sensorConnected = False

api_init()
try:
    light_value = 0
    try_to_connect()
    if sensorConnected:
        light_value = get_light_value()
    if light_value != 0:
        screen_brightness = calculate_screen_brightness(light_value)
        set_brightness(screen_brightness)
    else:
            logging.info("Waiting for the sensor to connect...")
except Exception as e:
        logging.error(f"Error in main loop: {e}")
