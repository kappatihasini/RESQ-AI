import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api.routes import router

app = FastAPI(
    title="RESQ-AI: Adaptive Emergency Decision & Resource Replanning Engine",
    description="Explainable, prioritized resource-allocation decisions and continuous dynamic replanning for disaster coordination.",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/api/health")
def health():
    return {
        "engine": "RESQ-AI",
        "full_name": "Adaptive Emergency Decision & Resource Replanning Engine",
        "status": "OPERATIONAL",
    }

# Mount compiled React frontend if present
dist_candidates = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")),
    os.path.abspath(os.path.join(os.getcwd(), "frontend", "dist")),
]
for dist_path in dist_candidates:
    if os.path.isdir(dist_path) and os.path.exists(os.path.join(dist_path, "index.html")):
        app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")
        break
