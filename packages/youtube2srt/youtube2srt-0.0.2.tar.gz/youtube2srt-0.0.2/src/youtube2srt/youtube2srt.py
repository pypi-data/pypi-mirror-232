from yt_dlp import YoutubeDL
import whisper
from whisper.utils import get_writer

ydl_opts = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}


def download_audio_from_link(yt_link):
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(yt_link, download=True)
        base_filename = ydl.prepare_filename(info_dict)
        download_path = base_filename.rsplit(".", 1)[0] + ".mp3"
        return download_path, info_dict["title"]


def transcribe_audio_to_srt(audio_path, title, translate_to_english=False):
    model = whisper.load_model("large")

    task_type = "translate" if translate_to_english else None
    result = model.transcribe(audio_path, task=task_type)

    writer = get_writer("srt", ".")
    writer(
        result,
        f"{title}.srt",
        {"max_line_width": None, "max_line_count": None, "highlight_words": 0},
    )


def generate_subtitles_from_youtube_links(urls: list, translate_to_english=False):
    for yt_link in urls:
        try:
            audio_path, title = download_audio_from_link(yt_link)
            transcribe_audio_to_srt(audio_path, title, translate_to_english)
        except Exception as e:
            print(f"Error processing link {yt_link}: {e}")

    print("Subtitle generation process is completed!")
