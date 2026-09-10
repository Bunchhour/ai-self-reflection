from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, reflections, experiments, emotions, goals, stats, users

app = FastAPI(
    title="Self-Reflection API",
    description="AI-powered Self-Reflection Platform Backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(reflections.router)
app.include_router(experiments.router)
app.include_router(emotions.router)
app.include_router(goals.router)
app.include_router(stats.router)
app.include_router(users.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
