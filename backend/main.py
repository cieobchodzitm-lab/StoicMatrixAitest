"""FastAPI main entry point - L7 CNOTA Dashboard backend."""
from __future__ import annotations

import argparse
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from routers import cnota, health, passport, rewards_processor

load_dotenv()

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup hook reserved for DB / bridge init
    yield


app = FastAPI(
    title="L7 CNOTA API",
    description="Virtue-Based Governance Dashboard - L7 Rzeczpospolita",
    version="1.0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers first (must win over SPA catch-all)
app.include_router(health.router)
app.include_router(cnota.router)
app.include_router(passport.router)
app.include_router(rewards_processor.router)


@app.get("/api")
async def api_root():
    return {
        "message": "L7 CNOTA API",
        "version": "1.0.1",
        "docs": "/docs",
        "health": "/api/health",
    }


# Static assets (JS/CSS) under /assets when present
if (FRONTEND_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="assets",
    )


@app.get("/")
async def spa_index():
    index = FRONTEND_DIST / "index.html"
    if index.is_file():
        return FileResponse(index)
    return JSONResponse(
        {
            "message": "L7 CNOTA API is running. Frontend not built yet.",
            "hint": "docker build . or: cd frontend && npm ci && npm run build",
        }
    )


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str, request: Request):
    """SPA history fallback — never intercept /api or /docs."""
    if full_path.startswith(("api/", "docs", "openapi.json", "redoc")):
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    # Prefer real files from dist (favicon, etc.)
    candidate = (FRONTEND_DIST / full_path).resolve()
    try:
        candidate.relative_to(FRONTEND_DIST.resolve())
        if candidate.is_file():
            return FileResponse(candidate)
    except (ValueError, OSError):
        pass

    index = FRONTEND_DIST / "index.html"
    if index.is_file():
        return FileResponse(index)
    return JSONResponse({"detail": "Not Found", "path": full_path}, status_code=404)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="L7 CNOTA Dashboard server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=7860, help="Bind port")
    args = parser.parse_args()

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=False,
        app_dir=str(Path(__file__).resolve().parent),
    )
