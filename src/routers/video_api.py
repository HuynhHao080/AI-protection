from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import cv2
import numpy as np
import tempfile
import os
import uuid
import moviepy as mp
from src.filters.image_filter import check_image
from src.utils.logger import log_alert
import asyncio
from src.utils.notifier import notify_parent

router = APIRouter()

async def analyze_video_frames(video_path: str, sample_rate: int = 30):
    """
    Analyze video frames for inappropriate content
    """
    try:
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        suspicious_frames = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Sample frames at specified rate
            if frame_count % sample_rate == 0:
                # Convert frame to image for analysis
                temp_frame_path = f"temp/frame_{frame_count}.jpg"
                cv2.imwrite(temp_frame_path, frame)

                # Analyze frame
                result = check_image(temp_frame_path)

                if result.get("label", "").lower() in ["nsfw", "porn", "unsafe", "suspicious"]:
                    suspicious_frames.append({
                        "frame": frame_count,
                        "timestamp": frame_count / cap.get(cv2.CAP_PROP_FPS),
                        "result": result
                    })

                # Clean up temp frame
                os.remove(temp_frame_path)

        cap.release()

        return {
            "total_frames": total_frames,
            "analyzed_frames": frame_count // sample_rate,
            "suspicious_frames": len(suspicious_frames),
            "details": suspicious_frames
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")

@router.post("/check_video")
async def check_video_api(file: UploadFile = File(...)):
    """
    Check uploaded video for inappropriate content
    """
    filename = file.filename or "unknown"

    # Validate file type
    if not filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only video files are allowed.")

    # Create temp directory if it doesn't exist
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Generate unique temp file path
    file_extension = os.path.splitext(filename)[1]
    temp_name = os.path.join(temp_dir, f"{uuid.uuid4()}{file_extension}")

    try:
        # Save uploaded file to temp location
        with open(temp_name, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Get video info
        clip = mp.VideoFileClip(temp_name)
        duration = clip.duration
        fps = clip.fps

        # Analyze video frames
        analysis_result = await analyze_video_frames(temp_name, sample_rate=30)

        # Determine overall result
        is_suspicious = analysis_result["suspicious_frames"] > 0

        result = {
            "filename": filename,
            "duration": duration,
            "fps": fps,
            "total_frames": analysis_result["total_frames"],
            "analyzed_frames": analysis_result["analyzed_frames"],
            "suspicious_frames": analysis_result["suspicious_frames"],
            "suspicious_percentage": (analysis_result["suspicious_frames"] / max(analysis_result["analyzed_frames"], 1)) * 100,
            "details": analysis_result["details"],
            "label": "suspicious" if is_suspicious else "safe",
            "score": min(analysis_result["suspicious_frames"] * 0.1, 1.0)
        }

        # Log and notify if suspicious content detected
        if is_suspicious:
            await log_alert("VIDEO", filename, result)
            notify_parent("VIDEO", filename, result)

        return result

    except Exception as e:
        print(f"[ERROR] Video processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")

    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_name):
                os.remove(temp_name)
        except Exception as e:
            print(f"[WARNING] Failed to clean up temp file {temp_name}: {e}")

@router.post("/check_video_url")
async def check_video_url_api(url: dict):
    """
    Check video from URL for inappropriate content
    """
    video_url = url.get("url")

    if not video_url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        # Download video temporarily
        import requests
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        # Create temp file
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_name = os.path.join(temp_dir, f"{uuid.uuid4()}.mp4")

        with open(temp_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Analyze video
        with open(temp_name, "rb") as video_file:
            upload_file = UploadFile(filename="url_video.mp4", file=video_file)
            result = await check_video_api(upload_file)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL video processing failed: {str(e)}")
