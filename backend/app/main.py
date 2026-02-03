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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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
