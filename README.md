# Transcript Service

A minimal FastAPI-based serverless endpoint (Vercel) for fetching YouTube video transcripts using `youtube-transcript-api`.

## Endpoint
POST /api/index
Body: {"videoId": "<YouTubeVideoID>"}

## Response (success)
{
  "transcript": [
    {"text": "...", "start": 12.34, "duration": 4.56},
    ...
  ],
  "metadata": {
    "language": "en",
    "isGenerated": true,
    "segmentCount": 123
  }
}

## Deploy on Vercel
1. vercel init (or add this folder to an existing project)
2. vercel deploy --prod

Ensure Python runtime is enabled by Vercel (see `vercel.json`).

## Local Dev
Install deps:
```
pip install -r requirements.txt
```
Run:
```
uvicorn api.index:app --reload --port 8000
```
Test:
```
curl -X POST http://127.0.0.1:8000/api/index -H "Content-Type: application/json" -d '{"videoId": "dQw4w9WgXcQ"}'
```
