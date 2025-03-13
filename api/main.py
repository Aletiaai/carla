from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core.config import settings
import os

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG_MODE)

# Mount static files
app.mount("/static", StaticFiles(directory="ui/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="ui/templates")

# Import and include routers
from api.routes.blog_routes import router as blog_router
app.include_router(blog_router, prefix="/api/blogs", tags=["blogs"])

# Root path for UI
from fastapi import Request

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)