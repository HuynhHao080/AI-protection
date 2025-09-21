from transformers import pipeline
import os
from PIL import Image
import numpy as np

# Mô hình phát hiện NSFW (ảnh không phù hợp)
try:
    image_classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection")
    MODEL_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] Failed to load NSFW model: {e}")
    MODEL_AVAILABLE = False

def check_image(image_path: str):
    """
    Kiểm tra hình ảnh có an toàn hay không.
    Trả về kết quả phân tích với label và score.
    """
    # Kiểm tra file tồn tại
    if not os.path.exists(image_path):
        return {
            "label": "error",
            "score": 0.0,
            "error": "File not found"
        }

    try:
        # Nếu model khả dụng, sử dụng AI
        if MODEL_AVAILABLE:
            result = image_classifier(image_path)[0]
            return {
                "label": result["label"],
                "score": float(result["score"])
            }
        else:
            # Fallback: Kiểm tra đơn giản dựa trên kích thước và format
            return simple_image_check(image_path)

    except Exception as e:
        print(f"[ERROR] Image analysis failed: {e}")
        # Fallback khi AI model gặp lỗi
        return simple_image_check(image_path)

def simple_image_check(image_path: str):
    """
    Kiểm tra hình ảnh đơn giản dựa trên metadata
    """
    try:
        with Image.open(image_path) as img:
            # Kiểm tra kích thước file (MB)
            file_size = os.path.getsize(image_path) / (1024 * 1024)

            # Kiểm tra kích thước ảnh
            width, height = img.size

            # Logic đơn giản: Ảnh lớn có thể đáng ngờ
            if file_size > 5.0:  # > 5MB
                return {
                    "label": "suspicious",
                    "score": 0.7
                }
            elif width * height > 1000000:  # > 1 megapixel
                return {
                    "label": "suspicious",
                    "score": 0.5
                }
            else:
                return {
                    "label": "safe",
                    "score": 0.9
                }

    except Exception as e:
        return {
            "label": "error",
            "score": 0.0,
            "error": str(e)
        }
