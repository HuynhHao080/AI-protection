from fastapi import APIRouter
from pydantic import BaseModel
from src.filters.text_filter import check_text
from src.utils.logger import log_alert
import asyncio
from src.utils.notifier import notify_parent

router = APIRouter()

class TextInput(BaseModel):
    content: str

@router.post("/check_text")
async def check_text_api(data: TextInput):
    result = check_text(data.content)

    # Nếu toxic thì log + notify
    if result["label"].lower() == "toxic":
        await log_alert("TEXT", data.content, result)
        notify_parent("TEXT", data.content, result)

    return {"input": data.content, "result": result}
