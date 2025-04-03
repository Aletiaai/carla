from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.routes.blog_routes import router as blog_router
from core.config import settings
import os

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG_MODE,
    servers=[
        {
            "url": "https://carla-app-3yywngljtq-ew.a.run.app",
            "description": "Production Cloud Run URL"
        }
    ]
)

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory="ui/static"),
    name="static"
)

# Configure templates with HTTPS awareness
templates = Jinja2Templates(directory="ui/templates")
templates.env.globals["url_for"] = app.url_path_for  # Ensures HTTPS URLs


# Include routers
app.include_router(blog_router, prefix="/api/blogs", tags=["blogs"])

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)