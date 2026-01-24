import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, List

router = APIRouter(
    prefix="/api/scripts/{script_id}/assets",
    tags=["assets"]
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"

@router.get("/", response_model=Dict[str, List[str]])
async def list_assets(script_id: str):
    script_dir = BASE_DIR / script_id
    if not script_dir.exists():
         raise HTTPException(status_code=404, detail="Script not found")
         
    # Handle Assets vs Assests typo support
    assets_dir = script_dir / "Assets"
    if not assets_dir.exists():
        if (script_dir / "Assests").exists():
            assets_dir = script_dir / "Assests"
    
    assets = {
        "Backgrounds": [],
        "Musics": [],
        "Sounds": [],
        "Effects": [],
        "Other": []
    }
    
    if not assets_dir.exists():
         return assets

    for root, dirs, files in os.walk(assets_dir):
        rel_root = Path(root).relative_to(assets_dir)
        parts = rel_root.parts
        
        category = "Other"
        if len(parts) > 0:
            top_folder = parts[0]
            # Use top folder as category
            category = top_folder
            if category not in assets:
                assets[category] = []
        
        # Files in root of Assets go to 'Other' unless we mapped them
        if len(parts) == 0:
            category = "Other"

        for file in files:
            # Full path relative to Assets root
            full_rel_path = (rel_root / file).as_posix()
            if full_rel_path.startswith("./"):
                full_rel_path = full_rel_path[2:]
            
            assets[category].append(full_rel_path)
            
    return assets
