#IMPORTS

#APScheduler (pip install APScheduler)
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import tzlocal
from time import sleep

#Outlook API (Pip install O365)

from O365 import Account
CLIENT_ID = "e91b486a-c2d6-41e3-a346-6964af4bfcac"
CLIENT_SECRET = "clF8Q~g4qaBLRNjcmi1QrMrH593BKgNbe6B8HduA"

#OpenAi API
from openai import OpenAI
client = OpenAI(api_key='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')
personality = 'You are a whacky, slightly sarcastic robot radio that wakes me up and gives me helpful information. You use informal language when saying the time.'
personality2 = 'You are a whacky, extremely sarcastic robot radio that wakes me up and gives me helpful information whilst making humourous, slightly insulting remarks. You use informal language when saying the time.'
messages = [{'role' : 'system', 'content' : f'{personality2}'}]

#Weather API
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
current_weather = None
forecast = None

#Arduino GPIO Setup (for IR sensor, temp & humidity sensor, maybe poking facility?)
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

#Spotify API
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import subprocess as cmdLine

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="0a4c9275e1314bedae0d5f91483bc6ae",
                                               client_secret="69b8750816be4f5a954801f205085f7c",
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="user-read-playback-state user-modify-playback-state app-remote-control user-library-read playlist-read-private"))


#VARIABLES

schedule_items = None
schedule_str = None
today = None
tomorrow = None
earliest_event = None
lat = 51.489488
lon = -0.197916
wake_up_time = None
song_title = None
artist_title = None
humidity = None
temperature = None
forecast_str = None
response = None
random_track_id = None

#APScheduler setup

sched = BackgroundScheduler(timezone=str(tzlocal.get_localzone()))
sched.start()
dt = datetime.datetime

def init_spotify():
    process = cmdLine.Popen(['librespot'])
    devices = sp.devices()
    print(devices)

    target_device_name = 'Librespot'
    target_device = None

    for device in devices['devices']:
        if device['name'] == target_device_name:
            target_device = device

    if target_device:
        print('Device found')
    else:
        print('No Device found')

    global random_track_id

    #sp.transfer_playback(device_id=target_device['id'], force_play=True)
    sp.start_playback(device_id=target_device['id'], uris=['spotify:track:' + random_track_id])
    sp.volume(70, device_id=target_device['id'])

def get_random_song():

    global random_track_id
    playlist_id = '5Hf11xqnO1T6p39qVvfNLR'
    playlist_tracks = sp.playlist_tracks(playlist_id)

    playlist_info = sp.playlist(playlist_id)
    total_tracks = playlist_info['tracks']['total']
        
    import random
    random_track_id = random.choice(playlist_tracks['items'][:total_tracks])['track']['id']

    track = sp.track(random_track_id)

    global song_title
    song_title = track['name']
    global artist_title
    artist_title = track['artists'][0]['name']

def generate_text():
    global messages
    response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=messages
    )
    bot_response = response.choices[0].message.content
    messages.append({'role' : 'assistant', 'content' : f'{bot_response}'})
    return bot_response

