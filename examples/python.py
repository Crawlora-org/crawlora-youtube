import os

from crawlora_youtube import YouTubeClient

api_key = os.environ.get("CRAWLORA_API_KEY")
if not api_key:
    raise RuntimeError("Set CRAWLORA_API_KEY before running this example.")

with YouTubeClient(api_key=api_key) as client:
    search = client.search(q='science explainers', type='video')
    print('search', search)
    video = client.video(id='dQw4w9WgXcQ')
    print('video', video)
    transcript = client.transcript(id='dQw4w9WgXcQ', format='text')
    print('transcript', transcript)
