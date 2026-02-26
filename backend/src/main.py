from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import scripts, assets, characters, preview

app = FastAPI(title="Script Editor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(scripts.router)
app.include_router(assets.router)
app.include_router(characters.router)
app.include_router(preview.router)

@app.get("/")
async def root():
    return {"message": "Script Editor API is running"}
