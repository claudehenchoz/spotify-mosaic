import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.oauth2 as oauth2
import json
from PIL import Image
from PIL import ImageDraw
import requests
from io import BytesIO
from dotenv import load_dotenv
import os


market     = "US"
width      = 320
height     = 320
rows       = 5
columns    = 8

# gets vars
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_PLAYLIST_USER = os.getenv("SPOTIFY_PLAYLIST_USER")
SPOTIFY_PLAYLIST_ID = os.getenv("SPOTIFY_PLAYLIST_ID")
OUTPUT_FILE = os.getenv("OUTPUT_FILE")

# authenticates
credentials = oauth2.SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET)
token = credentials.get_access_token()
spotify = spotipy.Spotify(auth=token)

# gets all playlist items (we have to get all to produce reverse order list)
results = spotify.user_playlist_tracks(SPOTIFY_PLAYLIST_USER, SPOTIFY_PLAYLIST_ID, limit=100)
tracks = results['items']
while results['next']:
    results = spotify.next(results)
    tracks.extend(results['items'])

# get album art for newest n tracks
img_list   = []
for track in tracks[-(rows*columns):]:
    response = requests.get(track["track"]["album"]["images"][0]["url"])
    img = Image.open(BytesIO(response.content))
    img_list.append(img)
for image in img_list:
    image.thumbnail((width, height))


columns = int(len(img_list)/rows)

# creates a new empty image, RGB mode
mosaic = Image.new('RGB',(columns* width,rows*height))

# prepares draw and font objects to render text
draw   = ImageDraw.Draw(mosaic)

# creates mosaic
k=0
for j in range( 0, rows * height, height ):
    for i in range( 0, columns * width, width ):
        # paste the image at location i,j:
        mosaic.paste( img_list[k], (i,j) )
        # Select next image and text
        k = k + 1

# Save image to file
mosaic.save(OUTPUT_FILE, 'JPEG', quality=95)
