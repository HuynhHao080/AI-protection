from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.routers import text_api, image_api, parent_alerts, stats_api, websocket_router, url_api
# from src.routers import video_api, audio_api  # Temporarily disabled due to dependency issues
import os

app = FastAPI(title="AI Child Protection – Online Safety (Upgraded)")

# Cấu hình templates
templates = Jinja2Templates(directory="src/templates")

# Gắn router
app.include_router(text_api.router, prefix="/api", tags=["Text"])
app.include_router(image_api.router, prefix="/api", tags=["Image"])
app.include_router(parent_alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(stats_api.router, prefix="/api", tags=["Stats"])
app.include_router(websocket_router.router, prefix="", tags=["WebSocket"])
# app.include_router(video_api.router, prefix="/api", tags=["Video"])  # Temporarily disabled
# app.include_router(audio_api.router, prefix="/api", tags=["Audio"])  # Temporarily disabled
app.include_router(url_api.router, prefix="/api", tags=["URL"])

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/mobile", response_class=HTMLResponse)
async def mobile_app():
    """Serve mobile app"""
    mobile_html_path = "mobile-app/index.html"
    if os.path.exists(mobile_html_path):
        return FileResponse(mobile_html_path)
    else:
        return HTMLResponse("""
        <h1>Mobile App Not Found</h1>
        <p>The mobile app files are not properly set up.</p>
        <a href="/">Go back to main dashboard</a>
        """, status_code=404)

# Mount static files cho mobile app resources
@app.get("/mobile/manifest.json")
async def mobile_manifest():
    manifest_path = "mobile-app/manifest.json"
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path)
    return HTMLResponse("{}", status_code=404)

@app.get("/mobile/sw.js")
async def mobile_sw():
    sw_path = "mobile-app/sw.js"
    if os.path.exists(sw_path):
        return FileResponse(sw_path)
    return HTMLResponse("", status_code=404)

@app.get("/mobile/icon-192.png")
async def mobile_icon_192():
    icon_path = "mobile-app/icon-192.png"
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    # Return a simple SVG icon as fallback
    return HTMLResponse("""
    <svg width="192" height="192" viewBox="0 0 192 192" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="192" height="192" rx="32" fill="#4f46e5"/>
      <path d="M96 40C96 40 72 56 72 80C72 104 96 120 96 120C96 120 120 104 120 80C120 56 96 40 96 40Z" fill="white" opacity="0.9"/>
      <circle cx="96" cy="80" r="16" fill="#4f46e5"/>
      <path d="M80 104L64 120M112 104L128 120M96 128L96 144" stroke="white" stroke-width="4" stroke-linecap="round"/>
    </svg>
    """, status_code=200, headers={"Content-Type": "image/svg+xml"})

@app.get("/mobile/icon-512.png")
async def mobile_icon_512():
    icon_path = "mobile-app/icon-512.png"
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    # Return a simple SVG icon as fallback
    return HTMLResponse("""
    <svg width="512" height="512" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="512" height="512" rx="80" fill="#4f46e5"/>
      <path d="M256 120C256 120 200 160 200 220C200 280 256 320 256 320C256 320 312 280 312 220C312 160 256 120 256 120Z" fill="white" opacity="0.9"/>
      <circle cx="256" cy="220" r="40" fill="#4f46e5"/>
      <path d="M220 280L180 320M292 280L332 320M256 340L256 380" stroke="white" stroke-width="8" stroke-linecap="round"/>
    </svg>
    """, status_code=200, headers={"Content-Type": "image/svg+xml"})
