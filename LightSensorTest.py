import time
import os
from yocto_api import *
from yocto_lightsensor import *

script_dir = os.path.dirname(os.path.abspath("/screen_brightness_control"))
sys.path.append(os.path.join(script_dir, 'screen_brightness_control'))

import screen_brightness_control as sbc

loopInterval = 0.33  # Time between measuring in seconds
debugMode = True  # Enables debug messages

def GetLightValue():
    light_value = lightsensor.get_currentValue()
    if debugMode: print(f"Current light intensity: {light_value} lux")
    return light_value
    if debugMode: print(f"Error reading light value: {e}")

def TryToConnect():
    global lightsensor, sensorConnected
    try:
        lightsensor = YLightSensor.FirstLightSensor()
        if lightsensor is None:
            if debugMode: print("No light sensor connected to the USB hub.")
            sensorConnected = False
        else:
            sensor_id = lightsensor.get_module().get_serialNumber()
            if debugMode: print(f"Using sensor: {sensor_id}")
            sensorConnected = lightsensor.isOnline()
            if not sensorConnected:
                if debugMode: print(f"Sensor {sensor_id} is not online.")
    except Exception as e:
        if debugMode: print(f"Error trying to connect to light sensor: {e}")
        sensorConnected = False

def API_init():
    errmsg = YRefParam()
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        if debugMode: print(f"Cannot initialize Yoctopuce API: {errmsg.value}")

def CalculateScreenBrightness(lightValue):
    return min(100, lightValue / 5 + 25)

sensorConnected = False
prevState = False 

API_init()
while True:
    API_init()
    TryToConnect()
    if sensorConnected:
        ScreenBrightness = CalculateScreenBrightness(GetLightValue())
        sbc.set_brightness(ScreenBrightness, display=0)
    else:
        if debugMode: print("Waiting for the sensor to connect...")
    YAPI.FreeAPI()
    time.sleep(loopInterval)
