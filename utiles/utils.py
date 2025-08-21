import subprocess
import json

# Obtiene la mejor URL del stream de YouTube usando yt-dlp

def get_stream_url_1(video_url):
    yt_dlp_cmd = ["yt-dlp", "--no-warnings", "-j", video_url]
    yt_dlp_output = subprocess.check_output(yt_dlp_cmd).decode('utf-8')
    video_info = json.loads(yt_dlp_output)
    return video_info['url']

def get_stream_url_2(video_url):
    yt_dlp_cmd = ["yt-dlp", "--no-warnings", "-j", video_url]
    yt_dlp_output = subprocess.check_output(yt_dlp_cmd).decode('utf-8')
    video_info = json.loads(yt_dlp_output)
    return video_info['url']





