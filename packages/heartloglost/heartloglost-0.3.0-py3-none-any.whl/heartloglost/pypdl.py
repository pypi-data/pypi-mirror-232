from pypdl import Downloader

def download_video(url, save_dest, num_connections=10):
    dl = Downloader()
    dl.start(url, save_dest, num_connections=num_connections, display=True, multithread=True)

# Example usage:
# url = "https://streamtape.com/get_video?id=d71p7vqm6gSQ0W&expires=1694917360&ip=FHIsDRqOKxSHDN&token=1M3hCTNqKz7w"
# dest = "/content/GoogleColab/lfab.mp4"
# download_video(url, dest)