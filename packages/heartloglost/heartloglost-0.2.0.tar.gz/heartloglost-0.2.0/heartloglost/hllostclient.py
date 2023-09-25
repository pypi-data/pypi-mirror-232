import requests
from bs4 import BeautifulSoup
import json
import os
import asyncio
import math

class STClient:
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key
    def auth(self):
        if not all((self.username, self.api_key)):
            raise ValueError("Username, password, and API key must be specified.")
        Api_info = f"https://api.streamtape.com/account/info?login={self.username}&key={self.api_key}"
        try:
            response = requests.get(Api_info)
            response.raise_for_status()  # Raise an exception if the request was not successful
            json_data = response.json()
            a_api = json_data["status"]
            if int(a_api) == 200:
                print("You are authorised")
            else:
                print("Unsuccessful ! Check credentials.")
        except Exception as e:
            print(e)

    def upload_video(self, file_path, folder_id):
        Main_API = f"https://api.streamtape.com/file/ul?login={self.username}&key={self.api_key}&folder={self.folder_id}"
        try:
            response = requests.get(Main_API)
            response.raise_for_status()  # Raise an exception if the request was not successful
            json_data = response.json()
            temp_api = json_data["result"]["url"]
            print("Temp URL:" + temp_api)
            files = {'file': open(file_path, 'rb')}
            response = requests.post(temp_api, files=files)
            response.raise_for_status()
            data_f = response.json()
            download_link = data_f["result"]["url"]
            print(download_link)
            return download_link
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return f"Error {e}"

    def get_image_url(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            og_image_tag = soup.find('meta', {'name': 'og:image'})
            if og_image_tag:
                image_url = og_image_tag['content']
                return image_url
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

async def progress(current, total):
    prog = "Progress: " + f"{current * 100 / total:.1f}%"
    print(f"{current * 100 / total:.1f}%")
    return prog

# Function get size
def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    size = humanbytes(size_bytes)
    print(size)
    return size

def humanbytes(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

# Example usage:
# client = HLClient("your_username", "your_api_key")
# client.auth()
# client.upload_video("path_to_video.mp4", "folder_id")
# upload_video()
