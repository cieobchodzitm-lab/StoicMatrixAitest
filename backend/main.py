"""FastAPI main entry point — L7 CNOTA Dashboard backend."""
import argparse
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from routers import health, cnota, passport, rewards_processor

load_dotenv()

app = FastAPI(
    title="L7 CNOTA API",
    description="Virtue-Based Governance Dashboard — L7 Rzeczpospolita",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(cnota.router)
app.include_router(passport.router)
app.include_router(rewards_processor.router)

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"


@app.on_event("startup")
async def startup_event():
    if FRONTEND_DIST.exists():
        app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")


@app.get("/")
async def root():
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "L7 CNOTA API is running. Frontend not built yet."}


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
    )
