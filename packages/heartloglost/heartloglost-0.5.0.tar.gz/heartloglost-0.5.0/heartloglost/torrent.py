from torrentp import TorrentDownloader
import os

# magnet = "magnet:?xt=urn:btih:8B7E180839C73FA9E1534CAE6CC31079D0A0D059&dn=Wednesday.S01.COMPLETE.720p.NF.WEBRip.x264-GalaxyTV&tr=udp://tracker.coppersurfer.tk:6969/announce&tr=udp://9.rarbg.to:2920/announce&tr=udp://tracker.opentrackr.org:1337&tr=udp://tracker.internetwarriors.net:1337/announce&tr=udp://tracker.leechers-paradise.org:6969/announce&tr=udp://tracker.coppersurfer.tk:6969/announce&tr=udp://tracker.pirateparty.gr:6969/announce&tr=udp://tracker.cyberia.is:6969/announce"

# dir = "/content/torr"

def torrent(magnet_URL, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    torrent_file = TorrentDownloader(magnet_URL, save_dir)
    torrent_file.start_download()