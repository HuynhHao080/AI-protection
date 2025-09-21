from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.database import get_db, Alert
import json, os

router = APIRouter()

def get_alerts_from_db(db: Session, limit: int):
    """Get alerts from database"""
    try:
        alerts = db.query(Alert).order_by(Alert.time.desc()).limit(limit).all()
        return [alert.__dict__ for alert in alerts]
    except Exception as e:
        print(f"[DB READ ERROR] {e}")
        return []

def get_alerts_from_json(limit: int):
    """Get alerts from JSON file as fallback"""
    try:
        file_path = "logs/alerts.json"
        if not os.path.exists(file_path):
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]  # lấy log mới nhất
            return [json.loads(line) for line in lines]
    except Exception as e:
        print(f"[JSON READ ERROR] {e}")
        return []

@router.get("/alerts")
async def get_alerts(limit: int = 20, db: Session = Depends(get_db)):
    """
    Get alerts with hybrid approach: Try DB first, fallback to JSON
    """
    # Try database first
    db_alerts = get_alerts_from_db(db, limit)

    # If no DB alerts, try JSON fallback
    if not db_alerts:
        json_alerts = get_alerts_from_json(limit)
        if json_alerts:
            print(f"[JSON FALLBACK] Serving {len(json_alerts)} alerts from JSON file")
        return json_alerts

    return db_alerts
