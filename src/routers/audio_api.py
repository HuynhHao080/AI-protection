from fastapi import APIRouter, UploadFile, File, HTTPException
import speech_recognition as sr
import tempfile
import os
import uuid
from pydub import AudioSegment
from src.filters.text_filter import check_text
from src.utils.logger import log_alert
import asyncio
from src.utils.notifier import notify_parent

router = APIRouter()

def convert_audio_to_wav(audio_path: str, output_path: str):
    """
    Convert audio file to WAV format for better recognition
    """
    try:
        audio = AudioSegment.from_file(audio_path)
        audio.export(output_path, format="wav")
        return True
    except Exception as e:
        print(f"[ERROR] Audio conversion failed: {e}")
        return False

def analyze_audio_content(audio_path: str):
    """
    Analyze audio content for inappropriate speech
    """
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()

        # Convert to WAV if needed
        if not audio_path.endswith('.wav'):
            wav_path = audio_path.replace(os.path.splitext(audio_path)[1], '.wav')
            if convert_audio_to_wav(audio_path, wav_path):
                audio_path = wav_path

        # Load audio file
        with sr.AudioFile(audio_path) as source:
            # Record audio
            audio_data = recognizer.record(source)

            # Try to recognize speech
            try:
                text = recognizer.recognize_google(audio_data, language='vi-VN')
                print(f"[AUDIO] Recognized text: {text}")

                # Analyze recognized text
                if text.strip():
                    result = check_text(text)
                    return {
                        "transcription": text,
                        "analysis": result,
                        "has_speech": True
                    }
                else:
                    return {
                        "transcription": "",
                        "analysis": {"label": "neutral", "score": 0.9},
                        "has_speech": False
                    }

            except sr.UnknownValueError:
                print("[AUDIO] Could not understand audio")
                return {
                    "transcription": "",
                    "analysis": {"label": "neutral", "score": 0.9},
                    "has_speech": False,
                    "error": "Could not understand audio"
                }

            except sr.RequestError as e:
                print(f"[AUDIO] Recognition service error: {e}")
                return {
                    "transcription": "",
                    "analysis": {"label": "neutral", "score": 0.9},
                    "has_speech": False,
                    "error": f"Recognition service error: {e}"
                }

    except Exception as e:
        print(f"[ERROR] Audio analysis failed: {e}")
        return {
            "transcription": "",
            "analysis": {"label": "neutral", "score": 0.9},
            "has_speech": False,
            "error": str(e)
        }

@router.post("/check_audio")
async def check_audio_api(file: UploadFile = File(...)):
    """
    Check uploaded audio for inappropriate speech content
    """
    filename = file.filename or "unknown"

    # Validate file type
    if not filename.lower().endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only audio files are allowed.")

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

        # Analyze audio
        result = analyze_audio_content(temp_name)

        # Determine if content is suspicious
        is_suspicious = result["analysis"]["label"].lower() in ["toxic", "suspicious"]

        # Add metadata
        result.update({
            "filename": filename,
            "label": "suspicious" if is_suspicious else "safe",
            "score": result["analysis"]["score"]
        })

        # Log and notify if suspicious content detected
        if is_suspicious:
            await log_alert("AUDIO", filename, result)
            notify_parent("AUDIO", filename, result)

        return result

    except Exception as e:
        print(f"[ERROR] Audio processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_name):
                os.remove(temp_name)
        except Exception as e:
            print(f"[WARNING] Failed to clean up temp file {temp_name}: {e}")

@router.post("/check_audio_url")
async def check_audio_url_api(url: dict):
    """
    Check audio from URL for inappropriate content
    """
    audio_url = url.get("url")

    if not audio_url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        # Download audio temporarily
        import requests
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()

        # Get file extension from URL or default to mp3
        file_extension = os.path.splitext(audio_url)[1] or '.mp3'

        # Create temp file
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_name = os.path.join(temp_dir, f"{uuid.uuid4()}{file_extension}")

        with open(temp_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Analyze audio
        result = await check_audio_api(UploadFile(filename="url_audio" + file_extension, file=open(temp_name, "rb")))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL audio processing failed: {str(e)}")

@router.post("/check_microphone")
async def check_microphone_api(data: dict):
    """
    Check live microphone input for inappropriate speech
    Note: This would require browser permissions and WebRTC
    """
    # This is a placeholder for real-time microphone analysis
    # In a real implementation, this would use WebRTC or similar technology

    return {
        "message": "Microphone analysis requires browser integration",
        "note": "This feature would analyze live speech in real-time",
        "supported": False
    }
