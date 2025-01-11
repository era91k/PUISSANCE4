from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permettre toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Permettre toutes les méthodes
    allow_headers=["*"],  # Permettre tous les en-têtes
)

app.include_router(ai.router, prefix="/ai")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Service for Connect 4"}