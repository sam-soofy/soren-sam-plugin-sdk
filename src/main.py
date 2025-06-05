from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router

app = FastAPI(
    title="Sam LMS Plugin",
    description="A FastAPI-based plugin for Soren Marketplace",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add version 1 routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "success", "message": "Plugin API is running"}
