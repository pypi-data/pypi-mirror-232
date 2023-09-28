import os
import asyncio
import math

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

def list_files(directory_path):
    try:
        # Get a list of all files in the specified directory
        files = os.listdir(directory_path)

        # Print the names of all files
        for file_name in files:
            print(file_name)
    except OSError as e:
        print(f"Error: {e}")

# Replace 'directory_path' with the path to the directory you want to list files from
# directory_path = "/content/torr/Wednesday.S01.COMPLETE.720p.NF.WEBRip.x264-GalaxyTV[TGx]"
# list_files(directory_path)