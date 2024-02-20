from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi

import json

# Define your API key and the playlist ID
api_key = "YOUR_GCP_API_KEY"
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

transcript_map ={}

for v in video_ids:
    transcripts = YouTubeTranscriptApi.get_transcript(v)
    transcript_map[v] = transcripts
    
with open('transcripts_MBA.json', 'w') as json_file:
    json.dump(transcript_map, json_file, indent=4)


