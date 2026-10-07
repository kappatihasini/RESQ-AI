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

app.include_router(router, prefix="/api")
app.include_router(router, prefix="")
app.include_router(router, prefix="/index.py")
app.include_router(router, prefix="/index.py/api")
app.include_router(router, prefix="/api/index.py")

@app.get("/api/health")
@app.get("/health")
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
    os.path.abspath(os.path.join(os.getcwd(), "dist")),
]

found_dist = None
for dist_path in dist_candidates:
    if os.path.isdir(dist_path) and os.path.exists(os.path.join(dist_path, "index.html")):
        found_dist = dist_path
        break

if found_dist:
    assets_dir = os.path.join(found_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    from fastapi.responses import FileResponse
    index_file = os.path.join(found_dist, "index.html")

    @app.get("/")
    @app.get("/index.html")
    @app.get("/index.py")
    def serve_frontend_index():
        return FileResponse(index_file)

    app.mount("/", StaticFiles(directory=found_dist, html=True), name="frontend")
