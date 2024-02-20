from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import os

import json

parent_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = parent_directory.replace('src', '')
src_folder = parent_directory + 'src'
artifacts_folder = parent_directory + 'artifacts/YouTube_API_Transcripts/'

# Define your API key and the playlist ID
api_key = "YOUR_API_KEY"
playlist_id = "PLUkh9m2BorqnhWfkEP2rRdhgpYKLS-NOJ"

# Create a YouTube Data API client
youtube = build('youtube', 'v3', developerKey=api_key)

# Function to fetch all video IDs in a playlist
def fetch_playlist_videos(playlist_id):
    video_ids = []
    next_page_token = None

    try:
        while True:
            # Fetch playlist items
            playlist_items = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,  # Max results per page
                pageToken=next_page_token
            ).execute()

            # Extract video IDs from playlist items
            for item in playlist_items['items']:
                video_ids.append(item['contentDetails']['videoId'])

            # Check if there are more pages
            next_page_token = playlist_items.get('nextPageToken')
            if not next_page_token:
                break

    except HttpError as e:
        print('An HTTP error {} occurred:\n{}'.format(e.resp.status, e.content))
    except Exception as e:
        print('An error occurred:', e)

    return video_ids

# Fetch video IDs from the playlist
video_ids = fetch_playlist_videos(playlist_id)
# Specify the path to your text file
file_path = "misc.txt"

# Open the file in read mode
with open(src_folder+"/data/"+file_path, "r") as file:
    # Read the contents of the file
    file_contents = file.read()

# Now you can work with the contents of the

videos_misc = file_contents.split("\n")

video_ids_misc = []

for vid in videos_misc:
    yt = YouTube(vid)
    video_ids_misc.append(yt.video_id)


transcript_map ={}

transcript_map_misc = {}

for v in video_ids:
    transcripts = YouTubeTranscriptApi.get_transcript(v)
    transcript_map[v] = transcripts
    
for v in video_ids_misc:
    transcripts = YouTubeTranscriptApi.get_transcript(v)
    transcript_map_misc[v] = transcripts


with open(f'{artifacts_folder}transcripts_MBA.json', 'w') as json_file:
    json.dump(transcript_map, json_file, indent=4)
    
with open(f'{artifacts_folder}misc_transcripts.json', 'w') as json_file:
    json.dump(transcript_map_misc, json_file, indent=4)


