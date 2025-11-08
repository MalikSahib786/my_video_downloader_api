from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pytube import YouTube
import os
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging to see detailed output in Render's logs
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Your Netlify frontend URL must be in origins for CORS to work
origins = [
    "https://easyytdownloader.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/AnotherAPI/downloader/YT/mp4/")
async def download_youtube_video(
    youtube_url: str = Query(...)
):
    output_directory = "/tmp"
    
    if not ("youtube.com/watch?v=" in youtube_url or "youtu.be/" in youtube_url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL format")

    try:
        logging.info(f"Received URL for MP4: {youtube_url}")
        yt = YouTube(youtube_url)
        logging.info(f"Processing video: {yt.title}")
        
        video = yt.streams.filter(res="720p", file_extension="mp4").first()
        if video is None:
            logging.warning("720p stream not found, searching for best available MP4.")
            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if video is None:
                logging.error("No progressive MP4 stream found.")
                raise HTTPException(status_code=404, detail="No downloadable MP4 video stream found.")

        unique_filename = f"{yt.title} - {yt.video_id}.mp4"
        safe_filename = "".join([c for c in unique_filename if c.isalpha() or c.isdigit() or c in (' ', '-', '_', '.')]).rstrip()
        file_path = os.path.join(output_directory, safe_filename)
        
        logging.info(f"Attempting to download video to: {file_path}")
        video.download(output_path=output_directory, filename=safe_filename)
        logging.info("Video download completed.")

        if not os.path.exists(file_path):
            logging.error("File not found after video download attempt.")
            raise HTTPException(status_code=404, detail="File not found after download.")

        return FileResponse(path=file_path, filename=safe_filename, media_type="video/mp4")

    except Exception as e:
        logging.error(f"An unexpected error occurred during MP4 download: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


@app.post("/AnotherAPI/new_downloader/YT/mp3/")
async def download_youtube_audio_new(
    youtube_url: str = Query(...)
):
    output_directory = "/tmp"

    if not ("youtube.com/watch?v=" in youtube_url or "youtu.be/" in youtube_url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL format")

    try:
        logging.info(f"Received URL for MP3: {youtube_url}")
        yt = YouTube(youtube_url)
        logging.info(f"Processing audio for: {yt.title}")

        audio = yt.streams.filter(only_audio=True).first()
        if audio is None:
            logging.error("No audio stream found for the video.")
            raise HTTPException(status_code=404, detail="No audio stream found for this video.")

        unique_filename = f"{yt.title} - {yt.video_id}.mp3"
        safe_filename = "".join([c for c in unique_filename if c.isalpha() or c.isdigit() or c in (' ', '-', '_', '.')]).rstrip()
        
        file_path = os.path.join(output_directory, safe_filename)
        logging.info(f"Attempting to download audio to: {file_path}")
        audio.download(output_path=output_directory, filename=safe_filename)
        logging.info("Audio download completed.")

        if not os.path.exists(file_path):
            logging.error("File not found after audio download attempt.")
            raise HTTPException(status_code=404, detail="File not found after download.")

        return FileResponse(path=file_path, filename=safe_filename, media_type="audio/mpeg")

    except Exception as e:
        logging.error(f"An unexpected error occurred during MP3 download: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")
