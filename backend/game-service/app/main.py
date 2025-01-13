from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import game, player

app = FastAPI()

# Configurer les en-têtes CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permettre toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Permettre toutes les méthodes
    allow_headers=["*"],  # Permettre tous les en-têtes
)

# Inclure les routes du service de jeu
app.include_router(game.router, prefix="/game", tags=["game"])
app.include_router(game.router_online, prefix="/game-online", tags=["game-online"])

# Route d'accueil
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Puissance 4"}

# Lancement de l'application avec Uvicorn (lorsque vous exécutez ce fichier)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)