import tempfile
import yt_dlp


class PodcastDownloader:
    @staticmethod
    def download_podcast(url: str) -> str:
        """Download podcast from YouTube URL"""
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": tempfile.mktemp(),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                temp_file_path = ydl.prepare_filename(info_dict)

            return temp_file_path + ".mp3"

        except Exception as e:
            raise Exception(f"Error downloading podcast: {str(e)}")
