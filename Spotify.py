#Client_Id= 0a4c9275e1314bedae0d5f91483bc6ae
#Client Secret: 69b8750816be4f5a954801f205085f7c
#http://localhost:8888/callback

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

import subprocess as cmdLine

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="0a4c9275e1314bedae0d5f91483bc6ae",
                                               client_secret="69b8750816be4f5a954801f205085f7c",
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="user-read-playback-state user-modify-playback-state app-remote-control user-library-read playlist-read-private"))


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
    print('Shit')

playlist_id = '5Hf11xqnO1T6p39qVvfNLR'

playlist_tracks = sp.playlist_tracks(playlist_id)

playlist_info = sp.playlist(playlist_id)
total_tracks = playlist_info['tracks']['total']

import random
random_track_id = random.choice(playlist_tracks['items'][:total_tracks])['track']['id']


#sp.transfer_playback(device_id=target_device['id'], force_play=True)
sp.start_playback(device_id=target_device['id'], uris=['spotify:track:' + random_track_id])


#results1 = sp.current_playback['item']['name']
#print(results1)
