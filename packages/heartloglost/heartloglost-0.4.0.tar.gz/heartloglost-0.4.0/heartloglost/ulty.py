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