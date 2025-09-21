import json
import os
import datetime
from src.utils.database import SessionLocal, Alert
from src.routers.websocket_router import broadcast_alert, broadcast_stats

# Fallback JSON file
LOG_FILE = "logs/alerts.json"

async def log_alert(alert_type: str, content: str, result: dict, level: str = "warning"):
    """
    Hybrid logging: Try database first, fallback to JSON file
    """
    # Try database first
    db_logged = await try_database_logging(alert_type, content, result, level)

    # If database fails, use JSON fallback
    if not db_logged:
        try_json_fallback(alert_type, content, result, level)

async def try_database_logging(alert_type: str, content: str, result: dict, level: str = "warning"):
    """Try to log to database and broadcast via WebSocket"""
    try:
        db = SessionLocal()
        new_alert = Alert(
            type=alert_type,
            content=content,
            result=result,
            level=level
        )
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)
        print(f"[DB LOGGED] Alert {new_alert.id} saved to database")

        # Broadcast alert via WebSocket
        try:
            alert_data = {
                "id": new_alert.id,
                "type": alert_type,
                "content": content,
                "result": result,
                "level": level,
                "time": new_alert.time.isoformat()
            }
            await broadcast_alert(alert_data)
            print(f"[WS BROADCAST] Alert {new_alert.id} broadcasted to WebSocket clients")
        except Exception as ws_error:
            print(f"[WS ERROR] Failed to broadcast alert: {ws_error}")

        return True
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return False
    finally:
        try:
            db.close()
        except:
            pass

def try_json_fallback(alert_type: str, content: str, result: dict, level: str = "warning"):
    """Fallback to JSON file logging"""
    try:
        os.makedirs("logs", exist_ok=True)

        entry = {
            "time": datetime.datetime.now().isoformat(),
            "type": alert_type,
            "content": content,
            "result": result,
            "level": level,
            "source": "json_fallback"
        }

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        print(f"[JSON FALLBACK] Alert saved to {LOG_FILE}")
        print("[LOGGED]", entry)

    except Exception as e:
        print(f"[FATAL ERROR] Could not log alert: {e}")
        print(f"[ALERT DATA] Type: {alert_type}, Content: {content}, Result: {result}")
