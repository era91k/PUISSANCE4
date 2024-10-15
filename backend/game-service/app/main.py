from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import game, player

# Créer une instance de FastAPI
app = FastAPI()

# Configuration des CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permettre toutes les origines (à modifier pour production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes des différentes fonctionnalités
app.include_router(game.router, prefix="/game", tags=["game"])
app.include_router(player.router, prefix="/player", tags=["player"])

# Route d'accueil
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Puissance 4"}

# Lancement de l'application avec Uvicorn (lorsque vous exécutez ce fichier)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
