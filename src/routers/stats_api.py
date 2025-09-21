from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.database import get_db, Alert
from collections import Counter
import json, os

router = APIRouter()

def get_stats_from_db(db: Session):
    """Get stats from database"""
    try:
        alerts = db.query(Alert).all()

        total_alerts = len(alerts)
        alerts_by_type = Counter(alert.type for alert in alerts)

        labels_by_type = {}
        for alert in alerts:
            alert_type = alert.type
            label = alert.result["label"]
            if alert_type not in labels_by_type:
                labels_by_type[alert_type] = Counter()
            labels_by_type[alert_type][label] += 1

        return {
            "total_alerts": total_alerts,
            "alerts_by_type": alerts_by_type,
            "labels_by_type": labels_by_type,
            "source": "database"
        }
    except Exception as e:
        print(f"[DB STATS ERROR] {e}")
        return None

def get_stats_from_json():
    """Get stats from JSON file as fallback"""
    try:
        file_path = "logs/alerts.json"
        if not os.path.exists(file_path):
            return {
                "total_alerts": 0,
                "alerts_by_type": {},
                "labels_by_type": {},
                "source": "json"
            }

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            alerts = [json.loads(line) for line in lines]

        total_alerts = len(alerts)
        alerts_by_type = Counter(alert["type"] for alert in alerts)

        labels_by_type = {}
        for alert in alerts:
            alert_type = alert["type"]
            label = alert["result"]["label"]
            if alert_type not in labels_by_type:
                labels_by_type[alert_type] = Counter()
            labels_by_type[alert_type][label] += 1

        return {
            "total_alerts": total_alerts,
            "alerts_by_type": alerts_by_type,
            "labels_by_type": labels_by_type,
            "source": "json"
        }
    except Exception as e:
        print(f"[JSON STATS ERROR] {e}")
        return {
            "total_alerts": 0,
            "alerts_by_type": {},
            "labels_by_type": {},
            "source": "error"
        }

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get stats with hybrid approach: Try DB first, fallback to JSON
    """
    # Try database first
    db_stats = get_stats_from_db(db)

    # If DB fails or returns no data, try JSON fallback
    if db_stats is None or db_stats["total_alerts"] == 0:
        json_stats = get_stats_from_json()
        if json_stats["total_alerts"] > 0:
            print(f"[JSON FALLBACK] Serving stats from JSON file ({json_stats['total_alerts']} alerts)")
        return json_stats

    return db_stats
