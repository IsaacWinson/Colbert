import Adafruit_DHT
import time
import RPi.GPIO as GPIO
import requests

thingspeak_write_key = 'JEBWJU38QA5Z25YC'


GPIO.setmode(GPIO.BCM)

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

PROX_PIN = 17
GPIO.setup(PROX_PIN, GPIO.IN)

from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
current_weather = None
forecast = None

owm = OWM('1c64a004d7a1c6520d24c89781bc9e40')
mgr = owm.weather_manager()
lat = 51.489488
lon = -0.197916

while True:
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
        print(GPIO.input(PROX_PIN))
        observation = mgr.weather_at_coords(lat, lon)
        current_weather = observation.weather
        out_temp = current_weather.temperature('celsius')['feels_like']
        out_humidity = current_weather.humidity
        print(f'out_temp = {out_temp}')
        url = f'https://api.thingspeak.com/update?api_key={thingspeak_write_key}&field1={temperature}&field2={out_temp}&field3={humidity}&field4={humidity}'
        response = requests.get(url)
    else:
        print("sensor failure")
    time.sleep(120)