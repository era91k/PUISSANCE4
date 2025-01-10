from fastapi import FastAPI, Depends
from app.routers import user
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the frontend origin here for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration de la connexion à MongoDB
mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
client = MongoClient(mongo_uri)
db = client["user_db"]

# Inclure les routes du service utilisateur
app.include_router(user.router)

# Route d'accueil
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Utilisateur"}

# Lancement de l'application avec Uvicorn (lorsque vous exécutez ce fichier)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)