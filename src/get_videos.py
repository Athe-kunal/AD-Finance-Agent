import requests
import os

os.environ['GOOGLE_API_KEY'] = "<<google_api_key>>"
os.environ['CHANNEL_ID'] = "UCLvnJL8htRR1T9cbSccaoVw"
os.environ['MAX_RESULTS'] = "200"
os.environ['CUTOFF_DATE'] = "2022-01-01T00:00:00Z"

def fetch_videos(url):
    video_ids = []
    response = requests.get(url)
    if response.status_code == 200:
        print("successfully fetched videos")
        try:
            video_ids.extend([b['id']['videoId'] for b in response.json()['items'] if not b['snippet']['title'].startswith('session')])
        except:
            print("exception in parsing response")
    else:
        print("error in fetching")
    videos = [f"https://www.youtube.com/watch?v={video_id}" for video_id in video_ids]
    return videos

def prepare_file(videos):
    file_path = "data/misc.txt"
    with open(file_path, 'a') as file:
        file.writelines('\n' + '\n'.join(videos))

if __name__ == "__main__":
    template_url = "https://www.googleapis.com/youtube/v3/search?key={google_api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults={max_results}&publishedAfter{cutoff_date}"
    final_url = template_url.format(google_api_key = os.environ['GOOGLE_API_KEY'], channel_id = os.environ['CHANNEL_ID'], max_results = os.environ['MAX_RESULTS'], cutoff_date = os.environ['CUTOFF_DATE'])
    videos = fetch_videos(final_url)
    prepare_file(videos)
    

