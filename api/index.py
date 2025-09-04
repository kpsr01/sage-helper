import json
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/index")
async def get_transcript(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})

    video_id = body.get("videoId") if isinstance(body, dict) else None

    if not video_id:
        return JSONResponse(status_code=400, content={"error": "Missing videoId parameter"})

    try:
        # Try English first; then fall back to any available
        transcript_list = None
        preferred_langs = ["en", "en-US", "en-GB"]
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except VideoUnavailable:
            return JSONResponse(status_code=404, content={"error": "Video is unavailable"})

        transcript = None
        # Attempt manual or generated English
        for lang in preferred_langs:
            if transcript_list is None:
                break
            try:
                transcript = transcript_list.find_transcript([lang])
                break
            except NoTranscriptFound:
                continue
            except TranscriptsDisabled:
                return JSONResponse(status_code=404, content={"error": "Transcripts are disabled for this video"})

        # Fallback: first available generated or translated transcript
        if transcript is None:
            try:
                transcript = transcript_list.find_manually_created_transcript(transcript_list._manually_created_transcripts.keys())
            except Exception:
                pass
        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript(transcript_list._generated_transcripts.keys())
            except Exception:
                pass

        if transcript is None:
            return JSONResponse(status_code=404, content={"error": "No transcript available for this video"})

        entries = transcript.fetch()
        structured = [
            {
                "text": e.get("text", ""),
                "start": e.get("start", 0.0),
                "duration": e.get("duration", 0.0)
            } for e in entries if e.get("text")
        ]
        full_text = " ".join(ch["text"].strip() for ch in structured)

        response = {
            "transcript": structured,
            "metadata": {
                "language": transcript.language_code,
                "isGenerated": getattr(transcript, 'is_generated', False),
                "segmentCount": len(structured)
            }
        }
        return JSONResponse(status_code=200, content=response)

    except TranscriptsDisabled:
        return JSONResponse(status_code=404, content={"error": "Transcripts are disabled for this video"})
    except NoTranscriptFound:
        return JSONResponse(status_code=404, content={"error": "No transcript found"})
    except VideoUnavailable:
        return JSONResponse(status_code=404, content={"error": "Video unavailable"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal server error", "details": str(e)})

# For local dev (optional)
# uvicorn api.index:app --reload
