from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re

PREFIX_TOXIC = "toxic-speech-detection: "
MODEL_NAME = "tarudesu/ViHateT5-base-HSD"

# Global variables để track model status
MODEL_AVAILABLE = False
tokenizer = None
model = None

def load_model():
    """Load model với error handling"""
    global MODEL_AVAILABLE, tokenizer, model

    try:
        print(f"[INFO] Loading text classification model: {MODEL_NAME}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        MODEL_AVAILABLE = True
        print("[INFO] Text classification model loaded successfully")
        return True
    except Exception as e:
        print(f"[WARNING] Failed to load text model: {e}")
        MODEL_AVAILABLE = False
        return False

# Try to load model on import
load_model()

def advanced_vietnamese_text_check(content: str):
    """
    Advanced Vietnamese text analysis with multiple detection layers
    """
    content_lower = content.lower()

    # Multi-layer detection system
    detection_results = {
        "cyberbullying": 0.0,
        "sexual_content": 0.0,
        "scam": 0.0,
        "hate_speech": 0.0,
        "violence": 0.0
    }

    # 1. Cyberbullying Detection (Bắt nạt mạng)
    cyberbullying_keywords = [
        'đồ ngu', 'đồ đần', 'đồ chó', 'đồ khốn', 'thằng ngu', 'con đĩ', 'mày ngu',
        'tao đánh', 'tao giết', 'tao đâm', 'mày chết đi', 'mày biến đi',
        'stupid', 'idiot', 'bitch', 'asshole', 'bastard', 'loser', 'ugly'
    ]

    cyberbullying_count = sum(1 for keyword in cyberbullying_keywords if keyword in content_lower)
    detection_results["cyberbullying"] = min(cyberbullying_count * 0.3, 1.0)

    # 2. Sexual Content Detection (Nội dung gợi dục)
    sexual_keywords = [
        'địt', 'đụ', 'cặc', 'lồn', 'buồi', 'vú', 'mông', 'khỏa thân',
        'phim sex', 'phim người lớn', 'sex', 'porn', 'fuck', 'suck', 'lick'
    ]

    sexual_count = sum(1 for keyword in sexual_keywords if keyword in content_lower)
    detection_results["sexual_content"] = min(sexual_count * 0.4, 1.0)

    # 3. Scam Detection (Lừa đảo)
    scam_keywords = [
        'chuyển khoản', 'gửi tiền', 'stk', 'số tài khoản', 'mật khẩu',
        'thông tin cá nhân', 'click vào link', 'trúng thưởng', 'giải thưởng',
        'khuyến mãi', 'giảm giá sốc', 'miễn phí', 'tặng quà'
    ]

    scam_count = sum(1 for keyword in scam_keywords if keyword in content_lower)
    detection_results["scam"] = min(scam_count * 0.2, 1.0)

    # 4. Hate Speech Detection (Ngôn từ thù địch)
    hate_keywords = [
        'phân biệt', 'kì thị', 'dân tộc', 'tôn giáo', 'chủng tộc',
        'ghét', 'khinh', 'xem thường', 'hạ đẳng', 'tồi tệ'
    ]

    hate_count = sum(1 for keyword in hate_keywords if keyword in content_lower)
    detection_results["hate_speech"] = min(hate_count * 0.35, 1.0)

    # 5. Violence Detection (Bạo lực)
    violence_keywords = [
        'đánh nhau', 'giết', 'chém', 'đâm', 'bắn', 'đấm', 'đá',
        'hành hạ', 'tra tấn', 'tàn nhẫn', 'máu me', 'xác chết'
    ]

    violence_count = sum(1 for keyword in violence_keywords if keyword in content_lower)
    detection_results["violence"] = min(violence_count * 0.4, 1.0)

    # Calculate overall score
    max_score = max(detection_results.values())
    total_score = sum(detection_results.values()) / len(detection_results)

    # Determine primary category
    primary_category = max(detection_results.keys(), key=lambda k: detection_results[k])

    # Classification logic
    if max_score > 0.7:
        label = "toxic"
        confidence = max_score
    elif total_score > 0.4:
        label = "suspicious"
        confidence = total_score
    else:
        label = "neutral"
        confidence = 0.9

    return {
        "label": label,
        "score": confidence,
        "categories": detection_results,
        "primary_category": primary_category,
        "analysis": "multi_layer_detection"
    }

def check_text(content: str):
    """
    Check text content for toxicity
    """
    if not content or not content.strip():
        return {"label": "neutral", "score": 0.9}

    # Try AI model first if available
    if MODEL_AVAILABLE and model is not None and tokenizer is not None:
        try:
            # thêm prefix
            input_text = PREFIX_TOXIC + content
            inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True, max_length=256)

            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=10)  # output text nhỏ

            decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # decoded có thể là "toxic" / "not_toxic" hoặc text mô tả
            label = decoded.lower().strip()

            # có thể thêm logic nếu decoded chứa từ "toxic" thì mark toxic, ngược lại neutral
            if "toxic" in label or "hate" in label or "offensive" in label:
                return {"label": "toxic", "score": 0.9}
            else:
                return {"label": "neutral", "score": 0.9}

        except Exception as e:
            print(f"[ERROR] AI text analysis failed: {e}")
            # Fallback to advanced analysis
            return advanced_vietnamese_text_check(content)
    else:
        # Use advanced analysis when model not available
        return advanced_vietnamese_text_check(content)
