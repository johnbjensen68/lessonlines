import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import (
    events_router,
    standards_router,
    timelines_router,
    auth_router,
    users_router,
    export_router,
)

app = FastAPI(
    title="LessonLines API",
    description="API for the LessonLines timeline builder for K-12 teachers",
    version="1.0.0",
)

# CORS middleware with dynamic origins
# In production, CORS_ORIGINS env var should be set to the Amplify domain
default_origins = ["http://localhost:5173", "http://localhost:3000"]
cors_origins_env = os.environ.get("CORS_ORIGINS", "")
if cors_origins_env:
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
else:
    cors_origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(events_router)
app.include_router(standards_router)
app.include_router(timelines_router)
app.include_router(export_router)


@app.get("/")
def root():
    return {"message": "LessonLines API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
