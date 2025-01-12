import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from game_manager import GameManager
from routes import GameRoutes, router, ws_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI()
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production should be replaced with frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize game manager and routes
    game_manager = GameManager()
    GameRoutes(game_manager)
    
    # Include routers
    app.include_router(router)
    app.include_router(ws_router)
    
    @app.on_event("startup")
    async def startup_event():
        """Clean up old games periodically"""
        game_manager.cleanup_old_games()
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)