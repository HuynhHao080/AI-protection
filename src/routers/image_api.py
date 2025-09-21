from fastapi import APIRouter, UploadFile, File, HTTPException
from src.filters.image_filter import check_image
from src.utils.logger import log_alert
import asyncio
from src.utils.notifier import notify_parent
import shutil, os, uuid, tempfile

router = APIRouter()

@router.post("/check_image")
async def check_image_api(file: UploadFile = File(...)):
    """
    Check uploaded image for inappropriate content
    """
    filename = file.filename or "unknown"

    # Validate file type
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only image files are allowed.")

    # Create temp directory if it doesn't exist
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Generate unique temp file path
    file_extension = os.path.splitext(filename)[1]
    temp_name = os.path.join(temp_dir, f"{uuid.uuid4()}{file_extension}")

    try:
        # Save uploaded file to temp location
        with open(temp_name, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Check image content
        result = check_image(temp_name)

        # Log and notify if unsafe content detected
        if result.get("label", "").lower() in ["nsfw", "porn", "unsafe", "suspicious"]:
            await log_alert("IMAGE", filename, result)
            notify_parent("IMAGE", filename, result)

        return {"filename": filename, "result": result}

    except Exception as e:
        print(f"[ERROR] Image processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_name):
                os.remove(temp_name)
        except Exception as e:
            print(f"[WARNING] Failed to clean up temp file {temp_name}: {e}")