def generate_audio():
    global response
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/XqV5HpZMJC68SpbTp4Gh"

    # nothern dry XqV5HpZMJC68SpbTp4Gh
    # smooth radio oSzkFWDSGBHgPT4ap3Gh

    headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": "88272f8b5104d78131a337a53064846b"
    }

    data = {
    "text": response,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.3,
        "similarity_boost": 1,
        "style": 0.7
    }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('monologue.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

def get_outlook_schedule():

    #Getting credentials and setting up
    credentials = (CLIENT_ID, CLIENT_SECRET)
    scopes = ['Calendars.Read']
    account = Account(credentials)

    if not account.is_authenticated:
        account.authenticate(scopes=scopes)
        print('Authenticated!')

    schedule = account.schedule()
    calendar = schedule.get_default_calendar()

    today = dt.now()
    start = dt.combine(datetime.date((today.year), (today.month), (today.day)), datetime.time(0, 00))
    end = dt.combine(datetime.date((today.year), (today.month), (today.day)), datetime.time(23, 59))

    query = calendar.new_query('start').greater_equal(start)
    query.new('end').less_equal(end)
    global schedule_items
    schedule_items = calendar.get_events(query=query, include_recurring=True)
    #Find earlest event of the day
    
    #sorted_items = sorted(schedule_items, key=lambda x:get_start_time(x))
    #print(sorted_items)
    global schedule_str
    schedule_str = 'first'
    for event in schedule_items:
        schedule_str = schedule_str + f" I have '{event.subject}' at {str(event.start)[11:-9]} until {str(event.end)[11:-9]}, then"

    schedule_str = schedule_str[:-6]
    schedule_str = schedule_str + ' to finish the day.'
    #print(schedule_str)

    global earliest_event
    query = calendar.new_query('start').greater_equal(start)
    query.new('end').less_equal(end)
    schedule_items = calendar.get_events(query=query, include_recurring=True)
    earliest_event = min(schedule_items, key=get_start_time)
    #print(earliest_event)

def get_start_time(event):
    return event.start

#call every 15 mins and compare to temp and humidity readings
#    Graph out and show on display

def get_readings():
    owm = OWM('1c64a004d7a1c6520d24c89781bc9e40')
    mgr = owm.weather_manager()
    global humidity
    global temperature

    while True:
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            print("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
            print(GPIO.input(PROX_PIN))
            observation = mgr.weather_at_coords(lat, lon)
            global current_weather
            current_weather = observation.weather
            out_temp = current_weather.temperature('celsius')['feels_like']
            out_humidity = current_weather.humidity
            print(f'out_temp = {out_temp}')
            url = f'https://api.thingspeak.com/update?api_key={thingspeak_write_key}&field1={temperature}&field2={out_temp}&field3={humidity}&field4={out_humidity}'
            response = requests.get(url)
            break
        else:
            print("sensor failure")

    
def weather_forecast():
    owm = OWM('1c64a004d7a1c6520d24c89781bc9e40')
    mgr = owm.weather_manager()
    global forecast
    forecast = mgr.forecast_at_coords(lat, lon, '3h').forecast
    global forecast_str
    forecast_str = "The weather will be "
    i = 0
    for weather in forecast:
        i += 1
        forecast_str = forecast_str + f"{weather.temperature('celsius')['feels_like']} degrees with {weather.detailed_status} at {str(weather.reference_time('iso'))[11:-9]}, and then "
        if i == 2:
            break
    forecast_str = forecast_str[:-11]
    print(forecast_str)

def make_wakeup_program():
    get_random_song()
    
    get_readings()
    weather_forecast()
    prompt = f""" Wake me up, telling me the following information:
                - The time is {str(wake_up_time)[11:-3]}
                - You are playing the song '{song_title}' by {artist_title}. 
                - In my calendar today, {schedule_str}
                - The weather is currently {current_weather.detailed_status} and {current_weather.temperature('celsius')['feels_like']} degrees.
                - The humidity in the room is currently {humidity} and outside is {current_weather.humidity}. If the humidity is higher than 60 in the room, tell me to open the window.
                - {forecast_str}. Only tell me the forecast if it's heavy rain or really clear weather.
                """
    """
    - When describing actions in square bracket, use only these options:
        - [sound of applause]
        - [sound of laughter]
        - [music playing]
        - [music stops]
        - [show weather results]
        """
    
    testprompt = f""" Wake me up, telling me the following information:
                - The time is {str(wake_up_time)[11:-3]}
                - You are playing the song '{song_title}' by {artist_title}. 
                - In my calendar today, I have 'weekly ERO meeting' at 12:00PM until 3:00PM.
                """
    print(testprompt)
    global messages
    messages.append({'role' : 'user', 'content' : testprompt})
    global response
    response = generate_text()
    print(response)
    generate_audio()

def play_mp3():
    import vlc
    p = vlc.MediaPlayer("monologue.mp3")
    p.play()


#WAKEUP PROGRAM
def wakeup():

    init_spotify()
    time.sleep(3)
    play_mp3()
    
    print('Wakeup! Done at:' + str(dt.now()))


#Midnight Reset
def midnight_reset():
    #set time for resetting and gathering data at start of day
    global today 
    today = dt.now()
    global tomorrow 
    tomorrow = dt.now() + datetime.timedelta(days=1)
    next_reset_time = dt((tomorrow.year), (tomorrow.month), (tomorrow.day), 0, 20, 00)

    #Looks at calendar for next day
    get_outlook_schedule()

    if earliest_event.start.hour < 9:
        wake_hour = earliest_event.start.hour - 1
        wake_minute = earliest_event.start.minute
    else:
        wake_hour = 8
        wake_minute = 0

    global wake_up_time
    wake_up_time = dt((today.year), (today.month), (today.day), wake_hour, wake_minute, 00)
    prep_time = wake_up_time - datetime.timedelta(minutes=1)

    make_wakeup_program()

    #set prep for wakeup program
    sched.add_job(make_wakeup_program, 'date', run_date=prep_time)
    #set when wake up program will happen
    ##sched.add_job(wakeup, 'date', run_date=wake_up_time)
    sched.add_job(wakeup, 'date', run_date=(dt.now() + datetime.timedelta(seconds=1)))
    #schedules next reset around midnight the next day
    sched.add_job(midnight_reset, 'date', run_date=next_reset_time)

sched.add_job(get_readings, 'interval', minutes=2)

midnight_reset()

while True:
    sleep(5)
