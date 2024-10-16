import os
import uuid
import yt_dlp
import shutil
import whisper
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from server.endpoints.deps import get_db


yt_router = APIRouter()


@yt_router.post("/youtube-to-text")
def youtube_to_text(yt_link: str, db: Session = Depends(get_db)):
    try:
        if not yt_link:
            raise HTTPException(status_code=404, detail="YouTube link is required")

        folder = str(uuid.uuid4())
        folder_path = f"static/{folder}"

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        audio_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": os.path.join(folder_path, "output_audio"),
        }

        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([yt_link])

        audio_path = os.path.join(folder_path, "output_audio.wav")

        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        text = result["text"]
        if text:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": text,
                    "error": None,
                    "message": "YouTube content fetched successfully.",
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )

    finally:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
