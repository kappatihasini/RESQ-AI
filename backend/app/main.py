from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router

app = FastAPI(
    title="RESQ-AI: Adaptive Emergency Decision & Resource Replanning Engine",
    description="Explainable, prioritized resource-allocation decisions and continuous dynamic replanning for disaster coordination.",
    version="1.0.0",
)

# CORS configuration for local React / Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "engine": "RESQ-AI",
        "full_name": "Adaptive Emergency Decision & Resource Replanning Engine",
        "domain": "Smart Automation / Disaster Resource Coordination",
        "status": "OPERATIONAL",
        "simulation_mode": True,
        "docs_url": "/docs",
    }
